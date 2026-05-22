from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: SQLi — month and plan params injected directly into WHERE clause
    @app.route('/billing')
    def billing():
        redir = _require_login()
        if redir:
            return redir
        uid   = session['user_id']
        month = request.args.get('month', '').strip()
        plan  = request.args.get('plan', '').strip()

        where = f"user_id = {uid}"
        if month:
            where += f" AND issued_date LIKE '{month}%'"
        if plan:
            where += f" AND description LIKE '%{plan}%'"

        invoices = get_db().execute(
            f"SELECT * FROM invoices WHERE {where} ORDER BY issued_date DESC"
        ).fetchall()
        return render_template('billing.html', invoices=invoices, month=month, plan=plan)

    # VULN: IDOR — no ownership check, any authenticated user can view any invoice
    @app.route('/billing/<int:invoice_id>')
    def invoice_detail(invoice_id):
        redir = _require_login()
        if redir:
            return redir
        row = get_db().execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
        if not row:
            return render_template('404.html'), 404
        owner = get_db().execute("SELECT * FROM users WHERE id = ?", (row['user_id'],)).fetchone()
        return render_template('invoice.html', invoice=row, owner=owner)

    @app.route('/billing/usage')
    def billing_usage():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        return render_template('usage.html', user=user)
