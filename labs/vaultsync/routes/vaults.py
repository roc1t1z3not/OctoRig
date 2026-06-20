# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: IDOR — no check that the vault is owned by, or shared with, the
    # current user. The vault_shares table exists and is queried on the
    # dashboard, but this route never consults it — any logged-in user can
    # view any vault and its items by guessing the sequential id.
    @app.route('/vaults/<int:vault_id>')
    def vault_detail(vault_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        vault = db.execute("SELECT * FROM vaults WHERE id = ?", (vault_id,)).fetchone()
        if not vault:
            return render_template('404.html'), 404
        owner = db.execute("SELECT * FROM users WHERE id = ?", (vault['owner_id'],)).fetchone()
        items = db.execute(
            "SELECT * FROM vault_items WHERE vault_id = ? ORDER BY id", (vault_id,)
        ).fetchall()
        return render_template('vault_detail.html', vault=vault, owner=owner, items=items)

    # VULN: IDOR — same issue at the item level, reachable directly without
    # ever loading the parent vault (so the per-vault check above wouldn't
    # have caught it even if it existed).
    @app.route('/vaults/items/<int:item_id>')
    def vault_item_detail(item_id):
        redir = _require_login()
        if redir:
            return redir
        item = get_db().execute("SELECT * FROM vault_items WHERE id = ?", (item_id,)).fetchone()
        if not item:
            return render_template('404.html'), 404
        return render_template('vault_item_detail.html', item=item)

    # VULN: SQLi — search term interpolated straight into a LIKE clause.
    @app.route('/vaults/search')
    def vault_search():
        redir = _require_login()
        if redir:
            return redir
        q = request.args.get('q', '')
        results = []
        error = None
        if q:
            try:
                results = get_db().execute(
                    f"SELECT id, title, site_url, item_user FROM vault_items WHERE title LIKE '%{q}%'"
                ).fetchall()
            except Exception as e:
                error = str(e)
        return render_template('vault_search.html', q=q, results=results, error=error)

    # "Report this item" — feeds the admin review queue. The note is stored
    # and later rendered unescaped in the admin review panel (stored XSS).
    @app.route('/vaults/items/<int:item_id>/flag', methods=['POST'])
    def vault_item_flag(item_id):
        redir = _require_login()
        if redir:
            return redir
        note = request.form.get('note', '')
        get_db().execute(
            "INSERT INTO review_queue (item_id, flagged_by, note, created_at) VALUES (?, ?, ?, ?)",
            (item_id, session['user_id'], note, datetime.utcnow().isoformat(sep=' ', timespec='seconds')),
        )
        get_db().commit()
        return redirect(url_for('vault_item_detail', item_id=item_id))
