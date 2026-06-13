from datetime import datetime, timezone
from flask import make_response, request, render_template, session, redirect, url_for
from db import get_db


def _apply_market_impact(db, symbol, action, quantity, exec_price):
    total     = quantity * exec_price
    pct       = min(0.05, total / 2_000_000)
    if action == 'buy':
        new_price = round(max(0.50, exec_price * (1 + pct)), 2)
    else:
        new_price = round(max(0.50, exec_price * (1 - pct)), 2)
    delta = round(new_price - exec_price, 2)
    db.execute("UPDATE market_data SET price = ?, change = ? WHERE symbol = ?",
               (new_price, delta, symbol))
    db.execute(
        "INSERT OR IGNORE INTO price_history (symbol, price, recorded_at) VALUES (?, ?, ?)",
        (symbol, new_price, datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'))
    )


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
                                 exec_price, datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                            )
                            _apply_market_impact(db, symbol.upper(), 'buy', quantity, exec_price)
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
                             price, datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
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
                                 exec_price, datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                            )
                            _apply_market_impact(db, symbol.upper(), 'sell', quantity, exec_price)
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
                             price, datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
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
        db = get_db()
        q  = request.args.get('q', '').strip()
        if q:
            # VULN: SQLi — q injected directly; VULN: reflected XSS — q echoed with | safe in template
            try:
                stocks = db.execute(
                    f"SELECT * FROM market_data WHERE symbol LIKE '%{q}%' "
                    f"OR name LIKE '%{q}%' ORDER BY symbol"
                ).fetchall()
            except Exception:
                stocks = []
        else:
            stocks = db.execute("SELECT * FROM market_data ORDER BY symbol").fetchall()
        resp = make_response(render_template('market.html', stocks=stocks, q=q))
        # Non-HttpOnly cookie — readable via document.cookie (XSS challenge target)
        resp.set_cookie('xss_challenge', 'FLAG{tf_reflected_xss_fired}', httponly=False)
        return resp

    @app.route('/market/<symbol>', methods=['GET', 'POST'])
    def market_detail(symbol):
        redir = _require_login()
        if redir:
            return redir
        symbol  = symbol.upper()
        db      = get_db()
        uid     = session['user_id']
        stock   = db.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol,)).fetchone()
        if not stock:
            return redirect(url_for('market'))

        message = None
        error   = None

        if request.method == 'POST':
            action     = request.form.get('action', 'buy').strip()
            order_type = request.form.get('order_type', 'market').strip()
            memo       = request.form.get('memo', '')
            try:
                quantity = int(request.form.get('quantity', 0) or 0)
                price    = float(request.form.get('price', 0) or 0)
            except ValueError:
                error = 'Invalid quantity or price.'
                quantity, price = 0, 0

            if not error:
                user       = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
                exec_price = stock['price'] if order_type == 'market' else price
                total      = exec_price * quantity

                if quantity <= 0:
                    error = 'Quantity must be at least 1.'
                elif action == 'buy':
                    if order_type == 'market':
                        if user['balance'] < total:
                            error = f'Insufficient funds. Need ${total:.2f}, have ${user["balance"]:.2f}'
                        else:
                            db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (total, uid))
                            ex = db.execute(
                                "SELECT * FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                                (uid, symbol)
                            ).fetchone()
                            if ex:
                                new_qty = ex['quantity'] + quantity
                                new_avg = ((ex['avg_price'] * ex['quantity']) + total) / new_qty
                                db.execute(
                                    "UPDATE portfolio_holdings SET quantity = ?, avg_price = ? "
                                    "WHERE user_id = ? AND symbol = ?",
                                    (new_qty, new_avg, uid, symbol)
                                )
                            else:
                                db.execute(
                                    "INSERT INTO portfolio_holdings (user_id, symbol, quantity, avg_price) "
                                    "VALUES (?, ?, ?, ?)", (uid, symbol, quantity, exec_price)
                                )
                            db.execute(
                                "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                                "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'filled', ?, ?)",
                                (uid, symbol, action, quantity, order_type, exec_price,
                                 datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                            )
                            _apply_market_impact(db, symbol, 'buy', quantity, exec_price)
                            db.commit()
                            message = f'Bought {quantity} × {symbol} @ ${exec_price:.2f} — cost ${total:.2f}'
                    else:
                        db.execute(
                            "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                            "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)",
                            (uid, symbol, action, quantity, order_type, price,
                             datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                        )
                        db.commit()
                        message = f'Limit BUY placed: {quantity} × {symbol} @ ${price:.2f}'

                elif action == 'sell':
                    ex = db.execute(
                        "SELECT * FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                        (uid, symbol)
                    ).fetchone()
                    if order_type == 'market':
                        held = ex['quantity'] if ex else 0
                        if held < quantity:
                            error = f'You hold {held} × {symbol} — cannot sell {quantity}.'
                        else:
                            proceeds = exec_price * quantity
                            db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (proceeds, uid))
                            new_qty = held - quantity
                            if new_qty == 0:
                                db.execute(
                                    "DELETE FROM portfolio_holdings WHERE user_id = ? AND symbol = ?",
                                    (uid, symbol)
                                )
                            else:
                                db.execute(
                                    "UPDATE portfolio_holdings SET quantity = ? "
                                    "WHERE user_id = ? AND symbol = ?", (new_qty, uid, symbol)
                                )
                            db.execute(
                                "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                                "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'filled', ?, ?)",
                                (uid, symbol, action, quantity, order_type, exec_price,
                                 datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                            )
                            _apply_market_impact(db, symbol, 'sell', quantity, exec_price)
                            db.commit()
                            message = f'Sold {quantity} × {symbol} @ ${exec_price:.2f} — proceeds ${proceeds:.2f}'
                    else:
                        db.execute(
                            "INSERT INTO orders (user_id, symbol, action, quantity, order_type, "
                            "price, status, created_at, memo) VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)",
                            (uid, symbol, action, quantity, order_type, price,
                             datetime.now(timezone.utc).strftime('%Y-%m-%d'), memo)
                        )
                        db.commit()
                        message = f'Limit SELL placed: {quantity} × {symbol} @ ${price:.2f}'

            # Re-fetch stock so price shown after trade is current
            stock = db.execute("SELECT * FROM market_data WHERE symbol = ?", (symbol,)).fetchone()

        user     = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        holding  = db.execute(
            "SELECT h.*, m.price FROM portfolio_holdings h "
            "JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = ? AND h.symbol = ?",
            (uid, symbol)
        ).fetchone()
        filings  = db.execute(
            "SELECT * FROM filings WHERE symbol = ? ORDER BY filed_date DESC", (symbol,)
        ).fetchall()
        wl_entry = db.execute(
            "SELECT id FROM watchlist WHERE user_id = ? AND symbol = ?", (uid, symbol)
        ).fetchone()
        hi_lo    = db.execute(
            "SELECT MAX(price) AS hi, MIN(price) AS lo FROM price_history WHERE symbol = ?",
            (symbol,)
        ).fetchone()
        return render_template('stock_detail.html', stock=stock, filings=filings,
                               wl_entry=wl_entry, user=user, holding=holding,
                               message=message, error=error, hi_lo=hi_lo)

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
