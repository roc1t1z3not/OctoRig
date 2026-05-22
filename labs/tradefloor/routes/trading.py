from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: CSRF — no token, state-changing trade form exploitable cross-origin
    @app.route('/trade', methods=['GET', 'POST'])
    def trade():
        redir = _require_login()
        if redir:
            return redir
        uid      = session['user_id']
        db       = get_db()
        message  = None
        error    = None
        symbols  = db.execute("SELECT * FROM market_data ORDER BY symbol").fetchall()

        if request.method == 'POST':
            symbol     = request.form.get('symbol', '').upper().strip()
            action     = request.form.get('action', 'buy')
            quantity   = int(request.form.get('quantity', 0) or 0)
            order_type = request.form.get('order_type', 'market')
            price      = float(request.form.get('price', 0) or 0)

            mkt = db.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol,)).fetchone()
            if not mkt or quantity <= 0:
                error = 'Invalid symbol or quantity.'
            else:
                exec_price = mkt['price'] if order_type == 'market' else price
                db.execute(
                    "INSERT INTO orders (user_id, symbol, action, quantity, order_type, price, status, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (uid, symbol, action, quantity, order_type,
                     exec_price, 'filled' if order_type == 'market' else 'open',
                     datetime.utcnow().strftime('%Y-%m-%d'))
                )
                db.commit()
                message = f"Order placed: {action.upper()} {quantity} x {symbol} @ ${exec_price:.2f}"

        return render_template('trade.html', symbols=symbols, message=message, error=error)

    @app.route('/market')
    def market():
        redir = _require_login()
        if redir:
            return redir
        stocks = get_db().execute("SELECT * FROM market_data ORDER BY symbol").fetchall()
        return render_template('market.html', stocks=stocks)

    @app.route('/market/<symbol>')
    def market_detail(symbol):
        redir = _require_login()
        if redir:
            return redir
        symbol = symbol.upper()
        db     = get_db()
        uid    = session['user_id']
        stock  = db.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol,)).fetchone()
        if not stock:
            return redirect(url_for('market'))
        filings  = db.execute(
            "SELECT * FROM filings WHERE symbol = ? ORDER BY filed_date DESC", (symbol,)
        ).fetchall()
        wl_entry = db.execute(
            "SELECT id FROM watchlist WHERE user_id = ? AND symbol = ?", (uid, symbol)
        ).fetchone()
        return render_template('stock_detail.html', stock=stock, filings=filings, wl_entry=wl_entry)

    # VULN: CSRF — cancel endpoint is state-changing with no CSRF token
    # VULN: IDOR — no ownership check on order_id
    @app.route('/orders/<int:order_id>/cancel', methods=['POST'])
    def order_cancel(order_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        db.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (order_id,))
        db.commit()
        return redirect(url_for('orders'))
