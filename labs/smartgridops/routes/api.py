# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from functools import wraps
from flask import request, jsonify
from db import get_db

# VULN: weak auth — device tokens are hardcoded in source and shared across the
# whole field fleet. The same static string authenticates every device call, and
# the admin token is equally guessable / leaked via FTP and SSH recon.
DEVICE_TOKEN = 'sgo-device-7f3a9c2e1b'
ADMIN_TOKEN  = 'sgo-admin-d41d8cd98f'


def _token():
    # Accept either header or query param — no rotation, no per-device secret.
    return request.headers.get('X-Device-Token') or request.args.get('token', '')


def require_device_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if _token() not in (DEVICE_TOKEN, ADMIN_TOKEN):
            return jsonify({'error': 'missing or invalid device token'}), 401
        return f(*args, **kwargs)
    return decorated


def init(app):

    @app.route('/api/device/list')
    @require_device_token
    def api_device_list():
        rows = get_db().execute(
            "SELECT id, name, zone_id, dtype, mgmt_ip, firmware, state FROM devices ORDER BY id"
        ).fetchall()
        return jsonify({'devices': [dict(r) for r in rows]})

    # Returns full device record including its api_token (token reuse exposure).
    @app.route('/api/device/<int:device_id>')
    @require_device_token
    def api_device_get(device_id):
        row = get_db().execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    # VULN: command issuing gated only by the shared static token.
    @app.route('/api/device/<int:device_id>/command', methods=['POST'])
    @require_device_token
    def api_device_command(device_id):
        row = get_db().execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        data = request.get_json(silent=True) or request.form
        command = data.get('command', '')
        return jsonify({
            'device_id': device_id,
            'mgmt_ip': row['mgmt_ip'],
            'accepted_command': command,
            'status': 'queued',
        })

    # Internal-only endpoint for SSRF challenge — flag is only served to localhost.
    @app.route('/api/internal/ssrf-flag')
    def api_internal_ssrf_flag():
        if request.remote_addr != '127.0.0.1':
            return jsonify({'error': 'internal only'}), 403
        row = get_db().execute(
            "SELECT value FROM _flags WHERE name = 'ssrf-poll'"
        ).fetchone()
        return jsonify({'flag': row['value'] if row else None})

    # Admin token dumps the full operator roster (including tokens / notes).
    @app.route('/api/admin/operators')
    def api_admin_operators():
        if _token() != ADMIN_TOKEN:
            return jsonify({'error': 'admin token required'}), 401
        rows = get_db().execute(
            "SELECT id, username, role, zone_id, api_token, notes FROM operators ORDER BY id"
        ).fetchall()
        return jsonify({'operators': [dict(r) for r in rows]})
