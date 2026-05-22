from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        holdings = db.execute(
            "SELECT h.*, m.name, m.price, m.change FROM portfolio_holdings h "
            "JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = ?",
            (uid,)
        ).fetchall()
        alerts = db.execute(
            "SELECT * FROM alerts WHERE user_id = ? AND active = 1 ORDER BY created_at DESC LIMIT 5",
            (uid,)
        ).fetchall()
        return render_template('dashboard.html', user=user, holdings=holdings, alerts=alerts)

    @app.route('/portfolio')
    def portfolio():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        holdings = db.execute(
            "SELECT h.*, m.name, m.price, m.change FROM portfolio_holdings h "
            "JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = ?",
            (uid,)
        ).fetchall()
        return render_template('portfolio.html', user=user, holdings=holdings)

    @app.route('/orders')
    def orders():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        rows = get_db().execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        return render_template('orders.html', orders=rows)

    # VULN: IDOR — no ownership check, any authenticated user can view any order
    @app.route('/orders/<int:order_id>')
    def order_detail(order_id):
        redir = _require_login()
        if redir:
            return redir
        order = get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            return render_template('404.html'), 404
        owner = get_db().execute("SELECT * FROM users WHERE id = ?", (order['user_id'],)).fetchone()
        return render_template('order_detail.html', order=order, owner=owner)
