# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import random
import string
from datetime import datetime
from flask import request, render_template, session, redirect, url_for, flash
from db import get_db
from helpers import booked_seats_for, hall_rows


def init(app):

    @app.route('/book/<int:showing_id>', methods=['GET', 'POST'])
    def book(showing_id):
        if not session.get('user_id'):
            return redirect(url_for('login', next=request.url))
        db      = get_db()
        showing = db.execute("SELECT s.*, m.title FROM showings s JOIN movies m ON s.movie_id = m.id WHERE s.id = ?",
                             (showing_id,)).fetchone()
        if not showing:
            return redirect(url_for('index'))
        booked  = booked_seats_for(showing_id)
        rows    = hall_rows(showing['hall'])
        if request.method == 'POST':
            seats_raw = request.form.get('seats', '')
            seats     = [s.strip() for s in seats_raw.split(',') if s.strip()]
            if not seats:
                error = 'Please select at least one seat.'
                return render_template('seats.html', showing=showing, booked=booked, rows=rows, error=error)
            # VULN: business logic — price taken from client POST, not from DB
            price       = float(request.form.get('price', showing['price']))
            total       = round(price * len(seats), 2)
            now         = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            # VULN: business logic — no uniqueness check; double-booking same seat is allowed
            code        = 'LML-' + ''.join(random.choices(string.digits, k=5))
            db.execute(
                "INSERT INTO bookings (user_id, showing_id, seat_labels, total_price, created_at, confirmation_code)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (session['user_id'], showing_id, ','.join(seats), total, now, code)
            )
            db.commit()
            booking = db.execute("SELECT * FROM bookings WHERE confirmation_code = ?", (code,)).fetchone()
            return redirect(url_for('view_booking', booking_id=booking['id']))
        return render_template('seats.html', showing=showing, booked=booked, rows=rows, error=None)

    @app.route('/booking/<int:booking_id>')
    def view_booking(booking_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        # VULN: IDOR — no check that booking.user_id == session['user_id']
        b = db.execute(
            "SELECT b.*, s.hall, s.show_time, s.price as unit_price, m.title"
            " FROM bookings b"
            " JOIN showings s ON b.showing_id = s.id"
            " JOIN movies m ON s.movie_id = m.id"
            " WHERE b.id = ?",
            (booking_id,)
        ).fetchone()
        if not b:
            return redirect(url_for('my_bookings'))
        return render_template('booking.html', b=b)

    @app.route('/bookings')
    def my_bookings():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        bookings = db.execute(
            "SELECT b.*, m.title, s.show_time, s.hall"
            " FROM bookings b"
            " JOIN showings s ON b.showing_id = s.id"
            " JOIN movies m ON s.movie_id = m.id"
            " WHERE b.user_id = ? ORDER BY b.id DESC",
            (session['user_id'],)
        ).fetchall()
        return render_template('bookings.html', bookings=bookings)
