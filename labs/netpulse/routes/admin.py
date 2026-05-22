import jinja2
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def _require_admin():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user = get_db().execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if not user or not user['is_admin']:
        return render_template('403.html'), 403
    return None


def init(app):

    @app.route('/admin')
    def admin_index():
        err = _require_admin()
        if err:
            return err
        users    = get_db().execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
        tickets  = get_db().execute("SELECT COUNT(*) AS c FROM support_tickets WHERE status='open'").fetchone()['c']
        return render_template('admin.html', user_count=users, open_tickets=tickets)

    @app.route('/admin/users')
    def admin_users():
        err = _require_admin()
        if err:
            return err
        rows = get_db().execute("SELECT * FROM users ORDER BY id").fetchall()
        return render_template('admin_users.html', users=rows)

    @app.route('/admin/users/<int:user_id>')
    def admin_user(user_id):
        err = _require_admin()
        if err:
            return err
        user     = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        tickets  = get_db().execute(
            "SELECT * FROM support_tickets WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        invoices = get_db().execute(
            "SELECT * FROM invoices WHERE user_id = ? ORDER BY issued_date DESC", (user_id,)
        ).fetchall()
        return render_template('admin_user.html', profile=user, tickets=tickets, invoices=invoices)

    @app.route('/admin/templates')
    def admin_templates():
        err = _require_admin()
        if err:
            return err
        tmpls = get_db().execute("SELECT * FROM notification_templates ORDER BY id").fetchall()
        return render_template('admin_templates.html', templates=tmpls)

    # VULN: SSTI — template body previewed via jinja2.Environment().from_string() (unsandboxed)
    # VULN: broken access control — only checks session['user_id'], NOT is_admin
    #   → any logged-in user who knows the template ID can POST here and trigger SSTI
    @app.route('/admin/templates/<int:tpl_id>/edit', methods=['GET', 'POST'])
    def admin_template_edit(tpl_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        tmpl = db.execute("SELECT * FROM notification_templates WHERE id = ?", (tpl_id,)).fetchone()
        if not tmpl:
            return render_template('404.html'), 404
        preview = None
        error   = None
        if request.method == 'POST':
            name        = request.form.get('name', '').strip()
            subject     = request.form.get('subject', '').strip()
            body        = request.form.get('body', '').strip()
            description = request.form.get('description', '').strip()
            action      = request.form.get('action', 'save')
            if action == 'preview':
                try:
                    sample_user = {'full_name': 'Dave Norton', 'username': 'dave.norton', 'plan': 'Dial-Up 56K'}
                    sample_invoice = {'description': 'Dial-Up 56K — May 1998', 'amount': '19.99', 'due_date': '1998-06-01'}
                    preview = jinja2.Environment().from_string(body).render(
                        user=sample_user, invoice=sample_invoice
                    )
                except Exception as e:
                    error = str(e)
            else:
                db.execute(
                    "UPDATE notification_templates SET name=?, subject=?, body=?, description=? WHERE id=?",
                    (name, subject, body, description, tpl_id)
                )
                db.commit()
                return redirect(url_for('admin_templates'))
            tmpl = {'id': tpl_id, 'name': name, 'subject': subject, 'body': body, 'description': description}
        return render_template('admin_template_edit.html', tmpl=tmpl, preview=preview, error=error)
