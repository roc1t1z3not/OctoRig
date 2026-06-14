# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
from flask import request, render_template, make_response, session, redirect, url_for
from db import get_db


UPLOAD_DIR = '/app/static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


def init(app):

    @app.route('/user/<username>')
    def user_profile(username):
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            return render_template('404.html'), 404
        posts = db.execute(
            "SELECT p.*, c.name as community_name FROM posts p "
            "JOIN communities c ON p.community_id = c.id "
            "WHERE p.user_id = ? AND p.status = 'published' ORDER BY p.created_at DESC LIMIT 10",
            (user['id'],)
        ).fetchall()
        resp = make_response(render_template('profile.html', target=user, posts=posts))
        resp.set_cookie('sv_session', 'FLAG{sv_xss_stored_bio}', httponly=False)
        return resp

    @app.route('/profile/edit', methods=['GET', 'POST'])
    def profile_edit():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db      = get_db()
        u       = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        error   = None
        success = None
        if request.method == 'POST':
            username = request.form.get('username', u['username']).strip()
            email    = request.form.get('email',    u['email']).strip()
            bio      = request.form.get('bio',      u['bio'])
            # VULN: mass assignment — role, karma, is_admin not rendered in form but processed if submitted
            role     = request.form.get('role',     u['role'])
            karma    = request.form.get('karma',    u['karma'])
            db.execute(
                "UPDATE users SET username = ?, email = ?, bio = ?, role = ?, karma = ? WHERE id = ?",
                (username, email, bio, role, karma, session['user_id'])
            )
            db.commit()
            u       = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
            success = 'Profile updated.'
        return render_template('profile_edit.html', u=u, error=error, success=success)

    @app.route('/profile/avatar', methods=['POST'])
    def profile_avatar():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db    = get_db()
        u     = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        error = None
        if 'avatar' not in request.files or request.files['avatar'].filename == '':
            error = 'No file selected.'
            return render_template('profile_edit.html', u=u, error=error, success=None)
        f    = request.files['avatar']
        ext  = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
        # VULN: extension-only check — no MIME type validation
        if ext not in ALLOWED_EXTENSIONS:
            error = 'Only jpg, jpeg, png, gif allowed.'
            return render_template('profile_edit.html', u=u, error=error, success=None)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{u['username']}_{f.filename}"
        f.save(os.path.join(UPLOAD_DIR, filename))
        db.execute("UPDATE users SET avatar = ? WHERE id = ?", (filename, session['user_id']))
        db.commit()
        return redirect(url_for('profile_edit'))
