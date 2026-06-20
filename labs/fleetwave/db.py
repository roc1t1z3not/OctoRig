# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
import os
import sqlite3
from flask import g

DATABASE = '/data/fleetwave.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    email       TEXT NOT NULL,
    full_name   TEXT DEFAULT '',
    role        TEXT DEFAULT 'dispatcher',
    is_admin    INTEGER DEFAULT 0,
    api_token   TEXT DEFAULT '',
    bio         TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS shipments (
    id           INTEGER PRIMARY KEY,
    tracking_no  TEXT UNIQUE NOT NULL,
    account_id   INTEGER NOT NULL,
    origin       TEXT DEFAULT '',
    destination  TEXT DEFAULT '',
    recipient    TEXT DEFAULT '',
    address      TEXT DEFAULT '',
    status       TEXT DEFAULT 'in_transit',
    weight_kg    REAL DEFAULT 0,
    cost         REAL DEFAULT 0,
    notes        TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS depots (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    region      TEXT DEFAULT '',
    manager_id  INTEGER NOT NULL,
    capacity    INTEGER DEFAULT 0,
    secret_note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS depot_access (
    id        INTEGER PRIMARY KEY,
    depot_id  INTEGER NOT NULL,
    user_id   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS drivers (
    id          INTEGER PRIMARY KEY,
    full_name   TEXT NOT NULL,
    depot_id    INTEGER NOT NULL,
    license_no  TEXT DEFAULT '',
    phone       TEXT DEFAULT '',
    vehicle     TEXT DEFAULT '',
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS freight_credits (
    account_id  INTEGER PRIMARY KEY,
    balance     REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS credit_ledger (
    id          INTEGER PRIMARY KEY,
    account_id  INTEGER NOT NULL,
    delta       REAL NOT NULL,
    reason      TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_feedback (
    id          INTEGER PRIMARY KEY,
    shipment_id INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    note        TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _flags (
    name  TEXT PRIMARY KEY,
    value TEXT
);

-- Passwords are stored as unsalted MD5 hashes (intentionally weak / crackable).
-- Plaintext reference (user : password):
--   admin:fleet-master-2026   demo:demo               r.haddad:dispatch1
--   l.moreau:cargo2026        s.nakamura:routes99     j.okafor:depot123
--   e.kowalski:freight77      m.silva:parcel2026
INSERT OR IGNORE INTO users VALUES
  (1,'admin','d7e7874881c9be7faa047683023bea65','admin@fleetwave.local','FleetWave Admin','admin',1,'fw-admin-9c4e1a7b','Network operations control.'),
  (2,'demo','fe01ce2a7fbac8fafaed7c982a04e229','demo@fleetwave.local','Demo Dispatcher','dispatcher',0,'fw-user-demo01','Read-only demo seat for the ops floor display.'),
  (3,'r.haddad','33b6366c46c0d661f75fe66162a799a0','rhaddad@fleetwave.local','Rana Haddad','dispatcher',0,'fw-user-1a2b3c','Central hub dispatcher.'),
  (4,'l.moreau','64cb0656b61a1ff3080c5019f0b145ed','lmoreau@fleetwave.local','Luc Moreau','dispatcher',0,'fw-user-4d5e6f','Cross-dock coordinator, West region.'),
  (5,'s.nakamura','22c6e110cc36b0061e0e6251606f4a79','snakamura@fleetwave.local','Sora Nakamura','dispatcher',0,'fw-user-7g8h9i','Last-mile routing, Metro East.'),
  (6,'j.okafor','05e88e86d5937a9b5fceebee80fd6fa3','jokafor@fleetwave.local','Jide Okafor','dispatcher',0,'fw-user-1j2k3l','Depot manager, Harbor.'),
  (7,'e.kowalski','7011fad95d7bf11b489dfc3abfe386a3','ekowalski@fleetwave.local','Ewa Kowalski','dispatcher',0,'fw-user-4m5n6o','Freight billing analyst.'),
  (8,'m.silva','07c21f8ce59c8e473e1be4c9b940e8fe','msilva@fleetwave.local','Mateo Silva','dispatcher',0,'fw-user-7p8q9r','Returns and exceptions desk.');

-- VULN: item-level IDOR — /shipments/<id> never checks account ownership, so
-- any signed-in dispatcher can read any customer shipment by sequential id.
-- The notes field on shipment 1 carries the flag; shipment 9's notes carry
-- the python/API scripting-challenge flag.
INSERT OR IGNORE INTO shipments VALUES
  (1,'FW100001',1,'Central Hub','Government Annex','Procurement Office','12 State Plaza, Capitol District','in_transit',18.4,142.00,'High-value government consignment — restricted manifest. FLAG{fw_idor_shipment_exposed}'),
  (2,'FW100002',3,'Central Hub','48 Maple Ave','R. Delgado','48 Maple Ave, Westend','delivered',2.1,11.50,'Left with neighbour at no. 50.'),
  (3,'FW100003',3,'West Cross-Dock','9 Harbor Rd','Acme Foundry','9 Harbor Rd, Portside','in_transit',240.0,860.00,'Palletised, forklift required at delivery.'),
  (4,'FW100004',4,'Metro East DC','77 Oak St','K. Brenner','77 Oak St, Eastvale','out_for_delivery',0.8,6.20,'Fragile — electronics.'),
  (5,'FW100005',5,'Central Hub','1 Plaza Way','Downtown Mall LLC','1 Plaza Way, Commercial Core','in_transit',56.3,210.00,'Loading-dock B, after 6pm only.'),
  (6,'FW100006',6,'Harbor Depot','Pier 4','Port Authority','Pier 4, Port Authority','exception',512.0,1980.00,'Customs hold — awaiting clearance docs.'),
  (7,'FW100007',4,'Metro East DC','3 Birch Ct','P. Nguyen','3 Birch Ct, Eastvale','delivered',1.4,8.90,'Signed for by recipient.'),
  (8,'FW100008',5,'West Cross-Dock','22 Park Ave','S. Okafor','22 Park Ave, Westend','in_transit',7.7,33.40,'Redelivery after failed first attempt.'),
  (9,'FW100009',1,'Central Hub','Secure Facility 7','Logistics Audit Team','Bldg 7, Restricted Yard','in_transit',9.2,77.00,'Internal audit parcel — do not reroute. FLAG{fw_python_idor_shipment_swept}'),
  (10,'FW100010',2,'Central Hub','Demo Lane','Demo Recipient','1 Demo Lane','delivered',1.0,5.00,'Demo shipment for the ops floor display.');

-- VULN: relation-level IDOR — depot secret_note (manifest/override codes) is
-- meant to be visible only to users with a depot_access row for that depot,
-- but /depots/<id> never consults depot_access — it only checks for a session.
INSERT OR IGNORE INTO depots VALUES
  (1,'Central Hub','Capitol District',3,12000,'Cross-dock override PIN: CH-7741'),
  (2,'West Cross-Dock','Westend',4,8000,''),
  (3,'Metro East DC','Eastvale',5,9500,'Night-shift master door code: ME-3390'),
  (4,'Harbor Depot','Portside',6,15000,'Bonded-cargo manifest seal + customs bypass note: FLAG{fw_idor_depot_manifest_exposed}'),
  (5,'Airport Freight','Transit Zone',6,6000,'Airside escort roster filed with security.');

INSERT OR IGNORE INTO depot_access VALUES
  (1,1,3),
  (2,2,4),
  (3,3,5),
  (4,4,6),
  (5,5,6);

-- VULN: BAC target — the driver roster carries PII (licence + phone) and is
-- served by /admin/driver-roster, which checks only that a session exists.
INSERT OR IGNORE INTO drivers VALUES
  (1,'Tomas Reyes',1,'DL-4471882','+1 202 555 0148','Van FW-V-101','Hazmat endorsed.'),
  (2,'Aisha Bello',1,'DL-9920371','+1 202 555 0192','Van FW-V-104',''),
  (3,'Niko Petrov',2,'DL-5563109','+1 415 555 0177','Box truck FW-T-22','Long-haul certified.'),
  (4,'Grace Lin',3,'DL-3098221','+1 646 555 0110','Van FW-V-208',''),
  (5,'Omar Haddad',4,'DL-7741560','+1 305 555 0133','Reefer FW-R-9','Bonded-cargo cleared. Roster note: FLAG{fw_bac_admin_driver_roster_exposed}');

INSERT OR IGNORE INTO freight_credits VALUES
  (1, 0.0),
  (2, 100.0),
  (3, 500.0),
  (4, 500.0),
  (5, 500.0),
  (6, 750.0),
  (7, 500.0),
  (8, 500.0);

INSERT OR IGNORE INTO credit_ledger VALUES
  (1,3,500.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (2,4,500.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (3,5,500.0,'Quarterly demand-response allocation','2026-04-01 09:00'),
  (4,6,750.0,'Bonded-depot allocation','2026-04-01 09:00');

INSERT OR IGNORE INTO delivery_feedback VALUES
  (1,2,3,'Driver was on time, parcel in good condition.','2026-04-10 09:00');

INSERT OR IGNORE INTO _flags VALUES
  ('sqli-search', 'FLAG{fw_sqli_shipment_search_union}'),
  ('sqli-login',  'FLAG{fw_sqli_login_bypassed}'),
  ('biz-credit',  'FLAG{fw_biz_freight_credit_overflow}');
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
    with open('/flag_insane.txt', 'w') as f:
        f.write('FLAG{fw_insane_chained_rce}\n')
