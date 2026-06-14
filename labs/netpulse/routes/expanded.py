# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "NetPulse API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/dashboard": {"get": {}},
        "/account/{user_id}": {"get": {}},
        "/account/{user_id}/update": {"post": {}},
        "/tools/linkcheck": {"get": {}, "post": {}},
        "/tools/dnslookup": {"get": {}, "post": {}},
        "/billing": {"get": {}},
        "/billing/{invoice_id}": {"get": {}},
        "/billing/usage": {"get": {}},
        "/tickets": {"get": {}},
        "/tickets/new": {"get": {}, "post": {}},
        "/tickets/{ticket_id}": {"get": {}},
        "/tickets/{ticket_id}/reply": {"post": {}},
        "/board": {"get": {}},
        "/board/new": {"get": {}, "post": {}},
        "/board/{thread_id}": {"get": {}},
        "/board/{thread_id}/reply": {"post": {}},
        "/admin": {"get": {}},
        "/admin/users": {"get": {}},
        "/admin/users/{user_id}": {"get": {}},
        "/admin/templates": {"get": {}},
        "/admin/templates/{tpl_id}/edit": {"get": {}, "post": {}},
        "/api/token": {"post": {}},
        "/api/account/{user_id}": {"get": {}},
        "/api/usage": {"get": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/invoices/{id}": {"get": {}},
        "/api/v1/users/{id}": {"get": {}},
        "/api/v1/tickets/{id}": {"get": {}},
        "/api/v1/threads/{id}": {"get": {}},
        "/api/v1/admin/config": {"get": {}},
        "/dialup-pool": {"get": {}},
        "/billing-db": {"get": {}},
        "/syslog": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/invoices/<id> — IDOR: no ownership check ─────────────────────

    @app.route("/api/v1/invoices/<int:invoice_id>")
    def api_v1_invoice(invoice_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT i.*, u.username, u.email "
            "FROM invoices i JOIN users u ON i.user_id = u.id WHERE i.id = ?",
            (invoice_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/users/<id> — IDOR: no ownership check ────────────────────────

    @app.route("/api/v1/users/<int:user_id>")
    def api_v1_user(user_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT id, username, email, full_name, phone, address, "
            "plan, data_used_mb, data_limit_mb, is_admin "
            "FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/tickets/<id> — IDOR ───────────────────────────────────────────

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

    # ── /api/v1/threads/<id> — IDOR on board threads ─────────────────────────

    @app.route("/api/v1/threads/<int:thread_id>")
    def api_v1_thread(thread_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT bt.*, u.username "
            "FROM board_threads bt JOIN users u ON bt.user_id = u.id WHERE bt.id = ?",
            (thread_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/admin/config — broken access (checks login, not is_admin) ──────

    @app.route("/api/v1/admin/config")
    def api_v1_admin_config():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, email, plan, data_used_mb, data_limit_mb, is_admin "
            "FROM users ORDER BY id"
        ).fetchall()
        return jsonify(
            {
                "users": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
                "flag": "FLAG{np_bac_admin_config_exposed}",
                "config": {
                    "db_path": "/data/netpulse.db",
                    "debug": False,
                    "jwt_secret": "netpulse",
                },
            }
        )

    # ── /dialup-pool — disallowed stub (checks login only) ────────────────────

    @app.route("/dialup-pool")
    def dialup_pool():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, plan, data_used_mb, data_limit_mb FROM users"
        ).fetchall()
        return jsonify({"connections": [dict(r) for r in rows], "admin": True})

    # ── /billing-db — no auth: exposes invoice data ───────────────────────────

    @app.route("/billing-db")
    def billing_db():
        rows = get_db().execute(
            "SELECT i.*, u.username, u.email FROM invoices i "
            "JOIN users u ON i.user_id = u.id ORDER BY i.id DESC LIMIT 100"
        ).fetchall()
        return jsonify({"invoices": [dict(r) for r in rows]})

    # ── /syslog — no auth: exposes user/ticket data ───────────────────────────

    @app.route("/syslog")
    def syslog():
        tickets = get_db().execute(
            "SELECT t.id, t.subject, t.status, u.username "
            "FROM support_tickets t JOIN users u ON t.user_id = u.id "
            "ORDER BY t.created_at DESC LIMIT 50"
        ).fetchall()
        return jsonify({"log": [dict(r) for r in tickets]})
