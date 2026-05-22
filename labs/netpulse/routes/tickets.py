from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/tickets')
    def tickets():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        rows = get_db().execute(
            "SELECT * FROM support_tickets WHERE user_id = ? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        return render_template('tickets.html', tickets=rows)

    @app.route('/tickets/new', methods=['GET', 'POST'])
    def ticket_new():
        redir = _require_login()
        if redir:
            return redir
        error = None
        if request.method == 'POST':
            subject = request.form.get('subject', '').strip()
            body    = request.form.get('body', '').strip()
            if not (subject and body):
                error = 'Subject and message are required.'
            else:
                uid = session['user_id']
                db  = get_db()
                db.execute(
                    "INSERT INTO support_tickets (user_id, subject, body, created_at) VALUES (?, ?, ?, ?)",
                    (uid, subject, body, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                )
                db.commit()
                return redirect(url_for('tickets'))
        return render_template('ticket_new.html', error=error)

    @app.route('/tickets/<int:ticket_id>')
    def ticket_detail(ticket_id):
        redir = _require_login()
        if redir:
            return redir
        ticket  = get_db().execute("SELECT * FROM support_tickets WHERE id = ?", (ticket_id,)).fetchone()
        if not ticket:
            return render_template('404.html'), 404
        replies = get_db().execute(
            "SELECT r.*, u.username FROM ticket_replies r "
            "JOIN users u ON r.user_id = u.id WHERE r.ticket_id = ? ORDER BY r.created_at",
            (ticket_id,)
        ).fetchall()
        return render_template('ticket_detail.html', ticket=ticket, replies=replies)

    @app.route('/tickets/<int:ticket_id>/reply', methods=['POST'])
    def ticket_reply(ticket_id):
        redir = _require_login()
        if redir:
            return redir
        body = request.form.get('body', '').strip()
        if body:
            uid = session['user_id']
            db  = get_db()
            db.execute(
                "INSERT INTO ticket_replies (ticket_id, user_id, body, created_at) VALUES (?, ?, ?, ?)",
                (ticket_id, uid, body, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
