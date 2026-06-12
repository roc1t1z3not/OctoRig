# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/messages')
    def messages_inbox():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        uid = session['user_id']
        inbox = db.execute(
            "SELECT m.*, u.username as sender_name FROM messages m "
            "JOIN users u ON m.sender_id = u.id "
            "WHERE m.recipient_id = ? ORDER BY m.created_at DESC",
            (uid,)
        ).fetchall()
        sent = db.execute(
            "SELECT m.*, u.username as recipient_name FROM messages m "
            "JOIN users u ON m.recipient_id = u.id "
            "WHERE m.sender_id = ? ORDER BY m.created_at DESC",
            (uid,)
        ).fetchall()
        return render_template('messages.html', inbox=inbox, sent=sent)

    @app.route('/messages/<int:msg_id>')
    def message_view(msg_id):
        # VULN: IDOR — fetches by id only, no sender/recipient ownership check
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        msg = db.execute(
            "SELECT m.*, su.username as sender_name, ru.username as recipient_name "
            "FROM messages m JOIN users su ON m.sender_id = su.id "
            "JOIN users ru ON m.recipient_id = ru.id "
            "WHERE m.id = ?",
            (msg_id,)
        ).fetchone()
        if not msg:
            return render_template('404.html'), 404
        db.execute("UPDATE messages SET read = 1 WHERE id = ?", (msg_id,))
        db.commit()
        return render_template('message_view.html', msg=msg)

    @app.route('/messages/new', methods=['GET', 'POST'])
    def message_new():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db    = get_db()
        error = None
        to    = request.args.get('to', '')
        if request.method == 'POST':
            to_name = request.form.get('to', '').strip()
            subject = request.form.get('subject', '').strip()
            body    = request.form.get('body', '').strip()
            if not (to_name and subject and body):
                error = 'All fields are required.'
            else:
                recipient = db.execute("SELECT * FROM users WHERE username = ?", (to_name,)).fetchone()
                if not recipient:
                    error = f'User "{to_name}" not found.'
                else:
                    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    db.execute(
                        "INSERT INTO messages (sender_id, recipient_id, subject, body, read, created_at)"
                        " VALUES (?, ?, ?, ?, 0, ?)",
                        (session['user_id'], recipient['id'], subject, body, now)
                    )
                    db.commit()
                    return redirect(url_for('messages_inbox'))
        return render_template('message_new.html', error=error, to=to)
