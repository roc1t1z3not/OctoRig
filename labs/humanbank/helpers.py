from flask import session
from db import get_db


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def get_unread_count():
    uid = session.get('user_id')
    if not uid:
        return 0
    row = get_db().execute(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id = ? AND read = 0", (uid,)
    ).fetchone()
    return row['cnt'] if row else 0
