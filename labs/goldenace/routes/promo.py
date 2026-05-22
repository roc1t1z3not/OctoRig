from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/promo', methods=['GET', 'POST'])
    def promo():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid   = session['user_id']
        db    = get_db()
        error = None
        success = None

        if request.method == 'POST':
            code = request.form.get('code', '').strip()
            # VULN: SQLi — code param injected directly into query
            row = db.execute(
                f"SELECT * FROM promo_codes WHERE code = '{code}'"
            ).fetchone()

            if not row:
                error = 'Invalid promo code.'
            elif row['uses_count'] >= row['max_uses']:
                error = 'This code has already been fully redeemed.'
            else:
                # VULN: promo reuse — no check in promo_redemptions before redeeming
                now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                db.execute(
                    "UPDATE promo_codes SET uses_count = uses_count + 1 WHERE id = ?",
                    (row['id'],)
                )
                db.execute("UPDATE users SET balance = balance + ? WHERE id = ?",
                           (row['value'], uid))
                db.execute(
                    "INSERT INTO promo_redemptions (user_id, promo_id, redeemed_at) VALUES (?,?,?)",
                    (uid, row['id'], now)
                )
                db.execute(
                    "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
                    " VALUES (?,?,?,?,?,?)",
                    (uid, 'promo', row['value'], f'Promo code: {code}', '', now)
                )
                db.commit()
                success = f'Code redeemed! ${row["value"]:,.2f} added to your balance.'

        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        return render_template('promo.html', user=user, error=error, success=success)
