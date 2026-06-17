# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db

# Threshold beyond which the "energy credit reconciliation" alarm leaks a flag.
CREDIT_ALARM_THRESHOLD = 1_000_000


def _require_login():
    if not session.get('operator_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/credits', methods=['GET', 'POST'])
    def credits():
        redir = _require_login()
        if redir:
            return redir
        db   = get_db()
        uid  = session['operator_id']
        flag = None
        message = None

        if request.method == 'POST':
            to_id  = request.form.get('to_operator', '').strip()
            amount = request.form.get('amount', '').strip()
            try:
                to_id  = int(to_id)
                amount = float(amount)
            except (TypeError, ValueError):
                message = 'Invalid transfer parameters.'
                to_id = amount = None

            if amount is not None:
                # VULN: business logic — no positivity check and no balance check.
                # A negative amount moves credit the wrong way, inflating the
                # sender's own balance without limit.
                db.execute(
                    "UPDATE credits SET balance = balance - ? WHERE operator_id = ?",
                    (amount, uid),
                )
                db.execute(
                    "INSERT OR IGNORE INTO credits (operator_id, balance) VALUES (?, 0)",
                    (to_id,),
                )
                db.execute(
                    "UPDATE credits SET balance = balance + ? WHERE operator_id = ?",
                    (amount, to_id),
                )
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
                db.execute(
                    "INSERT INTO credit_ledger (operator_id, delta, reason, created_at) VALUES (?, ?, ?, ?)",
                    (uid, -amount, f'transfer to operator {to_id}', now),
                )
                db.commit()
                message = f'Transferred {amount} credits to operator {to_id}.'

        balance = db.execute(
            "SELECT balance FROM credits WHERE operator_id = ?", (uid,)
        ).fetchone()
        balance = balance['balance'] if balance else 0.0

        # Reconciliation alarm fires when a balance becomes implausibly large.
        if balance >= CREDIT_ALARM_THRESHOLD:
            row = db.execute("SELECT value FROM _flags WHERE name = 'biz-credits'").fetchone()
            flag = row['value'] if row else None

        ledger = db.execute(
            "SELECT * FROM credit_ledger WHERE operator_id = ? ORDER BY id DESC LIMIT 12",
            (uid,),
        ).fetchall()
        operators = db.execute(
            "SELECT id, username, full_name FROM operators ORDER BY id"
        ).fetchall()
        return render_template(
            'credits.html',
            balance=balance, ledger=ledger, operators=operators,
            message=message, flag=flag, threshold=CREDIT_ALARM_THRESHOLD,
        )
