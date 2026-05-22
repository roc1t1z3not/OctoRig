from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: SQLi + reflected XSS — q injected into query and rendered with | safe
    @app.route('/board')
    def board():
        redir = _require_login()
        if redir:
            return redir
        q   = request.args.get('q', '')
        db  = get_db()
        if q:
            threads = db.execute(
                f"SELECT t.*, u.username FROM board_threads t JOIN users u ON t.user_id = u.id "
                f"WHERE t.title LIKE '%{q}%' OR t.body LIKE '%{q}%' ORDER BY t.created_at DESC"
            ).fetchall()
        else:
            threads = db.execute(
                "SELECT t.*, u.username FROM board_threads t JOIN users u ON t.user_id = u.id "
                "ORDER BY t.created_at DESC"
            ).fetchall()
        return render_template('board.html', threads=threads, q=q)

    @app.route('/board/new', methods=['GET', 'POST'])
    def board_new():
        redir = _require_login()
        if redir:
            return redir
        error = None
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            body  = request.form.get('body', '').strip()
            if not (title and body):
                error = 'Title and message are required.'
            else:
                uid = session['user_id']
                db  = get_db()
                db.execute(
                    "INSERT INTO board_threads (user_id, title, body, created_at) VALUES (?, ?, ?, ?)",
                    (uid, title, body, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                )
                db.commit()
                return redirect(url_for('board'))
        return render_template('board_new.html', error=error)

    @app.route('/board/<int:thread_id>')
    def board_thread(thread_id):
        redir = _require_login()
        if redir:
            return redir
        thread  = get_db().execute(
            "SELECT t.*, u.username FROM board_threads t JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (thread_id,)
        ).fetchone()
        if not thread:
            return render_template('404.html'), 404
        replies = get_db().execute(
            "SELECT r.*, u.username FROM board_replies r "
            "JOIN users u ON r.user_id = u.id WHERE r.thread_id = ? ORDER BY r.created_at",
            (thread_id,)
        ).fetchall()
        return render_template('board_thread.html', thread=thread, replies=replies)

    @app.route('/board/<int:thread_id>/reply', methods=['POST'])
    def board_reply(thread_id):
        redir = _require_login()
        if redir:
            return redir
        body = request.form.get('body', '').strip()
        if body:
            uid = session['user_id']
            db  = get_db()
            db.execute(
                "INSERT INTO board_replies (thread_id, user_id, body, created_at) VALUES (?, ?, ?, ?)",
                (thread_id, uid, body, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()
        return redirect(url_for('board_thread', thread_id=thread_id))
