# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session
from db import get_db


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def booked_seats_for(showing_id):
    rows = get_db().execute(
        "SELECT seat_labels FROM bookings WHERE showing_id = ?", (showing_id,)
    ).fetchall()
    booked = set()
    for r in rows:
        for label in r['seat_labels'].split(','):
            booked.add(label.strip())
    return booked


def hall_rows(hall):
    mapping = {'Hall 1': 'ABCDEFGHIJKLMNOPQR', 'Hall 2': 'ABCDEFGHIJKL', 'Hall 3': 'ABCDEFGH'}
    return mapping.get(hall, 'ABCDE')
