from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db


def init(app):

    @app.route('/messages')
    def inbox():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db = get_db()
        received = db.execute(
            "SELECT m.*, u.full_name as from_name, u.username as from_user "
            "FROM messages m JOIN users u ON m.from_id = u.id "
            "WHERE m.to_id = ? ORDER BY m.sent_at DESC",
            (uid,)
        ).fetchall()
        sent = db.execute(
            "SELECT m.*, u.full_name as to_name, u.username as to_user "
            "FROM messages m JOIN users u ON m.to_id = u.id "
            "WHERE m.from_id = ? ORDER BY m.sent_at DESC",
            (uid,)
        ).fetchall()
        return render_template('inbox.html', received=received, sent=sent)

    # IDOR: no check that viewer is recipient or sender
    @app.route('/messages/<int:msg_id>')
    def message_view(msg_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        msg = db.execute(
            "SELECT m.*, uf.full_name as from_name, uf.username as from_user, "
            "ut.full_name as to_name, ut.username as to_user "
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
        return render_template('message_view.html', msg=msg)

    @app.route('/messages/new', methods=['GET', 'POST'])
    def message_new():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        if request.method == 'POST':
            to_username = request.form.get('to_username', '').strip()
            subject     = request.form.get('subject', '').strip()
            body        = request.form.get('body', '').strip()
            recipient   = db.execute("SELECT id FROM users WHERE username = ?", (to_username,)).fetchone()
            if not recipient:
                users = db.execute("SELECT id, username, full_name, role FROM users ORDER BY full_name").fetchall()
                return render_template('message_new.html', error='User not found.', users=users)
            db.execute(
                "INSERT INTO messages (from_id, to_id, subject, body, sent_at) VALUES (?, ?, ?, ?, ?)",
                (session['user_id'], recipient['id'], subject, body, str(date.today()))
            )
            db.commit()
            return redirect(url_for('inbox'))
        users = db.execute("SELECT id, username, full_name, role FROM users ORDER BY full_name").fetchall()
        to_user = request.args.get('to', '')
        return render_template('message_new.html', error=None, users=users, to_user=to_user)
