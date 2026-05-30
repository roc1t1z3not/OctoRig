# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Rewind Range API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/browse": {
            "get": {
                "parameters": [
                    {"name": "genre", "in": "query"},
                    {"name": "platform", "in": "query"},
                    {"name": "year", "in": "query"},
                ]
            }
        },
        "/search": {"get": {"parameters": [{"name": "q", "in": "query"}]}},
        "/product/{product_id}": {"get": {}},
        "/product/{product_id}/review": {"post": {}},
        "/cart": {"get": {}},
        "/cart/add": {"post": {}},
        "/cart/coupon": {"post": {}},
        "/checkout": {"get": {}},
        "/account/{user_id}": {"get": {}, "post": {}},
        "/users": {"get": {}},
        "/inbox": {"get": {}},
        "/inbox/{msg_id}": {"get": {}},
        "/feedback": {"get": {}, "post": {}},
        "/admin/orders": {"get": {}},
        "/admin/feedback": {"get": {}},
        "/api/product": {
            "get": {"parameters": [{"name": "id", "in": "query"}]}
        },
        "/api/user/{user_id}/balance": {"get": {}},
        "/api/orders/{order_id}": {"get": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/rentals/{id}": {"get": {}},
        "/api/v1/customers/{id}": {"get": {}},
        "/api/v1/catalog": {
            "get": {
                "parameters": [
                    {"name": "genre", "in": "query"},
                    {"name": "year", "in": "query"},
                ]
            }
        },
        "/api/v1/products/{id}": {"get": {}},
        "/api/v1/reviews/{id}": {"get": {}},
        "/api/v1/admin/orders": {"get": {}},
        "/staff-portal": {"get": {}},
        "/inventory-manager": {"get": {}},
        "/late-returns": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/rentals/<id> — IDOR: no ownership check ──────────────────────

    @app.route("/api/v1/rentals/<int:rental_id>")
    def api_v1_rental(rental_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT o.*, u.username, u.email "
            "FROM orders o JOIN users u ON o.user_id = u.id WHERE o.id = ?",
            (rental_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/customers/<id> — IDOR: full user record ──────────────────────

    @app.route("/api/v1/customers/<int:customer_id>")
    def api_v1_customer(customer_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT id, username, email, address, phone FROM users WHERE id = ?",
            (customer_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/catalog?genre=&year= — SQLi via both query params ────────────

    @app.route("/api/v1/catalog")
    def api_v1_catalog():
        genre = request.args.get("genre", "")
        year = request.args.get("year", "")
        db = get_db()
        where = "1=1"
        if genre:
            where += f" AND genre LIKE '%{genre}%'"
        if year:
            where += f" AND year = {year}"
        try:
            rows = db.execute(
                f"SELECT id, title, genre, platform, year, price FROM products WHERE {where}"
            ).fetchall()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/products/<id> — path-param SQLi ──────────────────────────────

    @app.route("/api/v1/products/<id>")
    def api_v1_product_expanded(id):
        db = get_db()
        try:
            row = db.execute(
                f"SELECT * FROM products WHERE id = {id}"
            ).fetchone()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/reviews/<id> — IDOR on reviews ───────────────────────────────

    @app.route("/api/v1/reviews/<int:review_id>")
    def api_v1_review(review_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT r.*, u.username FROM reviews r "
            "JOIN users u ON r.user_id = u.id WHERE r.id = ?",
            (review_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/admin/orders — broken access (checks login, not is_admin) ─────

    @app.route("/api/v1/admin/orders")
    def api_v1_admin_orders():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT o.*, u.username, u.email "
            "FROM orders o JOIN users u ON o.user_id = u.id ORDER BY o.id DESC"
        ).fetchall()
        return jsonify(
            {
                "orders": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
            }
        )

    # ── /staff-portal — broken vertical access ────────────────────────────────

    @app.route("/staff-portal")
    def staff_portal():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        u = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        if not u or not u["is_admin"]:
            return jsonify({"error": "forbidden", "role": "user"}), 403
        return jsonify({"status": "ok", "role": "admin", "admin": True})

    # ── /inventory-manager — broken vertical access ───────────────────────────

    @app.route("/inventory-manager")
    def inventory_manager():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT * FROM products ORDER BY id"
        ).fetchall()
        return jsonify({"items": [dict(r) for r in rows], "admin": True})

    # ── /late-returns — no auth, leaks order data ─────────────────────────────

    @app.route("/late-returns")
    def late_returns():
        rows = get_db().execute(
            "SELECT o.*, u.username FROM orders o "
            "JOIN users u ON o.user_id = u.id WHERE o.status = 'pending'"
        ).fetchall()
        return jsonify([dict(r) for r in rows])
