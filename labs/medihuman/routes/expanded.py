# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Expanded attack surface — additional REST endpoints and OpenAPI spec."""
from __future__ import annotations

from flask import jsonify, request, session

from db import get_db

_SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "MediHuman API", "version": "1.0.0"},
    "paths": {
        "/": {"get": {}},
        "/dashboard": {"get": {}},
        "/patients": {
            "get": {"parameters": [{"name": "q", "in": "query"}]}
        },
        "/patients/{patient_id}": {"get": {}},
        "/patients/{patient_id}/edit": {"get": {}, "post": {}},
        "/appointments": {"get": {}},
        "/appointments/{appt_id}": {"get": {}},
        "/appointments/{appt_id}/notes": {"post": {}},
        "/prescriptions/{rx_id}": {"get": {}},
        "/labs/{lab_id}": {"get": {}},
        "/labs/{lab_id}/notes": {"post": {}},
        "/messages": {"get": {}},
        "/messages/{msg_id}": {"get": {}},
        "/messages/new": {"get": {}, "post": {}},
        "/profile": {"get": {}},
        "/profile/update": {"post": {}},
        "/admin": {"get": {}},
        "/admin/staff/{user_id}": {"get": {}},
        "/docs": {"get": {}},
        "/docs/upload": {"post": {}},
        "/docs/download/{stored_name}": {"get": {}},
        "/api/token": {"post": {}},
        "/api/patients/{patient_id}": {"get": {}},
        "/api/me": {"get": {}},
        "/health": {"get": {}},
        # ── New expanded endpoints ────────────────────────────────────────────
        "/api/v1/records/{patient_id}": {"get": {}},
        "/api/v1/physicians/{doctor_id}/schedule": {"get": {}},
        "/api/v1/prescriptions/{id}": {"get": {}},
        "/api/v1/appointments/{id}": {"get": {}, "put": {}},
        "/api/v1/admin/export": {"get": {}},
        "/mri-viewer": {"get": {}},
        "/billing-portal": {"get": {}},
    },
}


def init(app):

    @app.route("/openapi.json")
    def openapi_spec():
        return jsonify(_SPEC)

    # ── /api/v1/records/<patient_id> — IDOR: no ownership check ──────────────

    @app.route("/api/v1/records/<int:patient_id>")
    def api_v1_record(patient_id):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        db = get_db()
        patient = db.execute(
            "SELECT p.*, u.username, u.email, u.full_name "
            "FROM patients p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (patient_id,),
        ).fetchone()
        if not patient:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(patient))

    # ── /api/v1/physicians/<doctor_id>/schedule — IDOR ───────────────────────

    @app.route("/api/v1/physicians/<int:doctor_id>/schedule")
    def api_v1_physician_schedule(doctor_id):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        rows = get_db().execute(
            "SELECT a.*, u.full_name AS patient_name "
            "FROM appointments a "
            "JOIN patients p ON a.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "WHERE a.doctor_id = ? ORDER BY a.appt_date",
            (doctor_id,),
        ).fetchall()
        return jsonify([dict(r) for r in rows])

    # ── /api/v1/prescriptions/<id> — IDOR ────────────────────────────────────

    @app.route("/api/v1/prescriptions/<int:rx_id>")
    def api_v1_prescription(rx_id):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        row = get_db().execute(
            "SELECT * FROM prescriptions WHERE id = ?", (rx_id,)
        ).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(row))

    # ── /api/v1/appointments/<id> GET/PUT — IDOR + mass assignment ───────────

    @app.route("/api/v1/appointments/<int:appt_id>", methods=["GET", "PUT"])
    def api_v1_appointment(appt_id):
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        db = get_db()
        if request.method == "GET":
            row = db.execute(
                "SELECT * FROM appointments WHERE id = ?", (appt_id,)
            ).fetchone()
            if not row:
                return jsonify({"error": "Not found"}), 404
            return jsonify(dict(row))
        # PUT — mass assignment: any JSON field written directly to DB
        data = request.get_json(silent=True) or {}
        if data:
            fields = ", ".join(f"{k} = ?" for k in data.keys())
            values = list(data.values()) + [appt_id]
            try:
                db.execute(
                    f"UPDATE appointments SET {fields} WHERE id = ?", values
                )
                db.commit()
            except Exception as e:
                return jsonify({"error": str(e)}), 400
        row = db.execute(
            "SELECT * FROM appointments WHERE id = ?", (appt_id,)
        ).fetchone()
        return jsonify(dict(row)) if row else (jsonify({"error": "Not found"}), 404)

    # ── /api/v1/admin/export — broken access: checks login, not is_admin ──────

    @app.route("/api/v1/admin/export")
    def api_v1_admin_export():
        if not session.get("user_id"):
            return jsonify({"error": "Unauthorized"}), 401
        db = get_db()
        patients = db.execute(
            "SELECT p.*, u.full_name, u.username, u.email "
            "FROM patients p JOIN users u ON p.user_id = u.id"
        ).fetchall()
        return jsonify(
            {
                "patients": [dict(r) for r in patients],
                "admin": True,
                "role": "admin",
                "is_superuser": True,
                "export_format": "json",
            }
        )

    # ── /mri-viewer — broken access stub ──────────────────────────────────────

    @app.route("/mri-viewer")
    def mri_viewer():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute(
            "SELECT d.*, u.full_name "
            "FROM documents d JOIN users u ON d.user_id = u.id "
            "WHERE d.doc_type = 'mri'"
        ).fetchall()
        return jsonify({"scans": [dict(r) for r in rows], "admin": True, "role": "admin"})

    # ── /billing-portal — broken access: dumps all prescriptions ──────────────

    @app.route("/billing-portal")
    def billing_portal():
        if not session.get("user_id"):
            return jsonify({"error": "unauthorized"}), 401
        rows = get_db().execute("SELECT * FROM prescriptions").fetchall()
        return jsonify({"prescriptions": [dict(r) for r in rows], "admin": True})
