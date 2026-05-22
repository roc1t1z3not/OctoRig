from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    # VULN: IDOR — no ownership check; any user can view/edit any profile
    @app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
    def profile(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db     = get_db()
        target = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target:
            return render_template('profile.html', target=None, error='User not found.')
        error   = None
        success = None
        if request.method == 'POST':
            # VULN: stored XSS — display_name saved raw, rendered with | safe everywhere
            display_name = request.form.get('display_name', target['display_name'])
            email        = request.form.get('email', target['email'])
            # VULN: mass assignment — is_admin from POST allows privilege escalation
            is_admin     = int(request.form.get('is_admin', target['is_admin']))
            is_vip       = int(request.form.get('is_vip', target['is_vip']))
            db.execute(
                "UPDATE users SET display_name = ?, email = ?, is_admin = ?, is_vip = ? WHERE id = ?",
                (display_name, email, is_admin, is_vip, user_id)
            )
            db.commit()
            target  = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            success = 'Profile updated.'
        return render_template('profile.html', target=target, error=error, success=success)

    # VULN: IDOR — no ownership check on user_id; SQLi on q param; reflected XSS via q in template
    @app.route('/transactions/<int:user_id>')
    def transactions(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        q  = request.args.get('q', '')
        db = get_db()
        if q:
            rows = db.execute(
                f"SELECT * FROM transactions WHERE user_id = {user_id}"
                f" AND description LIKE '%{q}%' ORDER BY id DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC", (user_id,)
            ).fetchall()
        owner = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return render_template('transactions.html', rows=rows, owner=owner, user_id=user_id, q=q)

    @app.route('/transfer', methods=['GET', 'POST'])
    def transfer():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db      = get_db()
        users   = db.execute(
            "SELECT id, username, display_name FROM users WHERE is_admin = 0"
        ).fetchall()
        error   = None
        success = None
        if request.method == 'POST':
            # VULN: CSRF — no token; IDOR — from_user_id taken from form, not session
            from_uid = int(request.form.get('from_user_id', session['user_id']))
            to_uid   = int(request.form.get('to_user_id', 0))
            amount   = float(request.form.get('amount', 0))
            note     = request.form.get('note', '')
            src  = db.execute("SELECT * FROM users WHERE id = ?", (from_uid,)).fetchone()
            dest = db.execute("SELECT * FROM users WHERE id = ?", (to_uid,)).fetchone()
            if not src or not dest:
                error = 'Invalid user.'
            elif amount <= 0:
                error = 'Amount must be positive.'
            else:
                now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, from_uid))
                db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, to_uid))
                db.execute(
                    "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
                    " VALUES (?,?,?,?,?,?)",
                    (from_uid, 'transfer_out', -amount, f'Transfer to {dest["username"]}: {note}', '', now)
                )
                db.execute(
                    "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
                    " VALUES (?,?,?,?,?,?)",
                    (to_uid, 'transfer_in', amount, f'Transfer from {src["username"]}: {note}', '', now)
                )
                db.commit()
                success = f'Transferred ${amount:,.2f} to {dest["username"]}.'
        me = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        return render_template('transfer.html', user=me, users=users, error=error, success=success)
