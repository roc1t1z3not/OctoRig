# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Challenge registry and scoring store."""
from __future__ import annotations
import os
import sqlite3
import time

# ---------------------------------------------------------------------------
# Challenge registry
# ---------------------------------------------------------------------------

CHALLENGES: list[dict] = [
    # ── MySQL ────────────────────────────────────────────────────────────────
    dict(challenge_id="my1a", tier=1, title="First Blood",
         description="A user directory endpoint. Someone forgot to sanitise the ID field.",
         hint="An integer that isn't one makes the database loudly object.",
         technique="Error-based", endpoint="/challenges/my/users?id=1",
         points=100, flag="FIRE{my1a_integer_error_based}"),

    dict(challenge_id="my1b", tier=1, title="Secret Stash",
         description="A secrets endpoint returns one row. Hidden rows exist. Bring them out.",
         hint="Two columns ride the same wire. A second SELECT knows the way.",
         technique="UNION-based", endpoint="/challenges/my/secrets?id=1",
         points=100, flag="FIRE{my1b_union_secrets_extracted}"),

    dict(challenge_id="my1c", tier=1, title="Double Trouble",
         description="Notes are retrieved by author. The server broadcasts its own errors.",
         hint="Single-quote escaping was remembered. The other quote was not.",
         technique="Error-based", endpoint="/challenges/my/notes?author=admin",
         points=100, flag="FIRE{my1c_double_quote_error}"),

    dict(challenge_id="my2a", tier=2, title="Invisible Gate",
         description="A members-only lookup. The door either opens or stays shut — nothing more.",
         hint="A binary oracle still speaks. Enough questions reveal any secret.",
         technique="Boolean-blind", endpoint="/challenges/my/lookup?name=admin",
         points=250, flag="FIRE{my2a_boolean_blind_enumerated}"),

    dict(challenge_id="my2b", tier=2, title="Login Wall",
         description="A staff portal login form. Authentication is enforced by the database.",
         hint="Both fields feed the same query. Break the logic; skip the password.",
         technique="Error/Boolean", endpoint="/challenges/my/login",
         points=250, flag="FIRE{my2b_post_login_bypassed}",
         ui_endpoint="/challenges/my2b/ui"),

    dict(challenge_id="my2c", tier=2, title="OR Gate",
         description="The same membership check — but the account you want doesn't exist yet.",
         hint="A false condition plus a true one still returns a row.",
         technique="Boolean-blind (OR)", endpoint="/challenges/my/lookup?name=nobody",
         points=250, flag="FIRE{my2c_or_based_bypass}"),

    dict(challenge_id="my2d", tier=2, title="Second Sight",
         description="A search endpoint that stores your query. The result surfaces somewhere else.",
         hint="Poison the first request. The second request carries the answer.",
         technique="Two-step", endpoint="/challenges/my/search?user=admin",
         points=250, flag="FIRE{my2d_second_step_extracted}",
         ui_endpoint="/challenges/my2d/ui"),

    dict(challenge_id="my3a", tier=3, title="Sleeping Giant",
         description="A staff directory with uniform responses. The clock is the only channel.",
         hint="If the output never changes, make the server wait instead.",
         technique="Time-blind", endpoint="/challenges/my/search?name=admin",
         points=500, flag="FIRE{my3a_time_blind_confirmed}"),

    dict(challenge_id="my3b", tier=3, title="Hidden Corridor",
         description="An item catalogue with a clean-looking URL. The parameter is part of the path.",
         hint="The injection point lives before the question mark — inside the slashes.",
         technique="Path-param", endpoint="/challenges/my/item/1",
         points=500, flag="FIRE{my3b_path_param_pwned}"),

    dict(challenge_id="my3c", tier=3, title="Triple Threat",
         description="A three-column product catalogue. The flag is a row the query never intends to show.",
         hint="Order by one column, then two, then three — until the server stops complaining.",
         technique="UNION (3 cols)", endpoint="/challenges/my/products?id=1",
         points=500, flag="FIRE{my3c_multicolumn_union}"),

    dict(challenge_id="my3d", tier=3, title="High Five",
         description="A richer catalogue. Five columns, five chances to smuggle a payload out.",
         hint="Most columns carry junk. Find the one that reflects strings back to you.",
         technique="UNION (5 cols)", endpoint="/challenges/my/catalog?id=1",
         points=500, flag="FIRE{my3d_five_col_union}"),

    dict(challenge_id="my3e", tier=3, title="Paren Trap",
         description="An account lookup with a subtly bracketed WHERE clause.",
         hint="Close what was opened before you comment out the rest.",
         technique="Boolean-blind (paren)", endpoint="/challenges/my/account?username=jsmith",
         points=500, flag="FIRE{my3e_paren_context_blind}"),

    dict(challenge_id="my4a", tier=4, title="The Filter",
         description="A lookup endpoint with a comment-stripping guard. The guard has blind spots.",
         hint="Two comment styles are blocked. MySQL knows a third.",
         technique="WAF bypass", endpoint="/challenges/my/filtered?id=1",
         points=1000, flag="FIRE{my4a_waf_bypass_comment}"),

    dict(challenge_id="my4b", tier=4, title="API Whisperer",
         description="A JSON API. The content-type is modern; the query construction is not.",
         hint="What the JSON parser gives, the query builder uses verbatim.",
         technique="JSON body", endpoint="/challenges/my/api/user",
         points=1000, flag="FIRE{my4b_json_body_injection}",
         ui_endpoint="/challenges/my4b/ui"),

    dict(challenge_id="my4c", tier=4, title="Stack Attack",
         description="A numeric lookup endpoint. The database connection has no statement limit.",
         hint="One semicolon separates two worlds. The second is unguarded.",
         technique="Stacked", endpoint="/challenges/my/stacked?id=1",
         points=1000, flag="FIRE{my4c_stacked_confirmed}"),

    dict(challenge_id="my4d", tier=4, title="Tick Tock",
         description="A lookup that reports its own response time. That honesty is exploitable.",
         hint="String context this time. The quote opens the injection window.",
         technique="Time-blind", endpoint="/challenges/my/timer?val=x",
         points=1000, flag="FIRE{my4d_numeric_time_blind}"),

    dict(challenge_id="my4e", tier=4, title="Cookie Monster",
         description="A profile page that identifies you by a token your browser carries silently.",
         hint="The injection surface is neither the URL nor the body.",
         technique="Cookie injection", endpoint="/challenges/my/profile",
         points=1000, flag="FIRE{my4e_cookie_injection}",
         ui_endpoint="/challenges/my4e/ui"),

    dict(challenge_id="my4f", tier=4, title="Ghost Writer",
         description="A request logger that records who visited. The log field is injectable.",
         hint="The injection surface is an HTTP header your browser sends on every request.",
         technique="Header injection", endpoint="/challenges/my/agent",
         points=1000, flag="FIRE{my4f_header_injection}"),

    dict(challenge_id="my5a", tier=5, title="Full Chain",
         description="A high-privilege reporting endpoint. Every technique in your arsenal applies here.",
         hint="Each letter in EBTUS is a door. One of them will open.",
         technique="EBTUS", endpoint="/challenges/my/report?id=1",
         points=2500, flag="FIRE{my5a_legend_full_chain_owned}"),

    dict(challenge_id="my5b", tier=5, title="Crawl & Conquer",
         description="The endpoint that holds the flag isn't listed anywhere obvious. Find it first.",
         hint="The index page links to things the challenge list does not.",
         technique="Crawl + Error", endpoint="/challenges/my/dashboard?key=secret",
         points=2500, flag="FIRE{my5b_crawl_and_conquer}"),

    # ── PostgreSQL ──────────────────────────────────────────────────────────
    dict(challenge_id="pg1a", tier=6, title="PG Error",
         description="A PostgreSQL user lookup. The engine is strict about types and generous with error messages.",
         hint="Postgres casts aggressively. A type mismatch leaks the version string.",
         technique="Error-based (PG)", endpoint="/challenges/pg/users?id=1",
         points=300, flag="FIRE{pg1a_postgres_error_based}"),

    dict(challenge_id="pg1b", tier=6, title="PG Boolean",
         description="A secrets table on PostgreSQL. The endpoint answers only yes or no.",
         hint="SUBSTR and ASCII work on any string, including flags.",
         technique="Boolean-blind (PG)", endpoint="/challenges/pg/secrets?name=flag",
         points=300, flag="FIRE{pg1b_postgres_boolean_blind}"),

    dict(challenge_id="pg2a", tier=7, title="PG Sleep",
         description="A PostgreSQL employee directory. Every response looks identical.",
         hint="pg_sleep() is the only channel available. Use it.",
         technique="Time-blind (PG)", endpoint="/challenges/pg/employees?name=Jane+Doe",
         points=600, flag="FIRE{pg2a_postgres_sleep}"),

    dict(challenge_id="pg2b", tier=7, title="PG Union",
         description="An orders endpoint on PostgreSQL returning multiple columns. Add your own row.",
         hint="NULL placeholders satisfy Postgres type-checking when real values won't.",
         technique="UNION (PG)", endpoint="/challenges/pg/orders?id=1",
         points=600, flag="FIRE{pg2b_postgres_union}"),

    dict(challenge_id="pg2c", tier=7, title="PG Stacked",
         description="A PostgreSQL log search by IP address. The connection allows multiple statements.",
         hint="End the first query; start a second. Postgres will run both.",
         technique="Stacked (PG)", endpoint="/challenges/pg/logs?ip=10.0.0.1",
         points=600, flag="FIRE{pg2c_postgres_stacked}"),

    dict(challenge_id="pg3a", tier=8, title="PG Path Param",
         description="A PostgreSQL order lookup. The order ID is baked into the URL, not a query string.",
         hint="Slashes are just separators. What lies between them is still injectable.",
         technique="Path-param (PG)", endpoint="/challenges/pg/order/1",
         points=1200, flag="FIRE{pg3a_postgres_path_param}"),

    dict(challenge_id="pg3b", tier=8, title="PG POST Form",
         description="A PostgreSQL-backed login form. Two fields. No parameterisation.",
         hint="Either field will unravel the query — pick your preferred thread.",
         technique="Error/Boolean (PG)", endpoint="/challenges/pg/login",
         points=1200, flag="FIRE{pg3b_postgres_post_login}",
         ui_endpoint="/challenges/pg3b/ui"),

    dict(challenge_id="pg3c", tier=8, title="PG Cookie",
         description="A PostgreSQL session endpoint that trusts a cookie it should not.",
         hint="The injection surface is neither the URL nor the body — check the cookie jar.",
         technique="Cookie injection (PG)", endpoint="/challenges/pg/session",
         points=1200, flag="FIRE{pg3c_postgres_cookie}"),

    dict(challenge_id="pg4a", tier=9, title="PG Legend",
         description="A PostgreSQL vault report. No filters, no restrictions — just you and the query planner.",
         hint="The vault row exists. Every technique can reach it.",
         technique="EBTUS (PG)", endpoint="/challenges/pg/report?id=1",
         points=3000, flag="FIRE{pg4a_postgres_legend}"),

    # ── SQLite ───────────────────────────────────────────────────────────────
    dict(challenge_id="sq1a", tier=10, title="Lite Error",
         description="A SQLite user table. The engine is embedded — it is no less verbose about errors.",
         hint="sqlite_version() is a string. CAST it to an integer and watch.",
         technique="Error-based (SQLite)", endpoint="/challenges/sq/users?id=1",
         points=300, flag="FIRE{sq1a_sqlite_error_based}"),

    dict(challenge_id="sq1b", tier=10, title="Lite Boolean",
         description="A SQLite secrets table. The endpoint only says present or absent.",
         hint="SQLite's SUBSTR and GLOB are patient teachers. One character at a time.",
         technique="Boolean-blind (SQLite)", endpoint="/challenges/sq/secrets?name=flag",
         points=300, flag="FIRE{sq1b_sqlite_boolean_blind}"),

    dict(challenge_id="sq2a", tier=11, title="Lite Time",
         description="A file ownership lookup on SQLite. There is no SLEEP — but computation has a cost.",
         hint="randomblob(N) grows expensive as N grows. Time that expense.",
         technique="Time-blind (SQLite)", endpoint="/challenges/sq/files?owner=admin",
         points=600, flag="FIRE{sq2a_sqlite_time_blind}"),

    dict(challenge_id="sq2b", tier=11, title="Lite Union",
         description="A SQLite user lookup. The engine is relaxed about column types in UNION.",
         hint="NULL avoids every type conflict. A tacked-on SELECT returns what you ask.",
         technique="UNION (SQLite)", endpoint="/challenges/sq/users?id=1",
         points=600, flag="FIRE{sq2b_sqlite_union}"),

    dict(challenge_id="sq2c", tier=11, title="Lite Stacked",
         description="The same file lookup — but the underlying connection permits multiple statements.",
         hint="SQLite will execute a second statement if you give it one.",
         technique="Stacked (SQLite)", endpoint="/challenges/sq/files?owner=admin",
         points=600, flag="FIRE{sq2c_sqlite_stacked}"),

    dict(challenge_id="sq2d", tier=11, title="Lite Path",
         description="A SQLite item catalogue where the lookup key is embedded in the URL path.",
         hint="The slash is just a separator. What sits between two slashes is still user input.",
         technique="Path-param (SQLite)", endpoint="/challenges/sq/item/1",
         points=600, flag="FIRE{sq2d_sqlite_path_param}"),

    dict(challenge_id="sq2e", tier=11, title="Lite Login",
         description="A SQLite-backed login form. The credentials feed directly into a query.",
         hint="Two fields, one query. Either one will break the lock.",
         technique="POST login (SQLite)", endpoint="/challenges/sq/login",
         points=600, flag="FIRE{sq2e_sqlite_login}",
         ui_endpoint="/challenges/sq2e/ui"),

    dict(challenge_id="sq3a", tier=12, title="Lite Legend",
         description="A SQLite vault. The full technique set applies — prove your mastery.",
         hint="The vault row is there. Any of the five techniques will surface it.",
         technique="EBTUS (SQLite)", endpoint="/challenges/sq/report?id=1",
         points=3000, flag="FIRE{sq3a_sqlite_legend}"),

    # ── MySQL — new challenges ────────────────────────────────────────────────
    dict(challenge_id="my1d", tier=1, title="What's Your Version",
         description="A user directory endpoint. The server is running something. What exactly?",
         hint="@@version is a string. A UNION with the right column count will surface it.",
         technique="UNION / @@version", endpoint="/challenges/my/users?id=1",
         points=100, flag="FIRE{my1d_version_extracted}"),

    dict(challenge_id="my2e", tier=2, title="Group Think",
         description="An analytics summary that groups by department. The aggregation hides a secret.",
         hint="A HAVING clause can reference columns not in the SELECT list — and inject into them.",
         technique="HAVING / GROUP BY", endpoint="/challenges/my/groups?dept=engineering",
         points=250, flag="FIRE{my2e_having_group_by}"),

    dict(challenge_id="my3f", tier=3, title="Schema Walker",
         description="A product lookup. A shadow table exists that the app never shows you.",
         hint="information_schema.tables lists every table. UNION it into a visible column.",
         technique="information_schema enum", endpoint="/challenges/my/products?id=1",
         points=500, flag="FIRE{my3f_schema_walker}"),

    dict(challenge_id="my4g", tier=4, title="No Space No Problem",
         description="A lookup with a space-stripping WAF. Spaces are overrated anyway.",
         hint="MySQL allows /**/ between every keyword. The WAF only strips literal spaces.",
         technique="WAF bypass (/**/ spaces)", endpoint="/challenges/my/nospace?id=1",
         points=1000, flag="FIRE{my4g_no_space_bypass}"),

    dict(challenge_id="my4h", tier=4, title="Hex Spell",
         description="A lookup endpoint that rejects single-quote characters. Hex strings bypass that.",
         hint="0x48454c4c4f is just HELLO. MySQL accepts hex literals wherever strings are expected.",
         technique="Hex / CHAR() bypass", endpoint="/challenges/my/hexstore?id=1",
         points=1000, flag="FIRE{my4h_hex_char_bypass}"),

    dict(challenge_id="my4i", tier=4, title="Burning Cycles",
         description="A numeric lookup endpoint. SLEEP() is blocked — but BENCHMARK() is not.",
         hint="BENCHMARK(N, expr) burns CPU cycles proportional to N. Time that.",
         technique="BENCHMARK time-blind", endpoint="/challenges/my/benchmark?val=x",
         points=1000, flag="FIRE{my4i_benchmark_time_blind}"),

    dict(challenge_id="my4j", tier=4, title="Case Blind",
         description="A lookup guarded by a keyword blacklist. It only checks lowercase.",
         hint="SeLeCt is not select. MySQL's parser is case-insensitive; the WAF is not.",
         technique="Case-mixing WAF bypass", endpoint="/challenges/my/casefilter?id=1",
         points=1000, flag="FIRE{my4j_case_mixing_bypass}"),

    dict(challenge_id="my5c", tier=5, title="Broken Words",
         description="A vault endpoint where SQL keywords are stripped once. Break them apart.",
         hint="If SELECT is removed, what does SESELECTLECT become after the filter runs?",
         technique="Keyword doubling / CONCAT obfuscation", endpoint="/challenges/my/vault?id=1",
         points=2500, flag="FIRE{my5c_keyword_doubling}"),

    # ── PostgreSQL — new challenges ──────────────────────────────────────────
    dict(challenge_id="pg1c", tier=6, title="Engine Check",
         description="The same PostgreSQL user lookup. What version is the engine?",
         hint="version() returns a string. UNION it into any visible text column.",
         technique="UNION / version()", endpoint="/challenges/pg/users?id=1",
         points=300, flag="FIRE{pg1c_pg_version_extracted}"),

    dict(challenge_id="pg2d", tier=7, title="Aggregate Leak",
         description="A PostgreSQL department summary. The HAVING clause speaks freely.",
         hint="HAVING MIN(id)=1 OR 1=1-- will short-circuit the aggregate check.",
         technique="HAVING / GROUP BY (PG)", endpoint="/challenges/pg/groups?dept=engineering",
         points=600, flag="FIRE{pg2d_pg_having_group_by}"),

    dict(challenge_id="pg2e", tier=7, title="Catalog Diver",
         description="A PostgreSQL orders endpoint. A hidden table exists in the schema.",
         hint="information_schema.tables works on PostgreSQL too. UNION it in.",
         technique="information_schema enum (PG)", endpoint="/challenges/pg/orders?id=1",
         points=600, flag="FIRE{pg2e_pg_schema_walker}"),

    dict(challenge_id="pg2f", tier=7, title="PG Echo Chamber",
         description="A PostgreSQL profile update that stores your display name. The name is used elsewhere.",
         hint="Poison the UPDATE. The poisoned value is re-used verbatim in the next SELECT.",
         technique="Second-order (PG)", endpoint="/challenges/pg/profile",
         points=600, flag="FIRE{pg2f_pg_second_order}",
         ui_endpoint="/challenges/pg2f/ui"),

    dict(challenge_id="pg3d", tier=8, title="Dollar Sign",
         description="A PostgreSQL endpoint that rejects single quotes. Dollar-quoting is the answer.",
         hint="PostgreSQL supports $$string$$ syntax as a string literal. No single quotes needed.",
         technique="Dollar-quoting bypass", endpoint="/challenges/pg/dollarstore?id=1",
         points=1200, flag="FIRE{pg3d_dollar_quote_bypass}"),

    dict(challenge_id="pg3e", tier=8, title="PG Ghost Writer",
         description="A PostgreSQL request logger. The entry is written and immediately read back.",
         hint="The injection surface is an HTTP header. The ?ua= fallback is scanner-accessible.",
         technique="Header injection (PG)", endpoint="/challenges/pg/agent",
         points=1200, flag="FIRE{pg3e_pg_header_injection}"),

    dict(challenge_id="pg4b", tier=9, title="Pipe Dream",
         description="A PostgreSQL vault query built with || string concatenation.",
         hint="|| is PostgreSQL's concat operator — in the payload too. Obfuscate keywords with it.",
         technique="|| concat obfuscation", endpoint="/challenges/pg/vault?id=1",
         points=3000, flag="FIRE{pg4b_pg_pipe_concat}"),

    # ── SQLite — new challenges ──────────────────────────────────────────────
    dict(challenge_id="sq1c", tier=10, title="Lite Version",
         description="A SQLite user lookup. What version of SQLite is the app running?",
         hint="sqlite_version() returns the version string. UNION it alongside the normal columns.",
         technique="UNION / sqlite_version()", endpoint="/challenges/sq/users?id=1",
         points=300, flag="FIRE{sq1c_sqlite_version_extracted}"),

    dict(challenge_id="sq2f", tier=11, title="Char by Char",
         description="A SQLite lookup that blocks single-quote characters. CHAR() is your friend.",
         hint="CHAR(65,66,67) produces 'ABC' without any quote character.",
         technique="CHAR() quote bypass", endpoint="/challenges/sq/charstore?id=1",
         points=600, flag="FIRE{sq2f_char_quote_bypass}"),

    dict(challenge_id="sq2g", tier=11, title="Master Key",
         description="A SQLite item lookup. A hidden table is not listed in any API response.",
         hint="sqlite_master (or sqlite_schema) stores every table's CREATE statement.",
         technique="sqlite_master enumeration", endpoint="/challenges/sq/item/1",
         points=600, flag="FIRE{sq2g_sqlite_master_enum}"),

    dict(challenge_id="sq2h", tier=11, title="Lite Echo",
         description="A SQLite profile page that saves a bio. The bio is returned on a different page.",
         hint="Inject in the write endpoint. The payload surfaces verbatim at /sq/bio.",
         technique="Second-order (SQLite)", endpoint="/challenges/sq/profile",
         points=600, flag="FIRE{sq2h_sq_second_order}",
         ui_endpoint="/challenges/sq2h/ui"),

    dict(challenge_id="sq2i", tier=11, title="Lite Whisperer",
         description="A SQLite member lookup that accepts a JSON body instead of query params.",
         hint="What the JSON parser gives, the query builder uses verbatim.",
         technique="JSON body (SQLite)", endpoint="/challenges/sq/api/member",
         points=600, flag="FIRE{sq2i_sq_json_body}"),
]


def all_challenges() -> list[dict]:
    return CHALLENGES


def challenge_by_id(cid: str) -> dict | None:
    return next((c for c in CHALLENGES if c["challenge_id"] == cid), None)


# ---------------------------------------------------------------------------
# Score store
# ---------------------------------------------------------------------------

_SCORE_DB = os.environ.get("SCORE_DB", "/data/scores.db")


def _score_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_SCORE_DB), exist_ok=True)
    return sqlite3.connect(_SCORE_DB)


def init_score_db() -> None:
    with _score_conn() as cx:
        cx.execute("""
            CREATE TABLE IF NOT EXISTS solved (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                player       TEXT    NOT NULL,
                challenge_id TEXT    NOT NULL,
                points       INTEGER NOT NULL,
                solved_at    REAL    NOT NULL,
                UNIQUE(player, challenge_id)
            )
        """)


def get_scoreboard() -> list[dict]:
    with _score_conn() as cx:
        rows = cx.execute("""
            SELECT player, SUM(points) AS total, COUNT(*) AS solved
            FROM solved
            GROUP BY player
            ORDER BY total DESC, solved DESC
        """).fetchall()
    return [{"player": r[0], "total": r[1], "solved": r[2]} for r in rows]


def award_points(player: str, challenge_id: str, points: int) -> bool:
    try:
        with _score_conn() as cx:
            cx.execute(
                "INSERT INTO solved (player, challenge_id, points, solved_at) VALUES (?,?,?,?)",
                (player, challenge_id, points, time.time()),
            )
        return True
    except sqlite3.IntegrityError:
        return False
