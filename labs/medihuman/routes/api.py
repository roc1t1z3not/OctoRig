import base64
import hashlib
import hmac
import json
from flask import request, jsonify, session
from db import get_db

JWT_SECRET = 'medihuman'


def _b64url_enc(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64url_dec(s: str) -> bytes:
    s += '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s)


def _make_jwt(payload: dict) -> str:
    header  = _b64url_enc(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    body    = _b64url_enc(json.dumps(payload).encode())
    sig     = _b64url_enc(hmac.new(JWT_SECRET.encode(), f'{header}.{body}'.encode(), hashlib.sha256).digest())
    return f'{header}.{body}.{sig}'


def _verify_jwt(token: str):
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header  = json.loads(_b64url_dec(parts[0]))
        payload = json.loads(_b64url_dec(parts[1]))
        alg = header.get('alg', '').lower()
        if alg == 'none':
            return payload          # VULN: alg:none — skip signature check
        expected = _b64url_enc(
            hmac.new(JWT_SECRET.encode(), f'{parts[0]}.{parts[1]}'.encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(expected, parts[2]):
            return None
        return payload
    except Exception:
        return None


def init(app):

    @app.route('/api/token', methods=['POST'])
    def api_token():
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db   = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", (username, password)
        ).fetchone()
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        token = _make_jwt({'sub': user['id'], 'role': user['role']})
        return jsonify({'token': token})

    # IDOR: JWT sub not validated against patient ownership
    @app.route('/api/patients/<int:patient_id>')
    def api_patient(patient_id):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        payload = _verify_jwt(auth[7:])
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        db      = get_db()
        patient = db.execute(
            "SELECT p.*, u.username, u.email FROM patients p "
            "JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (patient_id,)
        ).fetchone()
        if not patient:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(dict(patient))

    @app.route('/api/me')
    def api_me():
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized'}), 401
        payload = _verify_jwt(auth[7:])
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        db   = get_db()
        user = db.execute("SELECT id, username, email, full_name, role FROM users WHERE id = ?",
                          (payload.get('sub'),)).fetchone()
        if not user:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(dict(user))
