# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/shipments')
    def shipments():
        redir = _require_login()
        if redir:
            return redir
        rows = get_db().execute("SELECT * FROM shipments ORDER BY id").fetchall()
        return render_template('shipments.html', shipments=rows)

    # VULN: item-level IDOR — no account-ownership check. Any signed-in
    # dispatcher can read any customer's shipment (recipient PII + manifest
    # notes) by walking the sequential id.
    @app.route('/shipments/<int:shipment_id>')
    def shipment_detail(shipment_id):
        redir = _require_login()
        if redir:
            return redir
        row = get_db().execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,)).fetchone()
        if not row:
            return render_template('404.html'), 404
        return render_template('shipment_detail.html', shipment=row)

    # VULN: SQLi — tracking/recipient search term interpolated straight into a
    # LIKE clause. Original query selects 4 columns → UNION SELECT into _flags.
    @app.route('/shipments/search')
    def shipment_search():
        redir = _require_login()
        if redir:
            return redir
        q = request.args.get('q', '')
        results = []
        error = None
        if q:
            try:
                results = get_db().execute(
                    f"SELECT tracking_no, recipient, destination, status FROM shipments "
                    f"WHERE tracking_no LIKE '%{q}%' OR recipient LIKE '%{q}%'"
                ).fetchall()
            except Exception as e:
                error = str(e)
        return render_template('shipment_search.html', q=q, results=results, error=error)

    # "Report a delivery issue" — feeds the admin feedback-review queue. The
    # note is stored and later rendered unescaped in the admin panel (stored XSS).
    @app.route('/shipments/<int:shipment_id>/feedback', methods=['POST'])
    def shipment_feedback(shipment_id):
        redir = _require_login()
        if redir:
            return redir
        note = request.form.get('note', '')
        db = get_db()
        db.execute(
            "INSERT INTO delivery_feedback (shipment_id, reported_by, note, created_at) VALUES (?, ?, ?, ?)",
            (shipment_id, session['user_id'], note, datetime.utcnow().isoformat(sep=' ', timespec='seconds')),
        )
        db.commit()
        return redirect(url_for('shipment_detail', shipment_id=shipment_id))
