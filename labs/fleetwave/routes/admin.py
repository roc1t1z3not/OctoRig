# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
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

    # VULN: BAC — checks that a session exists, never that the session belongs
    # to an admin. Any registered dispatcher can reach the driver roster (PII:
    # licence numbers, phone) directly.
    @app.route('/admin/driver-roster')
    def admin_driver_roster():
        redir = _require_login()
        if redir:
            return redir
        drivers = get_db().execute(
            "SELECT d.*, dp.name AS depot_name FROM drivers d "
            "JOIN depots dp ON dp.id = d.depot_id ORDER BY d.id"
        ).fetchall()
        return render_template('admin_driver_roster.html', drivers=drivers)

    # VULN: stored XSS sink — delivery-feedback notes (submitted by any user)
    # are rendered without escaping. Reachable only by an admin session, by
    # design: the player must already hold admin (via the SQLi bypass) to view
    # their own payload render back and read document.cookie on their own
    # (now-admin) session. The admin session cookie is not HttpOnly.
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
            "SELECT f.*, s.tracking_no FROM delivery_feedback f "
            "JOIN shipments s ON s.id = f.shipment_id ORDER BY f.id DESC"
        ).fetchall()
        resp = make_response(render_template('admin_review.html', rows=rows))
        resp.set_cookie('fw_admin_session', 'FLAG{fw_xss_admin_cookie_stolen}', httponly=False)
        return resp
