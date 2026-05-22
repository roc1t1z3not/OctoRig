import base64
import hashlib
import hmac
import json
from functools import wraps
from flask import request, jsonify, session
from db import get_db

JWT_SECRET = 'netpulse'


def _b64url_enc(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64url_dec(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def issue_jwt(user_id, username, role):
    header  = _b64url_enc(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload = _b64url_enc(json.dumps({'sub': user_id, 'username': username, 'role': role}).encode())
    sig = hmac.new(JWT_SECRET.encode(), f'{header}.{payload}'.encode(), hashlib.sha256).digest()
    return f'{header}.{payload}.{_b64url_enc(sig)}'


def verify_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header  = json.loads(_b64url_dec(parts[0]))
        payload = json.loads(_b64url_dec(parts[1]))
        alg = header.get('alg', '').lower()
        if alg == 'none':
            return payload          # VULN: alg:none accepted
        if alg == 'hs256':
            sig_input = f'{parts[0]}.{parts[1]}'.encode()
            expected  = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _b64url_dec(parts[2])):
                return None
            return payload
        return None
    except Exception:
        return None


def require_jwt(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'missing token'}), 401
        payload = verify_jwt(auth[7:])
        if not payload:
            return jsonify({'error': 'invalid token'}), 401
        request.jwt_payload = payload
        return f(*args, **kwargs)
    return decorated


def init(app):

    # VULN: SQLi — f-string on username/password
    @app.route('/api/token', methods=['POST'])
    def api_token():
        data     = request.get_json(silent=True) or request.form
        username = data.get('username', '')
        password = data.get('password', '')
        user = get_db().execute(
            f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        ).fetchone()
        if not user:
            return jsonify({'error': 'invalid credentials'}), 401
        role  = 'admin' if user['is_admin'] else 'user'
        token = issue_jwt(user['id'], user['username'], role)
        return jsonify({'token': token, 'user_id': user['id'], 'role': role})

    # VULN: IDOR — JWT sub not matched against user_id param
    @app.route('/api/account/<int:user_id>')
    @require_jwt
    def api_account(user_id):
        row = get_db().execute(
            "SELECT id, username, email, full_name, plan, data_used_mb, data_limit_mb FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    @app.route('/api/usage')
    @require_jwt
    def api_usage():
        uid = request.jwt_payload.get('sub')
        row = get_db().execute(
            "SELECT plan, data_used_mb, data_limit_mb FROM users WHERE id = ?", (uid,)
        ).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))
