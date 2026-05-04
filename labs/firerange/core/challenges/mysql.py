# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""MySQL challenge endpoints — Tiers 1-5."""
from __future__ import annotations
import re
import time

from flask import Blueprint, jsonify, request, current_app

from core.db.mysqldb import mysql

bp = Blueprint("mysql_challenges", __name__)


# ── Tier 1 — Beginner ────────────────────────────────────────────────────

@bp.get("/challenges/my1/users")
def my1_users():
    """MY1-A: Classic integer injection — raw id= parameter."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, username FROM my1_users WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my1/secrets")
def my1_secrets():
    """MY1-B: UNION-based 2-column; extract my1_secrets."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, name FROM my1_secrets WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my1/notes")
def my1_notes():
    """MY1-C: Double-quote context — author field wrapped in double quotes."""
    author = request.args.get("author", "admin")
    sql = f'SELECT id, content FROM my1_notes WHERE author = "{author}"'
    return jsonify(mysql(sql))


@bp.get("/challenges/my1/typecheck")
def my1_typecheck():
    """MY1-E: Type-cast error-based — string column vs integer comparison."""
    username = request.args.get("username", "admin")
    sql = f"SELECT id, username FROM my1_users WHERE username = {username}"
    return jsonify(mysql(sql))


# ── Tier 2 — Intermediate ────────────────────────────────────────────────

@bp.get("/challenges/my2/lookup")
def my2_lookup():
    """MY2-A / MY2-C: Boolean-blind — 200 if found, 404 if not."""
    name = request.args.get("name", "")
    sql  = f"SELECT id FROM my2_members WHERE username = '{name}'"
    rows = mysql(sql)
    if rows and "db_error" not in rows[0]:
        return jsonify({"found": True}), 200
    return jsonify({"found": False}), 404


@bp.post("/challenges/my2/login")
def my2_login():
    """MY2-B: POST login — both fields injectable; errors leaked."""
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    sql = (
        f"SELECT id, username FROM my2_members "
        f"WHERE username = '{username}' AND password = '{password}'"
    )
    rows = mysql(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"authenticated": False, "error": rows[0]["db_error"]}), 200
    if rows:
        return jsonify({"authenticated": True, "user": rows[0]}), 200
    return jsonify({"authenticated": False}), 401


@bp.get("/challenges/my2/search")
def my2_search():
    """MY2-D / MY3-A: Two-step or time-blind — inject here, read at /my/inbox."""
    user = request.args.get("user") or request.args.get("name", "admin")
    sql  = f"SELECT id FROM my2_members WHERE username = '{user}'"
    t0   = time.monotonic()
    rows = mysql(sql)
    elapsed = round(time.monotonic() - t0, 3)
    current_app.config["LAST_SEARCH"] = user
    if rows and "db_error" not in rows[0]:
        return jsonify({"found": True, "elapsed": elapsed, "hint": "check /challenges/my2/inbox"}), 200
    return jsonify({"found": False, "elapsed": elapsed}), 404


@bp.get("/challenges/my2/inbox")
def my2_inbox():
    """MY2-D (second URL): shows messages for the last searched user."""
    user = current_app.config.get("LAST_SEARCH", "admin")
    sql  = f"SELECT id, message FROM my2_inbox WHERE owner = '{user}'"
    return jsonify(mysql(sql))


# ── Tier 3 — Advanced ────────────────────────────────────────────────────

@bp.get("/challenges/my3/item/<id>")
def my3_item(id: str):
    """MY3-B: Path-parameter injection — numeric segment in URL."""
    sql = f"SELECT id, name, description FROM my3_items WHERE id = {id}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my3/products")
def my3_products():
    """MY3-C: 3-column UNION — SELECT id, name, category."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, name, category FROM my3_products WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my3/catalog")
def my3_catalog():
    """MY3-D: 5-column UNION — SELECT id, title, brand, sku, price."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, title, brand, sku, price FROM my3_catalog WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my3/account")
def my3_account():
    """MY3-E: Paren context — WHERE (username = 'val')."""
    username = request.args.get("username", "jsmith")
    sql = f"SELECT id, dept FROM my3_accounts WHERE (username = '{username}')"
    rows = mysql(sql)
    if rows and "db_error" not in rows[0]:
        return jsonify({"found": True, "data": rows}), 200
    return jsonify({"found": False}), 404


# ── Tier 4 — Expert ──────────────────────────────────────────────────────

def _strip_comments(s: str) -> str:
    """Naive WAF: remove -- and # comment sequences."""
    s = re.sub(r"--[^\n]*", "", s)
    s = re.sub(r"#[^\n]*",  "", s)
    return s


@bp.get("/challenges/my4/filtered")
def my4_filtered():
    """MY4-A: WAF strips -- and # — bypass with /**/ or other comment forms."""
    id_ = _strip_comments(request.args.get("id", "1"))
    sql = f"SELECT id, label FROM my4_entries WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.post("/challenges/my4/api/user")
def my4_api_user():
    """MY4-B: JSON body injection — user_id field embedded raw.
    Falls back to form data so the HTML UI page can also submit here.
    """
    body    = request.get_json(silent=True)
    if body is None:
        # form fallback (used by the browser UI page)
        body = request.form.to_dict()
    user_id = body.get("user_id", 1)
    sql     = f"SELECT user_id, username FROM my4_api_users WHERE user_id = {user_id}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my4/stacked")
def my4_stacked():
    """MY4-C: Stacked injection point (numeric context)."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, label FROM my4_entries WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my4/timer")
def my4_timer():
    """MY4-D: Time-blind in a string context (flag column lookup)."""
    val = request.args.get("val", "FIRE{my4d_numeric_time_blind}")
    sql = f"SELECT id, value FROM my4_numeric_store WHERE flag = '{val}'"
    t0  = time.monotonic()
    rows = mysql(sql)
    elapsed = round(time.monotonic() - t0, 3)
    return jsonify({"elapsed": elapsed, "rows": rows})


@bp.get("/challenges/my4/profile")
def my4_profile():
    """MY4-E: Cookie injection — session_id cookie embedded raw into query."""
    session_id = request.cookies.get("session_id", "sess_def456")
    sql = f"SELECT username FROM my4_sessions WHERE session_id = '{session_id}'"
    rows = mysql(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"error": rows[0]["db_error"]}), 200
    if rows:
        return jsonify({"user": rows[0]}), 200
    return jsonify({"user": None}), 200


@bp.get("/challenges/my4/agent")
def my4_agent():
    """MY4-F: Header injection — User-Agent logged raw into the query.
    The ?ua= param is provided as a scanner-accessible fallback; the intended
    surface is the User-Agent header itself.
    """
    user_agent = request.args.get("ua") or request.headers.get("User-Agent", "Mozilla/5.0")
    sql = f"SELECT id, label FROM my4_agent_log WHERE agent = '{user_agent}'"
    rows = mysql(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"logged": False, "error": rows[0]["db_error"]}), 200
    return jsonify({"logged": True}), 200


# ── Tier 5 — Legend ───────────────────────────────────────────────────────

@bp.get("/challenges/my5/report")
def my5_report():
    """MY5-A: Rich 4-column endpoint; all techniques apply."""
    id_ = request.args.get("id", "1")
    sql = f"SELECT id, title, author, status FROM my5_reports WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my5/dashboard")
def my5_dashboard():
    """MY5-B: Crawl-discovered endpoint — linked from the index page only."""
    key = request.args.get("key", "secret")
    sql = f"SELECT id, flag FROM my5_hidden WHERE `key` = '{key}'"
    return jsonify(mysql(sql))


# ── New challenges ────────────────────────────────────────────────────────

@bp.get("/challenges/my2/groups")
def my2_groups():
    """MY2-E: HAVING / GROUP BY column enumeration."""
    dept = request.args.get("dept", "engineering")
    sql = (
        f"SELECT dept, COUNT(*) as cnt FROM my2_group_targets "
        f"WHERE dept = '{dept}' GROUP BY dept HAVING COUNT(*) > 0"
    )
    rows = mysql(sql)
    if rows and "db_error" in rows[0]:
        return jsonify({"error": rows[0]["db_error"]}), 200
    return jsonify(rows)


@bp.get("/challenges/my4/benchmark")
def my4_benchmark():
    """MY4-I: BENCHMARK() time-blind — string context, SLEEP() blocked."""
    val = request.args.get("val", "x")
    sql = f"SELECT id, value FROM my4_numeric_store WHERE flag = '{val}'"
    t0  = time.monotonic()
    mysql(sql)
    elapsed = round(time.monotonic() - t0, 3)
    return jsonify({"elapsed": elapsed})


@bp.get("/challenges/my4/nospace")
def my4_nospace():
    """MY4-G: WAF strips space chars — bypass with /**/ between keywords."""
    id_ = request.args.get("id", "1")
    id_ = re.sub(r" ", "", id_)          # strip spaces only
    sql = f"SELECT id, label FROM my4_entries WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my4/hexstore")
def my4_hexstore():
    """MY4-H: Single-quote WAF — bypass with 0x… hex literals or CHAR()."""
    id_ = request.args.get("id", "1")
    id_ = id_.replace("'", "").replace('"', "")   # strip quotes
    sql = f"SELECT id, label FROM my4_hex_store WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my4/casefilter")
def my4_casefilter():
    """MY4-J: Keyword blacklist is case-sensitive — bypass with mixed case."""
    id_ = request.args.get("id", "1")
    # naive lowercase-only keyword block
    for kw in ["select", "union", "where", "from", "or", "and"]:
        if kw in id_:
            return jsonify({"error": "blocked"}), 403
    sql = f"SELECT id, label FROM my4_entries WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my4/doublelock")
def my4_doublelock():
    """MY4-K: Compound WAF — strips spaces AND blocks lowercase keywords."""
    id_ = request.args.get("id", "1")
    id_ = re.sub(r" ", "", id_)   # strip spaces
    for kw in ["select", "union", "where", "from", "or", "and"]:
        if kw in id_:
            return jsonify({"error": "blocked"}), 403
    sql = f"SELECT id, label FROM my4_entries WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my5/oob")
def my5_oob():
    """MY5-D: OOB teaser — LOAD_FILE / INTO OUTFILE surface; errors are instructive."""
    id_ = request.args.get("id", "1")
    # Intentionally allows LOAD_FILE() / UNION SELECT LOAD_FILE(...) to surface errors
    sql = f"SELECT id, note FROM my5_oob_notes WHERE id = {id_}"
    return jsonify(mysql(sql))


@bp.get("/challenges/my5/vault")
def my5_vault():
    """MY5-C: Keyword-doubling / CONCAT obfuscation vault."""
    id_ = request.args.get("id", "1")
    # strip one occurrence of each keyword (classic double-encode bypass)
    for kw in ["select", "union", "from", "where"]:
        id_ = re.sub(kw, "", id_, flags=re.IGNORECASE, count=1)
    sql = f"SELECT id, level, flag FROM my5_kwvault WHERE id = {id_}"
    return jsonify(mysql(sql))
