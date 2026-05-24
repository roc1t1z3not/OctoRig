# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import sqlite3
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
            # VULN: SQLi — raw f-string, no parameterisation
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
                session['is_admin'] = bool(user['is_admin'])
                # VULN: open redirect — ?next= accepted without validation
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
                from datetime import datetime
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    db.execute(
                        "INSERT INTO users (username, password, email, display_name, balance, created_at)"
                        " VALUES (?, ?, ?, ?, 0.0, ?)",
                        (username, password, email, username, now)
                    )
                    db.commit()
                    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                    session['user_id'] = user['id']
                    session['is_admin'] = False
                    return redirect(url_for('index'))
                except sqlite3.IntegrityError:
                    error = 'Username already taken.'
        return render_template('register.html', error=error)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
