# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""In-app storage for Stored / Blind XSS challenge content."""
from __future__ import annotations
import os
import sqlite3

_STORE_DB = os.environ.get("STORE_DB", "/data/store.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_STORE_DB), exist_ok=True)
    return sqlite3.connect(_STORE_DB)


def init_store_db() -> None:
    with _conn() as cx:
        cx.executescript("""
            CREATE TABLE IF NOT EXISTS guestbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS forum_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product TEXT NOT NULL DEFAULT 'Widget Pro',
                author TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                bio TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feed_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                open INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ua_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_agent TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS cookie_debug (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cookie_val TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS gql_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ws_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            );
        """)
        # seed a default profile
        try:
            cx.execute("INSERT INTO profiles (username, bio) VALUES ('admin','Site administrator')")
        except sqlite3.IntegrityError:
            pass
        # seed an initial feed item
        if cx.execute("SELECT COUNT(*) FROM feed_items").fetchone()[0] == 0:
            cx.execute("INSERT INTO feed_items (title,content) VALUES ('Welcome','This is the StingXSS news feed.')")


def store_get(table: str, cols: str = "*") -> list[dict]:
    cx = _conn()
    cx.row_factory = sqlite3.Row
    rows = [dict(r) for r in cx.execute(f"SELECT {cols} FROM {table}").fetchall()]
    cx.close()
    return rows


def store_insert(table: str, **kwargs) -> int:
    cols = ", ".join(kwargs.keys())
    placeholders = ", ".join("?" * len(kwargs))
    with _conn() as cx:
        cur = cx.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", list(kwargs.values()))
        return cur.lastrowid


def store_get_where(table: str, where: str, params: tuple, cols: str = "*") -> list[dict]:
    cx = _conn()
    cx.row_factory = sqlite3.Row
    rows = [dict(r) for r in cx.execute(f"SELECT {cols} FROM {table} WHERE {where}", params).fetchall()]
    cx.close()
    return rows


def store_update(table: str, set_clause: str, where: str, params: tuple) -> None:
    with _conn() as cx:
        cx.execute(f"UPDATE {table} SET {set_clause} WHERE {where}", params)


def store_delete(table: str, where: str, params: tuple) -> None:
    with _conn() as cx:
        cx.execute(f"DELETE FROM {table} WHERE {where}", params)
