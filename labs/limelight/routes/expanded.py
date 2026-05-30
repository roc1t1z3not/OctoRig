# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Limelight API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/movies": {
            "get": {"parameters": [{"name": "q", "in": "query"}]}
        },
        "/movie/{movie_id}": {"get": {}},
        "/movie/{movie_id}/review": {"post": {}},
        "/book/{showing_id}": {"get": {}, "post": {}},
        "/booking/{booking_id}": {"get": {}},
        "/bookings": {"get": {}},
        "/profile/{user_id}": {"get": {}, "post": {}},
        "/gift": {"get": {}, "post": {}},
        "/admin": {"get": {}},
        "/admin/movie/toggle/{movie_id}": {"post": {}},
        "/admin/announce": {"get": {}, "post": {}},
        "/admin/user/delete/{user_id}": {"post": {}},
        "/api/movies": {"get": {}},
        "/api/showings/{movie_id}": {"get": {}},
        "/api/booking/{booking_id}": {"get": {}},
        "/api/user/{user_id}": {"get": {}},
        "/api/seats/{showing_id}": {"get": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/tickets/{id}": {"get": {}},
        "/api/v1/users/{id}/history": {"get": {}},
        "/api/v1/movies/{id}/reviews": {"get": {}},
        "/api/v1/admin/refunds": {"get": {}},
        "/api/v1/showings/{id}/bookings": {"get": {}},
        "/projection-booth": {"get": {}},
        "/gift-card-admin": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/tickets/<id> — IDOR, unauthenticated (mirrors /api/booking/<id>) ─

    @app.route("/api/v1/tickets/<int:booking_id>")
    def api_v1_ticket(booking_id):
        row = get_db().execute(
            "SELECT b.*, u.username, u.email, m.title AS movie "
            "FROM bookings b "
            "JOIN users u ON b.user_id = u.id "
            "JOIN showings s ON b.showing_id = s.id "
            "JOIN movies m ON s.movie_id = m.id "
            "WHERE b.id = ?",
            (booking_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/users/<id>/history — IDOR: no ownership check ────────────────

    @app.route("/api/v1/users/<int:user_id>/history")
    def api_v1_user_history(user_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        rows = get_db().execute(
            "SELECT b.*, m.title, s.show_time "
            "FROM bookings b "
            "JOIN showings s ON b.showing_id = s.id "
            "JOIN movies m ON s.movie_id = m.id "
            "WHERE b.user_id = ? ORDER BY b.created_at DESC",
            (user_id,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/movies/<id>/reviews — path-param SQLi ────────────────────────

    @app.route("/api/v1/movies/<id>/reviews")
    def api_v1_movie_reviews(id):
        db = get_db()
        try:
            rows = db.execute(
                f"SELECT r.*, u.username FROM reviews r "
                f"JOIN users u ON r.user_id = u.id WHERE r.movie_id = {id}"
            ).fetchall()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/admin/refunds — broken access (checks login, not is_admin) ────

    @app.route("/api/v1/admin/refunds")
    def api_v1_admin_refunds():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT b.*, u.username, u.email, u.balance "
            "FROM bookings b JOIN users u ON b.user_id = u.id ORDER BY b.id DESC"
        ).fetchall()
        return jsonify(
            {
                "refunds": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
            }
        )

    # ── /api/v1/showings/<id>/bookings — IDOR: exposes all seats/bookings ─────

    @app.route("/api/v1/showings/<int:showing_id>/bookings")
    def api_v1_showing_bookings(showing_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        rows = get_db().execute(
            "SELECT b.*, u.username, u.email "
            "FROM bookings b JOIN users u ON b.user_id = u.id "
            "WHERE b.showing_id = ?",
            (showing_id,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # ── /projection-booth — broken access stub ────────────────────────────────

    @app.route("/projection-booth")
    def projection_booth():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        return jsonify({"status": "online", "screen": "A", "admin": True, "role": "admin"})

    # ── /gift-card-admin — no auth: exposes gift card codes ──────────────────

    @app.route("/gift-card-admin")
    def gift_card_admin():
        rows = get_db().execute(
            "SELECT id, code, balance, redeemed_by FROM gift_cards"
        ).fetchall()
        return jsonify({"cards": [dict(r) for r in rows], "admin": True})
