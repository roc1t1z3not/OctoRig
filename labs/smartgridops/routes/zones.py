# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('operator_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/zones')
    def zones():
        redir = _require_login()
        if redir:
            return redir
        rows = get_db().execute("SELECT * FROM zones ORDER BY id").fetchall()
        return render_template('zones.html', zones=rows)

    # VULN: IDOR — any authenticated operator can read any zone, including the
    # restricted secret_note, regardless of which zone they are assigned to.
    @app.route('/zones/<int:zone_id>')
    def zone_detail(zone_id):
        redir = _require_login()
        if redir:
            return redir
        zone = get_db().execute("SELECT * FROM zones WHERE id = ?", (zone_id,)).fetchone()
        if not zone:
            return render_template('404.html'), 404
        operator = get_db().execute(
            "SELECT * FROM operators WHERE id = ?", (zone['operator_id'],)
        ).fetchone()
        devices = get_db().execute(
            "SELECT * FROM devices WHERE zone_id = ? ORDER BY id", (zone_id,)
        ).fetchall()
        return render_template('zone_detail.html', zone=zone, operator=operator, devices=devices)
