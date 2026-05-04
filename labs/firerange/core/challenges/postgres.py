# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""PostgreSQL challenge endpoints."""
from __future__ import annotations
import time

from flask import Blueprint, jsonify, request, current_app

from core.db.pgdb import pg

bp = Blueprint("pg_challenges", __name__)


@bp.get("/challenges/pg/users")
def pg_users():
    """PG1-A: Error-based — integer id param, CAST error triggered."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, username FROM pg_users WHERE id = {id_}"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/secrets")
def pg_secrets():
    """PG1-B: Boolean-blind — 200 if name found, 404 if not."""
    name = request.args.get("name", "flag")
    sql  = f"SELECT id FROM pg_secrets WHERE name = '{name}'"
    rows = pg(sql)
    if rows and "db_error" not in rows[0]:
        return jsonify({"found": True}), 200
    return jsonify({"found": False}), 404


@bp.get("/challenges/pg/employees")
def pg_employees():
    """PG2-A: Time-blind — string context; pg_sleep() works here."""
    name = request.args.get("name", "Jane Doe")
    sql  = f"SELECT id, dept FROM pg_employees WHERE name = '{name}'"
    t0   = time.monotonic()
    rows = pg(sql)
    elapsed = round(time.monotonic() - t0, 3)
    return jsonify({"elapsed": elapsed, "rows": rows})


@bp.get("/challenges/pg/orders")
def pg_orders():
    """PG2-B: UNION-based — SELECT id, product, quantity, status."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, product, quantity, status FROM pg_orders WHERE id = {id_}"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/logs")
def pg_logs():
    """PG2-C: Stacked queries on PostgreSQL — string context (source_ip)."""
    ip = request.args.get("ip", "10.0.0.1")
    sql = f"SELECT id, event FROM pg_logs WHERE source_ip = '{ip}'"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/order/<id>")
def pg_order_path(id: str):
    """PG3-A: Path-parameter injection on PostgreSQL."""
    sql = f"SELECT id, product, quantity, status FROM pg_path_orders WHERE id = {id}"
    return jsonify(pg(sql))


@bp.post("/challenges/pg/login")
def pg_login():
    """PG3-B: POST login backed by PostgreSQL — both fields injectable."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    sql = (
        f"SELECT id, username FROM pg_users "
        f"WHERE username = '{username}' AND email = '{password}'"
    )
    rows = pg(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"authenticated": False, "error": rows[0]["db_error"]}), 200
    if rows:
        return jsonify({"authenticated": True, "user": rows[0]}), 200
    return jsonify({"authenticated": False}), 401


@bp.get("/challenges/pg/session")
def pg_session():
    """PG3-C: Cookie injection on PostgreSQL — auth_token cookie embedded raw."""
    token = request.cookies.get("auth_token", "tok_default")
    sql = f"SELECT username FROM pg_sessions WHERE token = '{token}'"
    rows = pg(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"error": rows[0]["db_error"]}), 200
    if rows:
        return jsonify({"user": rows[0]}), 200
    return jsonify({"user": None}), 200


@bp.get("/challenges/pg/report")
def pg_report():
    """PG4-A: Legend — full-chain PostgreSQL; extract vault flag."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, level FROM pg_vault WHERE id = {id_}"
    return jsonify(pg(sql))


# ── New challenges ────────────────────────────────────────────────────────

@bp.get("/challenges/pg/groups")
def pg_groups():
    """PG2-D: HAVING / GROUP BY column enumeration."""
    dept = request.args.get("dept", "engineering")
    sql = (
        f"SELECT dept, COUNT(*) as cnt FROM pg_group_targets "
        f"WHERE dept = '{dept}' GROUP BY dept HAVING COUNT(*) > 0"
    )
    rows = pg(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"error": rows[0]["db_error"]}), 200
    return jsonify(rows)


@bp.post("/challenges/pg/profile")
def pg_profile_update():
    """PG2-F: Second-order injection — bio stored then read back."""
    username = request.form.get("username", "alice")
    bio      = request.form.get("bio", "")
    # intentionally vulnerable UPDATE
    sql_write = f"UPDATE pg_profiles SET bio = '{bio}' WHERE username = '{username}'"
    write_rows = pg(sql_write)
    # read back — second use of stored bio
    sql_read = f"SELECT bio FROM pg_profiles WHERE username = '{username}'"
    rows = pg(sql_read)
    current_app.config["PG_LAST_BIO"] = bio
    if write_rows and "db_error" in write_rows[0]:
        return jsonify({"saved": False, "error": write_rows[0]["db_error"]}), 200
    return jsonify({"saved": True, "profile": rows})


@bp.get("/challenges/pg/profile")
def pg_profile_read():
    """PG2-F (read leg): surfaces the last stored bio."""
    username = request.args.get("username", "alice")
    sql = f"SELECT bio FROM pg_profiles WHERE username = '{username}'"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/dollarstore")
def pg_dollarstore():
    """PG3-D: Dollar-quoting bypass — single quotes stripped by naive WAF."""
    id_ = request.args.get("id", "1")
    id_ = id_.replace("'", "")   # strip single quotes only
    sql = f"SELECT id, label FROM pg_quote_store WHERE id = {id_}"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/agent")
def pg_agent():
    """PG3-E: Header injection (PG) — User-Agent or ?ua= fallback."""
    user_agent = request.args.get("ua") or request.headers.get("User-Agent", "Mozilla/5.0")
    sql = f"SELECT id, flag FROM pg_agent_log WHERE agent = '{user_agent}'"
    rows = pg(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"logged": False, "error": rows[0]["db_error"]}), 200
    return jsonify({"logged": True})


@bp.get("/challenges/pg/hidden")
def pg_hidden():
    """PG4-C: Crawl-discovered hidden PostgreSQL endpoint."""
    token = request.args.get("token", "secret")
    sql = f"SELECT id, flag FROM pg_crawl_hidden WHERE token = '{token}'"
    return jsonify(pg(sql))


@bp.get("/challenges/pg/vault")
def pg_vault():
    """PG4-B: Pipe-concat obfuscation vault."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, level, flag FROM pg_pipe_vault WHERE id = {id_}"
    return jsonify(pg(sql))
