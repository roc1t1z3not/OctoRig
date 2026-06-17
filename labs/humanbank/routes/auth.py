import hashlib
import sqlite3
import time
from datetime import datetime, timedelta
from flask import request, render_template, session, redirect, url_for
from db import get_db, gen_tan_codes, _iban_for


def init(app):

    # ── Login — SQLi via f-string, user enumeration, brute-forceable ─────────

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            db = get_db()
            # VULN: SQLi — both fields injected directly into query
            # bypass with: username=admin'-- (comments out password check)
            user = db.execute(
                f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            ).fetchone()
            if not user:
                # VULN: user enumeration — check username alone for distinct error
                exists = db.execute(
                    f"SELECT id FROM users WHERE username = '{username}'"
                ).fetchone()
                if exists:
                    error = 'Incorrect password.'
                else:
                    error = 'No account found for that username.'
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
                        "INSERT INTO users (username, password, email, full_name) "
                        "VALUES (?, ?, ?, ?)",
                        (username, password, email, full_name)
                    )
                    db.commit()
                    user = db.execute(
                        "SELECT * FROM users WHERE username = ?", (username,)
                    ).fetchone()
                    uid = user['id']
                    session['user_id'] = uid

                    # Create a checking account with starting balance
                    from datetime import date
                    acc_num = f'HB-{uid:04d}' if uid > 13 else f'HB-U{uid:03d}'
                    # Ensure uniqueness if slot already taken
                    existing = db.execute(
                        "SELECT id FROM accounts WHERE account_number = ?", (acc_num,)
                    ).fetchone()
                    if existing:
                        acc_num = f'HB-N{uid:04d}'
                    db.execute(
                        "INSERT INTO accounts (user_id, account_number, iban, account_type, balance, opened_date) "
                        "VALUES (?, ?, ?, 'checking', 5000.00, ?)",
                        (uid, acc_num, '', str(date.today()))
                    )
                    db.commit()
                    # Set the IBAN now that we have the account id
                    acc = db.execute(
                        "SELECT id FROM accounts WHERE account_number = ?", (acc_num,)
                    ).fetchone()
                    db.execute(
                        "UPDATE accounts SET iban = ? WHERE id = ?",
                        (_iban_for(acc['id']), acc['id'])
                    )

                    # Generate TAN codes
                    for code in gen_tan_codes(uid):
                        db.execute(
                            "INSERT INTO tan_codes (user_id, position, pin, used) VALUES (?, ?, ?, ?)",
                            code
                        )

                    # Default transfer limit
                    db.execute(
                        "INSERT OR IGNORE INTO transfer_limits (user_id, daily_limit) VALUES (?, 1000.0)",
                        (uid,)
                    )
                    db.commit()

                    # Signal that the TAN sheet should be shown once
                    session['show_tan_sheet'] = True
                    return redirect(url_for('tan_sheet'))
                except sqlite3.IntegrityError:
                    error = 'Username already taken.'
        return render_template('register.html', error=error)

    @app.route('/tan-sheet')
    def tan_sheet():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        if not session.pop('show_tan_sheet', False):
            return redirect(url_for('dashboard'))
        uid  = session['user_id']
        db   = get_db()
        codes = db.execute(
            "SELECT position, pin FROM tan_codes WHERE user_id = ? ORDER BY position",
            (uid,)
        ).fetchall()
        return render_template('tan_sheet.html', codes=codes)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    # ── Password reset — predictable token: md5(username + epoch_seconds) ────

    @app.route('/reset', methods=['GET', 'POST'])
    def reset_request():
        token_info = None
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            db    = get_db()
            user  = db.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()
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
