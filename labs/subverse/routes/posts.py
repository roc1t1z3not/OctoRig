# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import subprocess
from datetime import datetime
from flask import request, render_template, session, redirect, url_for, jsonify
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/')
    def index():
        db   = get_db()
        sort = request.args.get('sort', 'hot')
        order = 'p.score DESC' if sort != 'new' else 'p.created_at DESC'
        posts = db.execute(
            f"SELECT p.*, u.username, u.karma as author_karma, c.name as community_name "
            f"FROM posts p JOIN users u ON p.user_id = u.id "
            f"JOIN communities c ON p.community_id = c.id "
            f"WHERE p.status = 'published' ORDER BY {order} LIMIT 50"
        ).fetchall()
        communities = db.execute(
            "SELECT * FROM communities ORDER BY member_count DESC LIMIT 5"
        ).fetchall()
        return render_template('index.html', posts=posts, communities=communities, sort=sort)

    @app.route('/search')
    def search():
        q  = request.args.get('q', '')
        db = get_db()
        posts = []
        if q:
            # VULN: SQLi — f-string interpolation on q
            posts = db.execute(
                f"SELECT p.*, u.username, c.name as community_name "
                f"FROM posts p JOIN users u ON p.user_id = u.id "
                f"JOIN communities c ON p.community_id = c.id "
                f"WHERE p.status = 'published' AND (p.title LIKE '%{q}%' OR p.body LIKE '%{q}%') "
                f"ORDER BY p.score DESC"
            ).fetchall()
        return render_template('search.html', posts=posts, q=q)

    @app.route('/post/new', methods=['GET', 'POST'])
    def post_new():
        err = _require_login()
        if err:
            return err
        db    = get_db()
        error = None
        communities = db.execute("SELECT * FROM communities ORDER BY name").fetchall()
        if request.method == 'POST':
            title    = request.form.get('title', '').strip()
            body     = request.form.get('body', '')
            comm_id  = request.form.get('community_id', '')
            flair    = request.form.get('flair', '').strip()
            if not title or not comm_id:
                error = 'Title and community are required.'
            else:
                now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                db.execute(
                    "INSERT INTO posts (title, body, user_id, community_id, score, status, flair, created_at)"
                    " VALUES (?, ?, ?, ?, 0, 'published', ?, ?)",
                    (title, body, session['user_id'], int(comm_id), flair, now)
                )
                db.commit()
                post_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()['id']
                return redirect(url_for('post_view', post_id=post_id))
        return render_template('post_new.html', communities=communities, error=error)

    @app.route('/post/<int:post_id>')
    def post_view(post_id):
        db   = get_db()
        post = db.execute(
            "SELECT p.*, u.username, u.karma as author_karma, c.name as community_name "
            "FROM posts p JOIN users u ON p.user_id = u.id "
            "JOIN communities c ON p.community_id = c.id "
            "WHERE p.id = ? AND p.status = 'published'",
            (post_id,)
        ).fetchone()
        if not post:
            return render_template('404.html'), 404
        comments = db.execute(
            "SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id "
            "WHERE c.post_id = ? ORDER BY c.score DESC, c.created_at ASC",
            (post_id,)
        ).fetchall()
        return render_template('post.html', post=post, comments=comments)

    @app.route('/post/<int:post_id>/draft')
    def post_draft(post_id):
        # VULN: IDOR — checks login but not post ownership or admin role
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        post = db.execute(
            "SELECT p.*, u.username, c.name as community_name "
            "FROM posts p JOIN users u ON p.user_id = u.id "
            "JOIN communities c ON p.community_id = c.id "
            "WHERE p.id = ? AND p.status = 'draft'",
            (post_id,)
        ).fetchone()
        if not post:
            return render_template('404.html'), 404
        return render_template('post_draft.html', post=post)

    @app.route('/post/<int:post_id>/vote')
    def post_vote(post_id):
        # VULN: CSRF — vote accepted via GET with no token, triggerable by <img> tag
        if not session.get('user_id'):
            return redirect(url_for('login'))
        v  = int(request.args.get('v', '1'))
        v  = 1 if v >= 0 else -1
        db = get_db()
        db.execute("UPDATE posts SET score = score + ? WHERE id = ?", (v, post_id))
        db.commit()
        return redirect(request.referrer or url_for('index'))

    @app.route('/post/preview-link', methods=['POST'])
    def post_preview_link():
        # VULN: command injection — url passed to shell=True subprocess
        if not session.get('user_id'):
            return redirect(url_for('login'))
        url    = request.form.get('url', '').strip()
        output = ''
        error  = ''
        if url:
            try:
                output = subprocess.check_output(
                    f"curl -s --max-time 5 '{url}'",
                    shell=True, stderr=subprocess.STDOUT, timeout=8
                ).decode('utf-8', errors='replace')[:2000]
            except subprocess.CalledProcessError as e:
                output = e.output.decode('utf-8', errors='replace')[:2000]
            except Exception as e:
                error = str(e)
        return render_template('link_preview.html', url=url, output=output, error=error)
