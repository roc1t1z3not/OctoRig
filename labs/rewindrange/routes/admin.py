from flask import request, render_template, render_template_string, redirect, url_for, abort
from db import get_db
from helpers import current_user

VALID_STATUSES = ('pending', 'processing', 'shipped', 'delivered', 'cancelled')

# Login-bypass flag — shown to anyone who reaches an admin page
LOGIN_BYPASS_FLAG = "FLAG{rw_admin_login_bypassed}"


def init(app):

    @app.route('/admin')
    @app.route('/admin/')
    @app.route('/admin/orders')
    def admin_orders():
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        orders = get_db().execute(
            "SELECT o.*, u.username FROM orders o "
            "JOIN users u ON o.user_id = u.id "
            "ORDER BY o.order_date DESC"
        ).fetchall()
        # Inject flag banner via render_template_string wrapping the normal template
        base = render_template('admin_orders.html', orders=orders,
                               valid_statuses=VALID_STATUSES)
        banner = (
            f'<div style="background:#0d1117;color:#3fb950;font-family:monospace;'
            f'padding:.5rem 1rem;border-bottom:1px solid #21262d;">'
            f'&#x1F3C6; Login bypass confirmed &mdash; '
            f'<code>{LOGIN_BYPASS_FLAG}</code></div>'
        )
        return banner + base

    @app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
    def admin_order_status(order_id):
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        status = request.form.get('status', '').strip()
        if status in VALID_STATUSES:
            db = get_db()
            db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            db.commit()
        return redirect(url_for('admin_orders'))
