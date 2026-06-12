# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/communities')
    def communities_list():
        q  = request.args.get('q', '')
        db = get_db()
        if q:
            # VULN: SQLi — f-string on q
            rows = db.execute(
                f"SELECT * FROM communities WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
                f" ORDER BY member_count DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM communities ORDER BY member_count DESC"
            ).fetchall()
        return render_template('communities.html', communities=rows, q=q)

    @app.route('/community/<name>')
    def community_view(name):
        db   = get_db()
        comm = db.execute("SELECT * FROM communities WHERE name = ?", (name,)).fetchone()
        if not comm:
            return render_template('404.html'), 404
        sort  = request.args.get('sort', 'hot')
        order = 'p.score DESC' if sort != 'new' else 'p.created_at DESC'
        posts = db.execute(
            f"SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id "
            f"WHERE p.community_id = ? AND p.status = 'published' ORDER BY {order} LIMIT 50",
            (comm['id'],)
        ).fetchall()
        member = None
        if session.get('user_id'):
            member = db.execute(
                "SELECT * FROM community_members WHERE user_id = ? AND community_id = ?",
                (session['user_id'], comm['id'])
            ).fetchone()
        return render_template('community.html', comm=comm, posts=posts, member=member, sort=sort)

    @app.route('/community/<name>/join', methods=['POST'])
    def community_join(name):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        comm = db.execute("SELECT * FROM communities WHERE name = ?", (name,)).fetchone()
        if not comm:
            return redirect(url_for('communities_list'))
        existing = db.execute(
            "SELECT * FROM community_members WHERE user_id = ? AND community_id = ?",
            (session['user_id'], comm['id'])
        ).fetchone()
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        if existing:
            db.execute(
                "DELETE FROM community_members WHERE user_id = ? AND community_id = ?",
                (session['user_id'], comm['id'])
            )
            db.execute(
                "UPDATE communities SET member_count = member_count - 1 WHERE id = ?",
                (comm['id'],)
            )
        else:
            db.execute(
                "INSERT INTO community_members (user_id, community_id, role, joined_at) VALUES (?, ?, 'member', ?)",
                (session['user_id'], comm['id'], now)
            )
            db.execute(
                "UPDATE communities SET member_count = member_count + 1 WHERE id = ?",
                (comm['id'],)
            )
        db.commit()
        return redirect(url_for('community_view', name=name))

    @app.route('/community/<name>/modlog')
    def community_modlog(name):
        # VULN: IDOR — any logged-in user can view moderation log (not just moderators)
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        comm = db.execute("SELECT * FROM communities WHERE name = ?", (name,)).fetchone()
        if not comm:
            return render_template('404.html'), 404
        logs = db.execute(
            "SELECT ml.*, u.username as mod_username FROM mod_log ml "
            "JOIN users u ON ml.mod_id = u.id "
            "WHERE ml.community_id = ? ORDER BY ml.created_at DESC",
            (comm['id'],)
        ).fetchall()
        return render_template('modlog.html', comm=comm, logs=logs)
