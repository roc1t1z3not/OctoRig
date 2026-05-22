import base64
import hashlib
import hmac
import json
from functools import wraps
from flask import request, jsonify
from db import get_db

JWT_SECRET = 'humanbank'


def _b64url_enc(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64url_dec(s):
    return base64.urlsafe_b64decode(s + '=' * (-len(s) % 4))


def issue_jwt(user_id, username, role):
    header  = _b64url_enc(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload = _b64url_enc(json.dumps(
        {'sub': user_id, 'username': username, 'role': role}
    ).encode())
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
            return payload                                   # VULN: alg:none accepted
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

    @app.route('/api/accounts')
    @require_jwt
    def api_accounts():
        rows = get_db().execute(
            "SELECT a.*, u.username FROM accounts a JOIN users u ON a.user_id = u.id"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # IDOR: JWT sub is not matched against account.user_id
    @app.route('/api/accounts/<int:account_id>')
    @require_jwt
    def api_account(account_id):
        row = get_db().execute(
            "SELECT a.*, u.username, u.email FROM accounts a "
            "JOIN users u ON a.user_id = u.id WHERE a.id = ?",
            (account_id,)
        ).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    @app.route('/api/transactions/<int:account_id>')
    @require_jwt
    def api_transactions(account_id):
        rows = get_db().execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY txn_date DESC",
            (account_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # VULN: negative amount + no ownership check on from_account_id
    @app.route('/api/transfer', methods=['POST'])
    @require_jwt
    def api_transfer():
        data    = request.get_json(silent=True) or {}
        from_id = int(data.get('from_account_id', 0))
        to_num  = data.get('to_account_number', '')
        amount  = float(data.get('amount', 0))
        memo    = data.get('memo', '')
        db  = get_db()
        src = db.execute("SELECT * FROM accounts WHERE id = ?", (from_id,)).fetchone()
        dst = db.execute(
            "SELECT * FROM accounts WHERE account_number = ?", (to_num,)
        ).fetchone()
        if not src or not dst:
            return jsonify({'error': 'invalid accounts'}), 400
        db.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, src['id']))
        db.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, dst['id']))
        from datetime import date as _date
        db.execute(
            "INSERT INTO transactions (account_id, type, amount, memo, counterparty, txn_date) "
            "VALUES (?, 'debit', ?, ?, ?, ?)",
            (src['id'], amount, memo, to_num, str(_date.today()))
        )
        db.commit()
        return jsonify({'status': 'ok', 'new_balance': src['balance'] - amount})
