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

-- Passwords are stored as unsalted MD5 hashes (intentionally weak / crackable).
-- Plaintext reference (operator : password):
--   admin:grid-master-2023  j.tanaka:transformer1  m.okoro:feeder2023
--   l.svensson:recloser99   demo:demo              r.fischer:summer2024
--   a.kowalski:password123  s.haddad:griddy2023    t.bergmann:letmein99
--   n.popova:qwerty2024     d.mwangi:substation7   e.larsen:winter2023
--   v.rossi:inverter01      c.dubois:charger2024   y.nakamura:feeder123
INSERT OR IGNORE INTO operators VALUES
  (1,'admin','652e25599dc885271f2a68e59412be2e','admin@smartgridops.local','Grid Operations Admin',1,'admin',0,'sgo-admin-d41d8cd98f','FLAG{sgo_idor_operator_token_exposed}'),
  (2,'j.tanaka','18e8692ec887749697163562266d1f45','jtanaka@smartgridops.local','Junko Tanaka',0,'operator',1,'sgo-op-1a2b3c','Zone 1 (Substation A) primary operator.'),
  (3,'m.okoro','2009409a9983e4f5d42e15536e22869f','mokoro@smartgridops.local','Michael Okoro',0,'operator',2,'sgo-op-4d5e6f','Zone 2 (Downtown) operator.'),
  (4,'l.svensson','e1adce188340729330a2a336e7d33c3d','lsvensson@smartgridops.local','Lena Svensson',0,'operator',3,'sgo-op-7g8h9i','Zone 3 (North Feeder) operator.'),
  (5,'demo','fe01ce2a7fbac8fafaed7c982a04e229','demo@smartgridops.local','Demo Operator',0,'operator',2,'sgo-op-demo01','Read-only demo account for the control room display.'),
  (6,'r.fischer','bb834ec54553cd09d92f34ced6aa5c15','rfischer@smartgridops.local','Rolf Fischer',0,'operator',6,'sgo-op-9a1b2c','Zone 6 (West Industrial) operator.'),
  (7,'a.kowalski','482c811da5d5b4bc6d497ffa98491e38','akowalski@smartgridops.local','Anna Kowalski',0,'operator',7,'sgo-op-3d4e5f','Zone 7 (Riverside) operator.'),
  (8,'s.haddad','f1e328cc117b3817d2ff47f6308bc138','shaddad@smartgridops.local','Samir Haddad',0,'operator',8,'sgo-op-6g7h8i','Zone 8 (Tech Campus) operator.'),
  (9,'t.bergmann','4d67bc7b403791c738186a1d8e82c8a8','tbergmann@smartgridops.local','Tomas Bergmann',0,'operator',9,'sgo-op-1j2k3l','Zone 9 (Stadium) operator.'),
  (10,'n.popova','ba90bf4e632e2c47969a737c7f10e8ed','npopova@smartgridops.local','Nadia Popova',0,'operator',10,'sgo-op-4m5n6o','Zone 10 (Hospital Priority) operator.'),
  (11,'d.mwangi','62659a192b59e888e2336db18e81f9e0','dmwangi@smartgridops.local','David Mwangi',0,'operator',11,'sgo-op-7p8q9r','Zone 11 (University) operator.'),
  (12,'e.larsen','b648997175aecaec689212b6fae20b99','elarsen@smartgridops.local','Erik Larsen',0,'operator',12,'sgo-op-1s2t3u','Zone 12 (Old Town) operator.'),
  (13,'v.rossi','0d74840cfb2e1262bbb2c92ac2e9023d','vrossi@smartgridops.local','Valentina Rossi',0,'operator',13,'sgo-op-4v5w6x','Zone 13 (Solar Farm) operator.'),
  (14,'c.dubois','571d205bdfd17bf73068c2360a21983e','cdubois@smartgridops.local','Claire Dubois',0,'operator',14,'sgo-op-7y8z9a','Zone 14 (Wind Intertie) operator.'),
  (15,'y.nakamura','734c57e3a4fa9adfa85703aa29df5b9b','ynakamura@smartgridops.local','Yuki Nakamura',0,'operator',15,'sgo-op-1b2c3d','Zone 15 (Data Center Row) operator.');

INSERT OR IGNORE INTO zones VALUES
  (1,'Substation A','Central District',2,142.5,200.0,'nominal','Bypass relay override code: BR-1-7741'),
  (2,'Downtown Grid','Commercial Core',3,188.2,220.0,'elevated','Load-shed sequence keyed to MQTT topic grid/zone/2/cmd'),
  (3,'North Feeder','Residential North',4,96.7,150.0,'nominal',''),
  (4,'Harbor Industrial','Port Authority',1,210.9,250.0,'critical','FLAG{sgo_idor_zone_secret_note} — restricted: blackstart procedure stored in historian'),
  (5,'Airport Microgrid','Transit Zone',1,64.3,120.0,'nominal','Islanding switch under maintenance lockout.'),
  (6,'West Industrial Park','West District',6,178.4,210.0,'nominal',''),
  (7,'Riverside Residential','Riverside',7,72.1,130.0,'nominal',''),
  (8,'Tech Campus Microgrid','Innovation Quarter',8,118.6,160.0,'elevated','Demand-response auto-curtailment armed.'),
  (9,'Stadium Complex','Sports District',9,54.9,180.0,'nominal','Event-day surge plan: tie to zones 2 and 6.'),
  (10,'Hospital Priority Feed','Medical District',10,96.2,140.0,'critical','Life-safety circuit — never load-shed. Override code: HP-10-3321'),
  (11,'University Grid','Education Zone',11,88.7,150.0,'nominal',''),
  (12,'Old Town Heritage','Historic Core',12,41.3,90.0,'nominal',''),
  (13,'Solar Farm Tie-In','South Plains',13,133.5,300.0,'nominal','Reverse-power export capped at 120 MW.'),
  (14,'Wind Intertie North','Highlands',14,159.8,280.0,'elevated','Curtailment governed by MQTT topic grid/zone/14/cmd.'),
  (15,'Data Center Row','Enterprise Park',15,224.6,260.0,'critical','N+1 UPS bypass procedure restricted to ops leads.');

INSERT OR IGNORE INTO devices VALUES
  (1,'Substation A Transformer',1,'transformer','10.20.1.10','http://10.20.1.10/status','TX-fw-4.1.2','online','sgo-device-7f3a9c2e1b'),
  (2,'Downtown EV Charger Bank',2,'ev_charger','10.20.2.20','http://10.20.2.20/status','EVC-fw-2.8.0','online','sgo-device-7f3a9c2e1b'),
  (3,'North Feeder Recloser',3,'recloser','10.20.3.30','http://10.20.3.30/status','RC-fw-1.5.4','online','sgo-device-7f3a9c2e1b'),
  (4,'Harbor Smart Switch',4,'switch','10.20.4.40','http://10.20.4.40/status','SW-fw-3.0.1','online','sgo-device-7f3a9c2e1b'),
  (5,'Airport Battery Inverter',5,'inverter','10.20.5.50','http://10.20.5.50/status','INV-fw-5.2.0','online','sgo-device-7f3a9c2e1b'),
  (6,'West Park Transformer',6,'transformer','10.20.6.10','http://10.20.6.10/status','TX-fw-4.1.2','online','sgo-device-7f3a9c2e1b'),
  (7,'Riverside Recloser',7,'recloser','10.20.7.30','http://10.20.7.30/status','RC-fw-1.5.4','online','sgo-device-7f3a9c2e1b'),
  (8,'Tech Campus Inverter',8,'inverter','10.20.8.50','http://10.20.8.50/status','INV-fw-5.2.0','online','sgo-device-7f3a9c2e1b'),
  (9,'Stadium Load Bank',9,'switch','10.20.9.40','http://10.20.9.40/status','SW-fw-3.0.1','online','sgo-device-7f3a9c2e1b'),
  (10,'Hospital ATS',10,'switch','10.20.10.40','http://10.20.10.40/status','SW-fw-3.0.1','online','sgo-device-7f3a9c2e1b'),
  (11,'University EV Bank',11,'ev_charger','10.20.11.20','http://10.20.11.20/status','EVC-fw-2.8.0','online','sgo-device-7f3a9c2e1b'),
  (12,'Old Town Sensor Node',12,'sensor','10.20.12.60','http://10.20.12.60/status','SN-fw-0.9.7','online','sgo-device-7f3a9c2e1b'),
  (13,'Solar Combiner',13,'inverter','10.20.13.50','http://10.20.13.50/status','INV-fw-5.2.0','online','sgo-device-7f3a9c2e1b'),
  (14,'Wind Intertie Relay',14,'recloser','10.20.14.30','http://10.20.14.30/status','RC-fw-1.5.4','offline','sgo-device-7f3a9c2e1b'),
  (15,'Data Center UPS Bypass',15,'switch','10.20.15.40','http://10.20.15.40/status','SW-fw-3.0.1','online','sgo-device-7f3a9c2e1b');

INSERT OR IGNORE INTO meters VALUES
  (1,'MTR-0001',1,'Acme Foundry','14 Mill Road, Central District',48211.4,'industrial','2026-06-15 23:50'),
  (2,'MTR-0002',1,'R. Delgado','22 Park Ave, Central District',9123.7,'residential','2026-06-15 23:51'),
  (3,'MTR-0003',2,'Downtown Mall LLC','1 Plaza Way, Commercial Core',152340.9,'commercial','2026-06-15 23:49'),
  (4,'MTR-0004',2,'K. Brenner','88 5th Street, Commercial Core',7610.2,'residential','2026-06-15 23:52'),
  (5,'MTR-0005',3,'P. Nguyen','3 Birch Court, Residential North',4502.8,'residential','2026-06-15 23:48'),
  (6,'MTR-0006',4,'Port Authority Crane 7','Pier 4, Port Authority',331290.5,'industrial','2026-06-15 23:47'),
  (7,'MTR-0007',4,'Harbor Cold Storage','Pier 6, Port Authority',274118.0,'industrial','2026-06-15 23:46'),
  (8,'MTR-0008',6,'Westside Logistics','5 Depot Road, West District',119820.3,'industrial','2026-06-15 23:45'),
  (9,'MTR-0009',7,'H. Andersson','40 River Walk, Riverside',6210.5,'residential','2026-06-15 23:44'),
  (10,'MTR-0010',8,'Innovexa Labs','12 Campus Drive, Innovation Quarter',88340.7,'commercial','2026-06-15 23:43'),
  (11,'MTR-0011',9,'City Stadium Authority','1 Arena Way, Sports District',204550.9,'commercial','2026-06-15 23:42'),
  (12,'MTR-0012',10,'Central Hospital','200 Health Blvd, Medical District',412900.1,'industrial','2026-06-15 23:41'),
  (13,'MTR-0013',11,'State University','77 College Ave, Education Zone',176430.4,'commercial','2026-06-15 23:40'),
  (14,'MTR-0014',12,'G. Romano','3 Cobble Lane, Historic Core',3920.8,'residential','2026-06-15 23:39'),
  (15,'MTR-0015',13,'SunPlains Energy Co','Plot 9, South Plains',501230.6,'industrial','2026-06-15 23:38'),
  (16,'MTR-0016',14,'Highland Wind LLC','Ridge Site 2, Highlands',460110.2,'industrial','2026-06-15 23:37'),
  (17,'MTR-0017',15,'HyperScale DC','1 Server Park, Enterprise Park',987650.0,'industrial','2026-06-15 23:36');

INSERT OR IGNORE INTO credits VALUES
  (1, 0.0),
  (2, 250.0),
  (3, 250.0),
  (4, 250.0),
  (5, 50.0),
  (6, 250.0),
  (7, 180.0),
  (8, 320.0),
  (9, 140.0),
  (10, 500.0),
  (11, 210.0),
  (12, 90.0),
  (13, 410.0),
  (14, 360.0),
  (15, 600.0);

INSERT OR IGNORE INTO credit_ledger VALUES
  (1,2,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (2,3,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (3,4,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (4,5,50.0,'Demo allocation','2026-04-01 09:00'),
  (5,6,250.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (6,7,180.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (7,8,320.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (8,9,140.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (9,10,500.0,'Priority-feed allocation','2026-04-01 09:00'),
  (10,11,210.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (11,12,90.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (12,13,410.0,'Renewable export bonus','2026-04-01 09:00'),
  (13,14,360.0,'Renewable export bonus','2026-04-01 09:00'),
  (14,15,600.0,'Enterprise SLA allocation','2026-04-01 09:00');

INSERT OR IGNORE INTO mqtt_log VALUES
  (1,'grid/zone/1/cmd','{"cmd":"status"}',2,'2026-06-15 22:01:10'),
  (2,'grid/zone/2/cmd','{"cmd":"load_shed","step":1}',3,'2026-06-15 22:05:44'),
  (3,'grid/zone/3/cmd','{"cmd":"status"}',4,'2026-06-15 22:09:02'),
  (4,'grid/zone/6/cmd','{"cmd":"setpoint","mw":170}',6,'2026-06-15 22:14:31'),
  (5,'grid/zone/7/cmd','{"cmd":"status"}',7,'2026-06-15 22:18:50'),
  (6,'grid/zone/8/cmd','{"cmd":"curtail","pct":15}',8,'2026-06-15 22:22:13'),
  (7,'grid/zone/9/cmd','{"cmd":"status"}',9,'2026-06-15 22:27:39'),
  (8,'grid/zone/10/cmd','{"cmd":"priority_lock"}',10,'2026-06-15 22:31:55'),
  (9,'grid/zone/13/cmd','{"cmd":"export_cap","mw":120}',13,'2026-06-15 22:36:20'),
  (10,'grid/zone/14/cmd','{"cmd":"curtail","pct":30}',14,'2026-06-15 22:41:07');

INSERT OR IGNORE INTO _flags VALUES
  ('biz-credits',  'FLAG{sgo_business_logic_credit_overflow}'),
  ('mqtt-inject',  'FLAG{sgo_mqtt_topic_injection}'),
  ('sqli-login',   'FLAG{sgo_sqli_login_bypassed}'),
  ('ssrf-poll',    'FLAG{sgo_ssrf_internal_fetch}');
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
    with open('/flag_py_cmdi.txt', 'w') as f:
        f.write('FLAG{sgo_python_cmdi_automated}\n')
