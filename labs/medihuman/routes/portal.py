from datetime import date
from flask import request, render_template, session, redirect, url_for, abort
from db import get_db
from helpers import current_user


def init(app):

    # ── Index / Dashboard ─────────────────────────────────────────────────────

    @app.route('/')
    def index():
        u = current_user()
        if u:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        u  = current_user()
        db = get_db()
        stats = {
            'patients':     db.execute("SELECT COUNT(*) FROM patients").fetchone()[0],
            'appointments': db.execute("SELECT COUNT(*) FROM appointments WHERE status='scheduled'").fetchone()[0],
            'messages':     db.execute("SELECT COUNT(*) FROM messages WHERE to_id=? AND read=0", (u['id'],)).fetchone()[0],
        }
        recent_appts = db.execute(
            "SELECT a.*, u.full_name as patient_name FROM appointments a "
            "JOIN patients p ON a.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "ORDER BY a.appt_date DESC LIMIT 5"
        ).fetchall()
        return render_template('dashboard.html', u=u, stats=stats, recent_appts=recent_appts)

    # ── Patients — IDOR + SQLi search ────────────────────────────────────────

    @app.route('/patients')
    def patients():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        q  = request.args.get('q', '').strip()
        if q:
            # VULN: SQLi + reflected XSS via {{ q | safe }} in template
            rows = db.execute(
                f"SELECT p.*, u.full_name, u.username FROM patients p "
                f"JOIN users u ON p.user_id = u.id "
                f"WHERE u.full_name LIKE '%{q}%' OR p.ssn LIKE '%{q}%' OR p.insurance_id LIKE '%{q}%'"
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT p.*, u.full_name, u.username FROM patients p "
                "JOIN users u ON p.user_id = u.id ORDER BY p.id"
            ).fetchall()
        return render_template('patients.html', patients=rows, q=q)

    # IDOR: no check that viewer is assigned doctor or the patient themselves
    @app.route('/patients/<int:patient_id>')
    def patient_detail(patient_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db      = get_db()
        patient = db.execute(
            "SELECT p.*, u.full_name, u.username, u.email, u.role "
            "FROM patients p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (patient_id,)
        ).fetchone()
        if not patient:
            abort(404)
        appts = db.execute(
            "SELECT a.*, u.full_name as doctor_name FROM appointments a "
            "JOIN users u ON a.doctor_id = u.id WHERE a.patient_id = ? ORDER BY a.appt_date DESC",
            (patient_id,)
        ).fetchall()
        rxs = db.execute(
            "SELECT r.*, u.full_name as doctor_name FROM prescriptions r "
            "JOIN users u ON r.doctor_id = u.id WHERE r.patient_id = ? ORDER BY r.prescribed_date DESC",
            (patient_id,)
        ).fetchall()
        labs = db.execute(
            "SELECT l.*, u.full_name as doctor_name FROM lab_results l "
            "JOIN users u ON l.doctor_id = u.id WHERE l.patient_id = ? ORDER BY l.result_date DESC",
            (patient_id,)
        ).fetchall()
        docs = db.execute("SELECT * FROM documents WHERE patient_id = ?", (patient_id,)).fetchall()
        return render_template('patient_detail.html', patient=patient, appts=appts, rxs=rxs, labs=labs, docs=docs)

    @app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
    def patient_edit(patient_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db      = get_db()
        patient = db.execute(
            "SELECT p.*, u.full_name FROM patients p JOIN users u ON p.user_id = u.id WHERE p.id = ?",
            (patient_id,)
        ).fetchone()
        if not patient:
            abort(404)
        if request.method == 'POST':
            bio      = request.form.get('bio', '')
            allergies = request.form.get('allergies', '').strip()
            phone    = request.form.get('phone', '').strip()
            db.execute(
                "UPDATE patients SET bio = ?, allergies = ? WHERE id = ?",
                (bio, allergies, patient_id)
            )
            db.commit()
            return redirect(url_for('patient_detail', patient_id=patient_id))
        return render_template('patient_edit.html', patient=patient)

    # ── Appointments — IDOR ───────────────────────────────────────────────────

    @app.route('/appointments')
    def appointments():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        rows = db.execute(
            "SELECT a.*, u.full_name as patient_name, d.full_name as doctor_name "
            "FROM appointments a "
            "JOIN patients p ON a.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "JOIN users d ON a.doctor_id = d.id "
            "ORDER BY a.appt_date DESC"
        ).fetchall()
        return render_template('appointments.html', appointments=rows)

    # IDOR: no ownership check
    @app.route('/appointments/<int:appt_id>')
    def appointment_detail(appt_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db   = get_db()
        appt = db.execute(
            "SELECT a.*, u.full_name as patient_name, d.full_name as doctor_name "
            "FROM appointments a "
            "JOIN patients p ON a.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "JOIN users d ON a.doctor_id = d.id "
            "WHERE a.id = ?",
            (appt_id,)
        ).fetchone()
        if not appt:
            abort(404)
        return render_template('appointment_detail.html', appt=appt)

    @app.route('/appointments/<int:appt_id>/notes', methods=['POST'])
    def appointment_add_notes(appt_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        notes = request.form.get('notes', '')
        db    = get_db()
        db.execute("UPDATE appointments SET notes = ? WHERE id = ?", (notes, appt_id))
        db.commit()
        return redirect(url_for('appointment_detail', appt_id=appt_id))

    # ── Prescriptions — IDOR ──────────────────────────────────────────────────

    # IDOR: no ownership check
    @app.route('/prescriptions/<int:rx_id>')
    def prescription_detail(rx_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db = get_db()
        rx = db.execute(
            "SELECT r.*, u.full_name as patient_name, d.full_name as doctor_name "
            "FROM prescriptions r "
            "JOIN patients p ON r.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "JOIN users d ON r.doctor_id = d.id "
            "WHERE r.id = ?",
            (rx_id,)
        ).fetchone()
        if not rx:
            abort(404)
        return render_template('prescription_detail.html', rx=rx)

    # ── Lab Results — IDOR ────────────────────────────────────────────────────

    # IDOR: no ownership check
    @app.route('/labs/<int:lab_id>')
    def lab_detail(lab_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        db  = get_db()
        lab = db.execute(
            "SELECT l.*, u.full_name as patient_name, d.full_name as doctor_name "
            "FROM lab_results l "
            "JOIN patients p ON l.patient_id = p.id "
            "JOIN users u ON p.user_id = u.id "
            "JOIN users d ON l.doctor_id = d.id "
            "WHERE l.id = ?",
            (lab_id,)
        ).fetchone()
        if not lab:
            abort(404)
        return render_template('lab_detail.html', lab=lab)

    @app.route('/labs/<int:lab_id>/notes', methods=['POST'])
    def lab_add_notes(lab_id):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        notes = request.form.get('notes', '')
        db    = get_db()
        db.execute("UPDATE lab_results SET notes = ? WHERE id = ?", (notes, lab_id))
        db.commit()
        return redirect(url_for('lab_detail', lab_id=lab_id))

    # ── Profile ───────────────────────────────────────────────────────────────

    @app.route('/profile')
    def profile():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        u       = current_user()
        db      = get_db()
        patient = db.execute("SELECT * FROM patients WHERE user_id = ?", (u['id'],)).fetchone()
        return render_template('profile.html', u=u, patient=patient)

    @app.route('/profile/update', methods=['POST'])
    def profile_update():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        full_name = request.form.get('full_name', '').strip()
        email     = request.form.get('email', '').strip()
        db        = get_db()
        db.execute("UPDATE users SET full_name = ?, email = ? WHERE id = ?",
                   (full_name, email, session['user_id']))
        db.commit()
        return redirect(url_for('profile'))
