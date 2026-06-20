# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/vaults/<int:vault_id>/share', methods=['GET', 'POST'])
    def vault_share(vault_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        vault = db.execute(
            "SELECT * FROM vaults WHERE id = ? AND owner_id = ?",
            (vault_id, session['user_id']),
        ).fetchone()
        if not vault:
            return render_template('403.html'), 403
        error = None
        if request.method == 'POST':
            target_username = request.form.get('username', '').strip()
            target = db.execute("SELECT id FROM users WHERE username = ?", (target_username,)).fetchone()
            if not target:
                error = 'No such user.'
            else:
                db.execute(
                    "INSERT INTO vault_shares (vault_id, shared_with, permission) VALUES (?, ?, 'read')",
                    (vault_id, target['id']),
                )
                db.commit()
        shares = db.execute(
            "SELECT s.*, u.username FROM vault_shares s JOIN users u ON u.id = s.shared_with WHERE s.vault_id = ?",
            (vault_id,),
        ).fetchall()
        return render_template('vault_share.html', vault=vault, shares=shares, error=error)
