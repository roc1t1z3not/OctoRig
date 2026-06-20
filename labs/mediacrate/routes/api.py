# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import subprocess
import requests as _requests
from flask import request, session, jsonify
from db import get_db


def _require_login_json():
    if not session.get('user_id'):
        return jsonify({'error': 'login required'}), 401
    return None


def init(app):

    # VULN: IDOR — same missing visibility check as /videos/<id>, exposed
    # over the API. Lets a scripted sweep enumerate every video by id.
    @app.route('/api/v1/videos/<int:video_id>')
    def api_video_detail(video_id):
        err = _require_login_json()
        if err:
            return err
        video = get_db().execute("SELECT * FROM videos WHERE id = ?", (video_id,)).fetchone()
        if not video:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(video))

    # VULN: SSRF — "import thumbnail from URL" fetches an operator-supplied
    # URL server-side and reflects the response back. Gated behind is_admin,
    # which is exactly why the mass-assignment escalation matters for the
    # insane chain: this endpoint is otherwise unreachable to a freshly
    # registered account.
    @app.route('/api/admin/import-thumbnail', methods=['POST'])
    def api_import_thumbnail():
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
    # loopback address (i.e. via the SSRF above), so it was never hardened
    # against malicious input. The `format` param is interpolated unsanitised
    # into a shell call that builds the transcode job. Reaching this endpoint
    # at all (the SSRF half of the chain) already returns a job token; only
    # injecting a command appends the insane-tier flag file's contents.
    @app.route('/api/internal/transcode')
    def api_internal_transcode():
        if request.remote_addr != '127.0.0.1':
            return jsonify({'error': 'internal only'}), 403
        fmt = request.args.get('format', 'mp4').strip()
        try:
            output = subprocess.check_output(
                f"echo transcoding video as {fmt}",
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=8,
            ).decode(errors='replace')
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return jsonify({'transcode': output, 'job_token': 'FLAG{mc_ssrf_internal_transcode}'})
