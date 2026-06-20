# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, redirect, url_for, render_template
from db import get_db


def init(app):

    @app.route('/playlists')
    def playlists():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        playlist = db.execute(
            "SELECT * FROM playlists WHERE owner_id = ?", (session['user_id'],)
        ).fetchone()
        items = []
        if playlist:
            items = db.execute(
                "SELECT v.* FROM playlist_items pi JOIN videos v ON v.id = pi.video_id "
                "WHERE pi.playlist_id = ?",
                (playlist['id'],),
            ).fetchall()
        return render_template('playlists.html', playlist=playlist, items=items)

    @app.route('/videos/<int:video_id>/watch-later', methods=['POST'])
    def add_watch_later(video_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        playlist = db.execute(
            "SELECT * FROM playlists WHERE owner_id = ?", (session['user_id'],)
        ).fetchone()
        if not playlist:
            db.execute(
                "INSERT INTO playlists (owner_id, name) VALUES (?, 'Watch Later')",
                (session['user_id'],),
            )
            db.commit()
            playlist = db.execute(
                "SELECT * FROM playlists WHERE owner_id = ?", (session['user_id'],)
            ).fetchone()
        db.execute(
            "INSERT INTO playlist_items (playlist_id, video_id) VALUES (?, ?)",
            (playlist['id'], video_id),
        )
        db.commit()
        return redirect(url_for('video_detail', video_id=video_id))
