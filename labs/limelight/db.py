# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import os
import sqlite3
from flask import g

DATABASE = '/data/limelight.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    email        TEXT NOT NULL,
    display_name TEXT DEFAULT '',
    is_admin     INTEGER DEFAULT 0,
    balance      REAL DEFAULT 0.0,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS movies (
    id           INTEGER PRIMARY KEY,
    title        TEXT NOT NULL,
    genre        TEXT NOT NULL,
    description  TEXT DEFAULT '',
    director     TEXT DEFAULT '',
    rating       TEXT DEFAULT 'PG',
    duration_min INTEGER DEFAULT 0,
    is_showing   INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS showings (
    id          INTEGER PRIMARY KEY,
    movie_id    INTEGER NOT NULL,
    hall        TEXT NOT NULL,
    show_time   TEXT NOT NULL,
    price       REAL NOT NULL,
    seats_total INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id                INTEGER PRIMARY KEY,
    user_id           INTEGER NOT NULL,
    showing_id        INTEGER NOT NULL,
    seat_labels       TEXT NOT NULL,
    total_price       REAL NOT NULL,
    created_at        TEXT NOT NULL,
    confirmation_code TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id         INTEGER PRIMARY KEY,
    movie_id   INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    rating     INTEGER NOT NULL,
    text       TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gift_cards (
    id          INTEGER PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,
    balance     REAL NOT NULL,
    redeemed_by INTEGER DEFAULT NULL
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@limelight.local','Cinema Admin',1,500.00,'2026-01-01 00:00:00'),
  (2,'john.doe','popcorn123','john@mail.example','John Doe',0,25.50,'2026-02-01 09:00:00'),
  (3,'sarah.k','movies4ever','sarah@mail.example','Sarah K',0,0.00,'2026-02-10 14:00:00'),
  (4,'tom.b','letmein99','tomb@mail.example','Tom B',0,50.00,'2026-03-01 08:00:00'),
  (5,'cinephile','reelgood1','cine@mail.example','The Cinephile',0,12.00,'2026-03-15 11:00:00'),
  (6,'commonhuman','commonhuman-lab','lab@commonhuman.local','CommonHuman',1,0.00,'2026-01-01 00:00:01');

INSERT OR IGNORE INTO movies VALUES
  (1,'Echoes of Tomorrow','Sci-Fi','A scientist discovers a way to receive messages from her future self — but each message changes the timeline in ways she cannot predict.','Elena Vasquez','12A',135,1),
  (2,'The Last Garden','Drama','In a near-future city where nature has all but disappeared, a groundskeeper tends the last living park and fights to keep it alive.','Marcus Bell','PG',118,1),
  (3,'Wraith Protocol','Action','An ex-intelligence operative uncovers a global surveillance network and must go off-grid to expose it before being silenced.','James Okafor','15',125,1),
  (4,'Hollow Crown','Horror','A family inherits a remote manor and slowly realises the previous occupants never truly left.','Nadia Bloom','18',102,1),
  (5,'Sundown Reef','Romance','Two marine biologists clash — and fall — while racing to document an endangered coral reef before a hotel development destroys it.','Priya Nair','PG',115,1),
  (6,'Iron Circuit','Action','A combat robot designed for peacekeeping goes rogue and its creator has 48 hours to shut it down.','David Chen','15',140,1),
  (7,'The CommonHuman Experiment','Mystery','No synopsis available. Screening status: unknown. Do not look further into this.','-','',0,1);

INSERT OR IGNORE INTO showings VALUES
  (1, 1,'Hall 1','2026-05-25 13:00',8.50,180),
  (2, 1,'Hall 1','2026-05-25 16:15',8.50,180),
  (3, 1,'Hall 2','2026-05-25 19:30',12.00,120),
  (4, 2,'Hall 3','2026-05-25 14:00',8.50,80),
  (5, 2,'Hall 3','2026-05-25 17:30',8.50,80),
  (6, 2,'Hall 2','2026-05-25 20:00',12.00,120),
  (7, 3,'Hall 1','2026-05-25 12:30',8.50,180),
  (8, 3,'Hall 1','2026-05-25 15:45',8.50,180),
  (9, 3,'Hall 2','2026-05-25 19:00',12.00,120),
  (10,4,'Hall 3','2026-05-25 13:30',8.50,80),
  (11,4,'Hall 3','2026-05-25 16:45',8.50,80),
  (12,4,'Hall 2','2026-05-25 21:00',12.00,120),
  (13,5,'Hall 2','2026-05-25 14:30',8.50,120),
  (14,5,'Hall 2','2026-05-25 17:00',8.50,120),
  (15,5,'Hall 3','2026-05-25 19:45',12.00,80),
  (16,6,'Hall 1','2026-05-25 11:00',8.50,180),
  (17,6,'Hall 1','2026-05-25 14:15',8.50,180),
  (18,6,'Hall 2','2026-05-25 18:00',12.00,120);

INSERT OR IGNORE INTO bookings VALUES
  (1,1,3, 'D7,D8',   24.00,'2026-05-22 10:00:00','LML-00001'),
  (2,2,4, 'B5',       8.50,'2026-05-22 11:30:00','LML-00002'),
  (3,3,7, 'A1,A2,A3',25.50,'2026-05-23 09:15:00','LML-00003'),
  (4,4,12,'E1,E2',   24.00,'2026-05-23 14:00:00','LML-00004'),
  (5,5,1, 'C3',       8.50,'2026-05-24 08:45:00','LML-00005');

INSERT OR IGNORE INTO reviews VALUES
  (1,1,2,5,'Absolutely stunning sci-fi. The timeline mechanics are mind-bending and the acting is superb. Highly recommend!','2026-05-23 12:00:00'),
  (2,1,3,4,'Great concept, slightly slow in the second act but the ending makes up for it.','2026-05-23 14:30:00'),
  (3,2,4,5,'A quiet, devastating film. Stayed with me for days.','2026-05-23 16:00:00'),
  (4,3,5,4,'Non-stop action with a surprisingly intelligent plot. Okafor is back in form.','2026-05-24 09:00:00'),
  (5,4,2,3,'Creepy atmosphere, a bit predictable. Worth watching at night.','2026-05-24 11:00:00'),
  (6,5,3,5,'Perfect date movie. Beautiful underwater cinematography.','2026-05-24 13:00:00'),
  (7,6,4,4,'Feels like a mix of Terminator and Ex Machina — in a good way.','2026-05-24 15:00:00'),
  (8,7,6,5,'You were not supposed to find this. But since you did — keep looking. The experiment is ongoing.','2026-01-01 00:00:01');

INSERT OR IGNORE INTO gift_cards VALUES
  (1,'WELCOME20',20.00,NULL),
  (2,'MOVIE10',10.00,NULL),
  (3,'SCREEN50',50.00,NULL),
  (4,'CMNH-SCREEN',1337.00,NULL);
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
