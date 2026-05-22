import os
from flask import request, render_template, session, redirect, url_for, abort, send_file
from db import get_db


def init(app):

    # IDOR: lists documents for all patients
    @app.route('/docs')
    def docs():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        rows = get_db().execute(
            "SELECT d.*, u.full_name, u.username FROM documents d "
            "JOIN users u ON d.patient_id = u.id ORDER BY d.id"
        ).fetchall()
        return render_template('docs.html', docs=rows)

    # VULN: no extension check, no MIME check, sequential predictable stored_name
    @app.route('/docs/upload', methods=['POST'])
    def doc_upload():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        f        = request.files.get('file')
        doc_type = request.form.get('doc_type', 'other').strip()
        if not f or not f.filename:
            abort(400)
        db    = get_db()
        count = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        ext   = os.path.splitext(f.filename)[1]
        stored_name = f"file_{count + 1:03d}{ext}"
        f.save(f'/data/uploads/{stored_name}')
        # Use the current user's patient record if they are a patient
        patient = db.execute(
            "SELECT id FROM patients WHERE user_id = ?", (session['user_id'],)
        ).fetchone()
        patient_id = patient['id'] if patient else session['user_id']
        db.execute(
            "INSERT INTO documents (patient_id, filename, stored_name, doc_type, uploaded_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (patient_id, f.filename, stored_name, doc_type, __import__('datetime').date.today())
        )
        db.commit()
        return redirect(url_for('docs'))

    # VULN: <path:> allows slashes → path traversal; no ownership check → IDOR
    @app.route('/docs/download/<path:stored_name>')
    def doc_download(stored_name):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        full_path = os.path.join('/data/uploads', stored_name)
        return send_file(full_path)
