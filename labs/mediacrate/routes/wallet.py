# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import session, redirect, url_for, render_template, request
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/wallet')
    def wallet():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        tips = db.execute(
            "SELECT t.*, c.name AS channel_name FROM tips t JOIN channels c ON c.id = t.channel_id "
            "WHERE t.tipper_id = ? ORDER BY t.id DESC",
            (session['user_id'],),
        ).fetchall()
        return render_template('wallet.html', user=user, tips=tips)

    # VULN: CSRF — no token, no Origin/Referer check. A self-submitting HTML
    # form hosted anywhere can drain a logged-in victim's coin balance to an
    # attacker-controlled channel the moment they open it.
    @app.route('/channels/<int:channel_id>/tip', methods=['POST'])
    def channel_tip(channel_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        if not channel:
            return render_template('404.html'), 404
        try:
            amount = int(request.form.get('amount', '0'))
        except ValueError:
            amount = 0
        uid = session['user_id']
        flag = None
        if amount > 0 and channel['owner_id'] != uid:
            user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
            if user['coins'] >= amount:
                db.execute("UPDATE users SET coins = coins - ? WHERE id = ?", (amount, uid))
                db.execute("UPDATE channels SET coin_balance = coin_balance + ? WHERE id = ?", (amount, channel_id))
                db.execute(
                    "INSERT INTO tips (channel_id, tipper_id, amount, created_at) VALUES (?, ?, ?, ?)",
                    (channel_id, uid, amount, datetime.utcnow().isoformat(sep=' ', timespec='seconds')),
                )
                db.commit()
                flag = 'FLAG{mc_csrf_tip_drained}'
        return render_template('tip_result.html', channel=channel, amount=amount, flag=flag)
