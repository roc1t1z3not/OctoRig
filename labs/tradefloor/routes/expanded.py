# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db
from routes.api import require_jwt

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "TradeFloor API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/dashboard": {"get": {}},
        "/portfolio": {"get": {}},
        "/portfolio/{portfolio_id}": {"get": {}},
        "/trade": {"get": {}, "post": {}},
        "/orders": {"get": {}},
        "/orders/{order_id}": {"get": {}},
        "/orders/{order_id}/cancel": {"post": {}},
        "/profile/{user_id}": {"get": {}},
        "/filings": {
            "get": {"parameters": [{"name": "q", "in": "query"}]}
        },
        "/filings/{filing_id}": {"get": {}},
        "/admin": {"get": {}},
        "/admin/users": {"get": {}},
        "/api/prices": {"get": {}},
        "/api/prices/{symbol}/history": {"get": {}},
        "/api/prices/{symbol}/stream": {"get": {}},
        "/api/token": {"post": {}},
        "/api/portfolio": {"get": {}},
        "/api/users/{user_id}": {"put": {}},
        "/api/market/quote": {
            "get": {"parameters": [{"name": "symbol", "in": "query"}]}
        },
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/accounts/{user_id}": {"get": {}},
        "/api/v1/transactions/{order_id}": {"get": {}},
        "/api/v1/analysis": {
            "get": {"parameters": [{"name": "symbol", "in": "query"}]}
        },
        "/api/v1/users/{user_id}/portfolio": {"get": {}},
        "/api/v1/admin/accounts": {"get": {}},
        "/risk-engine": {"get": {}},
        "/fund-manager": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/accounts/<user_id> — IDOR: JWT sub not matched against user_id ─

    @app.route("/api/v1/accounts/<int:user_id>")
    @require_jwt
    def api_v1_account(user_id):
        row = get_db().execute(
            "SELECT id, username, email, balance, is_admin FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/transactions/<order_id> — IDOR: any JWT holder sees any order ──

    @app.route("/api/v1/transactions/<int:order_id>")
    @require_jwt
    def api_v1_transaction(order_id):
        row = get_db().execute(
            "SELECT o.*, u.username FROM orders o "
            "JOIN users u ON o.user_id = u.id WHERE o.id = ?",
            (order_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/analysis?symbol= — SQLi in filings query ─────────────────────

    @app.route("/api/v1/analysis")
    @require_jwt
    def api_v1_analysis():
        symbol = request.args.get("symbol", "")
        try:
            rows = get_db().execute(
                f"SELECT * FROM filings WHERE symbol = '{symbol}' ORDER BY filed_date DESC"
            ).fetchall()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/users/<user_id>/portfolio — IDOR ─────────────────────────────

    @app.route("/api/v1/users/<int:user_id>/portfolio")
    @require_jwt
    def api_v1_user_portfolio(user_id):
        rows = get_db().execute(
            "SELECT h.*, m.name, m.price FROM portfolio_holdings h "
            "JOIN market_data m ON h.symbol = m.symbol WHERE h.user_id = ?",
            (user_id,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/admin/accounts — broken access (auth but no admin check) ──────

    @app.route("/api/v1/admin/accounts")
    @require_jwt
    def api_v1_admin_accounts():
        rows = get_db().execute(
            "SELECT id, username, email, balance, is_admin FROM users ORDER BY id"
        ).fetchall()
        return jsonify(
            {
                "users": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
            }
        )

    # ── /risk-engine — broken vertical access (session, checks login only) ────

    @app.route("/risk-engine")
    def risk_engine():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        return jsonify(
            {
                "status": "active",
                "mode": "live",
                "admin": True,
                "role": "admin",
                "risk_params": {"margin_call_pct": 0.2, "max_leverage": 10},
            }
        )

    # ── /fund-manager — broken vertical access: dumps all accounts ───────────

    @app.route("/fund-manager")
    def fund_manager():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, email, balance, is_admin FROM users ORDER BY id"
        ).fetchall()
        return jsonify({
            "users": [dict(r) for r in rows],
            "admin": True,
            "flag": "FLAG{tf_fund_manager_found}",
        })

    # ── /api/admin/report — JWT required, role must be admin ─────────────────

    @app.route("/api/admin/report")
    @require_jwt
    def api_admin_report():
        if request.jwt_payload.get("role") != "admin":
            return jsonify({"error": "forbidden"}), 403
        return jsonify({
            "report": "Q1 2000 risk summary",
            "total_aum": 212670.50,
            "open_orders": 7,
            "flag": "FLAG{tf_jwt_alg_none_bypassed}",
        })
