# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('operator_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/dashboard')
    def dashboard():
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        zones   = db.execute("SELECT * FROM zones ORDER BY id").fetchall()
        devices = db.execute("SELECT * FROM devices ORDER BY id").fetchall()
        total_load = sum(z['load_mw'] for z in zones)
        total_cap  = sum(z['capacity_mw'] for z in zones)
        return render_template(
            'dashboard.html',
            zones=zones, devices=devices,
            total_load=total_load, total_cap=total_cap,
        )

    # Admin overview — control-room operator roster.
    @app.route('/admin')
    def admin_index():
        redir = _require_login()
        if redir:
            return redir
        user = get_db().execute(
            "SELECT * FROM operators WHERE id = ?", (session['operator_id'],)
        ).fetchone()
        if not user or not user['is_admin']:
            return render_template('403.html'), 403
        operators = get_db().execute("SELECT * FROM operators ORDER BY id").fetchall()
        return render_template('admin.html', operators=operators)
