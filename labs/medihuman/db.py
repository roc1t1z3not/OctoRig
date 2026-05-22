import sqlite3
from flask import g

DB_PATH = '/data/medihuman.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            email       TEXT,
            full_name   TEXT,
            role        TEXT DEFAULT 'patient',
            is_admin    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS patients (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER NOT NULL,
            dob                 TEXT,
            blood_type          TEXT,
            ssn                 TEXT,
            insurance_id        TEXT,
            allergies           TEXT,
            assigned_doctor_id  INTEGER,
            bio                 TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   INTEGER NOT NULL,
            appt_date   TEXT,
            reason      TEXT,
            notes       TEXT DEFAULT '',
            status      TEXT DEFAULT 'scheduled'
        );

        CREATE TABLE IF NOT EXISTS prescriptions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id      INTEGER NOT NULL,
            doctor_id       INTEGER NOT NULL,
            drug            TEXT,
            dosage          TEXT,
            instructions    TEXT,
            prescribed_date TEXT,
            notes           TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS lab_results (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            doctor_id   INTEGER NOT NULL,
            test_type   TEXT,
            result      TEXT,
            notes       TEXT DEFAULT '',
            result_date TEXT
        );

        CREATE TABLE IF NOT EXISTS documents (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id  INTEGER NOT NULL,
            filename    TEXT,
            stored_name TEXT,
            doc_type    TEXT DEFAULT 'other',
            uploaded_at TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            from_id INTEGER NOT NULL,
            to_id   INTEGER NOT NULL,
            subject TEXT,
            body    TEXT DEFAULT '',
            sent_at TEXT,
            read    INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS reset_tokens (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            token       TEXT NOT NULL,
            expires_at  TEXT,
            used        INTEGER DEFAULT 0
        );
    """)

    # ── Seed users ────────────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO users (id, username, password, email, full_name, role, is_admin) VALUES
          (1, 'admin',         'medihuman-admin-2026', 'admin@medihuman.local',          'Admin',           'admin',   1),
          (2, 'dr.carter',     'password1',            'carter@medihuman.local',          'Dr. James Carter', 'doctor',  0),
          (3, 'dr.patel',      'letmein',              'patel@medihuman.local',           'Dr. Priya Patel',  'doctor',  0),
          (4, 'patient.john',  'sunshine1',            'john.walker@mail.example',        'John Walker',      'patient', 0),
          (5, 'patient.maria', 'baseball99',           'maria.santos@mail.example',       'Maria Santos',     'patient', 0),
          (6, 'patient.kevin', 'iloveyou',             'kevin.park@mail.example',         'Kevin Park',       'patient', 0),
          (7, 'patient.sara',  'monkey123',            'sara.mitchell@mail.example',      'Sara Mitchell',    'patient', 0),
          (8, 'nurse.lisa',    'dragon99',             'lisa.huang@medihuman.local',      'Lisa Huang',       'nurse',   0);
    """)

    # ── Seed patients ─────────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO patients (id, user_id, dob, blood_type, ssn, insurance_id, allergies, assigned_doctor_id, bio) VALUES
          (1, 4, '1985-03-12', 'O+',  '123-45-6789', 'INS-00441', 'Penicillin',    2, 'No significant history.'),
          (2, 5, '1992-07-24', 'A-',  '234-56-7890', 'INS-00442', 'None known',    2, 'Asthma, controlled.'),
          (3, 6, '1978-11-05', 'B+',  '345-67-8901', 'INS-00443', 'Sulfa drugs',   3, 'Type 2 diabetic.'),
          (4, 7, '2001-02-18', 'AB+', '456-78-9012', 'INS-00444', 'Latex',         3, 'Healthy, routine checkups.');
    """)

    # ── Seed appointments ──────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO appointments (id, patient_id, doctor_id, appt_date, reason, notes, status) VALUES
          (1,  1, 2, '2026-04-10', 'Annual physical',       'BP slightly elevated. Follow up in 3 months.',  'completed'),
          (2,  1, 2, '2026-07-15', 'Follow-up',             '',                                              'scheduled'),
          (3,  2, 2, '2026-03-22', 'Asthma review',         'Inhaler prescription renewed.',                 'completed'),
          (4,  2, 2, '2026-06-18', 'Routine checkup',       '',                                              'scheduled'),
          (5,  3, 3, '2026-04-05', 'Diabetes management',   'HbA1c at 7.1. Diet adjusted.',                  'completed'),
          (6,  3, 3, '2026-08-01', 'Quarterly review',      '',                                              'scheduled'),
          (7,  4, 3, '2026-02-14', 'Wellness exam',         'All results within normal range.',              'completed'),
          (8,  4, 3, '2026-09-10', 'Annual physical',       '',                                              'scheduled');
    """)

    # ── Seed prescriptions ────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO prescriptions (id, patient_id, doctor_id, drug, dosage, instructions, prescribed_date, notes) VALUES
          (1, 1, 2, 'Lisinopril',   '10mg',   'Once daily in the morning', '2026-04-10', 'Monitor potassium levels.'),
          (2, 1, 2, 'Aspirin',      '81mg',   'Once daily with food',      '2026-04-10', ''),
          (3, 2, 2, 'Albuterol',    '90mcg',  '2 puffs as needed',         '2026-03-22', 'Rescue inhaler only.'),
          (4, 2, 2, 'Fluticasone',  '110mcg', '2 puffs twice daily',       '2026-03-22', ''),
          (5, 3, 3, 'Metformin',    '500mg',  'Twice daily with meals',    '2026-04-05', 'Check kidney function annually.'),
          (6, 3, 3, 'Atorvastatin', '20mg',   'Once daily at bedtime',     '2026-04-05', ''),
          (7, 4, 3, 'Vitamin D',    '2000IU', 'Once daily with food',      '2026-02-14', 'Routine supplement.'),
          (8, 4, 3, 'Folic acid',   '400mcg', 'Once daily',                '2026-02-14', '');
    """)

    # ── Seed lab results ──────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO lab_results (id, patient_id, doctor_id, test_type, result, notes, result_date) VALUES
          (1, 1, 2, 'CBC',            'WBC 6.5, RBC 4.8, Hgb 14.2 — Normal',     '',                           '2026-04-10'),
          (2, 2, 2, 'Spirometry',     'FEV1/FVC 0.72 — Mild obstruction',         'Consistent with asthma.',    '2026-03-22'),
          (3, 3, 3, 'HbA1c',         '7.1% — Borderline',                         'Target <7.0%. Adjust diet.', '2026-04-05'),
          (4, 4, 3, 'Lipid panel',    'Total 182, LDL 105, HDL 62, TG 75 — Normal','',                          '2026-02-14');
    """)

    # ── Seed documents ────────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO documents (id, patient_id, filename, stored_name, doc_type, uploaded_at) VALUES
          (1, 1, 'referral_cardiology.pdf', 'file_001.pdf', 'referral',  '2026-04-12'),
          (2, 2, 'spirometry_results.pdf',  'file_002.pdf', 'test',      '2026-03-23'),
          (3, 3, 'diabetes_log.pdf',        'file_003.pdf', 'other',     '2026-04-06'),
          (4, 4, 'insurance_card.pdf',      'file_004.pdf', 'insurance', '2026-02-15');
    """)

    # ── Seed messages ─────────────────────────────────────────────────────────
    db.executescript("""
        INSERT OR IGNORE INTO messages (id, from_id, to_id, subject, body, sent_at, read) VALUES
          (1, 2, 4, 'Your next appointment',   'Hi John, your follow-up is scheduled for July 15. Please fast for 12 hours before.',            '2026-05-01', 1),
          (2, 4, 2, 'Question about medication','Dr. Carter — I have been experiencing some dizziness on the Lisinopril. Is this normal?',       '2026-05-03', 1),
          (3, 2, 4, 'Re: Question about medication','Some dizziness is common when starting. Take it at night and stay hydrated. Call if it persists.','2026-05-04', 0),
          (4, 3, 6, 'Lab results ready',       'Kevin, your HbA1c results are in. Please log in to review.',                                    '2026-05-10', 0),
          (5, 1, 8, 'Shift coverage needed',   'Lisa, can you cover Ward B on Friday? Let me know by EOD.',                                      '2026-05-12', 0);
    """)

    db.commit()
    db.close()
