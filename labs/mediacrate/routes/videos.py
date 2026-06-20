# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: IDOR — visibility ('public'/'unlisted'/'private') is enforced only
    # by not linking to the video in the UI; the route itself never checks it
    # or who owns the parent channel. Any logged-in user can view any video by
    # guessing the sequential id.
    @app.route('/videos/<int:video_id>')
    def video_detail(video_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        video = db.execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        if not video:
            return render_template('404.html'), 404
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (video['channel_id'],)).fetchone()
        return render_template('video_detail.html', video=video, channel=channel)

    # VULN: SQLi — search term interpolated straight into a LIKE clause.
    @app.route('/videos/search')
    def video_search():
        redir = _require_login()
        if redir:
            return redir
        q = request.args.get('q', '')
        results = []
        error = None
        if q:
            try:
                results = get_db().execute(
                    f"SELECT id, title, description, views FROM videos WHERE title LIKE '%{q}%' AND visibility = 'public'"
                ).fetchall()
            except Exception as e:
                error = str(e)
        return render_template('video_search.html', q=q, results=results, error=error)

    # "Report this video" — feeds the admin review queue. The note is stored
    # and later rendered unescaped in the admin review panel (stored XSS).
    @app.route('/videos/<int:video_id>/report', methods=['POST'])
    def video_report(video_id):
        redir = _require_login()
        if redir:
            return redir
        note = request.form.get('note', '')
        get_db().execute(
            "INSERT INTO comment_reports (video_id, reported_by, note, created_at) VALUES (?, ?, ?, ?)",
            (video_id, session['user_id'], note, datetime.utcnow().isoformat(sep=' ', timespec='seconds')),
        )
        get_db().commit()
        return redirect(url_for('video_detail', video_id=video_id))
