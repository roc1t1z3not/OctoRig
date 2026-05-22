from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db


def init(app):

    # ── Board — SQLi via ?q search, stored XSS via body/reply ────────────────

    @app.route('/board')
    def board():
        q  = request.args.get('q', '').strip()
        db = get_db()
        if q:
            threads = db.execute(
                f"SELECT bt.*, u.username FROM board_threads bt "
                f"JOIN users u ON bt.user_id = u.id "
                f"WHERE bt.title LIKE '%{q}%' OR bt.body LIKE '%{q}%' "
                f"ORDER BY bt.posted_at DESC"
            ).fetchall()
        else:
            threads = db.execute(
                "SELECT bt.*, u.username FROM board_threads bt "
                "JOIN users u ON bt.user_id = u.id ORDER BY bt.posted_at DESC"
            ).fetchall()
        return render_template('board.html', threads=threads, q=q)

    @app.route('/board/new', methods=['GET', 'POST'])
    def board_new():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            body  = request.form.get('body', '').strip()
            if title and body:
                db = get_db()
                db.execute(
                    "INSERT INTO board_threads (user_id, title, body, posted_at) VALUES (?, ?, ?, ?)",
                    (session['user_id'], title, body, str(date.today()))
                )
                db.commit()
                tid = db.execute("SELECT last_insert_rowid()").fetchone()[0]
                return redirect(url_for('board_thread', thread_id=tid))
        return render_template('board_new.html')

    @app.route('/board/<int:thread_id>')
    def board_thread(thread_id):
        db = get_db()
        t = db.execute(
            "SELECT bt.*, u.username FROM board_threads bt "
            "JOIN users u ON bt.user_id = u.id WHERE bt.id = ?",
            (thread_id,)
        ).fetchone()
        if not t:
            abort(404)
        replies = db.execute(
            "SELECT br.*, u.username FROM board_replies br "
            "JOIN users u ON br.user_id = u.id WHERE br.thread_id = ? "
            "ORDER BY br.posted_at ASC",
            (thread_id,)
        ).fetchall()
        return render_template('thread.html', thread=t, replies=replies)

    @app.route('/board/<int:thread_id>/reply', methods=['POST'])
    def board_reply(thread_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        body = request.form.get('body', '').strip()
        if body:
            db = get_db()
            db.execute(
                "INSERT INTO board_replies (thread_id, user_id, body, posted_at) VALUES (?, ?, ?, ?)",
                (thread_id, session['user_id'], body, str(date.today()))
            )
            db.commit()
        return redirect(url_for('board_thread', thread_id=thread_id))

    # IDOR: no ownership check — any logged-in user can edit any thread
    @app.route('/board/<int:thread_id>/edit', methods=['GET', 'POST'])
    def board_edit(thread_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        t = db.execute("SELECT * FROM board_threads WHERE id = ?", (thread_id,)).fetchone()
        if not t:
            abort(404)
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            body  = request.form.get('body', '').strip()
            if title and body:
                db.execute(
                    "UPDATE board_threads SET title = ?, body = ? WHERE id = ?",
                    (title, body, thread_id)
                )
                db.commit()
            return redirect(url_for('board_thread', thread_id=thread_id))
        return render_template('board_edit.html', thread=t)

    # IDOR: no ownership check — any logged-in user can delete any thread
    @app.route('/board/<int:thread_id>/delete', methods=['POST'])
    def board_delete(thread_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        db.execute("DELETE FROM board_threads WHERE id = ?", (thread_id,))
        db.execute("DELETE FROM board_replies WHERE thread_id = ?", (thread_id,))
        db.commit()
        return redirect(url_for('board'))

    # IDOR: no ownership check on reply edit/delete either
    @app.route('/board/reply/<int:reply_id>/edit', methods=['GET', 'POST'])
    def reply_edit(reply_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        r = db.execute("SELECT * FROM board_replies WHERE id = ?", (reply_id,)).fetchone()
        if not r:
            abort(404)
        if request.method == 'POST':
            body = request.form.get('body', '').strip()
            if body:
                db.execute("UPDATE board_replies SET body = ? WHERE id = ?", (body, reply_id))
                db.commit()
            return redirect(url_for('board_thread', thread_id=r['thread_id']))
        return render_template('reply_edit.html', reply=r)

    @app.route('/board/reply/<int:reply_id>/delete', methods=['POST'])
    def reply_delete(reply_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        r = db.execute("SELECT thread_id FROM board_replies WHERE id = ?", (reply_id,)).fetchone()
        if not r:
            abort(404)
        db.execute("DELETE FROM board_replies WHERE id = ?", (reply_id,))
        db.commit()
        return redirect(url_for('board_thread', thread_id=r['thread_id']))
