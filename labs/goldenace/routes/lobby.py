from flask import request, render_template, session, redirect, url_for
from db import get_db
from helpers import current_user


def init(app):

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/lobby')
    def lobby():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user  = current_user()
        feed  = get_db().execute(
            "SELECT f.message, f.created_at FROM live_feed f ORDER BY f.id DESC LIMIT 20"
        ).fetchall()
        board = get_db().execute(
            "SELECT id, username, display_name, balance, is_vip FROM users"
            " WHERE is_admin = 0 ORDER BY balance DESC LIMIT 10"
        ).fetchall()
        return render_template('lobby.html', user=user, feed=feed, board=board)

    # VULN: SQLi — f-string on q param; reflected XSS — q rendered with | safe in template
    @app.route('/leaderboard')
    def leaderboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        q    = request.args.get('q', '')
        db   = get_db()
        if q:
            rows = db.execute(
                f"SELECT id, username, display_name, balance, is_vip FROM users"
                f" WHERE is_admin = 0 AND username LIKE '%{q}%' ORDER BY balance DESC"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT id, username, display_name, balance, is_vip FROM users"
                " WHERE is_admin = 0 ORDER BY balance DESC"
            ).fetchall()
        return render_template('leaderboard.html', rows=rows, q=q)

    # VULN: IDOR — user_id param in URL, no ownership check
    @app.route('/suite/<int:user_id>')
    def suite(user_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        target = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not target:
            return render_template('suite.html', error='User not found.', target=None)
        return render_template('suite.html', target=target, error=None)
