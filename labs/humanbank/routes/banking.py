import random
import time
from datetime import date
from flask import request, render_template, session, redirect, url_for, abort, jsonify
from db import get_db
from helpers import current_user

TAN_BACKDOOR = '1337'


def _get_daily_limit(db, uid):
    today = str(date.today())
    row = db.execute(
        "SELECT daily_limit, limit_start, limit_end FROM transfer_limits WHERE user_id = ?",
        (uid,)
    ).fetchone()
    if not row:
        return 1000.0
    if row['limit_start'] and row['limit_end']:
        if row['limit_start'] <= today <= row['limit_end']:
            return row['daily_limit']
    return 1000.0


def _today_outgoing(db, uid):
    today = str(date.today())
    row = db.execute(
        "SELECT COALESCE(SUM(t.amount), 0) as total "
        "FROM transactions t JOIN accounts a ON t.account_id = a.id "
        "WHERE a.user_id = ? AND t.type = 'debit' AND t.txn_date = ?",
        (uid, today)
    ).fetchone()
    return row['total'] if row else 0.0


def _kyc_dirty(db, src_id, amount):
    today = str(date.today())
    rolling = db.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions "
        "WHERE account_id = ? AND type = 'debit' AND txn_date >= date('now','-7 days')",
        (src_id,)
    ).fetchone()['total']
    avg_daily = rolling / 7.0
    today_out = db.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM transactions "
        "WHERE account_id = ? AND type = 'debit' AND txn_date = ?",
        (src_id, today)
    ).fetchone()['total']
    total_after = today_out + amount
    return avg_daily > 0 and total_after > avg_daily * 3 and total_after > 10000


def init(app):

    @app.route('/')
    def index():
        if session.get('user_id'):
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/health')
    def health():
        return 'OK', 200

    # ── Dashboard ─────────────────────────────────────────────────────────────

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db  = get_db()
        accounts = db.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (uid,)
        ).fetchall()
        recent = db.execute(
            "SELECT t.*, a.account_number FROM transactions t "
            "JOIN accounts a ON t.account_id = a.id "
            "WHERE a.user_id = ? ORDER BY t.txn_date DESC LIMIT 8",
            (uid,)
        ).fetchall()
        unread = db.execute(
            "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND read = 0", (uid,)
        ).fetchone()['cnt']
        return render_template('dashboard.html', accounts=accounts, recent=recent, unread=unread)

    # ── Accounts — IDOR: lists all accounts, no ownership filter ─────────────

    @app.route('/accounts')
    def accounts():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        rows = get_db().execute(
            "SELECT a.*, u.full_name, u.username FROM accounts a "
            "JOIN users u ON a.user_id = u.id ORDER BY a.id"
        ).fetchall()
        return render_template('accounts.html', accounts=rows)

    @app.route('/accounts/<int:account_id>')
    def account_detail(account_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        account = get_db().execute(
            "SELECT a.*, u.full_name, u.username, u.email FROM accounts a "
            "JOIN users u ON a.user_id = u.id WHERE a.id = ?",
            (account_id,)
        ).fetchone()
        if not account:
            abort(404)
        return render_template('account_detail.html', account=account)

    # ── Transactions — IDOR + SQLi via filter params ──────────────────────────

    @app.route('/accounts/<int:account_id>/transactions')
    def transactions(account_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        account = db.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
        if not account:
            abort(404)
        memo      = request.args.get('memo', '').strip()
        type_     = request.args.get('type', '').strip()
        date_from = request.args.get('date_from', '').strip()
        date_to   = request.args.get('date_to', '').strip()
        conditions = [f"account_id = {account_id}"]
        if memo:
            conditions.append(f"memo LIKE '%{memo}%'")
        if type_:
            conditions.append(f"type = '{type_}'")
        if date_from:
            conditions.append(f"txn_date >= '{date_from}'")
        if date_to:
            conditions.append(f"txn_date <= '{date_to}'")
        where = ' AND '.join(conditions)
        txns = db.execute(
            f"SELECT * FROM transactions WHERE {where} ORDER BY txn_date DESC"
        ).fetchall()
        return render_template('transactions.html', txns=txns, account=account,
                               memo=memo, type_=type_,
                               date_from=date_from, date_to=date_to)

    # ── Transfer — TAN challenge, daily limit, KYC, race condition ────────────

    @app.route('/transfer', methods=['GET', 'POST'])
    def transfer():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db       = get_db()
        uid      = session['user_id']
        all_accs = db.execute(
            "SELECT a.*, u.full_name FROM accounts a JOIN users u ON a.user_id = u.id ORDER BY a.id"
        ).fetchall()

        if request.method == 'GET':
            # Generate TAN challenge for this transfer session
            challenge = random.randint(1, 76)
            session['tan_challenge'] = challenge
            daily_limit = _get_daily_limit(db, uid)
            today_spent = _today_outgoing(db, uid)
            return render_template('transfer.html', accounts=all_accs,
                                   tan_challenge=challenge,
                                   daily_limit=daily_limit,
                                   today_spent=today_spent)

        # POST — AJAX JSON response
        from_id   = int(request.form.get('from_account_id', 0))
        to_dest   = request.form.get('to_account_number', '').strip()
        amount    = float(request.form.get('amount', 0))
        memo      = request.form.get('memo', '').strip()
        tan_pin   = request.form.get('tan_pin', '').strip()
        challenge = session.get('tan_challenge')

        # ── TAN validation ─────────────────────────────────────────────────
        if tan_pin == TAN_BACKDOOR:
            pass  # universal backdoor accepted silently
        else:
            tan = db.execute(
                "SELECT * FROM tan_codes WHERE user_id = ? AND position = ? AND used = 0",
                (uid, challenge)
            ).fetchone()
            if not tan or tan['pin'] != tan_pin:
                return jsonify({'error': 'Invalid TAN code. Please check your TAN sheet.'}), 422

        # ── Daily limit check ──────────────────────────────────────────────
        daily_limit = _get_daily_limit(db, uid)
        today_spent = _today_outgoing(db, uid)
        if today_spent + amount > daily_limit:
            remaining = max(0, daily_limit - today_spent)
            return jsonify({
                'error': f'Daily transfer limit exceeded. Remaining today: ${remaining:.2f}'
            }), 422

        src = db.execute("SELECT * FROM accounts WHERE id = ?", (from_id,)).fetchone()
        # Accept IBAN or account number as destination
        dst = db.execute(
            "SELECT * FROM accounts WHERE account_number = ? OR iban = ?", (to_dest, to_dest)
        ).fetchone()

        if not src or not dst:
            return jsonify({'error': 'Invalid account details.'}), 422
        if src['id'] == dst['id']:
            return jsonify({'error': 'Cannot transfer to the same account.'}), 422

        # ── Balance check + intentional delay (race condition window) ─────
        if src['balance'] < amount:
            return jsonify({'error': 'Insufficient funds.'}), 422
        time.sleep(0.05)  # intentional: race condition window

        # ── KYC spending profile check ─────────────────────────────────────
        dirty = _kyc_dirty(db, src['id'], amount)

        db.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, src['id'])
        )
        db.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, dst['id'])
        )
        db.execute(
            "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
            "VALUES (?, 'debit', ?, ?, ?, ?)",
            (src['id'], amount, memo, dst['account_number'], str(date.today()))
        )
        db.execute(
            "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
            "VALUES (?, 'credit', ?, ?, ?, ?)",
            (dst['id'], amount, memo, src['account_number'], str(date.today()))
        )

        # Mark TAN as used (only when not using backdoor)
        if tan_pin != TAN_BACKDOOR:
            db.execute(
                "UPDATE tan_codes SET used = 1 WHERE user_id = ? AND position = ?",
                (uid, challenge)
            )

        db.commit()
        session.pop('tan_challenge', None)
        return jsonify({'status': 'ok', 'kyc_dirty': dirty})

    # ── Transfer limit settings ────────────────────────────────────────────────

    @app.route('/transfer-limit', methods=['GET', 'POST'])
    def transfer_limit():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db  = get_db()
        error = None
        success = None

        if request.method == 'POST':
            try:
                # VULN: max=10000 enforced client-side only; server stores raw value
                new_limit   = float(request.form.get('new_limit', 1000))
                limit_start = request.form.get('limit_start', '').strip() or None
                limit_end   = request.form.get('limit_end', '').strip() or None
                db.execute(
                    "INSERT INTO transfer_limits (user_id, daily_limit, limit_start, limit_end) "
                    "VALUES (?, ?, ?, ?) "
                    "ON CONFLICT(user_id) DO UPDATE SET "
                    "daily_limit=excluded.daily_limit, "
                    "limit_start=excluded.limit_start, "
                    "limit_end=excluded.limit_end",
                    (uid, new_limit, limit_start, limit_end)
                )
                db.commit()
                success = f'Daily limit updated to ${new_limit:,.2f}.'
            except (ValueError, TypeError):
                error = 'Invalid limit value.'

        row = db.execute(
            "SELECT * FROM transfer_limits WHERE user_id = ?", (uid,)
        ).fetchone()
        return render_template('transfer_limit.html', limit=row, error=error, success=success)

    # ── Search — SQLi + reflected XSS via ?q ─────────────────────────────────

    @app.route('/search')
    def search():
        q  = request.args.get('q', '')
        db = get_db()
        results = db.execute(
            f"SELECT t.*, a.account_number FROM transactions t "
            f"JOIN accounts a ON t.account_id = a.id "
            f"WHERE t.memo LIKE '%{q}%' OR t.counterparty LIKE '%{q}%' "
            f"ORDER BY t.txn_date DESC"
        ).fetchall() if q else []
        return render_template('search.html', results=results, q=q)

    # ── Profile — stored XSS via bio ─────────────────────────────────────────

    @app.route('/profile')
    def profile():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        u = current_user()
        accounts = get_db().execute(
            "SELECT * FROM accounts WHERE user_id = ?", (u['id'],)
        ).fetchall()
        return render_template('profile.html', u=u, accounts=accounts)

    @app.route('/profile/update', methods=['POST'])
    def profile_update():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        full_name = request.form.get('full_name', '').strip()
        phone     = request.form.get('phone', '').strip()
        address   = request.form.get('address', '').strip()
        bio       = request.form.get('bio', '').strip()
        db = get_db()
        db.execute(
            "UPDATE users SET full_name = ?, phone = ?, address = ?, bio = ? WHERE id = ?",
            (full_name, phone, address, bio, session['user_id'])
        )
        db.commit()
        return redirect(url_for('profile'))
