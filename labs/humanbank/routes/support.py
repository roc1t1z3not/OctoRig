from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db


def init(app):

    # ── Tickets — IDOR on detail (no ownership check), stored XSS in body ────

    @app.route('/tickets')
    def tickets():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        rows = get_db().execute(
            "SELECT * FROM support_tickets WHERE user_id = ? ORDER BY created_at DESC",
            (session['user_id'],)
        ).fetchall()
        return render_template('tickets.html', tickets=rows)

    @app.route('/tickets/new', methods=['GET', 'POST'])
    def ticket_new():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        if request.method == 'POST':
            subject = request.form.get('subject', '').strip()
            body    = request.form.get('body', '').strip()
            if subject and body:
                db = get_db()
                db.execute(
                    "INSERT INTO support_tickets (user_id, subject, body, status, created_at) "
                    "VALUES (?, ?, ?, 'open', ?)",
                    (session['user_id'], subject, body, str(date.today()))
                )
                db.commit()
                return redirect(url_for('tickets'))
        return render_template('ticket_new.html')

    # IDOR: no check that ticket belongs to session user
    @app.route('/tickets/<int:ticket_id>')
    def ticket_detail(ticket_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db     = get_db()
        ticket = db.execute(
            "SELECT t.*, u.username, u.full_name FROM support_tickets t "
            "JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (ticket_id,)
        ).fetchone()
        if not ticket:
            abort(404)
        replies = db.execute(
            "SELECT r.*, u.username FROM ticket_replies r "
            "JOIN users u ON r.user_id = u.id WHERE r.ticket_id = ? "
            "ORDER BY r.created_at ASC",
            (ticket_id,)
        ).fetchall()
        return render_template('ticket_detail.html', ticket=ticket, replies=replies)

    @app.route('/tickets/<int:ticket_id>/reply', methods=['POST'])
    def ticket_reply(ticket_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        body = request.form.get('body', '').strip()
        if body:
            db = get_db()
            db.execute(
                "INSERT INTO ticket_replies (ticket_id, user_id, body, is_admin, created_at) "
                "VALUES (?, ?, ?, 0, ?)",
                (ticket_id, session['user_id'], body, str(date.today()))
            )
            db.commit()
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
