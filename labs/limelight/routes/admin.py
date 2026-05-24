# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import request, render_template, render_template_string, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/admin')
    def admin_index():
        # VULN: broken access control — checks login but never verifies is_admin
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db       = get_db()
        users    = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        bookings = db.execute(
            "SELECT b.*, u.username, m.title, s.show_time"
            " FROM bookings b"
            " JOIN users u ON b.user_id = u.id"
            " JOIN showings s ON b.showing_id = s.id"
            " JOIN movies m ON s.movie_id = m.id"
            " ORDER BY b.id DESC LIMIT 50"
        ).fetchall()
        movies   = db.execute("SELECT * FROM movies ORDER BY id").fetchall()
        return render_template('admin.html', users=users, bookings=bookings, movies=movies)

    @app.route('/admin/movie/toggle/<int:movie_id>', methods=['POST'])
    def admin_toggle_movie(movie_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        db.execute("UPDATE movies SET is_showing = 1 - is_showing WHERE id = ?", (movie_id,))
        db.commit()
        return redirect(url_for('admin_index'))

    @app.route('/admin/announce', methods=['GET', 'POST'])
    def admin_announce():
        # VULN: broken access control — no admin check
        if not session.get('user_id'):
            return redirect(url_for('login'))
        preview = None
        error   = None
        tmpl    = ''
        if request.method == 'POST':
            tmpl = request.form.get('template', '')
            try:
                # VULN: SSTI — user-supplied template rendered directly via render_template_string
                preview = render_template_string(tmpl)
            except Exception as e:
                error = str(e)
        return render_template('admin_announce.html', preview=preview, error=error, tmpl=tmpl)

    @app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
    def admin_delete_user(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return redirect(url_for('admin_index'))
