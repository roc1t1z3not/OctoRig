from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db


def init(app):

    # ── Inbox — IDOR: message detail has no ownership check ──────────────────

    @app.route('/inbox')
    def inbox():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db  = get_db()
        received = db.execute(
            "SELECT m.*, u.username as from_username FROM messages m "
            "JOIN users u ON m.from_id = u.id WHERE m.to_id = ? ORDER BY m.sent_at DESC",
            (uid,)
        ).fetchall()
        sent = db.execute(
            "SELECT m.*, u.username as to_username FROM messages m "
            "JOIN users u ON m.to_id = u.id WHERE m.from_id = ? ORDER BY m.sent_at DESC",
            (uid,)
        ).fetchall()
        return render_template('inbox.html', received=received, sent=sent)

    # IDOR: fetches by id only — no check that viewer is the recipient
    @app.route('/inbox/<int:msg_id>')
    def inbox_message(msg_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        msg = db.execute(
            "SELECT m.*, uf.username as from_username, ut.username as to_username "
            "FROM messages m "
            "JOIN users uf ON m.from_id = uf.id "
            "JOIN users ut ON m.to_id = ut.id "
            "WHERE m.id = ?",
            (msg_id,)
        ).fetchone()
        if not msg:
            abort(404)
        db.execute("UPDATE messages SET read = 1 WHERE id = ?", (msg_id,))
        db.commit()
        return render_template('message.html', msg=msg)

    @app.route('/inbox/compose', methods=['GET', 'POST'])
    def inbox_compose():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db    = get_db()
        users = db.execute(
            "SELECT id, username FROM users WHERE id != ? ORDER BY username",
            (session['user_id'],)
        ).fetchall()
        if request.method == 'POST':
            to_id   = int(request.form.get('to_id', 0))
            subject = request.form.get('subject', '').strip()
            body    = request.form.get('body', '').strip()
            if to_id and subject and body:
                db.execute(
                    "INSERT INTO messages (from_id, to_id, subject, body, sent_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (session['user_id'], to_id, subject, body, str(date.today()))
                )
                db.commit()
                return redirect(url_for('inbox'))
        to_id = request.args.get('to', '')
        return render_template('compose.html', users=users, to_id=str(to_id))
