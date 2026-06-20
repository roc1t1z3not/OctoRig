# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db

# Threshold beyond which the freight-credit reconciliation alarm fires.
CREDIT_ALARM_THRESHOLD = 1_000_000


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: business logic — freight-credit transfers accept negative and
    # unbounded amounts with no balance check, so sending a negative amount to
    # another account inflates the sender's own balance without limit. Once a
    # balance crosses the reconciliation threshold the flag is leaked.
    @app.route('/billing', methods=['GET', 'POST'])
    def billing():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        uid = session['user_id']
        message = None
        flag = None

        if request.method == 'POST':
            to_id = request.form.get('to_account', '').strip()
            amount = request.form.get('amount', '').strip()
            try:
                to_id = int(to_id)
                amount = float(amount)
            except (TypeError, ValueError):
                message = 'Invalid transfer parameters.'
                to_id = amount = None

            if amount is not None:
                db.execute(
                    "INSERT OR IGNORE INTO freight_credits (account_id, balance) VALUES (?, 0)", (uid,)
                )
                db.execute(
                    "INSERT OR IGNORE INTO freight_credits (account_id, balance) VALUES (?, 0)", (to_id,)
                )
                db.execute(
                    "UPDATE freight_credits SET balance = balance - ? WHERE account_id = ?", (amount, uid)
                )
                db.execute(
                    "UPDATE freight_credits SET balance = balance + ? WHERE account_id = ?", (amount, to_id)
                )
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                db.execute(
                    "INSERT INTO credit_ledger (account_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
                    (uid, -amount, f'transfer to account {to_id}', now),
                )
                db.commit()
                message = f'Transferred {amount} freight credits to account {to_id}.'

        row = db.execute("SELECT balance FROM freight_credits WHERE account_id = ?", (uid,)).fetchone()
        balance = row['balance'] if row else 0.0
        if balance >= CREDIT_ALARM_THRESHOLD:
            fr = db.execute("SELECT value FROM _flags WHERE name = 'biz-credit'").fetchone()
            flag = fr['value'] if fr else None

        ledger = db.execute(
            "SELECT * FROM credit_ledger WHERE account_id = ? ORDER BY id DESC LIMIT 12", (uid,)
        ).fetchall()
        accounts = db.execute("SELECT id, username, full_name FROM users ORDER BY id").fetchall()
        return render_template(
            'billing.html', balance=balance, ledger=ledger, accounts=accounts,
            message=message, flag=flag, threshold=CREDIT_ALARM_THRESHOLD,
        )
