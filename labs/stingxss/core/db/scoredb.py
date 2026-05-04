# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Score / solved tracking DB (SQLite, persisted in /data volume)."""
from __future__ import annotations
import os
import sqlite3
import time

_SCORE_DB = os.environ.get("SCORE_DB", "/data/scores.db")


def _conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(_SCORE_DB), exist_ok=True)
    return sqlite3.connect(_SCORE_DB)


def init_score_db() -> None:
    with _conn() as cx:
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
        cx.execute("""
            CREATE TABLE IF NOT EXISTS catches (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id TEXT NOT NULL,
                player       TEXT NOT NULL DEFAULT '',
                flag         TEXT NOT NULL,
                caught_at    REAL NOT NULL
            )
        """)


def get_scoreboard() -> list[dict]:
    with _conn() as cx:
        rows = cx.execute("""
            SELECT player, SUM(points) AS total, COUNT(*) AS solved
            FROM solved GROUP BY player ORDER BY total DESC, solved DESC
        """).fetchall()
    return [{"player": r[0], "total": r[1], "solved": r[2]} for r in rows]


def get_player_solved(player: str) -> list[str]:
    with _conn() as cx:
        rows = cx.execute(
            "SELECT challenge_id FROM solved WHERE player=? ORDER BY solved_at",
            (player,),
        ).fetchall()
    return [r[0] for r in rows]


def award_points(player: str, challenge_id: str, points: int) -> bool:
    try:
        with _conn() as cx:
            cx.execute(
                "INSERT INTO solved (player,challenge_id,points,solved_at) VALUES (?,?,?,?)",
                (player, challenge_id, points, time.time()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def log_catch(challenge_id: str, player: str, flag: str) -> None:
    with _conn() as cx:
        cx.execute(
            "INSERT INTO catches (challenge_id,player,flag,caught_at) VALUES (?,?,?,?)",
            (challenge_id, player, flag, time.time()),
        )
