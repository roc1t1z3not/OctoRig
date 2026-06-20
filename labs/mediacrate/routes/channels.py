# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, render_template, redirect, url_for
from db import get_db


def init(app):

    @app.route('/channels/<int:channel_id>')
    def channel_detail(channel_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        if not channel:
            return render_template('404.html'), 404
        videos = db.execute(
            "SELECT * FROM videos WHERE channel_id = ? AND visibility = 'public' ORDER BY id",
            (channel_id,),
        ).fetchall()
        return render_template('channel_detail.html', channel=channel, videos=videos)

    # VULN: relation-level IDOR — exclusive_content is meant to be gated by a
    # tier>=2 row in subscriptions, but this route only checks that *some*
    # session exists, never consulting the subscriptions table at all.
    @app.route('/channels/<int:channel_id>/exclusive')
    def channel_exclusive(channel_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        if not channel:
            return render_template('404.html'), 404
        return render_template('channel_exclusive.html', channel=channel)
