# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
import subprocess
import requests as _requests
from flask import request, session, jsonify
from db import get_db


def _require_login_json():
    if not session.get('user_id'):
        return jsonify({'error': 'login required'}), 401
    return None


def init(app):

    # VULN: IDOR — same missing ownership check as /shipments/<id>, exposed
    # over the JSON API. Lets a scripted sweep enumerate every shipment by id.
    @app.route('/api/v1/shipments/<int:shipment_id>')
    def api_shipment_detail(shipment_id):
        err = _require_login_json()
        if err:
            return err
        row = get_db().execute("SELECT * FROM shipments WHERE id = ?", (shipment_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    # VULN: SSRF — "carrier status check" fetches an operator-supplied URL
    # server-side and reflects the response back. Gated behind admin, which is
    # why the mass-assignment escalation matters for the insane chain: this is
    # otherwise unreachable to a freshly registered dispatcher.
    @app.route('/api/admin/carrier-check', methods=['POST'])
    def api_carrier_check():
        err = _require_login_json()
        if err:
            return err
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not (user['is_admin'] or user['role'] == 'admin'):
            return jsonify({'error': 'admin only'}), 403
        url = (request.get_json(silent=True) or request.form).get('url', '').strip()
        if not url:
            return jsonify({'error': 'url required'}), 400
        try:
            resp = _requests.get(url, timeout=5, allow_redirects=True)
            return jsonify({'status': resp.status_code, 'body': resp.text[:4096]})
        except Exception as e:
            return jsonify({'error': str(e)}), 502

    # VULN: command injection — only reachable from the container's own
    # loopback address (i.e. via the SSRF above), so it was never hardened.
    # The `format` param is interpolated unsanitised into a shell call.
    # Reaching this endpoint at all (the SSRF half of the chain) already
    # returns a job token; injecting a command appends the insane-tier flag.
    @app.route('/api/internal/manifest-export')
    def api_internal_manifest_export():
        if request.remote_addr != '127.0.0.1':
            return jsonify({'error': 'internal only'}), 403
        fmt = request.args.get('format', 'csv').strip()
        try:
            output = subprocess.check_output(
                f"echo building manifest export as {fmt}",
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=8,
            ).decode(errors='replace')
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return jsonify({'export': output, 'job_token': 'FLAG{fw_ssrf_internal_manifest}'})
