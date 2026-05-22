from flask import request, render_template, session, redirect, url_for, abort
from db import get_db


def init(app):

    # ── Account — IDOR: no ownership check on view or update ─────────────────

    @app.route('/account/<int:user_id>')
    def account(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404)
        return render_template('account.html', profile=user)

    @app.route('/account/<int:user_id>/update', methods=['POST'])
    def account_update(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        first = request.form.get('first_name', '').strip()
        last  = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        addr  = request.form.get('address', '').strip()
        bio   = request.form.get('bio', '').strip()
        db = get_db()
        db.execute(
            "UPDATE users SET first_name = ?, last_name = ?, phone = ?, address = ?, bio = ? WHERE id = ?",
            (first, last, phone, addr, bio, user_id)
        )
        db.commit()
        return redirect(url_for('account', user_id=user_id))

    # ── Members directory — SQLi via ?q, exposes emails/bios (IDOR) ──────────

    @app.route('/users')
    def users():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        q  = request.args.get('q', '').strip()
        db = get_db()
        if q:
            members = db.execute(
                f"SELECT id, username, email, first_name, last_name, bio FROM users "
                f"WHERE username LIKE '%{q}%' OR first_name LIKE '%{q}%' OR email LIKE '%{q}%' "
                f"ORDER BY username"
            ).fetchall()
        else:
            members = db.execute(
                "SELECT id, username, email, first_name, last_name, bio FROM users ORDER BY username"
            ).fetchall()
        return render_template('users.html', members=members, q=q)

    # ── Orders — IDOR: order detail has no ownership check ───────────────────

    @app.route('/orders')
    def orders():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user_orders = get_db().execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC",
            (session['user_id'],)
        ).fetchall()
        return render_template('orders.html', orders=user_orders)

    @app.route('/orders/<int:order_id>')
    def order(order_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db    = get_db()
        o     = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not o:
            abort(404)
        items = db.execute(
            "SELECT oi.*, p.title, p.type, p.platform, p.creator FROM order_items oi "
            "JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
            (order_id,)
        ).fetchall()
        owner = db.execute(
            "SELECT username, email FROM users WHERE id = ?", (o['user_id'],)
        ).fetchone()
        return render_template('order.html', order=o, items=items, owner=owner)

    # ── Wishlist — IDOR: no ownership check ──────────────────────────────────

    @app.route('/wishlist/<int:user_id>')
    def wishlist(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404)
        items = db.execute(
            "SELECT p.* FROM wishlists w JOIN products p ON w.product_id = p.id "
            "WHERE w.user_id = ?",
            (user_id,)
        ).fetchall()
        return render_template('wishlist.html', profile=user, items=items)
