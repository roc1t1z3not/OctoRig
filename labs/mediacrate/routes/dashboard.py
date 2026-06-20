# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, redirect, url_for, render_template
from db import get_db


def init(app):

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        channel = db.execute(
            "SELECT * FROM channels WHERE owner_id = ?", (session['user_id'],)
        ).fetchone()
        subs = db.execute(
            "SELECT c.* FROM channels c JOIN subscriptions s ON s.channel_id = c.id WHERE s.subscriber_id = ?",
            (session['user_id'],),
        ).fetchall()
        return render_template('dashboard.html', channel=channel, subs=subs)
