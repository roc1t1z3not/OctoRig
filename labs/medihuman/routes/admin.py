from flask import request, render_template, session, redirect, url_for, abort
from db import get_db
from helpers import current_user


def init(app):

    # ── Admin overview — correct is_admin check ───────────────────────────────

    @app.route('/admin')
    def admin_panel():
        u = current_user()
        if not u or not u['is_admin']:
            abort(403)
        db = get_db()
        users    = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        patients = db.execute(
            "SELECT p.*, u.full_name, u.username FROM patients p "
            "JOIN users u ON p.user_id = u.id"
        ).fetchall()
        return render_template('admin_panel.html', users=users, patients=patients)

    # ── Staff detail — VULN: only checks login, not is_admin ─────────────────

    @app.route('/admin/staff/<int:user_id>')
    def admin_staff_detail(user_id):
        if not session.get('user_id'):   # VULN: missing is_admin check
            return redirect(url_for('login'))
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            abort(404)
        patient = db.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,)).fetchone()
        docs    = db.execute("SELECT * FROM documents WHERE patient_id = (SELECT id FROM patients WHERE user_id = ?)", (user_id,)).fetchall()
        return render_template('admin_staff_detail.html', profile=user, patient=patient, docs=docs)
