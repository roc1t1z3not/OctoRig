# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
import subprocess
import requests as _requests
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('operator_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/devices')
    def devices():
        redir = _require_login()
        if redir:
            return redir
        rows = get_db().execute("SELECT * FROM devices ORDER BY id").fetchall()
        return render_template('devices.html', devices=rows)

    @app.route('/devices/<int:device_id>')
    def device_detail(device_id):
        redir = _require_login()
        if redir:
            return redir
        row = get_db().execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        if not row:
            return render_template('404.html'), 404
        return render_template('device_detail.html', device=row, result=None, output=None, error=None)

    # VULN: SSRF — the "device status poller" fetches an operator-supplied URL
    # server-side and reflects the body back. No allow-list, no scheme/host check.
    @app.route('/devices/poll', methods=['GET', 'POST'])
    def device_poll():
        redir = _require_login()
        if redir:
            return redir
        result = None
        error  = None
        url    = request.values.get('url', '').strip()
        if url:
            try:
                resp = _requests.get(url, timeout=5, allow_redirects=True)
                result = {
                    'status':  resp.status_code,
                    'size':    len(resp.content),
                    'preview': resp.text[:4096],
                }
            except Exception as e:
                error = str(e)
        return render_template('poll.html', url=url, result=result, error=error)

    # VULN: command injection — device mgmt hostname/IP interpolated into a shell
    # command used to "ping the device before issuing a reboot".
    @app.route('/devices/<int:device_id>/reboot', methods=['POST'])
    def device_reboot(device_id):
        redir = _require_login()
        if redir:
            return redir
        row = get_db().execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        if not row:
            return render_template('404.html'), 404
        # Operator may override the management target before the reboot ping.
        target = request.form.get('target', '').strip() or row['mgmt_ip']
        output = None
        error  = None
        try:
            output = subprocess.check_output(
                f"ping -c 1 -W 1 {target} && echo 'reboot signal queued for {target}'",
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=8,
            ).decode(errors='replace')
        except subprocess.TimeoutExpired:
            error = 'Device ping timed out.'
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return render_template('device_detail.html', device=row, result='reboot', output=output, error=error)

    # VULN: command injection — config push writes operator-supplied config via a
    # shell pipeline; the filename/value is interpolated unsanitised.
    @app.route('/devices/<int:device_id>/config-push', methods=['POST'])
    def device_config_push(device_id):
        redir = _require_login()
        if redir:
            return redir
        row = get_db().execute("SELECT * FROM devices WHERE id = ?", (device_id,)).fetchone()
        if not row:
            return render_template('404.html'), 404
        key   = request.form.get('key', 'setpoint').strip()
        value = request.form.get('value', '').strip()
        output = None
        error  = None
        try:
            output = subprocess.check_output(
                f"echo 'pushing {key}={value} to {row['mgmt_ip']}'",
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=8,
            ).decode(errors='replace')
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return render_template('device_detail.html', device=row, result='config', output=output, error=error)
