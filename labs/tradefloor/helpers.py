from flask import session
from db import get_db


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
