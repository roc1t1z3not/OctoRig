# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, redirect, url_for, render_template, make_response
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/admin')
    def admin_index():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not (user['is_admin'] or user['role'] == 'admin'):
            return render_template('403.html'), 403
        users = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        resp = make_response(render_template('admin.html', users=users))
        # VULN: reachable to admin sessions obtained via SQLi login bypass —
        # the flag rewards getting *here* as admin, not just being logged in.
        flag_row = db.execute("SELECT value FROM _flags WHERE name = 'sqli-login'").fetchone()
        resp.headers['X-Admin-Flag'] = flag_row['value'] if flag_row else ''
        return resp

    # VULN: BAC — checks that a session exists, never that the session
    # belongs to an admin. Any registered user can reach this directly.
    @app.route('/admin/recovery-codes')
    def admin_recovery_codes():
        redir = _require_login()
        if redir:
            return redir
        return render_template('recovery_codes.html')

    # VULN: stored XSS sink — review notes (submitted by any user via the
    # "report item" feature) are rendered without escaping. Reachable only
    # by an admin session, by design: the player must already hold admin
    # access (via the SQLi bypass) to view their own payload render back and
    # read document.cookie on their own (now-admin) session.
    @app.route('/admin/review')
    def admin_review():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not (user['is_admin'] or user['role'] == 'admin'):
            return render_template('403.html'), 403
        rows = db.execute(
            "SELECT r.*, i.title FROM review_queue r JOIN vault_items i ON i.id = r.item_id ORDER BY r.id DESC"
        ).fetchall()
        resp = make_response(render_template('admin_review.html', rows=rows))
        resp.set_cookie('vs_admin_session', 'FLAG{vs_xss_admin_cookie_stolen}', httponly=False)
        return resp
