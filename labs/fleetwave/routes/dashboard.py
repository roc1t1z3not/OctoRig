# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import session, redirect, url_for, render_template
from db import get_db


def init(app):

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        shipments = db.execute("SELECT * FROM shipments ORDER BY id").fetchall()
        depots = db.execute("SELECT * FROM depots ORDER BY id").fetchall()
        counts = {
            'in_transit':       sum(1 for s in shipments if s['status'] == 'in_transit'),
            'out_for_delivery': sum(1 for s in shipments if s['status'] == 'out_for_delivery'),
            'delivered':        sum(1 for s in shipments if s['status'] == 'delivered'),
            'exception':        sum(1 for s in shipments if s['status'] == 'exception'),
        }
        return render_template('dashboard.html', shipments=shipments, depots=depots, counts=counts)
