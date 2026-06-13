# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import make_response, request, render_template, session, redirect, url_for
from db import get_db
from helpers import current_user


def init(app):

    @app.route('/')
    def index():
        db = get_db()
        movies = db.execute(
            "SELECT * FROM movies WHERE is_showing = 1"
        ).fetchall()
        return render_template('index.html', movies=movies)

    @app.route('/movies')
    def movies():
        db = get_db()
        q     = request.args.get('q', '')
        genre = request.args.get('genre', '')
        if q:
            # VULN: SQLi — LIKE injection; VULN: reflected XSS — query echoed with | safe in template
            results = db.execute(
                f"SELECT * FROM movies WHERE (title LIKE '%{q}%' OR genre LIKE '%{q}%') AND is_showing = 1"
            ).fetchall()
        elif genre:
            results = db.execute(
                f"SELECT * FROM movies WHERE genre LIKE '%{genre}%' AND is_showing = 1"
            ).fetchall()
        else:
            results = db.execute("SELECT * FROM movies WHERE is_showing = 1").fetchall()
        genres = db.execute("SELECT DISTINCT genre FROM movies WHERE is_showing = 1").fetchall()
        return render_template('movies.html', movies=results, query=q, genre=genre, genres=genres)

    @app.route('/movie/<int:movie_id>')
    def movie(movie_id):
        db = get_db()
        m  = db.execute("SELECT * FROM movies WHERE id = ?", (movie_id,)).fetchone()
        if not m:
            return redirect(url_for('index'))
        showings = db.execute(
            "SELECT * FROM showings WHERE movie_id = ? ORDER BY show_time", (movie_id,)
        ).fetchall()
        # VULN: stored XSS — review text and reviewer display_name rendered with | safe in template
        reviews = db.execute(
            "SELECT r.*, u.username, u.display_name FROM reviews r"
            " JOIN users u ON r.user_id = u.id"
            " WHERE r.movie_id = ? ORDER BY r.id DESC",
            (movie_id,)
        ).fetchall()
        error   = request.args.get('error')
        success = request.args.get('success')
        resp = make_response(render_template('movie.html', m=m, showings=showings, reviews=reviews,
                                            error=error, success=success))
        resp.set_cookie('xss_challenge', 'FLAG{ll_xss_cookie_captured}', httponly=False)
        return resp

    @app.route('/movie/<int:movie_id>/review', methods=['POST'])
    def review(movie_id):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.url))
        rating = request.form.get('rating', '3')
        text   = request.form.get('text', '').strip()
        if not text:
            return redirect(url_for('movie', movie_id=movie_id, error='Review cannot be empty.'))
        db  = get_db()
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        # VULN: stored XSS — text stored raw, no sanitisation
        db.execute(
            "INSERT INTO reviews (movie_id, user_id, rating, text, created_at) VALUES (?, ?, ?, ?, ?)",
            (movie_id, session['user_id'], int(rating), text, now)
        )
        db.commit()
        return redirect(url_for('movie', movie_id=movie_id, success='Review posted.'))
