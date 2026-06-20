# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import hashlib
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


# VULN: mass assignment — any key the client sends that matches an allow-listed
# column is written straight to the users row, including columns that were
# never meant to be self-editable (plan, role).
PROFILE_FIELDS = ('full_name', 'email', 'plan', 'role')


def init(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    # VULN: SQLi — username interpolated straight into the query string.
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            pw_md5 = hashlib.md5(password.encode()).hexdigest()
            row = get_db().execute(
                f"SELECT * FROM users WHERE username = '{username}' AND password = '{pw_md5}'"
            ).fetchone()
            if row:
                session['user_id'] = row['id']
                return redirect(url_for('dashboard'))
            error = 'Invalid username or master password.'
        return render_template('login.html', error=error)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            email = request.form.get('email', '').strip()
            if not username or not password or not email:
                error = 'All fields are required.'
            else:
                db = get_db()
                exists = db.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
                if exists:
                    error = 'That username is already taken.'
                else:
                    pw_md5 = hashlib.md5(password.encode()).hexdigest()
                    db.execute(
                        "INSERT INTO users (username, password, email, full_name, role, plan, is_admin, api_token, notes) "
                        "VALUES (?, ?, ?, '', 'user', 'free', 0, '', '')",
                        (username, pw_md5, email),
                    )
                    db.commit()
                    row = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
                    session['user_id'] = row['id']
                    return redirect(url_for('dashboard'))
        return render_template('register.html', error=error)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        uid = session['user_id']
        saved = False
        if request.method == 'POST':
            data = request.get_json(silent=True) or request.form
            updates = {k: v for k, v in data.items() if k in PROFILE_FIELDS}
            if updates:
                set_clause = ', '.join(f"{col} = ?" for col in updates)
                db.execute(
                    f"UPDATE users SET {set_clause} WHERE id = ?",
                    (*updates.values(), uid),
                )
                db.commit()
                saved = True
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        return render_template('profile.html', user=user, saved=saved, now=datetime.utcnow())
