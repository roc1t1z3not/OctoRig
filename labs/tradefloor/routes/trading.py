from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: CSRF — no token on any POST; state-changing trade form exploitable cross-origin
    @app.route('/trade', methods=['GET', 'POST'])
    def trade():
        redir = _require_login()
        if redir:
            return redir
        uid     = session['user_id']
        db      = get_db()
        message = None
        error   = None
        symbols = db.execute("SELECT * FROM market_data ORDER BY symbol").fetchall()
        user    = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

        # Pre-load holding for the requested symbol so the market detail TRADE button works.
        # VULN: SQLi — symbol_pre is concatenated directly into the query string
        symbol_pre = request.args.get('symbol', '').upper()
        action_pre = request.args.get('action', 'buy').lower()
        holding = None
        if symbol_pre:
            try:
                holding = db.execute(
                    f"SELECT h.*, m.price, m.name FROM portfolio_holdings h "
                    f"JOIN market_data m ON h.symbol = m.symbol "
                    f"WHERE h.user_id = {uid} AND h.symbol = '{symbol_pre}'"
                ).fetchone()
            except Exception:
                holding = None

        if request.method == 'POST':
            symbol     = request.form.get('symbol', '').strip()
            action     = request.form.get('action', 'buy').strip()
            quantity   = int(request.form.get('quantity', 0) or 0)
            order_type = request.form.get('order_type', 'market').strip()
            price      = float(request.form.get('price', 0) or 0)
            # VULN: stored XSS — memo saved raw and rendered with | safe in order detail
            memo = request.form.get('memo', '')

            mkt = db.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol.upper(),)).fetchone()
            if not mkt or quantity <= 0:
                # VULN: reflected XSS — symbol echoed back inside HTML with | safe
                error = f'Invalid order: symbol <b>{symbol}</b> — unknown or quantity invalid.'
            else:
                exec_price = mkt['price'] if order_type == 'market' else price
                total      = exec_price * quantity

                if action == 'buy':
                    if order_type == 'market':
                        if user['balance'] < total:
                            error = (f'Insufficient funds. '
                                     f'Required: ${total:.2f} — Available: ${user["balance"]:.2f}')
                        else:
                            db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total, uid))
                            ex = db.execute(
                                "SELECT * FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                                (uid, symbol.upper())
                            ).fetchone()
                            if ex:
                                new_qty = ex['quantity'] + quantity
                                new_avg = ((ex['avg_price'] * ex['quantity']) + total) / new_qty
                                db.execute(
                                    "UPDATE portfolio_holdings SET quantity = ?, avg_price = ? "
                                    "WHERE user_id = ? AND symbol = ?",
                                    (new_qty, new_avg, uid, symbol.upper())
                                )
                            else:
                                db.execute(
                                    "INSERT INTO portfolio_holdings (user_id, symbol, quantity, avg_price) "
                                    "VALUES (?, ?, ?, ?)",
                                    (uid, symbol.upper(), quantity, exec_price)
                                )
                            db.execute(
                                "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                                "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'filled', ?, ?)",
                                (uid, symbol.upper(), action, quantity, order_type,
                                 exec_price, datetime.utcnow().strftime('%Y-%m-%d'), memo)
                            )
                            db.commit()
                            user       = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
                            symbol_pre = symbol.upper()
                            holding    = db.execute(
                                "SELECT h.*, m.price, m.name FROM portfolio_holdings h "
                                "JOIN market_data m ON h.symbol = m.symbol "
                                "WHERE h.user_id = ? AND h.symbol = ?",
                                (uid, symbol.upper())
                            ).fetchone()
                            message = f'Bought {quantity} x {symbol.upper()} @ ${exec_price:.2f} — cost ${total:.2f}'
                    else:
                        db.execute(
                            "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                            "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)",
                            (uid, symbol.upper(), action, quantity, order_type,
                             price, datetime.utcnow().strftime('%Y-%m-%d'), memo)
                        )
                        db.commit()
                        message = f'Limit BUY placed: {quantity} x {symbol.upper()} @ ${price:.2f}'

                elif action == 'sell':
                    ex = db.execute(
                        "SELECT * FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                        (uid, symbol.upper())
                    ).fetchone()
                    if order_type == 'market':
                        held = ex['quantity'] if ex else 0
                        if held < quantity:
                            error = (f'Insufficient holdings: holding {held} x {symbol.upper()}, '
                                     f'cannot sell {quantity}.')
                        else:
                            proceeds = exec_price * quantity
                            db.execute(
                                "UPDATE users SET balance = balance + ? WHERE id = ?", (proceeds, uid)
                            )
                            new_qty = held - quantity
                            if new_qty == 0:
                                db.execute(
                                    "DELETE FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                                    (uid, symbol.upper())
                                )
                            else:
                                db.execute(
                                    "UPDATE portfolio_holdings SET quantity = ? "
                                    "WHERE user_id = ? AND symbol = ?",
                                    (new_qty, uid, symbol.upper())
                                )
                            db.execute(
                                "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                                "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'filled', ?, ?)",
                                (uid, symbol.upper(), action, quantity, order_type,
                                 exec_price, datetime.utcnow().strftime('%Y-%m-%d'), memo)
                            )
                            db.commit()
                            user       = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
                            symbol_pre = symbol.upper()
                            holding    = db.execute(
                                "SELECT h.*, m.price, m.name FROM portfolio_holdings h "
                                "JOIN market_data m ON h.symbol = m.symbol "
                                "WHERE h.user_id = ? AND h.symbol = ?",
                                (uid, symbol.upper())
                            ).fetchone()
                            message = f'Sold {quantity} x {symbol.upper()} @ ${exec_price:.2f} — proceeds ${proceeds:.2f}'
                    else:
                        db.execute(
                            "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                            "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)",
                            (uid, symbol.upper(), action, quantity, order_type,
                             price, datetime.utcnow().strftime('%Y-%m-%d'), memo)
                        )
                        db.commit()
                        message = f'Limit SELL placed: {quantity} x {symbol.upper()} @ ${price:.2f}'

        return render_template('trade.html',
                               symbols=symbols, message=message, error=error,
                               user=user, symbol_pre=symbol_pre,
                               action_pre=action_pre, holding=holding)

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
