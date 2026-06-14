from flask import make_response, request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    # VULN: broken access control — checks session['user_id'] only, not is_admin
    @app.route('/admin')
    def admin_index():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db    = get_db()
        users = db.execute(
            "SELECT id, username, display_name, balance, is_admin, is_vip, created_at"
            " FROM users ORDER BY id"
        ).fetchall()
        stats = {
            'total_users':    db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            'total_games':    db.execute("SELECT COUNT(*) FROM game_history").fetchone()[0],
            'total_wagered':  db.execute("SELECT COALESCE(SUM(bet),0) FROM game_history").fetchone()[0],
            'total_messages': db.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0],
        }
        html = render_template('admin.html', users=users, stats=stats)
        banner = (
            '<div style="background:#0b0f1a;color:#f59e0b;font-family:monospace;'
            'font-size:0.75rem;padding:0.5rem 1rem;border-bottom:1px solid #78350f;">'
            '&#x1F3C6; Broken access control confirmed &mdash; '
            '<code>FLAG{ga_bac_admin_panel}</code></div>'
        )
        return make_response(banner + html)

    # VULN: IDOR — no is_admin check on GET
    @app.route('/admin/users/<int:user_id>', methods=['GET', 'POST'])
    def admin_user(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db     = get_db()
        target = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        error  = None
        success = None
        if not target:
            return render_template('admin_users.html', target=None, error='User not found.')
        if request.method == 'POST':
            balance      = float(request.form.get('balance', target['balance']))
            is_admin     = int(request.form.get('is_admin', target['is_admin']))
            is_vip       = int(request.form.get('is_vip', target['is_vip']))
            display_name = request.form.get('display_name', target['display_name'])
            db.execute(
                "UPDATE users SET balance = ?, is_admin = ?, is_vip = ?, display_name = ? WHERE id = ?",
                (balance, is_admin, is_vip, display_name, user_id)
            )
            db.commit()
            target  = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            success = 'User updated.'
        game_hist = db.execute(
            "SELECT * FROM game_history WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,)
        ).fetchall()
        return render_template('admin_users.html', target=target, game_hist=game_hist,
                               error=error, success=success)
