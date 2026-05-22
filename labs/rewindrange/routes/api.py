from flask import request, session, jsonify, abort
from db import get_db


def init(app):

    @app.route('/health')
    def health():
        return 'OK', 200

    # ── /api/product — SQLi via id parameter ─────────────────────────────────

    @app.route('/api/product')
    def api_product():
        product_id = request.args.get('id', '')
        db = get_db()
        try:
            row = db.execute(f"SELECT * FROM products WHERE id = {product_id}").fetchone()
        except Exception as e:
            return jsonify({'error': str(e)}), 400
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    # ── /api/user/<id>/balance — IDOR: no ownership check ────────────────────

    @app.route('/api/user/<int:user_id>/balance')
    def api_balance(user_id):
        if not session.get('user_id'):
            return jsonify({'error': 'unauthenticated'}), 401
        row = get_db().execute(
            "SELECT id, username, email, balance FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    # ── /api/orders/<id> — IDOR: no ownership check ──────────────────────────

    @app.route('/api/orders/<int:order_id>')
    def api_order(order_id):
        if not session.get('user_id'):
            return jsonify({'error': 'unauthenticated'}), 401
        db    = get_db()
        o     = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not o:
            return jsonify({'error': 'not found'}), 404
        items = db.execute(
            "SELECT oi.*, p.title, p.type FROM order_items oi "
            "JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
            (order_id,)
        ).fetchall()
        owner = db.execute(
            "SELECT id, username, email FROM users WHERE id = ?", (o['user_id'],)
        ).fetchone()
        return jsonify({
            'order':    dict(o),
            'items':    [dict(i) for i in items],
            'customer': dict(owner) if owner else None,
        })
