# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import session
from db import get_db


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute(
        "SELECT * FROM users WHERE id = ?", (uid,)
    ).fetchone()
