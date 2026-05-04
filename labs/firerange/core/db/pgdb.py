# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""PostgreSQL connection helpers."""
from __future__ import annotations
import os
import psycopg2
import psycopg2.extras


def _pg_conn():
    return psycopg2.connect(
        host=os.environ.get("PG_HOST", "127.0.0.1"),
        port=int(os.environ.get("PG_PORT", "5432")),
        user=os.environ.get("PG_USER", "firerange"),
        password=os.environ.get("PG_PASSWORD", "firerange"),
        dbname=os.environ.get("PG_DATABASE", "firerange"),
    )


def pg(sql: str) -> list[dict]:
    """Run *sql* against PostgreSQL; leak DB errors intentionally."""
    try:
        cx = _pg_conn()
        cur = cx.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        cx.close()
        return rows
    except Exception as exc:
        return [{"db_error": str(exc)}]
