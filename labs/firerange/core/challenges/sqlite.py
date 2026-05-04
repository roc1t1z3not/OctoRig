# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""SQLite challenge endpoints."""
from __future__ import annotations
import time

import re

from flask import Blueprint, jsonify, request, current_app

from core.db.sqdb import sq

bp = Blueprint("sq_challenges", __name__)


@bp.get("/challenges/sq/users")
def sq_users():
    """SQ1-A: Error-based SQLite — CAST(sqlite_version() AS INTEGER) pattern."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, username FROM sq_users WHERE id = {id_}"
    return jsonify(sq(sql))


@bp.get("/challenges/sq/secrets")
def sq_secrets():
    """SQ1-B: Boolean-blind — 200 if name found, 404 if not."""
    name = request.args.get("name", "flag")
    sql  = f"SELECT id FROM sq_secrets WHERE name = '{name}'"
    rows = sq(sql)
    if rows and "db_error" not in rows[0]:
        return jsonify({"found": True}), 200
    return jsonify({"found": False}), 404


@bp.get("/challenges/sq/files")
def sq_files():
    """SQ2-A (time-blind) and SQ2-C (stacked) — string owner context."""
    owner = request.args.get("owner", "admin")
    sql   = f"SELECT id, filename FROM sq_files WHERE owner = '{owner}'"
    t0    = time.monotonic()
    rows  = sq(sql)
    elapsed = round(time.monotonic() - t0, 3)
    return jsonify({"elapsed": elapsed, "rows": rows})


@bp.get("/challenges/sq/item/<id>")
def sq_item(id: str):
    """SQ2-D: Path-parameter injection on SQLite."""
    sql = f"SELECT id, name, description FROM sq_items WHERE id = {id}"
    return jsonify(sq(sql))


@bp.post("/challenges/sq/login")
def sq_login():
    """SQ2-E: POST login backed by SQLite — both fields injectable."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    sql = (
        f"SELECT id, username FROM sq_members "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    rows = sq(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"authenticated": False, "error": rows[0]["db_error"]}), 200
    if rows:
        return jsonify({"authenticated": True, "user": rows[0]}), 200
    return jsonify({"authenticated": False}), 401


@bp.get("/challenges/sq/report")
def sq_report():
    """SQ3-A: Legend — full-chain SQLite; extract vault flag."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, level FROM sq_vault WHERE id = {id_}"
    return jsonify(sq(sql))


# ── New challenges ────────────────────────────────────────────────────────

@bp.get("/challenges/sq/charstore")
def sq_charstore():
    """SQ2-F: CHAR() quote bypass — single quotes stripped by naive WAF."""
    id_ = request.args.get("id", "1")
    id_ = id_.replace("'", "")   # strip single quotes
    sql = f"SELECT id, label FROM sq_char_store WHERE id = {id_}"
    return jsonify(sq(sql))


@bp.post("/challenges/sq/profile")
def sq_profile_update():
    """SQ2-H: Second-order injection — bio stored then read back."""
    username = request.form.get("username", "alice")
    bio      = request.form.get("bio", "")
    sql_write = f"UPDATE sq_profiles SET bio = '{bio}' WHERE username = '{username}'"
    write_rows = sq(sql_write)
    sql_read  = f"SELECT bio FROM sq_profiles WHERE username = '{username}'"
    rows = sq(sql_read)
    current_app.config["SQ_LAST_BIO"] = bio
    if write_rows and "db_error" in write_rows[0]:
        return jsonify({"saved": False, "error": write_rows[0]["db_error"]}), 200
    return jsonify({"saved": True, "profile": rows})


@bp.get("/challenges/sq/profile")
def sq_profile_read():
    """SQ2-H (read leg): surfaces the last stored bio."""
    username = request.args.get("username", "alice")
    sql = f"SELECT bio FROM sq_profiles WHERE username = '{username}'"
    return jsonify(sq(sql))


@bp.get("/challenges/sq/nospace")
def sq_nospace():
    """SQ2-J: WAF strips spaces — bypass with /**/ between keywords."""
    id_ = request.args.get("id", "1")
    id_ = re.sub(r" ", "", id_)   # strip spaces only
    sql = f"SELECT id, label FROM sq_char_store WHERE id = {id_}"
    return jsonify(sq(sql))


@bp.get("/challenges/sq/quotefilter")
def sq_quotefilter():
    """SQ2-K: Single-quote filter — bypass with CHAR() function."""
    id_ = request.args.get("id", "1")
    id_ = id_.replace("'", "")   # strip single quotes
    sql = f"SELECT id, label FROM sq_char_store WHERE id = {id_}"
    return jsonify(sq(sql))


@bp.get("/challenges/sq/hidden")
def sq_hidden():
    """SQ3-B: Crawl-discovered hidden SQLite endpoint."""
    token = request.args.get("token", "secret")
    sql = f"SELECT id, flag FROM sq_crawl_hidden WHERE token = '{token}'"
    return jsonify(sq(sql))


@bp.post("/challenges/sq/api/member")
def sq_api_member():
    """SQ2-I: JSON body injection — member_id embedded raw.
    Falls back to form data so an HTML form can also reach this endpoint.
    """
    body      = request.get_json(silent=True)
    if body is None:
        body = request.form.to_dict()
    member_id = body.get("member_id", 1)
    sql = f"SELECT id, username FROM sq_members WHERE id = {member_id}"
    return jsonify(sq(sql))
