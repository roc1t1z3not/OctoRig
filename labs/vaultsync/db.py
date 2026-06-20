# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
import sqlite3
from flask import g

DATABASE = '/data/vaultsync.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    email       TEXT NOT NULL,
    full_name   TEXT DEFAULT '',
    role        TEXT DEFAULT 'user',
    plan        TEXT DEFAULT 'free',
    is_admin    INTEGER DEFAULT 0,
    api_token   TEXT DEFAULT '',
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vaults (
    id          INTEGER PRIMARY KEY,
    owner_id    INTEGER NOT NULL,
    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS vault_items (
    id          INTEGER PRIMARY KEY,
    vault_id    INTEGER NOT NULL,
    title       TEXT NOT NULL,
    site_url    TEXT DEFAULT '',
    item_user   TEXT DEFAULT '',
    secret      TEXT DEFAULT '',
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS vault_shares (
    id          INTEGER PRIMARY KEY,
    vault_id    INTEGER NOT NULL,
    shared_with INTEGER NOT NULL,
    permission  TEXT DEFAULT 'read'
);

CREATE TABLE IF NOT EXISTS review_queue (
    id          INTEGER PRIMARY KEY,
    item_id     INTEGER NOT NULL,
    flagged_by  INTEGER NOT NULL,
    note        TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _flags (
    name  TEXT PRIMARY KEY,
    value TEXT
);

-- Passwords are stored as unsalted MD5 hashes (intentionally weak / crackable).
-- Plaintext reference (user : password):
--   admin:vault-master-2023  j.reyes:correct1   m.haddad:sunflower9
--   demo:demo                k.olsen:letmein22  t.kowalski:p@ssw0rd1
--   a.nakamura:rainbow7      s.brennan:dolphin5
INSERT OR IGNORE INTO users VALUES
  (1,'admin','1ce76475fb7673e985e1f32608b1b591','admin@vaultsync.local','VaultSync Admin','admin','enterprise',1,'vs-admin-9f3a7c1e8b','Recovery codes for the platform master key live behind /admin/recovery-codes.'),
  (2,'j.reyes','c9f4b2d4bf4e2ccf3ea2ff31b326faa0','jreyes@vaultsync.local','Jordan Reyes','user','premium',0,'vs-user-1a2b3c','Premium plan since 2024.'),
  (3,'m.haddad','24aa734961bafbc2c0d45e5ac4e997f7','mhaddad@vaultsync.local','Mona Haddad','user','free',0,'vs-user-4d5e6f',''),
  (4,'demo','fe01ce2a7fbac8fafaed7c982a04e229','demo@vaultsync.local','Demo User','user','free',0,'vs-user-demo01','Read-only demo account.'),
  (5,'k.olsen','2646b43413c1233f9b5d8073aabbbfee','kolsen@vaultsync.local','Kristin Olsen','user','free',0,'vs-user-7g8h9i',''),
  (6,'t.kowalski','350310b6de1650447ec723b1a5df8e96','tkowalski@vaultsync.local','Tomas Kowalski','user','premium',0,'vs-user-1j2k3l',''),
  (7,'a.nakamura','c42796b06c24276a184a9b819cb9aa92','anakamura@vaultsync.local','Aiko Nakamura','user','free',0,'vs-user-4m5n6o',''),
  (8,'s.brennan','0f57198f80b000a5fc7dd5285f38d1bb','sbrennan@vaultsync.local','Sean Brennan','user','free',0,'vs-user-7p8q9r','');

INSERT OR IGNORE INTO vaults VALUES
  (1,1,'Admin Infrastructure','2026-01-05 09:00'),
  (2,2,'Personal Logins','2026-02-11 14:20'),
  (3,3,'Work Accounts','2026-02-18 10:05'),
  (4,4,'Demo Vault','2026-03-01 08:00'),
  (5,5,'Personal Logins','2026-03-09 19:40'),
  (6,6,'Client Portals','2026-03-15 11:15'),
  (7,7,'Personal Logins','2026-03-22 16:50'),
  (8,8,'Shared Family Vault','2026-04-02 12:30');

-- VULN: notes column on vault_items is a free-text field with no ownership
-- check enforced on the item-detail route — any authenticated user can read
-- any item by guessing its sequential id.
INSERT OR IGNORE INTO vault_items VALUES
  (1,1,'Root Database','db.vaultsync.internal','root','Tr0ub4dor&3','Master DB credentials — rotate quarterly. FLAG{vs_idor_vault_item_exposed}'),
  (2,1,'AWS Root Account','aws.amazon.com','admin@vaultsync.local','S3cr3tAccessKey!','Root account — MFA enforced.'),
  (3,2,'Gmail','mail.google.com','j.reyes','rainydays22',''),
  (4,3,'Corp VPN','vpn.work.local','m.haddad','officeWifi!1',''),
  (5,4,'Example Login','example.com','demo','demo1234',''),
  (6,5,'Bank Portal','mybank.example','k.olsen','sav!ngs2024',''),
  (7,6,'Client Stripe','dashboard.stripe.com','t.kowalski','strp_l1ve_k3y',''),
  (8,7,'Netflix','netflix.com','a.nakamura','popcorn99',''),
  (9,8,'Family Photos Cloud','photos.example','s.brennan','memori3s!','Shared with j.reyes via vault_shares. FLAG{vs_idor_shared_vault_read}'),
  (10,6,'Internal Billing API','billing.vaultsync.internal','t.kowalski','b1ll1ngK3y!','Service account for the billing API. FLAG{vs_python_idor_vault_swept}'),
  -- VULN (intentional, by design): j.reyes reused their own VaultSync master
  -- password ('correct1') as their HumanBank login. This item is reachable
  -- through the same item-level IDOR as item id 1 above — it's simply the
  -- next sequential id. See vs-credential-reuse-pivot: the password only
  -- pays off if HumanBank (lab id 4, 172.28.4.0/24) is also running.
  (11,2,'HumanBank Online Banking','humanbank.local','j.reyes','correct1','Reused my VaultSync master password here too. Really should fix that.');

-- VULN: vault_shares grants explicit access, but the vault-detail route never
-- checks it — only checks "is this vault owned by *some* user", so any
-- logged-in user reaching /vaults/<id> directly bypasses the share gate.
INSERT OR IGNORE INTO vault_shares VALUES
  (1,8,2,'read');

INSERT OR IGNORE INTO review_queue VALUES
  (1,3,1,'Routine compliance check on work vault items.','2026-04-10 09:00');

INSERT OR IGNORE INTO _flags VALUES
  ('sqli-search', 'FLAG{vs_sqli_vault_search_union}'),
  ('sqli-login',  'FLAG{vs_sqli_login_bypassed}');
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
        f.write('FLAG{vs_insane_chained_rce}\n')
