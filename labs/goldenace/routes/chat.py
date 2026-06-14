from datetime import datetime, timezone
from flask import make_response, request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/chat', methods=['GET', 'POST'])
    def chat():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid = session['user_id']
        db  = get_db()

        if request.method == 'POST':
            # VULN: stored XSS — message stored raw with no sanitisation
            msg = request.form.get('message', '').strip()
            if msg:
                now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                db.execute(
                    "INSERT INTO chat_messages (user_id, message, created_at) VALUES (?, ?, ?)",
                    (uid, msg, now)
                )
                db.commit()
            return redirect(url_for('chat'))

        messages = db.execute(
            "SELECT c.id, c.message, c.created_at, u.username, u.display_name"
            " FROM chat_messages c JOIN users u ON c.user_id = u.id"
            " ORDER BY c.id DESC LIMIT 50"
        ).fetchall()
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        resp = make_response(render_template('chat.html', messages=messages, user=user))
        resp.set_cookie('xss_challenge', 'FLAG{ga_xss_chat_cookie}', httponly=False)
        return resp
