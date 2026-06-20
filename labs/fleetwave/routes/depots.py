# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import session, render_template, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/depots')
    def depots():
        redir = _require_login()
        if redir:
            return redir
        rows = get_db().execute("SELECT * FROM depots ORDER BY id").fetchall()
        return render_template('depots.html', depots=rows)

    # VULN: relation-level IDOR — the depot secret_note (override PINs, bonded
    # manifest seals) is meant to be visible only to a user who holds a
    # depot_access row for that depot. This route never consults depot_access;
    # it only checks that *some* session exists, so any dispatcher can read
    # every depot's restricted note by id.
    @app.route('/depots/<int:depot_id>')
    def depot_detail(depot_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        depot = db.execute("SELECT * FROM depots WHERE id = ?", (depot_id,)).fetchone()
        if not depot:
            return render_template('404.html'), 404
        manager = db.execute("SELECT * FROM users WHERE id = ?", (depot['manager_id'],)).fetchone()
        shipments = db.execute(
            "SELECT * FROM shipments WHERE origin = ? ORDER BY id", (depot['name'],)
        ).fetchall()
        return render_template('depot_detail.html', depot=depot, manager=manager, shipments=shipments)
