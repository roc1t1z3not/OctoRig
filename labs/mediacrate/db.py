# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
import sqlite3
from flask import g

DATABASE = '/data/mediacrate.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    email       TEXT NOT NULL,
    full_name   TEXT DEFAULT '',
    role        TEXT DEFAULT 'user',
    is_admin    INTEGER DEFAULT 0,
    api_token   TEXT DEFAULT '',
    bio         TEXT DEFAULT '',
    coins       INTEGER DEFAULT 500
);

CREATE TABLE IF NOT EXISTS channels (
    id                   INTEGER PRIMARY KEY,
    owner_id             INTEGER NOT NULL,
    name                 TEXT NOT NULL,
    description          TEXT DEFAULT '',
    subscriber_count     INTEGER DEFAULT 0,
    is_verified          INTEGER DEFAULT 0,
    exclusive_content     TEXT DEFAULT '',
    coin_balance         INTEGER DEFAULT 0,
    banner_path          TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS videos (
    id          INTEGER PRIMARY KEY,
    channel_id  INTEGER NOT NULL,
    title       TEXT NOT NULL,
    description TEXT DEFAULT '',
    visibility  TEXT DEFAULT 'public',
    views       INTEGER DEFAULT 0,
    upload_date TEXT NOT NULL,
    notes       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS streams (
    id          INTEGER PRIMARY KEY,
    channel_id  INTEGER NOT NULL,
    title       TEXT NOT NULL,
    is_live     INTEGER DEFAULT 0,
    started_at  TEXT NOT NULL,
    stream_key  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id            INTEGER PRIMARY KEY,
    channel_id    INTEGER NOT NULL,
    subscriber_id INTEGER NOT NULL,
    tier          INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS comment_reports (
    id          INTEGER PRIMARY KEY,
    video_id    INTEGER NOT NULL,
    reported_by INTEGER NOT NULL,
    note        TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS _flags (
    name  TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    id          INTEGER PRIMARY KEY,
    video_id    INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    body        TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    kind        TEXT NOT NULL,
    body        TEXT NOT NULL,
    is_read     INTEGER DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS playlists (
    id          INTEGER PRIMARY KEY,
    owner_id    INTEGER NOT NULL,
    name        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS playlist_items (
    id            INTEGER PRIMARY KEY,
    playlist_id   INTEGER NOT NULL,
    video_id      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS tips (
    id          INTEGER PRIMARY KEY,
    channel_id  INTEGER NOT NULL,
    tipper_id   INTEGER NOT NULL,
    amount      INTEGER NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stream_chat (
    id          INTEGER PRIMARY KEY,
    stream_id   INTEGER NOT NULL,
    display_name TEXT NOT NULL,
    message     TEXT NOT NULL
);

-- Passwords are stored as unsalted MD5 hashes (intentionally weak / crackable).
-- Plaintext reference (user : password):
--   admin:create2026     demo:demo            nova.lee:popcorn21
--   theo.park:letmein9   mira.santos:sunsetwave   kenji.ito:tokyo2024
--   priya.rao:masala007  owen.fitz:fitzy55
INSERT OR IGNORE INTO users VALUES
  (1,'admin','a82b7eef403a975673f6d50f1d35446e','admin@mediacrate.local','MediaCrate Admin','admin',1,'mc-admin-7f2e9b1a','Platform operations.',2000),
  (2,'demo','fe01ce2a7fbac8fafaed7c982a04e229','demo@mediacrate.local','Demo Viewer','user',0,'mc-user-demo01','Just here to watch.',500),
  (3,'nova.lee','a27cf0aae011db129351209b24d23bb5','nova@mediacrate.local','Nova Lee','user',0,'mc-user-1a2b3c','Gaming + vlogs. Streaming most nights.',500),
  (4,'theo.park','321cdb03a667fbf008d2e8596410d801','theo@mediacrate.local','Theo Park','user',0,'mc-user-4d5e6f','Cooking channel.',500),
  (5,'mira.santos','87eead70aa653391b351c8588b6a837c','mira@mediacrate.local','Mira Santos','user',0,'mc-user-7g8h9i','Music covers and live sets.',500),
  (6,'kenji.ito','c52172481d91be3a612ec2e7814d3fdf','kenji@mediacrate.local','Kenji Ito','user',0,'mc-user-1j2k3l','Tech reviews.',500),
  (7,'priya.rao','fafda9c4622b8323c1f33a7b9eb975a2','priya@mediacrate.local','Priya Rao','user',0,'mc-user-4m5n6o','Travel + food.',500),
  (8,'owen.fitz','9f14c57d3d12b1b4fc108a9b1bd1d04f','owen@mediacrate.local','Owen Fitzgerald','user',0,'mc-user-7p8q9r','Fitness streams.',500);

INSERT OR IGNORE INTO channels VALUES
  (1,1,'MediaCrate Ops','Official platform announcements and operations.',1200,1,'',0,''),
  (2,3,'Nova Plays','Gaming highlights and full VODs.',48200,1,'',0,''),
  (3,4,'Theo Cooks','Weeknight recipes and pantry tips.',9100,0,'',0,''),
  -- VULN: relation-level IDOR target — the subscriber tier-2 perk text below
  -- is only meant to be readable by someone with a tier>=2 row in
  -- subscriptions, but the /channels/<id>/exclusive route never checks
  -- that table — it only checks that *some* session exists.
  (4,5,'Mira Sessions','Music covers, acoustic sets, and live shows.',15300,0,'Tier 2 perk unlock code for this month''s livestream: FLAG{mc_idor_subscriber_content_exposed}',0,''),
  (5,6,'Kenji Reviews','Hands-on tech reviews and teardown.',6700,0,'',0,''),
  (6,7,'Priya Roams','Travel vlogs and street food crawls.',22800,1,'',0,''),
  (7,8,'Fitz Fitness','Daily workout streams.',3400,0,'',0,''),
  (8,2,'Demo Channel','Demo account test uploads.',5,0,'',0,'');

-- VULN: item-level IDOR — visibility is enforced only in the UI, never on
-- the /videos/<id> route itself, so unlisted/private videos are reachable
-- by anyone who knows (or guesses) the sequential id.
INSERT OR IGNORE INTO videos VALUES
  (1,1,'Q3 Platform Roadmap (internal draft)','Draft roadmap, not for public release yet.','private',0,'2026-01-05','Internal draft — embargo lifts next quarter. FLAG{mc_idor_video_exposed}'),
  (2,2,'Speedrun World Record Attempt','Full VOD of the run.','public',184213,'2026-02-11',''),
  (3,2,'Behind the scenes (unlisted draft)','Raw footage, not edited yet.','unlisted',12,'2026-02-12','Editor notes: cut the first ten minutes before publishing.'),
  (4,3,'Sunday Pasta, Three Ways','Recipe walkthrough.','public',5320,'2026-02-18',''),
  (5,4,'Acoustic Set — Live from the Studio','Full setlist in the description.','public',8841,'2026-03-01',''),
  (6,5,'Teardown: Budget Earbuds','Is it worth it?','public',15990,'2026-03-09',''),
  (7,6,'Street Food Crawl — Bangkok','Day 1 of 5.','public',31022,'2026-03-15',''),
  (8,7,'Full Body Day 12','Daily streak continues.','public',900,'2026-03-22',''),
  -- VULN (python challenge target): another unlisted video, reachable the
  -- same way but exposed over the JSON API for the scripting challenge.
  (9,5,'Unreleased Demo Track','Scratch take, not mixed yet.','unlisted',3,'2026-04-02','Scratch vocal take — flag in case anyone finds this early: FLAG{mc_python_idor_video_swept}'),
  (10,8,'Demo Upload Test','Test video.','public',1,'2026-04-05',''),
  -- VULN (cross-lab pivot): another item-level IDOR target — no new bug,
  -- just keep enumerating past id 10. The notes field is a personal aside
  -- that leaks a password reused on Limelight (id=7, slug=limelight).
  (11,2,'Unlisted vlog — late night thoughts','Just rambling, don''t link this anywhere.','unlisted',7,'2026-05-30','Reminder to self: stop reusing nova.lee / Popcorn21! for everything — used it on MediaCrate AND my Limelight bookings account. Need to fix that.');

INSERT OR IGNORE INTO streams VALUES
  (1,2,'Late Night Ranked Grind',1,'2026-06-19 22:00','sk_live_nova_8f3a1c'),
  (2,4,'Sunday Live Set',0,'2026-06-15 18:00','sk_live_mira_2b7d9e'),
  (3,5,'Unboxing Livestream',0,'2026-06-10 14:00','sk_live_kenji_4c1f8a');

INSERT OR IGNORE INTO subscriptions VALUES
  (1,2,2,1),
  (2,3,2,1);

INSERT OR IGNORE INTO comment_reports VALUES
  (1,4,2,'Routine moderation pass on the recipe comments.','2026-04-10 09:00');

INSERT OR IGNORE INTO comments VALUES
  (1,2,2,'That last-second clutch was unreal, GG!','2026-02-12 08:00'),
  (2,2,4,'How did you not panic at 1hp lol','2026-02-12 09:15'),
  (3,4,3,'Recipe came out great, thanks for the tip on the sauce.','2026-02-19 18:30'),
  (4,5,2,'This acoustic version is so much better than the studio cut.','2026-03-02 10:05');

INSERT OR IGNORE INTO notifications VALUES
  (1,3,'subscriber','theo.park just subscribed to Nova Plays.',0,'2026-06-18 12:00'),
  (2,3,'stream_live','Your stream "Late Night Ranked Grind" is now live.',0,'2026-06-19 22:00'),
  (3,2,'reply','mira.santos replied to your comment.',1,'2026-03-03 09:00');

INSERT OR IGNORE INTO playlists VALUES
  (1,2,'Watch Later');

INSERT OR IGNORE INTO playlist_items VALUES
  (1,1,2),
  (2,1,6);

INSERT OR IGNORE INTO tips VALUES
  (1,2,2,50,'2026-03-01 12:00');

INSERT OR IGNORE INTO stream_chat VALUES
  (1,1,'viewer482','first!! love the grind streams'),
  (2,1,'nova.lee','thanks for hanging out everyone'),
  (3,1,'gg_ez22','that ranked queue is brutal tonight');

INSERT OR IGNORE INTO _flags VALUES
  ('sqli-search', 'FLAG{mc_sqli_search_videos_union}'),
  ('sqli-login',  'FLAG{mc_sqli_login_bypassed}');
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
        f.write('FLAG{mc_insane_chained_rce}\n')
