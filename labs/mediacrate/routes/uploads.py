# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
from flask import session, redirect, url_for, render_template, request
from db import get_db

UPLOAD_DIR = '/app/uploads'


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/channels/<int:channel_id>/banner', methods=['GET', 'POST'])
    def channel_banner(channel_id):
        redir = _require_login()
        if redir:
            return redir
        db = get_db()
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        if not channel:
            return render_template('404.html'), 404
        if channel['owner_id'] != session['user_id']:
            return render_template('403.html'), 403
        error = None
        if request.method == 'POST':
            file = request.files.get('banner')
            if not file or not file.filename:
                error = 'Choose a file to upload.'
            else:
                # VULN: file upload — the raw client-supplied filename is
                # joined straight onto the channel's upload directory with no
                # secure_filename() and no extension allow-list.
                channel_dir = os.path.join(UPLOAD_DIR, str(channel_id))
                os.makedirs(channel_dir, exist_ok=True)
                dest = os.path.join(channel_dir, file.filename)
                file.save(dest)
                db.execute("UPDATE channels SET banner_path = ? WHERE id = ?", (file.filename, channel_id))
                db.commit()
        channel = db.execute("SELECT * FROM channels WHERE id = ?", (channel_id,)).fetchone()
        return render_template('channel_banner.html', channel=channel, error=error)

    # VULN: path traversal — same naive os.path.join() on the read side as
    # the upload route above. A filename like
    # ../../../../data/.private/legal_takedowns.txt walks straight out of
    # the upload directory and reads any file the process can see.
    @app.route('/uploads/<int:channel_id>/<path:filename>')
    def uploaded_banner(channel_id, filename):
        redir = _require_login()
        if redir:
            return redir
        path = os.path.join(UPLOAD_DIR, str(channel_id), filename)
        if not os.path.isfile(path):
            return render_template('404.html'), 404
        with open(path, 'rb') as f:
            data = f.read()
        return data, 200, {'Content-Type': 'application/octet-stream'}
