# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import jsonify, session
from db import get_db


def init(app):

    @app.route('/api/movies')
    def api_movies():
        rows = get_db().execute("SELECT * FROM movies WHERE is_showing = 1").fetchall()
        return jsonify([dict(r) for r in rows])

    @app.route('/api/showings/<int:movie_id>')
    def api_showings(movie_id):
        rows = get_db().execute(
            "SELECT * FROM showings WHERE movie_id = ? ORDER BY show_time", (movie_id,)
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # VULN: IDOR — no authentication required; enumerate booking IDs freely
    @app.route('/api/booking/<int:booking_id>')
    def api_booking(booking_id):
        row = get_db().execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    # VULN: IDOR — no authentication; exposes all user fields including password
    @app.route('/api/user/<int:user_id>')
    def api_user(user_id):
        row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row:
            return jsonify({'error': 'not found'}), 404
        return jsonify(dict(row))

    @app.route('/api/seats/<int:showing_id>')
    def api_seats(showing_id):
        from helpers import booked_seats_for
        booked = list(booked_seats_for(showing_id))
        return jsonify({'showing_id': showing_id, 'booked': booked})
