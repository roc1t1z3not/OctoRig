from datetime import date
from flask import request, render_template, abort
from db import get_db
from helpers import current_user


def init(app):

    # ── Feedback — stored XSS: message rendered unsanitised in admin view ────

    @app.route('/feedback', methods=['GET', 'POST'])
    def feedback():
        submitted = False
        if request.method == 'POST':
            name    = request.form.get('name', '').strip()
            email   = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            if name and message:
                db = get_db()
                db.execute(
                    "INSERT INTO feedback (name, email, message, submitted_at) VALUES (?, ?, ?, ?)",
                    (name, email, message, str(date.today()))
                )
                db.commit()
                submitted = True
        return render_template('feedback.html', submitted=submitted)

    @app.route('/admin/feedback')
    def admin_feedback():
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        items = get_db().execute(
            "SELECT * FROM feedback ORDER BY submitted_at DESC"
        ).fetchall()
        return render_template('admin_feedback.html', items=items)
