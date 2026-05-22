from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/alerts')
    def alerts():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        rows = get_db().execute(
            "SELECT * FROM alerts WHERE user_id = ? ORDER BY created_at DESC", (uid,)
        ).fetchall()
        return render_template('alerts.html', alerts=rows)

    @app.route('/alerts/new', methods=['GET', 'POST'])
    def alert_new():
        redir = _require_login()
        if redir:
            return redir
        error   = None
        symbols = get_db().execute("SELECT symbol, name FROM market_data ORDER BY symbol").fetchall()
        if request.method == 'POST':
            name      = request.form.get('name', '').strip()
            symbol    = request.form.get('symbol', '').strip()
            condition = request.form.get('condition', 'above')
            threshold = float(request.form.get('threshold', 0) or 0)
            if not (name and symbol):
                error = 'Name and symbol are required.'
            else:
                uid = session['user_id']
                db  = get_db()
                db.execute(
                    "INSERT INTO alerts (user_id, name, symbol, condition, threshold, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (uid, name, symbol, condition, threshold,
                     datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                )
                db.commit()
                return redirect(url_for('alerts'))
        return render_template('alert_new.html', error=error, symbols=symbols)

    # VULN: CSRF — state-changing edit endpoint, no CSRF token
    @app.route('/alerts/<int:alert_id>/edit', methods=['GET', 'POST'])
    def alert_edit(alert_id):
        redir = _require_login()
        if redir:
            return redir
        db    = get_db()
        alert = db.execute("SELECT * FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if not alert:
            return render_template('404.html'), 404
        symbols = db.execute("SELECT symbol, name FROM market_data ORDER BY symbol").fetchall()
        if request.method == 'POST':
            name      = request.form.get('name', '').strip()
            symbol    = request.form.get('symbol', '').strip()
            condition = request.form.get('condition', 'above')
            threshold = float(request.form.get('threshold', 0) or 0)
            active    = 1 if request.form.get('active') else 0
            db.execute(
                "UPDATE alerts SET name=?, symbol=?, condition=?, threshold=?, active=? WHERE id=?",
                (name, symbol, condition, threshold, active, alert_id)
            )
            db.commit()
            return redirect(url_for('alerts'))
        return render_template('alert_edit.html', alert=alert, symbols=symbols)
