import random
from datetime import date, datetime
from flask import request, render_template, session, redirect, url_for, abort, jsonify
from db import get_db

TAN_BACKDOOR = '1337'


def init(app):

    # ── Request Money ─────────────────────────────────────────────────────────

    @app.route('/request-money', methods=['GET', 'POST'])
    def request_money():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db  = get_db()
        error   = None
        success = None

        my_accounts = db.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (uid,)
        ).fetchall()

        if request.method == 'POST':
            target_input = request.form.get('target', '').strip()
            to_account   = request.form.get('to_account', '').strip()
            amount_str   = request.form.get('amount', '').strip()
            memo         = request.form.get('memo', '').strip()

            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                error = 'Please enter a valid amount.'
                return render_template('request_money.html', my_accounts=my_accounts,
                                       error=error, success=success)

            # Resolve target user by username or email
            target_user = db.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (target_input, target_input)
            ).fetchone()
            if not target_user:
                error = 'No user found with that username or email.'
                return render_template('request_money.html', my_accounts=my_accounts,
                                       error=error, success=success)

            # Resolve requester's credit account
            credit_acc = db.execute(
                "SELECT * FROM accounts WHERE account_number = ? OR iban = ?",
                (to_account, to_account)
            ).fetchone()
            if not credit_acc or credit_acc['user_id'] != uid:
                error = 'Invalid destination account — must be one of your accounts.'
                return render_template('request_money.html', my_accounts=my_accounts,
                                       error=error, success=success)

            # Find a checking account to debit from the target
            debit_acc = db.execute(
                "SELECT * FROM accounts WHERE user_id = ? AND account_type = 'checking' LIMIT 1",
                (target_user['id'],)
            ).fetchone()
            if not debit_acc:
                error = 'Target user has no eligible account.'
                return render_template('request_money.html', my_accounts=my_accounts,
                                       error=error, success=success)

            tan_challenge = str(random.randint(1, 76))
            created_at    = str(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

            db.execute(
                "INSERT INTO payment_requests "
                "(requester_id, target_id, from_account, to_account, amount, memo, pin, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)",
                (uid, target_user['id'], debit_acc['id'], credit_acc['id'],
                 amount, memo, tan_challenge, created_at)
            )
            db.commit()
            req_id = db.execute("SELECT last_insert_rowid() as id").fetchone()['id']

            requester = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
            name = requester['full_name'] or requester['username']

            # Internal notification for target — IDOR: no ownership check on /notifications/<id>
            db.execute(
                "INSERT INTO notifications (user_id, type, title, message, link, read, created_at) "
                "VALUES (?, 'payment_request', ?, ?, ?, 0, ?)",
                (
                    target_user['id'],
                    f'Payment request from {name}',
                    f'{name} is requesting ${amount:.2f}. Memo: "{memo or "—"}". '
                    f'To approve, open the request and enter TAN code at position {tan_challenge} from your TAN sheet.',
                    f'/payment-requests/{req_id}',
                    created_at
                )
            )
            db.commit()
            success = (f'Request sent to {target_user["username"]}. '
                       f'They will see a notification to approve.')

        return render_template('request_money.html', my_accounts=my_accounts,
                               error=error, success=success)

    # ── Payment Request Detail ────────────────────────────────────────────────

    # IDOR: no ownership check — any logged-in user can view any request
    @app.route('/payment-requests/<int:req_id>')
    def payment_request_detail(req_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        req = db.execute(
            "SELECT pr.*, "
            "ru.username as requester_name, ru.full_name as requester_fullname, "
            "tu.username as target_name, "
            "fa.account_number as from_acc_num, fa.iban as from_iban, "
            "ta.account_number as to_acc_num, ta.iban as to_iban "
            "FROM payment_requests pr "
            "JOIN users ru ON pr.requester_id = ru.id "
            "JOIN users tu ON pr.target_id    = tu.id "
            "JOIN accounts fa ON pr.from_account = fa.id "
            "JOIN accounts ta ON pr.to_account   = ta.id "
            "WHERE pr.id = ?",
            (req_id,)
        ).fetchone()
        if not req:
            abort(404)
        return render_template('payment_request.html', req=req)

    # ── Approve Payment Request — IDOR on uid param ───────────────────────────

    @app.route('/payment-requests/<int:req_id>/approve', methods=['POST'])
    def approve_payment_request(req_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        req = db.execute(
            "SELECT * FROM payment_requests WHERE id = ? AND status = 'pending'", (req_id,)
        ).fetchone()
        if not req:
            abort(404)

        uid_param = int(request.form.get('uid', 0))
        tan_param = request.form.get('tan', '').strip()

        # VULN: trusts uid from POST body instead of session['user_id']
        # An attacker can submit uid=<victim_id> without being that user
        if req['target_id'] != uid_param:
            return render_template('payment_request.html', req=req,
                                   error='Approval failed: user mismatch.')

        # ── TAN validation ─────────────────────────────────────────────────
        if tan_param == TAN_BACKDOOR:
            tan_row = None  # backdoor accepted silently
        else:
            tan_row = db.execute(
                "SELECT * FROM tan_codes WHERE user_id = ? AND position = ? AND used = 0",
                (uid_param, req['pin'])
            ).fetchone()
            if not tan_row or tan_row['pin'] != tan_param:
                return render_template('payment_request.html', req=req,
                                       error='Invalid TAN code. Please check your TAN sheet.')

        # Execute the transfer
        db.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (req['amount'], req['from_account'])
        )
        db.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (req['amount'], req['to_account'])
        )
        src_acc = db.execute("SELECT account_number FROM accounts WHERE id = ?",
                             (req['from_account'],)).fetchone()
        dst_acc = db.execute("SELECT account_number FROM accounts WHERE id = ?",
                             (req['to_account'],)).fetchone()
        today = str(date.today())
        db.execute(
            "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
            "VALUES (?, 'debit', ?, ?, ?, ?)",
            (req['from_account'], req['amount'],
             f'Payment request #{req_id}', dst_acc['account_number'], today)
        )
        db.execute(
            "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
            "VALUES (?, 'credit', ?, ?, ?, ?)",
            (req['to_account'], req['amount'],
             f'Payment request #{req_id}', src_acc['account_number'], today)
        )
        db.execute(
            "UPDATE payment_requests SET status = 'approved' WHERE id = ?", (req_id,)
        )
        if tan_row:
            db.execute(
                "UPDATE tan_codes SET used = 1 WHERE user_id = ? AND position = ?",
                (uid_param, req['pin'])
            )
        db.commit()
        return redirect(url_for('dashboard'))

    # ── Notifications ─────────────────────────────────────────────────────────

    @app.route('/notifications')
    def notifications():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid  = session['user_id']
        db   = get_db()
        rows = db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        return render_template('notifications.html', notifications=rows)

    # IDOR: no user_id check — any logged-in user can read any notification
    @app.route('/notifications/<int:notif_id>')
    def notification_detail(notif_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        notif = db.execute(
            "SELECT * FROM notifications WHERE id = ?", (notif_id,)
        ).fetchone()
        if not notif:
            abort(404)
        # Mark read (no ownership check here either)
        db.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notif_id,))
        db.commit()
        return render_template('notification_detail.html', notif=notif)
