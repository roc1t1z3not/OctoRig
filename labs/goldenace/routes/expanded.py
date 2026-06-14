# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "GoldenAce API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/lobby": {"get": {}},
        "/leaderboard": {"get": {}},
        "/suite/{user_id}": {"get": {}},
        "/slots": {"get": {}},
        "/slots/spin": {"post": {}},
        "/blackjack": {"get": {}},
        "/blackjack/deal": {"post": {}},
        "/blackjack/action": {"post": {}},
        "/roulette": {"get": {}},
        "/roulette/spin": {"post": {}},
        "/dice": {"get": {}},
        "/dice/roll": {"post": {}},
        "/account/profile/{user_id}": {"get": {}, "post": {}},
        "/account/transactions/{user_id}": {"get": {}},
        "/account/transfer": {"get": {}, "post": {}},
        "/chat": {"get": {}, "post": {}},
        "/promo": {"get": {}, "post": {}},
        "/admin": {"get": {}},
        "/admin/users/{user_id}": {"get": {}, "post": {}},
        "/api/token": {"post": {}},
        "/api/balance/{user_id}": {"get": {}},
        "/api/history/{user_id}": {"get": {}},
        "/api/users/{user_id}": {"put": {}},
        "/api/feed": {"get": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/players/{id}": {"get": {}},
        "/api/v1/games/{id}": {"get": {}},
        "/api/v1/leaderboard": {
            "get": {"parameters": [{"name": "q", "in": "query"}]}
        },
        "/api/v1/transactions/{id}": {"get": {}},
        "/api/v1/admin/players": {"get": {}},
        "/vault-room": {"get": {}},
        "/high-rollers": {"get": {}},
        "/cashier-office": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/players/<id> — IDOR: auth required, no ownership check ────────

    @app.route("/api/v1/players/<int:player_id>")
    def api_v1_player(player_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT id, username, email, display_name, balance, is_vip, is_admin "
            "FROM users WHERE id = ?",
            (player_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/games/<id> — IDOR: any auth user sees any game history entry ──

    @app.route("/api/v1/games/<int:game_id>")
    def api_v1_game(game_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT g.*, u.username FROM game_history g "
            "JOIN users u ON g.user_id = u.id WHERE g.id = ?",
            (game_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/leaderboard?q= — SQLi in leaderboard search ──────────────────

    @app.route("/api/v1/leaderboard")
    def api_v1_leaderboard():
        q = request.args.get("q", "")
        db = get_db()
        try:
            rows = db.execute(
                f"SELECT id, username, display_name, balance, is_vip "
                f"FROM users WHERE username LIKE '%{q}%' ORDER BY balance DESC"
            ).fetchall()
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/transactions/<id> — IDOR on transactions ─────────────────────

    @app.route("/api/v1/transactions/<int:txn_id>")
    def api_v1_transaction(txn_id):
        if not session.get("user_id"):
            return jsonify({"error": "unauthenticated"}), 401
        row = get_db().execute(
            "SELECT t.*, u.username FROM transactions t "
            "JOIN users u ON t.user_id = u.id WHERE t.id = ?",
            (txn_id,),
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/admin/players — broken access (checks login, not is_admin) ────

    @app.route("/api/v1/admin/players")
    def api_v1_admin_players():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, email, balance, is_admin, is_vip FROM users ORDER BY id"
        ).fetchall()
        return jsonify(
            {
                "players": [dict(r) for r in rows],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
            }
        )

    # ── /vault-room — disallowed hidden endpoint ──────────────────────────────

    @app.route("/vault-room")
    def vault_room():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        u = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        if not u or not u["is_admin"]:
            return jsonify({"error": "forbidden", "role": "user"}), 403
        return jsonify({"status": "online", "admin": True, "role": "admin"})

    # ── /high-rollers — broken access (checks login, not vip/admin) ───────────

    @app.route("/high-rollers")
    def high_rollers():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT id, username, display_name, balance FROM users "
            "WHERE is_vip = 1 OR balance > 10000 ORDER BY balance DESC"
        ).fetchall()
        return jsonify({
            "players": [dict(r) for r in rows],
            "admin": True,
            "flag": "FLAG{ga_high_rollers_bac}",
        })

    # ── /cashier-office — no auth: exposes promo codes ────────────────────────

    @app.route("/cashier-office")
    def cashier_office():
        rows = get_db().execute(
            "SELECT id, code, value, max_uses, uses_count FROM promo_codes"
        ).fetchall()
        return jsonify({
            "promos": [dict(r) for r in rows],
            "admin": True,
            "flag": "FLAG{ga_cashier_no_auth}",
        })
