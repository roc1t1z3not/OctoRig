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
            user = get_db().execute(
                f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            ).fetchone()
            if user:
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            error = 'Invalid username or password.'
        return render_template('login.html', error=error)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email    = request.form.get('email', '').strip()
            first    = request.form.get('first_name', '').strip()
            last     = request.form.get('last_name', '').strip()
            if not (username and password and email):
                error = 'All fields are required.'
            else:
                db = get_db()
                try:
                    db.execute(
                        "INSERT INTO users (username, password, email, first_name, last_name, balance) "
                        "VALUES (?, ?, ?, ?, ?, 100.00)",
                        (username, password, email, first, last)
                    )
                    db.commit()
                    user = db.execute(
                        "SELECT * FROM users WHERE username = ?", (username,)
                    ).fetchone()
                    session['user_id'] = user['id']
                    return redirect(url_for('index'))
                except sqlite3.IntegrityError:
                    error = 'Username already taken.'
        return render_template('register.html', error=error)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
