from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db
from helpers import current_user


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
        return render_template('dashboard.html', accounts=accounts, recent=recent)

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

    # ── Transfer — IDOR on source account + business logic flaws ─────────────

    @app.route('/transfer', methods=['GET', 'POST'])
    def transfer():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db       = get_db()
        all_accs = db.execute(
            "SELECT a.*, u.full_name FROM accounts a JOIN users u ON a.user_id = u.id ORDER BY a.id"
        ).fetchall()
        error = None
        if request.method == 'POST':
            from_id = int(request.form.get('from_account_id', 0))
            to_num  = request.form.get('to_account_number', '').strip()
            amount  = float(request.form.get('amount', 0))
            memo    = request.form.get('memo', '').strip()
            src = db.execute("SELECT * FROM accounts WHERE id = ?", (from_id,)).fetchone()
            dst = db.execute(
                "SELECT * FROM accounts WHERE account_number = ?", (to_num,)
            ).fetchone()
            if not src or not dst:
                error = 'Invalid account details.'
            elif src['id'] == dst['id']:
                error = 'Cannot transfer to the same account.'
            else:
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
                    (src['id'], amount, memo, to_num, str(date.today()))
                )
                db.execute(
                    "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
                    "VALUES (?, 'credit', ?, ?, ?, ?)",
                    (dst['id'], amount, memo, src['account_number'], str(date.today()))
                )
                db.commit()
                return redirect(url_for('dashboard'))
        return render_template('transfer.html', accounts=all_accs, error=error)

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
