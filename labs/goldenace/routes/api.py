import base64
import hashlib
import hmac
import json
from functools import wraps
from flask import request, jsonify, session
from db import get_db

JWT_SECRET = 'goldenace'


def _b64url_enc(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64url_dec(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def issue_jwt(user_id, username, role):
    header  = _b64url_enc(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload = _b64url_enc(json.dumps({'sub': user_id, 'username': username, 'role': role}).encode())
    sig     = hmac.new(JWT_SECRET.encode(), f'{header}.{payload}'.encode(), hashlib.sha256).digest()
    return f'{header}.{payload}.{_b64url_enc(sig)}'


def verify_jwt(token):
    try:
        parts   = token.split('.')
        if len(parts) != 3:
            return None
        header  = json.loads(_b64url_dec(parts[0]))
        payload = json.loads(_b64url_dec(parts[1]))
        alg     = header.get('alg', '').lower()
        if alg == 'none':
            return payload          # VULN: alg:none accepted — no signature check
        if alg == 'hs256':
            sig_in   = f'{parts[0]}.{parts[1]}'.encode()
            expected = hmac.new(JWT_SECRET.encode(), sig_in, hashlib.sha256).digest()
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

    # VULN: SQLi — credentials injected directly
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

    # VULN: IDOR — JWT sub not matched against path user_id
    @app.route('/api/balance/<int:user_id>')
    @require_jwt
    def api_balance(user_id):
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        # VULN: information disclosure — leaks all user fields
        return jsonify(dict(row))

    # VULN: IDOR — no ownership check; SQLi on ?type= param
    @app.route('/api/history/<int:user_id>')
    @require_jwt
    def api_history(user_id):
        game_type = request.args.get('type', '')
        db        = get_db()
        if game_type:
            rows = db.execute(
                f"SELECT * FROM game_history WHERE user_id = {user_id}"
                f" AND game_type = '{game_type}' ORDER BY id DESC LIMIT 50"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM game_history WHERE user_id = ? ORDER BY id DESC LIMIT 50",
                (user_id,)
            ).fetchall()
        return jsonify([dict(r) for r in rows])

    # VULN: mass assignment — arbitrary fields updated without allowlist
    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @require_jwt
    def api_user_update(user_id):
        data = request.get_json(silent=True) or {}
        if not data:
            return jsonify({'error': 'no data'}), 400
        fields = ', '.join(f"{k} = ?" for k in data.keys())
        values = list(data.values()) + [user_id]
        try:
            db = get_db()
            db.execute(f"UPDATE users SET {fields} WHERE id = ?", values)
            db.commit()
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return jsonify(dict(row))

    @app.route('/api/feed')
    def api_feed():
        rows = get_db().execute(
            "SELECT message, created_at FROM live_feed ORDER BY id DESC LIMIT 20"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
