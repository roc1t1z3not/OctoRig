# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
import hashlib
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    # VULN: SQLi — username/password interpolated straight into the query.
    # Also: open redirect via ?next= with no validation.
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        nxt = request.args.get('next', '')
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            nxt = request.form.get('next', nxt)
            # Passwords are stored as unsalted MD5 — hash the supplied password
            # before comparison. (username is still interpolated unsanitised → SQLi)
            pw_md5 = hashlib.md5(password.encode()).hexdigest()
            row = get_db().execute(
                f"SELECT * FROM operators WHERE username = '{username}' AND password = '{pw_md5}'"
            ).fetchone()
            if row:
                session['operator_id'] = row['id']
                # VULN: open redirect — next is trusted verbatim
                if nxt:
                    return redirect(nxt)
                return redirect(url_for('dashboard'))
            error = 'Invalid operator credentials.'
        return render_template('login.html', error=error, next=nxt)

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))
