# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
import os
import sqlite3
from flask import g

DATABASE = '/data/smartgridops.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS operators (
    id          INTEGER PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    email       TEXT NOT NULL,
    full_name   TEXT DEFAULT '',
    is_admin    INTEGER DEFAULT 0,
    role        TEXT DEFAULT 'operator',
    zone_id     INTEGER DEFAULT 0,
    api_token   TEXT DEFAULT '',
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS zones (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    region      TEXT DEFAULT '',
    operator_id INTEGER NOT NULL,
    load_mw     REAL DEFAULT 0,
    capacity_mw REAL DEFAULT 0,
    status      TEXT DEFAULT 'nominal',
    secret_note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS devices (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    zone_id     INTEGER NOT NULL,
    dtype       TEXT DEFAULT 'sensor',
    mgmt_ip     TEXT DEFAULT '',
    status_url  TEXT DEFAULT '',
    firmware    TEXT DEFAULT '',
    state       TEXT DEFAULT 'online',
    api_token   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS meters (
    id          INTEGER PRIMARY KEY,
    serial      TEXT UNIQUE NOT NULL,
    zone_id     INTEGER NOT NULL,
    customer    TEXT DEFAULT '',
    address     TEXT DEFAULT '',
    reading_kwh REAL DEFAULT 0,
    tariff      TEXT DEFAULT 'residential',
    last_seen   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS credits (
    operator_id INTEGER PRIMARY KEY,
    balance     REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS credit_ledger (
    id          INTEGER PRIMARY KEY,
    operator_id INTEGER NOT NULL,
    delta       REAL NOT NULL,
    reason      TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS mqtt_log (
    id          INTEGER PRIMARY KEY,
    topic       TEXT NOT NULL,
    payload     TEXT NOT NULL,
    published_by INTEGER NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _flags (
    name  TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR IGNORE INTO operators VALUES
  (1,'admin','grid-master-2023','admin@smartgridops.local','Grid Operations Admin',1,'admin',0,'sgo-admin-d41d8cd98f','FLAG{sgo_idor_operator_token_exposed}'),
  (2,'j.tanaka','transformer1','jtanaka@smartgridops.local','Junko Tanaka',0,'operator',1,'sgo-op-1a2b3c','Zone 1 (Substation A) primary operator.'),
  (3,'m.okoro','feeder2023','mokoro@smartgridops.local','Michael Okoro',0,'operator',2,'sgo-op-4d5e6f','Zone 2 (Downtown) operator.'),
  (4,'l.svensson','recloser99','lsvensson@smartgridops.local','Lena Svensson',0,'operator',3,'sgo-op-7g8h9i','Zone 3 (North Feeder) operator.'),
  (5,'demo','demo','demo@smartgridops.local','Demo Operator',0,'operator',2,'sgo-op-demo01','Read-only demo account for the control room display.');

INSERT OR IGNORE INTO zones VALUES
  (1,'Substation A','Central District',2,142.5,200.0,'nominal','Bypass relay override code: BR-1-7741'),
  (2,'Downtown Grid','Commercial Core',3,188.2,220.0,'elevated','Load-shed sequence keyed to MQTT topic grid/zone/2/cmd'),
  (3,'North Feeder','Residential North',4,96.7,150.0,'nominal',''),
  (4,'Harbor Industrial','Port Authority',1,210.9,250.0,'critical','FLAG{sgo_idor_zone_secret_note} — restricted: blackstart procedure stored in historian'),
  (5,'Airport Microgrid','Transit Zone',1,64.3,120.0,'nominal','Islanding switch under maintenance lockout.');

INSERT OR IGNORE INTO devices VALUES
  (1,'Substation A Transformer',1,'transformer','10.20.1.10','http://10.20.1.10/status','TX-fw-4.1.2','online','sgo-device-7f3a9c2e1b'),
  (2,'Downtown EV Charger Bank',2,'ev_charger','10.20.2.20','http://10.20.2.20/status','EVC-fw-2.8.0','online','sgo-device-7f3a9c2e1b'),
  (3,'North Feeder Recloser',3,'recloser','10.20.3.30','http://10.20.3.30/status','RC-fw-1.5.4','online','sgo-device-7f3a9c2e1b'),
  (4,'Harbor Smart Switch',4,'switch','10.20.4.40','http://10.20.4.40/status','SW-fw-3.0.1','online','sgo-device-7f3a9c2e1b'),
  (5,'Airport Battery Inverter',5,'inverter','10.20.5.50','http://10.20.5.50/status','INV-fw-5.2.0','online','sgo-device-7f3a9c2e1b');

INSERT OR IGNORE INTO meters VALUES
  (1,'MTR-0001',1,'Acme Foundry','14 Mill Road, Central District',48211.4,'industrial','2026-06-15 23:50'),
  (2,'MTR-0002',1,'R. Delgado','22 Park Ave, Central District',9123.7,'residential','2026-06-15 23:51'),
  (3,'MTR-0003',2,'Downtown Mall LLC','1 Plaza Way, Commercial Core',152340.9,'commercial','2026-06-15 23:49'),
  (4,'MTR-0004',2,'K. Brenner','88 5th Street, Commercial Core',7610.2,'residential','2026-06-15 23:52'),
  (5,'MTR-0005',3,'P. Nguyen','3 Birch Court, Residential North',4502.8,'residential','2026-06-15 23:48'),
  (6,'MTR-0006',4,'Port Authority Crane 7','Pier 4, Port Authority',331290.5,'industrial','2026-06-15 23:47'),
  (7,'MTR-0007',4,'Harbor Cold Storage','Pier 6, Port Authority',274118.0,'industrial','2026-06-15 23:46');

INSERT OR IGNORE INTO credits VALUES
  (1, 0.0),
  (2, 250.0),
  (3, 250.0),
  (4, 250.0),
  (5, 50.0);

INSERT OR IGNORE INTO credit_ledger VALUES
  (1,2,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (2,3,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (3,4,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (4,5,50.0,'Demo allocation','2026-04-01 09:00');

INSERT OR IGNORE INTO _flags VALUES
  ('biz-credits', 'FLAG{sgo_business_logic_credit_overflow}'),
  ('mqtt-inject', 'FLAG{sgo_mqtt_topic_injection}');
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
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    with open('/flag_cmdi.txt', 'w') as f:
        f.write('FLAG{sgo_cmdi_device_reboot_rce}\n')
