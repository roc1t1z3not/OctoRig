# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import hashlib
import sqlite3
import time
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _md5(s):
    return hashlib.md5(s.encode()).hexdigest()


def init(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            phash    = _md5(password)
            db       = get_db()
            # VULN: SQLi — f-string on both username and phash
            user = db.execute(
                f"SELECT * FROM users WHERE username = '{username}' AND password_hash = '{phash}'"
            ).fetchone()
            if not user:
                exists = db.execute(
                    f"SELECT id FROM users WHERE username = '{username}'"
                ).fetchone()
                error = 'Incorrect password.' if exists else 'No account found for that username.'
            else:
                session['user_id'] = user['id']
                # VULN: open redirect — ?next= accepted without host validation
                next_url = request.args.get('next') or url_for('index')
                return redirect(next_url)
        return render_template('login.html', error=error)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email    = request.form.get('email', '').strip()
            if not (username and password and email):
                error = 'All fields are required.'
            else:
                db  = get_db()
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    db.execute(
                        "INSERT INTO users (username, email, password_hash, role, karma, created_at)"
                        " VALUES (?, ?, ?, 'user', 0, ?)",
                        (username, email, _md5(password), now)
                    )
                    db.commit()
                    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                    session['user_id'] = user['id']
                    return redirect(url_for('index'))
                except sqlite3.IntegrityError:
                    error = 'Username already taken.'
        return render_template('register.html', error=error)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/reset', methods=['GET', 'POST'])
    def reset_request():
        info  = None
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            db       = get_db()
            user     = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user:
                # VULN: predictable reset token — md5(username + epoch floored to hour)
                token = _md5(username + str(int(time.time()) // 3600))
                db.execute("UPDATE users SET reset_token = ? WHERE id = ?", (token, user['id']))
                db.commit()
                info = f'Reset link: /reset/{token}'
            else:
                error = 'No account with that username.'
        return render_template('reset_request.html', info=info, error=error)

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    def reset_confirm(token):
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE reset_token = ?", (token,)).fetchone()
        if not user:
            return render_template('reset_confirm.html', error='Invalid or expired token.', valid=False)
        error   = None
        success = None
        if request.method == 'POST':
            password = request.form.get('password', '').strip()
            if not password:
                error = 'Password cannot be empty.'
            else:
                db.execute(
                    "UPDATE users SET password_hash = ?, reset_token = NULL WHERE id = ?",
                    (_md5(password), user['id'])
                )
                db.commit()
                success = 'Password updated. You can now log in.'
        return render_template('reset_confirm.html', error=error, success=success, valid=True, token=token)
