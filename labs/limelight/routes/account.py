# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
    def profile(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db     = get_db()
        # VULN: IDOR — only checks auth, never verifies user_id == session['user_id']
        target = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target:
            return redirect(url_for('index'))
        error   = None
        success = None
        if request.method == 'POST':
            display_name = request.form.get('display_name', target['display_name'])
            email        = request.form.get('email', target['email'])
            password     = request.form.get('password', '').strip() or target['password']
            # VULN: mass assignment — is_admin and balance accepted directly from the form
            is_admin     = int(request.form.get('is_admin', target['is_admin']))
            balance      = float(request.form.get('balance', target['balance']))
            db.execute(
                "UPDATE users SET display_name=?, email=?, password=?, is_admin=?, balance=? WHERE id=?",
                (display_name, email, password, is_admin, balance, user_id)
            )
            db.commit()
            target  = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            success = 'Profile updated.'
        return render_template('profile.html', target=target, error=error, success=success)

    @app.route('/gift', methods=['GET', 'POST'])
    def gift():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db      = get_db()
        error   = None
        success = None
        if request.method == 'POST':
            code = request.form.get('code', '').strip()
            # VULN: SQLi — code injected directly into query
            card = db.execute(
                f"SELECT * FROM gift_cards WHERE code = '{code}' AND redeemed_by IS NULL"
            ).fetchone()
            if not card:
                error = 'Invalid or already redeemed gift card code.'
            else:
                db.execute(
                    "UPDATE gift_cards SET redeemed_by = ? WHERE id = ?",
                    (session['user_id'], card['id'])
                )
                db.execute(
                    "UPDATE users SET balance = balance + ? WHERE id = ?",
                    (card['balance'], session['user_id'])
                )
                db.commit()
                success = f'£{card["balance"]:.2f} added to your account!'
        return render_template('gift.html', error=error, success=success)
