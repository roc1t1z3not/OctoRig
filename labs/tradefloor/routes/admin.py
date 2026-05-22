from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_admin():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user or not user['is_admin']:
        return render_template('403.html'), 403
    return None


def init(app):

    @app.route('/admin')
    def admin_index():
        err = _require_admin()
        if err:
            return err
        db        = get_db()
        users     = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
        orders    = db.execute("SELECT COUNT(*) AS c FROM orders WHERE status='open'").fetchone()['c']
        return render_template('admin.html', user_count=users, open_orders=orders)

    @app.route('/admin/users')
    def admin_users():
        err = _require_admin()
        if err:
            return err
        rows = get_db().execute("SELECT * FROM users ORDER BY id").fetchall()
        return render_template('admin_users.html', users=rows)

    # VULN: broken access control — only checks session['user_id'], NOT is_admin
    @app.route('/admin/users/<int:user_id>')
    def admin_user(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user   = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return render_template('404.html'), 404
        orders = get_db().execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        holdings = get_db().execute(
            "SELECT h.*, m.name, m.price FROM portfolio_holdings h "
            "JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = ?",
            (user_id,)
        ).fetchall()
        return render_template('admin_user.html', profile=user, orders=orders, holdings=holdings)

    @app.route('/admin/corporate_action', methods=['POST'])
    def admin_corporate_action():
        err = _require_admin()
        if err:
            return err
        action_type = request.form.get('action_type', '')
        symbol      = request.form.get('symbol', '').upper().strip()
        value       = request.form.get('value', '')
        db          = get_db()
        if action_type == 'price_update' and symbol and value:
            db.execute("UPDATE market_data SET price = ? WHERE symbol = ?", (float(value), symbol))
            db.commit()
        return redirect(url_for('admin_index'))
