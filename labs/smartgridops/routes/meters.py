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

    # Lists only the meters in the operator's own assigned zone — but the detail
    # endpoint below does not enforce the same scoping.
    @app.route('/meters')
    def meters():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['operator_id']
        op   = get_db().execute("SELECT * FROM operators WHERE id = ?", (uid,)).fetchone()
        rows = get_db().execute(
            "SELECT * FROM meters WHERE zone_id = ? ORDER BY id", (op['zone_id'],)
        ).fetchall()
        return render_template('meters.html', meters=rows, zone_id=op['zone_id'])

    # VULN: IDOR — meter detail (customer name, address, consumption) is served
    # by sequential id with no ownership / zone check.
    @app.route('/meters/<int:meter_id>')
    def meter_detail(meter_id):
        redir = _require_login()
        if redir:
            return redir
        meter = get_db().execute("SELECT * FROM meters WHERE id = ?", (meter_id,)).fetchone()
        if not meter:
            return render_template('404.html'), 404
        return render_template('meter_detail.html', meter=meter)
