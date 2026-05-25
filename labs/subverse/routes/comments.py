# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import request, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/post/<int:post_id>/comment', methods=['POST'])
    def comment_add(post_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        body      = request.form.get('body', '').strip()
        parent_id = request.form.get('parent_id') or None
        if body:
            db  = get_db()
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            db.execute(
                "INSERT INTO comments (body, user_id, post_id, parent_id, score, created_at)"
                " VALUES (?, ?, ?, ?, 0, ?)",
                (body, session['user_id'], post_id, parent_id, now)
            )
            db.commit()
        return redirect(url_for('post_view', post_id=post_id))

    @app.route('/comment/<int:comment_id>/vote')
    def comment_vote(comment_id):
        # VULN: CSRF — GET-based vote with no token
        if not session.get('user_id'):
            return redirect(url_for('login'))
        v  = int(request.args.get('v', '1'))
        v  = 1 if v >= 0 else -1
        db = get_db()
        db.execute("UPDATE comments SET score = score + ? WHERE id = ?", (v, comment_id))
        db.commit()
        return redirect(request.referrer or url_for('index'))
