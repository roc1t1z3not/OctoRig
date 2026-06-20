# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import session, redirect, url_for, render_template
from db import get_db


def init(app):

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        vaults = db.execute(
            "SELECT * FROM vaults WHERE owner_id = ? ORDER BY id", (session['user_id'],)
        ).fetchall()
        shared = db.execute(
            "SELECT v.* FROM vaults v JOIN vault_shares s ON s.vault_id = v.id WHERE s.shared_with = ?",
            (session['user_id'],),
        ).fetchall()
        return render_template('dashboard.html', vaults=vaults, shared=shared)
