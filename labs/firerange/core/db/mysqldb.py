# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""MySQL connection helpers."""
from __future__ import annotations
import os
import mysql.connector

_connector = mysql.connector


def _mysql_conn():
    return _connector.connect(
        host=os.environ.get("MYSQL_HOST", "172.28.8.2"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "firerange"),
        password=os.environ.get("MYSQL_PASSWORD", "firerange"),
        database=os.environ.get("MYSQL_DATABASE", "firerange"),
    )


def mysql(sql: str) -> list[dict]:
    """Run *sql* against MySQL; leak DB errors intentionally."""
    try:
        cx = _mysql_conn()
        cur = cx.cursor(dictionary=True)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        cx.close()
        return rows
    except _connector.Error as exc:
        return [{"db_error": str(exc)}]

