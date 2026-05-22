from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db
from helpers import current_user


def init(app):

    # ── Admin tickets — correct is_admin check, stored XSS fires here ────────

    @app.route('/admin/tickets')
    def admin_tickets():
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        db      = get_db()
        tickets = db.execute(
            "SELECT t.*, u.username, u.full_name FROM support_tickets t "
            "JOIN users u ON t.user_id = u.id ORDER BY t.created_at DESC"
        ).fetchall()
        replies = {
            r['ticket_id']: r for r in db.execute(
                "SELECT r.*, u.username FROM ticket_replies r "
                "JOIN users u ON r.user_id = u.id ORDER BY r.created_at ASC"
            ).fetchall()
        }
        return render_template('admin_tickets.html', tickets=tickets, replies=replies)

    @app.route('/admin/tickets/<int:ticket_id>/reply', methods=['POST'])
    def admin_ticket_reply(ticket_id):
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        body = request.form.get('body', '').strip()
        if body:
            db = get_db()
            db.execute(
                "INSERT INTO ticket_replies (ticket_id, user_id, body, is_admin, created_at) "
                "VALUES (?, ?, ?, 1, ?)",
                (ticket_id, u['id'], body, str(date.today()))
            )
            db.execute(
                "UPDATE support_tickets SET status = 'closed' WHERE id = ?", (ticket_id,)
            )
            db.commit()
        return redirect(url_for('admin_tickets'))

    # ── Admin users — correct check on list, BROKEN check on detail ──────────

    @app.route('/admin/users')
    def admin_users():
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        users = get_db().execute(
            "SELECT u.*, COUNT(a.id) as account_count FROM users u "
            "LEFT JOIN accounts a ON u.id = a.user_id GROUP BY u.id ORDER BY u.id"
        ).fetchall()
        return render_template('admin_users.html', users=users)

    # VULN: only checks login, not is_admin — broken access control
    @app.route('/admin/users/<int:user_id>')
    def admin_user_detail(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404)
        accounts = db.execute(
            "SELECT * FROM accounts WHERE user_id = ?", (user_id,)
        ).fetchall()
        tickets = db.execute(
            "SELECT * FROM support_tickets WHERE user_id = ?", (user_id,)
        ).fetchall()
        docs = db.execute(
            "SELECT * FROM documents WHERE user_id = ?", (user_id,)
        ).fetchall()
        return render_template('admin_user_detail.html',
                               profile=user, accounts=accounts,
                               tickets=tickets, docs=docs)
