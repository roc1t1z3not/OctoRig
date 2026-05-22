from flask import session
from db import get_db


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def cart_count():
    return len(session.get('cart', []))


def product_rating(product_id):
    row = get_db().execute(
        "SELECT ROUND(AVG(rating),1) as avg, COUNT(*) as cnt "
        "FROM reviews WHERE product_id = ?",
        (product_id,)
    ).fetchone()
    return {'avg': row['avg'] or 0, 'cnt': row['cnt'] or 0}
