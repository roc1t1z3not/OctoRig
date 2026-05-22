import os
import sqlite3
from flask import g

DATABASE = '/data/humanbank.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY,
    username  TEXT UNIQUE NOT NULL,
    password  TEXT NOT NULL,
    email     TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    is_admin  INTEGER DEFAULT 0,
    bio       TEXT DEFAULT '',
    phone     TEXT DEFAULT '',
    address   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS accounts (
    id             INTEGER PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    account_number TEXT UNIQUE NOT NULL,
    account_type   TEXT NOT NULL,
    balance        REAL DEFAULT 0.0,
    opened_date    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id           INTEGER PRIMARY KEY,
    account_id   INTEGER NOT NULL,
    type         TEXT NOT NULL,
    amount       REAL NOT NULL,
    memo         TEXT DEFAULT '',
    counterparty TEXT DEFAULT '',
    txn_date     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    subject    TEXT NOT NULL,
    body       TEXT NOT NULL,
    status     TEXT DEFAULT 'open',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ticket_replies (
    id         INTEGER PRIMARY KEY,
    ticket_id  INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    body       TEXT NOT NULL,
    is_admin   INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    filename    TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    doc_type    TEXT NOT NULL,
    uploaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used       INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@humanbank.local','HumanBank Admin',1,'','555-0100','HumanBank HQ'),
  (2,'alice.wang','sunshine1','alice@example.com','Alice Wang',0,'Passionate about personal finance and travel.','+1 503 555 0201','14 Cedar Ave, Portland OR'),
  (3,'bob.harris','baseball99','bob@example.com','Bob Harris',0,'','','42 Oak Street, Seattle WA'),
  (4,'carol.lee','iloveyou','carol@example.com','Carol Lee',0,'Coffee addict. Saving for a house.','','88 Pine Road, Austin TX'),
  (5,'dan.murphy','letmein','dan@example.com','Dan Murphy',0,'','','22 Elm Drive, Denver CO'),
  (6,'eva.santos','monkey123','eva@example.com','Eva Santos',0,'Freelance designer. Multiple income streams.','','9 Birch Lane, Miami FL'),
  (7,'frank.kim','dragon99','frank@example.com','Frank Kim',0,'','','77 Maple Court, Chicago IL'),
  (8,'c.human','commonhuman-lab','accounts@commonhuman.local','CommonHuman Labs',0,'Categorisation not possible.','','Unknown');

INSERT OR IGNORE INTO accounts VALUES
  (1, 2,'HB-0001','checking', 4823.50,'2024-01-15'),
  (2, 2,'HB-0002','savings', 12400.00,'2024-01-15'),
  (3, 3,'HB-0003','checking',   875.25,'2024-03-02'),
  (4, 3,'HB-0004','savings',  3200.00,'2024-03-02'),
  (5, 4,'HB-0005','checking',  2100.00,'2024-06-18'),
  (6, 4,'HB-0006','savings',   8500.00,'2024-06-18'),
  (7, 5,'HB-0007','checking',   560.00,'2025-01-10'),
  (8, 5,'HB-0008','savings',   1200.00,'2025-01-10'),
  (9, 6,'HB-0009','checking',  9345.80,'2023-11-05'),
  (10,6,'HB-0010','savings',  24000.00,'2023-11-05'),
  (11,7,'HB-0011','checking',  1870.00,'2025-04-22'),
  (12,7,'HB-0012','savings',   5000.00,'2025-04-22'),
  (13,8,'HB-CMNH','checking',1337000.00,'2026-01-01');

INSERT OR IGNORE INTO transactions VALUES
  (1, 1,'credit',3200.00,'Payroll — April 2026','ACME Corp','2026-04-30'),
  (2, 1,'debit', 1200.00,'Rent — May 2026','City Properties LLC','2026-05-01'),
  (3, 1,'debit',   85.50,'Grocery shopping','Whole Foods Market','2026-05-03'),
  (4, 1,'debit',   45.00,'Streaming subscription','Netflix Inc','2026-05-05'),
  (5, 1,'credit',3200.00,'Payroll — May 2026','ACME Corp','2026-05-31'),
  (6, 2,'credit', 500.00,'Transfer from checking','HB-0001','2026-04-01'),
  (7, 2,'credit',  12.40,'Monthly interest','HumanBank','2026-04-30'),
  (8, 3,'credit',1800.00,'Payroll — April 2026','TechStart Inc','2026-04-30'),
  (9, 3,'debit',  650.00,'Rent payment','Metro Rentals','2026-05-01'),
  (10,3,'debit',   42.99,'Mobile phone bill','Verizon','2026-05-08'),
  (11,5,'credit',2500.00,'Freelance invoice — Project A','Studio Blue','2026-04-20'),
  (12,5,'debit',  350.00,'Creative Cloud annual','Adobe Systems','2026-05-01'),
  (13,5,'debit',   88.00,'Electricity bill','Pacific Power Co','2026-05-10'),
  (14,7,'credit',1200.00,'Rideshare earnings','Uber Technologies','2026-05-05'),
  (15,7,'debit',  120.00,'Fuel — full tank','Shell Gas Station','2026-05-07'),
  (16,7,'debit',   55.00,'Dinner','The Burger Place','2026-05-12'),
  (17,9,'credit',5400.00,'Client payment — Branding project','Santos Design Studio','2026-04-25'),
  (18,9,'credit',3200.00,'Client payment — Web redesign','Apex Corp','2026-05-10'),
  (19,9,'debit',  800.00,'Software subscriptions','Various vendors','2026-05-15'),
  (20,11,'credit',2100.00,'Monthly salary','First National Corp','2026-04-30'),
  (21,11,'debit',  900.00,'Mortgage repayment','City Mortgage Bank','2026-05-01'),
  (22,11,'debit',   65.00,'Broadband service','Comcast','2026-05-08'),
  (23,1,'debit',  200.00,'Transfer to Bob','HB-0003','2026-05-14'),
  (24,3,'credit', 200.00,'Transfer from Alice','HB-0001','2026-05-14'),
  (25,9,'debit',  150.00,'Payment to Carol','HB-0005','2026-05-18'),
  (26,13,'credit',1337000.00,'Initial deposit — origin unverified','CommonHuman','2026-01-01');

INSERT OR IGNORE INTO support_tickets VALUES
  (1,2,'Card declined abroad','I tried using my debit card in Europe last week and it was repeatedly declined. My balance is sufficient. This was very inconvenient. Please investigate and confirm whether international transactions are enabled on my account.','closed','2026-04-10'),
  (2,3,'Unrecognised transaction','There is a transaction for $42.99 on 8th May that I do not recognise. The description shows Verizon but I do not have a Verizon account. Please investigate this urgently.','open','2026-05-09'),
  (3,4,'Password reset not arriving','I have requested a password reset three times over the past two days and have not received any email. I have checked my spam folder. Please manually reset my password or advise.','open','2026-05-11'),
  (4,5,'Transfer showed complete but money still in account','I submitted a transfer of $100 to a friend yesterday evening. The confirmation page said it was successful but the money is still showing in my account and my friend has not received it.','open','2026-05-13'),
  (5,6,'Official statement for visa application','I need a certified bank statement covering the last six months for a visa application. The statement must show my name, account number, and transaction history. Please generate and provide.','open','2026-05-18'),
  (6,7,'Direct debit amount incorrect','My mortgage direct debit was collected for the wrong amount this month — $1,200 instead of $900. Please reverse the overpayment and confirm the correct amount has been updated for next month.','closed','2026-05-19'),
  (7,8,'This account should not exist','I would like to close this account. I did not open it. I do not know who did. Handle with care.','open','2026-01-02');

INSERT OR IGNORE INTO ticket_replies VALUES
  (1,1,1,'Hi Alice, we have lifted the international transaction restriction on your account. You should now be able to use your card abroad without issues. Please contact us if the problem persists.',1,'2026-04-12'),
  (2,6,1,'Hi Frank, we have identified the error and corrected the direct debit mandate to $900. A refund of $300 has been processed to your account and should appear within 2 business days.',1,'2026-05-21');

INSERT OR IGNORE INTO documents VALUES
  (1,2,'alice_passport.pdf','doc_001.pdf','id','2026-04-10'),
  (2,2,'statement_apr2026.pdf','doc_002.pdf','statement','2026-05-01'),
  (3,3,'bob_drivers_licence.pdf','doc_003.pdf','id','2026-05-05'),
  (4,4,'carol_statement_q1_2026.pdf','doc_004.pdf','statement','2026-05-12');
"""


def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def close_db(_):
    db = getattr(g, '_db', None)
    if db:
        db.close()


def init_db():
    os.makedirs('/data', exist_ok=True)
    os.makedirs('/data/uploads', exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
