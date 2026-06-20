# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import base64
import hashlib
import hmac
import json
import subprocess
import requests as _requests
from flask import request, session, jsonify
from db import get_db

JWT_SECRET = 'mc-dev-secret-2026'


def _require_login_json():
    if not session.get('user_id'):
        return jsonify({'error': 'login required'}), 401
    return None


def _b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64url_decode(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def _issue_jwt(claims):
    header_b64 = _b64url_encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload_b64 = _b64url_encode(json.dumps(claims).encode())
    sig = hmac.new(JWT_SECRET.encode(), f'{header_b64}.{payload_b64}'.encode(), hashlib.sha256).digest()
    return f'{header_b64}.{payload_b64}.{_b64url_encode(sig)}'


# VULN: JWT / weak auth — the verifier trusts the client-supplied "alg"
# header to decide *whether* to check the signature at all. A forged token
# with header {"alg":"none"} and an empty signature segment sails through
# with whatever claims (e.g. role: admin) the attacker put in the payload.
def _verify_jwt(token):
    header_b64, payload_b64, sig_b64 = token.split('.')
    header = json.loads(_b64url_decode(header_b64))
    payload = json.loads(_b64url_decode(payload_b64))
    alg = header.get('alg', '')
    if alg == 'HS256':
        expected = hmac.new(JWT_SECRET.encode(), f'{header_b64}.{payload_b64}'.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64url_decode(sig_b64)):
            raise ValueError('bad signature')
    elif alg != 'none':
        raise ValueError('unsupported alg')
    return payload


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

    # "Developer API token" — issues a JWT for the signed-in user, meant to
    # be used as a Bearer token against the /api/v1/* endpoints below.
    @app.route('/api/v1/auth/token')
    def api_auth_token():
        err = _require_login_json()
        if err:
            return err
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        token = _issue_jwt({'user_id': user['id'], 'username': user['username'], 'role': user['role']})
        return jsonify({'token': token})

    @app.route('/api/v1/me')
    def api_me():
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'token required'}), 401
        try:
            claims = _verify_jwt(auth[len('Bearer '):])
        except Exception:
            return jsonify({'error': 'invalid token'}), 401
        return jsonify(claims)

    # VULN target — admin-only by JWT claim, not by re-checking the DB. An
    # alg=none forged token with role=admin reaches this without ever
    # holding an admin session.
    @app.route('/api/v1/admin/secrets')
    def api_admin_secrets():
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'token required'}), 401
        try:
            claims = _verify_jwt(auth[len('Bearer '):])
        except Exception:
            return jsonify({'error': 'invalid token'}), 401
        if claims.get('role') != 'admin':
            return jsonify({'error': 'admin only'}), 403
        return jsonify({'secret': 'platform master switch token', 'flag': 'FLAG{mc_jwt_alg_none_admin}'})
