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
        uid = session['user_id']
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        invoices = get_db().execute(
            "SELECT * FROM invoices WHERE user_id = ? ORDER BY issued_date DESC LIMIT 3", (uid,)
        ).fetchall()
        return render_template('dashboard.html', user=user, invoices=invoices)

    # VULN: IDOR — no ownership check, any authenticated user can view any profile
    @app.route('/account/<int:user_id>')
    def account(user_id):
        redir = _require_login()
        if redir:
            return redir
        user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return render_template('404.html'), 404
        return render_template('account.html', profile=user)

    # VULN: IDOR write — no ownership check, any authenticated user can update any profile
    @app.route('/account/<int:user_id>/update', methods=['POST'])
    def account_update(user_id):
        redir = _require_login()
        if redir:
            return redir
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        phone     = request.form.get('phone', '').strip()
        address   = request.form.get('address', '').strip()
        bio       = request.form.get('bio', '').strip()
        db = get_db()
        db.execute(
            "UPDATE users SET full_name=?, email=?, phone=?, address=?, bio=? WHERE id=?",
            (full_name, email, phone, address, bio, user_id)
        )
        db.commit()
        return redirect(url_for('account', user_id=user_id))
