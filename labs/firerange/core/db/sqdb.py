# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""SQLite challenge DB helpers."""
from __future__ import annotations
import os
import sqlite3

_SQ_DB = os.environ.get("SQ_DB", "/data/sqlite_challenges.db")


def _sq_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_SQ_DB), exist_ok=True)
    return sqlite3.connect(_SQ_DB)


def init_sq_db() -> None:
    with _sq_conn() as cx:
        cx.executescript("""
            CREATE TABLE IF NOT EXISTS sq_users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT    NOT NULL,
                email    TEXT    NOT NULL,
                password TEXT    NOT NULL DEFAULT '',
                flag     TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_secrets (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_files (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                owner    TEXT NOT NULL,
                flag     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_members (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                flag     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_vault (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                flag  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_char_store (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                flag  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_hidden_flag (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                note TEXT NOT NULL,
                flag TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sq_profiles (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                bio      TEXT NOT NULL DEFAULT '',
                flag     TEXT NOT NULL DEFAULT 'not_the_flag'
            );
        """)
        if cx.execute("SELECT COUNT(*) FROM sq_users").fetchone()[0] == 0:
            cx.executescript("""
                INSERT INTO sq_users (username, email, password, flag) VALUES
                    ('admin', 'admin@sq.local', 'letmein', 'FIRE{sq1a_sqlite_error_based}'),
                    ('alice', 'alice@sq.local', 'p@ssword', 'FIRE{sq2b_sqlite_union}');

                INSERT INTO sq_secrets (name, value) VALUES
                    ('flag',    'FIRE{sq1b_sqlite_boolean_blind}'),
                    ('api_key', 'sq-key-deadbeef');

                INSERT INTO sq_files (filename, owner, flag) VALUES
                    ('report.pdf', 'admin', 'FIRE{sq2a_sqlite_time_blind}'),
                    ('notes.txt',  'alice', 'not_the_flag');

                INSERT INTO sq_items (name, description) VALUES
                    ('Widget', 'Standard widget'),
                    ('Gadget', 'Premium gadget'),
                    ('Flag',   'FIRE{sq2d_sqlite_path_param}');

                INSERT INTO sq_members (username, password, flag) VALUES
                    ('admin', 'letmein', 'FIRE{sq2e_sqlite_login}'),
                    ('alice', 'p@ssword', 'not_the_flag');

                INSERT INTO sq_vault (level, flag) VALUES
                    ('legend', 'FIRE{sq3a_sqlite_legend}');

                INSERT INTO sq_char_store (label, flag) VALUES
                    ('public', 'not_the_flag'),
                    ('secret', 'FIRE{sq2f_char_quote_bypass}');

                INSERT INTO sq_hidden_flag (note, flag) VALUES
                    ('hidden', 'FIRE{sq2g_sqlite_master_enum}');

                INSERT INTO sq_profiles (username, bio, flag) VALUES
                    ('admin', '', 'FIRE{sq2h_sq_second_order}'),
                    ('alice', '', 'not_the_flag');
            """)


def sq(sql: str) -> list[dict]:
    """Run *sql* against the SQLite challenge DB; leak DB errors intentionally."""
    try:
        cx = _sq_conn()
        cx.row_factory = sqlite3.Row
        cur = cx.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cx.close()
        return rows
    except sqlite3.Error as exc:
        return [{"db_error": str(exc)}]
