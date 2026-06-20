# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, redirect, url_for, render_template
from db import get_db


def init(app):

    @app.route('/notifications')
    def notifications():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        rows = db.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC",
            (session['user_id'],),
        ).fetchall()
        return render_template('notifications.html', notifications=rows)
