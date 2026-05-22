import base64
import hashlib
import hmac
import json
from functools import wraps
from flask import request, jsonify, session
from db import get_db

JWT_SECRET = 'tradefloor'


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

    @app.route('/api/prices')
    def api_prices():
        rows = get_db().execute(
            "SELECT symbol, name, price, change FROM market_data ORDER BY symbol"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

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

    # VULN: IDOR — JWT sub not matched against user_id in query param
    @app.route('/api/portfolio')
    @require_jwt
    def api_portfolio():
        # VULN: SQLi — user_id from query param concatenated into query
        user_id = request.args.get('user_id', request.jwt_payload.get('sub'))
        rows = get_db().execute(
            f"SELECT h.*, m.name, m.price FROM portfolio_holdings h "
            f"JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = {user_id}"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # VULN: mass assignment — JSON body passed directly to UPDATE without field allowlist
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

    # VULN: SQLi — symbol param injected directly into query
    @app.route('/api/market/quote')
    @require_jwt
    def api_market_quote():
        symbol = request.args.get('symbol', '')
        row = get_db().execute(
            f"SELECT * FROM market_data WHERE symbol = '{symbol}'"
        ).fetchone()
        if not row:
            return jsonify({'error': 'symbol not found'}), 404
        return jsonify(dict(row))
