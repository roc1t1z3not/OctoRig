# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import request, jsonify, session
from db import get_db


def init(app):

    @app.route('/api/posts')
    def api_posts():
        db    = get_db()
        posts = db.execute(
            "SELECT p.id, p.title, p.score, p.created_at, u.username, c.name as community "
            "FROM posts p JOIN users u ON p.user_id = u.id "
            "JOIN communities c ON p.community_id = c.id "
            "WHERE p.status = 'published' ORDER BY p.score DESC LIMIT 20"
        ).fetchall()
        return jsonify([dict(r) for r in posts])

    @app.route('/api/search')
    def api_search():
        q  = request.args.get('q', '')
        db = get_db()
        # VULN: SQLi — f-string on q, returns JSON
        rows = db.execute(
            f"SELECT p.id, p.title, p.score, u.username FROM posts p "
            f"JOIN users u ON p.user_id = u.id "
            f"WHERE p.status = 'published' AND p.title LIKE '%{q}%'"
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/user/<username>')
    def api_user(username):
        db   = get_db()
        user = db.execute(
            "SELECT id, username, karma, role, bio, created_at FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not user:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(user))

    @app.route('/api/internal')
    def api_internal():
        # Only reachable if you find it via robots.txt
        if not session.get('user_id'):
            return jsonify({'error': 'unauthorized'}), 401
        db    = get_db()
        users = db.execute("SELECT id, username, email, role, password_hash FROM users").fetchall()
        return jsonify([dict(u) for u in users])
