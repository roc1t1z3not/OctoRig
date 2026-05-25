# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import jinja2
from flask import request, render_template, session, redirect, url_for, render_template_string
from db import get_db


def _require_admin():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user or user['role'] != 'admin':
        return render_template('403.html'), 403
    return None


def init(app):

    @app.route('/admin')
    def admin_index():
        err = _require_admin()
        if err:
            return err
        db         = get_db()
        user_count = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
        post_count = db.execute("SELECT COUNT(*) AS c FROM posts").fetchone()['c']
        users      = db.execute("SELECT * FROM users ORDER BY id").fetchall()
        return render_template('admin.html', user_count=user_count, post_count=post_count, users=users)

    @app.route('/admin/users')
    def admin_users():
        err = _require_admin()
        if err:
            return err
        users = get_db().execute("SELECT * FROM users ORDER BY id").fetchall()
        return render_template('admin_users.html', users=users)

    @app.route('/admin/community/<name>/announce', methods=['GET', 'POST'])
    def admin_announce(name):
        # VULN: broken access — GET checks admin, POST only checks login
        # VULN: SSTI — announcement rendered via render_template_string (Flask Jinja2 env, unsandboxed)
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        comm = db.execute("SELECT * FROM communities WHERE name = ?", (name,)).fetchone()
        if not comm:
            return render_template('404.html'), 404
        # GET requires admin
        if request.method == 'GET':
            user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
            if not user or user['role'] != 'admin':
                return render_template('403.html'), 403
        preview = None
        error   = None
        if request.method == 'POST':
            announcement = request.form.get('announcement', '')
            action       = request.form.get('action', 'save')
            if action == 'preview':
                try:
                    preview = render_template_string(announcement)
                except Exception as e:
                    error = str(e)
            else:
                db.execute(
                    "UPDATE communities SET announcement = ? WHERE id = ?",
                    (announcement, comm['id'])
                )
                db.commit()
                return redirect(url_for('community_view', name=name))
        return render_template('admin_announce.html', comm=comm, preview=preview, error=error)
