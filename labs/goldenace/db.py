import os
import sqlite3
from flask import g

DATABASE = '/data/goldenace.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY,
    username     TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL,
    email        TEXT NOT NULL,
    display_name TEXT DEFAULT '',
    balance      REAL DEFAULT 1000.0,
    is_admin     INTEGER DEFAULT 0,
    is_vip       INTEGER DEFAULT 0,
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    type        TEXT NOT NULL,
    amount      REAL NOT NULL,
    description TEXT DEFAULT '',
    game_type   TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS game_history (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    game_type   TEXT NOT NULL,
    bet         REAL NOT NULL,
    result      TEXT NOT NULL,
    payout      REAL NOT NULL,
    memo        TEXT DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    message    TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS promo_codes (
    id          INTEGER PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,
    value       REAL NOT NULL,
    description TEXT DEFAULT '',
    max_uses    INTEGER DEFAULT 1,
    uses_count  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS promo_redemptions (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    promo_id    INTEGER NOT NULL,
    redeemed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS live_feed (
    id         INTEGER PRIMARY KEY,
    message    TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used       INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@goldenace.local','Casino Admin',999999.0,1,1,'2026-01-01 00:00:00'),
  (2,'lucky_larry','sunshine1','larry@mail.example','Lucky Larry',48320.0,0,1,'2026-01-15 10:00:00'),
  (3,'high_roller','password1','highroller@mail.example','High Roller',98750.0,0,1,'2026-01-20 11:00:00'),
  (4,'jane.doe','iloveyou','jane@mail.example','Jane Doe',12500.0,0,0,'2026-02-01 09:00:00'),
  (5,'mike.b','letmein','mikeb@mail.example','Mike B',750.0,0,0,'2026-02-10 14:00:00'),
  (6,'poker_queen','baseball99','poker@mail.example','Poker Queen',31200.0,0,0,'2026-02-20 16:00:00'),
  (7,'chips_ahoy','monkey123','chips@mail.example','Chips Ahoy',7800.0,0,0,'2026-03-01 08:00:00'),
  (8,'novak.m','dragon99','novak@mail.example','Novak M',2100.0,0,0,'2026-03-10 12:00:00');

INSERT OR IGNORE INTO promo_codes VALUES
  (1,'WELCOME100',100.0,'Welcome bonus for new players',999,0),
  (2,'RELOAD50',50.0,'Weekly reload bonus',999,0),
  (3,'VIP200',200.0,'VIP players exclusive bonus',10,3),
  (4,'CMNH-LAB',1337.0,'Experimental. Handle with care.',1,0);

INSERT OR IGNORE INTO game_history VALUES
  (1, 2,'slots',    100.0,'win',  500.0,'','2026-05-20 09:10:00'),
  (2, 2,'roulette', 500.0,'win', 1000.0,'','2026-05-20 09:25:00'),
  (3, 2,'blackjack',200.0,'loss',   0.0,'','2026-05-20 10:00:00'),
  (4, 2,'dice',     150.0,'win',  300.0,'','2026-05-20 10:30:00'),
  (5, 2,'slots',    250.0,'loss',   0.0,'','2026-05-20 11:00:00'),
  (6, 3,'blackjack',1000.0,'win',2000.0,'big win','2026-05-20 09:00:00'),
  (7, 3,'roulette',2000.0,'loss',  0.0,'','2026-05-20 09:45:00'),
  (8, 3,'blackjack', 500.0,'win',1000.0,'','2026-05-20 10:15:00'),
  (9, 3,'slots',    300.0,'loss',   0.0,'','2026-05-20 11:30:00'),
  (10,3,'dice',     200.0,'win',  400.0,'','2026-05-20 12:00:00'),
  (11,4,'slots',     50.0,'win',  250.0,'','2026-05-20 10:00:00'),
  (12,4,'roulette', 100.0,'loss',   0.0,'','2026-05-20 10:40:00'),
  (13,4,'blackjack', 75.0,'push',  75.0,'','2026-05-20 11:10:00'),
  (14,4,'dice',      50.0,'loss',   0.0,'','2026-05-20 11:50:00'),
  (15,4,'slots',    100.0,'win',  200.0,'','2026-05-20 12:20:00'),
  (16,5,'slots',     25.0,'loss',   0.0,'','2026-05-21 08:00:00'),
  (17,5,'dice',      50.0,'loss',   0.0,'','2026-05-21 08:30:00'),
  (18,5,'blackjack', 25.0,'loss',   0.0,'','2026-05-21 09:00:00'),
  (19,5,'roulette',  25.0,'win',   50.0,'','2026-05-21 09:30:00'),
  (20,5,'slots',     50.0,'loss',   0.0,'','2026-05-21 10:00:00'),
  (21,6,'blackjack', 500.0,'win',1000.0,'','2026-05-21 09:00:00'),
  (22,6,'roulette',  300.0,'win', 600.0,'','2026-05-21 09:45:00'),
  (23,6,'slots',     200.0,'loss',  0.0,'','2026-05-21 10:30:00'),
  (24,6,'blackjack', 400.0,'win', 800.0,'','2026-05-21 11:00:00'),
  (25,6,'dice',      250.0,'loss',  0.0,'','2026-05-21 11:30:00'),
  (26,7,'slots',     100.0,'win', 300.0,'','2026-05-21 10:00:00'),
  (27,7,'roulette',  200.0,'loss',  0.0,'','2026-05-21 10:45:00'),
  (28,7,'dice',      100.0,'win', 200.0,'','2026-05-21 11:15:00'),
  (29,7,'blackjack', 150.0,'loss',  0.0,'','2026-05-21 12:00:00'),
  (30,7,'slots',      50.0,'loss',  0.0,'','2026-05-21 12:30:00'),
  (31,8,'slots',      50.0,'win', 150.0,'','2026-05-22 08:00:00'),
  (32,8,'dice',      100.0,'loss',  0.0,'','2026-05-22 08:30:00'),
  (33,8,'roulette',  200.0,'loss',  0.0,'','2026-05-22 09:00:00'),
  (34,8,'blackjack', 100.0,'win', 200.0,'','2026-05-22 09:30:00'),
  (35,8,'slots',      50.0,'loss',  0.0,'','2026-05-22 10:00:00'),
  (36,2,'blackjack', 800.0,'win',1600.0,'nice run','2026-05-22 08:00:00'),
  (37,3,'roulette', 1000.0,'win',2000.0,'straight bet on 7','2026-05-22 08:15:00'),
  (38,6,'blackjack', 600.0,'win',1200.0,'','2026-05-22 09:00:00'),
  (39,2,'dice',      200.0,'loss',   0.0,'','2026-05-22 09:45:00'),
  (40,3,'slots',     500.0,'win', 2500.0,'jackpot','2026-05-22 10:00:00');

INSERT OR IGNORE INTO transactions VALUES
  (1, 2,'win',  500.0,'Slots win','slots','2026-05-20 09:10:00'),
  (2, 2,'win', 1000.0,'Roulette win','roulette','2026-05-20 09:25:00'),
  (3, 2,'loss',-200.0,'Blackjack loss','blackjack','2026-05-20 10:00:00'),
  (4, 2,'win',  300.0,'Dice win','dice','2026-05-20 10:30:00'),
  (5, 2,'loss',-250.0,'Slots loss','slots','2026-05-20 11:00:00'),
  (6, 3,'win', 2000.0,'Blackjack win','blackjack','2026-05-20 09:00:00'),
  (7, 3,'loss',-2000.0,'Roulette loss','roulette','2026-05-20 09:45:00'),
  (8, 3,'win', 1000.0,'Blackjack win','blackjack','2026-05-20 10:15:00'),
  (9, 3,'win',  400.0,'Dice win','dice','2026-05-20 12:00:00'),
  (10,4,'win',  250.0,'Slots win','slots','2026-05-20 10:00:00'),
  (11,4,'loss',-100.0,'Roulette loss','roulette','2026-05-20 10:40:00'),
  (12,5,'loss',-100.0,'Lost streak','slots','2026-05-21 09:00:00'),
  (13,6,'win', 1000.0,'Blackjack win','blackjack','2026-05-21 09:00:00'),
  (14,6,'win',  600.0,'Roulette win','roulette','2026-05-21 09:45:00'),
  (15,6,'win',  800.0,'Blackjack win','blackjack','2026-05-21 11:00:00'),
  (16,7,'win',  300.0,'Slots win','slots','2026-05-21 10:00:00'),
  (17,7,'win',  200.0,'Dice win','dice','2026-05-21 11:15:00'),
  (18,8,'win',  150.0,'Slots win','slots','2026-05-22 08:00:00'),
  (19,8,'win',  200.0,'Blackjack win','blackjack','2026-05-22 09:30:00'),
  (20,2,'win', 1600.0,'Blackjack win','blackjack','2026-05-22 08:00:00');

INSERT OR IGNORE INTO chat_messages VALUES
  (1, 2,'just hit 3 sevens on slots, easy money','2026-05-22 09:10:00'),
  (2, 3,'roulette is rigged lol, lost 5k on red','2026-05-22 09:15:00'),
  (3, 4,'anyone know if there are bonus codes? heard there''s a new one','2026-05-22 09:20:00'),
  (4, 6,'double down on blackjack 11 every time, basic strategy','2026-05-22 09:25:00'),
  (5, 2,'the high roller suite is something else, wish more people knew about it','2026-05-22 09:30:00'),
  (6, 7,'lost my whole stack on dice, rip','2026-05-22 09:35:00'),
  (7, 3,'someone split aces and got two blackjacks at the same time, insane','2026-05-22 09:40:00'),
  (8, 8,'trying to grind back up from 2k, slow going','2026-05-22 09:45:00'),
  (9, 4,'what''s the payout on a straight bet in roulette?','2026-05-22 09:50:00'),
  (10,6,'35 to 1, and you will never hit it','2026-05-22 09:55:00'),
  (11,2,'lmao the admin has 999k balance, unfair advantage','2026-05-22 10:00:00'),
  (12,5,'down to my last 750, need a miracle','2026-05-22 10:05:00'),
  (13,3,'@poker_queen how are you keeping that blackjack streak going','2026-05-22 10:10:00'),
  (14,6,'card counting, obviously ;)','2026-05-22 10:15:00'),
  (15,7,'has anyone tried the cmnh-lab promo? wild value if it still works','2026-05-22 10:20:00');

INSERT OR IGNORE INTO live_feed VALUES
  (1, 'lucky_larry won $500.00 on slots!','2026-05-22 09:10:00'),
  (2, 'high_roller won $2,000.00 on blackjack!','2026-05-22 09:00:00'),
  (3, 'poker_queen won $1,000.00 on blackjack!','2026-05-22 09:45:00'),
  (4, 'chips_ahoy won $300.00 on slots!','2026-05-22 10:00:00'),
  (5, 'lucky_larry won $1,600.00 on blackjack!','2026-05-22 08:00:00'),
  (6, 'high_roller won $2,000.00 on roulette — straight bet on 7!','2026-05-22 08:15:00'),
  (7, 'poker_queen won $1,200.00 on blackjack!','2026-05-22 09:00:00'),
  (8, 'novak.m won $200.00 on blackjack!','2026-05-22 09:30:00'),
  (9, 'high_roller hit the jackpot — $2,500.00 on slots!','2026-05-22 10:00:00'),
  (10,'lucky_larry won $1,000.00 on roulette!','2026-05-22 09:25:00');
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
