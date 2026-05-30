# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "HumanBank API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/dashboard": {"get": {}},
        "/accounts": {"get": {}},
        "/accounts/{account_id}": {"get": {}},
        "/accounts/{account_id}/transactions": {"get": {}},
        "/transfer": {"get": {}, "post": {}},
        "/search": {
            "get": {"parameters": [{"name": "q", "in": "query"}]}
        },
        "/profile": {"get": {}},
        "/profile/update": {"post": {}},
        "/tickets": {"get": {}},
        "/tickets/new": {"get": {}, "post": {}},
        "/tickets/{ticket_id}": {"get": {}},
        "/tickets/{ticket_id}/reply": {"post": {}},
        "/admin/tickets": {"get": {}},
        "/admin/users": {"get": {}},
        "/admin/users/{user_id}": {"get": {}},
        "/docs": {"get": {}},
        "/docs/upload": {"post": {}},
        "/docs/download/{stored_name}": {"get": {}},
        "/api/token": {"post": {}},
        "/api/accounts": {"get": {}},
        "/api/accounts/{account_id}": {"get": {}},
        "/api/transactions/{account_id}": {"get": {}},
        "/api/transfer": {"post": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/accounts/{id}": {"get": {}},
        "/api/v1/users/{id}": {"get": {}},
        "/api/v1/tickets/{id}": {"get": {}},
        "/api/v1/transfers/{id}": {"get": {}},
        "/api/v1/admin/users": {"get": {}},
        "/vault": {"get": {}},
        "/wire-transfers": {"get": {}},
        "/audit-log": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/accounts/<id> — IDOR: no ownership check ─────────────────────

    @app.route("/api/v1/accounts/<int:account_id>")
    def api_v1_account(account_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT a.*, u.username, u.email "
            "FROM accounts a JOIN users u ON a.user_id = u.id WHERE a.id = ?",
            (account_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/users/<id> — IDOR: full user profile including sensitive fields ─

    @app.route("/api/v1/users/<int:user_id>")
    def api_v1_user(user_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT id, username, email, full_name, phone, address, bio, is_admin "
            "FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/tickets/<id> — IDOR: no ownership check ──────────────────────

    @app.route("/api/v1/tickets/<int:ticket_id>")
    def api_v1_ticket(ticket_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT t.*, u.username FROM support_tickets t "
            "JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (ticket_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/transfers/<id> — IDOR on transaction records ─────────────────

    @app.route("/api/v1/transfers/<int:txn_id>")
    def api_v1_transfer(txn_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT t.*, a.account_number FROM transactions t "
            "JOIN accounts a ON t.account_id = a.id WHERE t.id = ?",
            (txn_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/admin/users — broken access (checks login, not is_admin) ──────

    @app.route("/api/v1/admin/users")
    def api_v1_admin_users():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, email, full_name, phone, address, is_admin FROM users ORDER BY id"
        ).fetchall()
        return jsonify(
            {
                "users": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
            }
        )

    # ── /vault — broken access stub (disallowed in robots.txt) ────────────────

    @app.route("/vault")
    def vault():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        u = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        if not u or not u["is_admin"]:
            return jsonify({"error": "forbidden", "role": "user"}), 403
        return jsonify({"status": "online", "admin": True, "role": "admin"})

    # ── /wire-transfers — broken access: checks login only ────────────────────

    @app.route("/wire-transfers")
    def wire_transfers():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT t.*, a.account_number, a.user_id "
            "FROM transactions t JOIN accounts a ON t.account_id = a.id "
            "WHERE t.type = 'transfer' ORDER BY t.txn_date DESC"
        ).fetchall()
        return jsonify(
            {"transfers": [dict(r) for r in rows], "admin": True, "role": "admin"}
        )

    # ── /audit-log — no auth: leaks all transactions ──────────────────────────

    @app.route("/audit-log")
    def audit_log():
        rows = get_db().execute(
            "SELECT t.id, t.type, t.amount, t.memo, t.txn_date, a.account_number "
            "FROM transactions t JOIN accounts a ON t.account_id = a.id "
            "ORDER BY t.txn_date DESC LIMIT 200"
        ).fetchall()
        return jsonify({"log": [dict(r) for r in rows]})
