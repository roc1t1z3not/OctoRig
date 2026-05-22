import hashlib
import sqlite3
import time
from datetime import datetime, timedelta
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            db = get_db()
            # VULN: SQLi — f-string, no parameterisation
            user = db.execute(
                f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            ).fetchone()
            if not user:
                exists = db.execute(
                    f"SELECT id FROM users WHERE username = '{username}'"
                ).fetchone()
                error = 'Incorrect password.' if exists else 'No account found for that username.'
            else:
                session['user_id'] = user['id']
                return redirect(url_for('dashboard'))
        return render_template('login.html', error=error)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            username  = request.form.get('username', '').strip()
            password  = request.form.get('password', '').strip()
            email     = request.form.get('email', '').strip()
            full_name = request.form.get('full_name', '').strip()
            if not (username and password and email):
                error = 'All fields are required.'
            else:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password, email, full_name) VALUES (?, ?, ?, ?)",
                        (username, password, email, full_name)
                    )
                    db.commit()
                    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                    session['user_id'] = user['id']
                    return redirect(url_for('dashboard'))
                except sqlite3.IntegrityError:
                    error = 'Username already taken.'
        return render_template('register.html', error=error)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    # VULN: weak reset token — md5(username + epoch_seconds)
    @app.route('/reset', methods=['GET', 'POST'])
    def reset_request():
        token_info = None
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            db    = get_db()
            user  = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user:
                raw   = user['username'] + str(int(time.time()))
                token = hashlib.md5(raw.encode()).hexdigest()
                expires = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                db.execute(
                    "INSERT INTO reset_tokens (user_id, token, expires_at) VALUES (?, ?, ?)",
                    (user['id'], token, expires)
                )
                db.commit()
                token_info = token
        return render_template('reset_request.html', token_info=token_info)

    @app.route('/reset/<token>', methods=['GET', 'POST'])
    def reset_confirm(token):
        db  = get_db()
        row = db.execute(
            "SELECT * FROM reset_tokens WHERE token = ? AND used = 0", (token,)
        ).fetchone()
        error = None
        if not row:
            error = 'Invalid or expired reset link.'
            return render_template('reset_confirm.html', error=error, token=token)
        if request.method == 'POST':
            new_pw = request.form.get('password', '').strip()
            if new_pw:
                db.execute("UPDATE users SET password = ? WHERE id = ?", (new_pw, row['user_id']))
                db.execute("UPDATE reset_tokens SET used = 1 WHERE id = ?", (row['id'],))
                db.commit()
                return redirect(url_for('login'))
        return render_template('reset_confirm.html', error=None, token=token)
