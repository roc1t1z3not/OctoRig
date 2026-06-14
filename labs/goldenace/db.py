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
  (1, 'admin',        'commonhuman-lab','admin@goldenace.local',         'Casino Admin',    999999.0,1,1,'2026-01-01 00:00:00'),
  (2, 'lucky_larry',  'sunshine1',     'larry.simmons@mail.example',    'Larry Simmons',    48320.0,0,1,'2026-01-15 10:00:00'),
  (3, 'high_roller',  'password1',     'henry.roland@mail.example',     'Henry Roland',     98750.0,0,1,'2026-01-20 11:00:00'),
  (4, 'jane.doe',     'iloveyou',      'jane.doe@mail.example',         'Jane Doe',         12500.0,0,0,'2026-02-01 09:00:00'),
  (5, 'mike.b',       'letmein',       'michael.bauer@mail.example',    'Michael Bauer',      750.0,0,0,'2026-02-10 14:00:00'),
  (6, 'poker_queen',  'baseball99',    'christine.webb@mail.example',   'Christine Webb',   31200.0,0,0,'2026-02-20 16:00:00'),
  (7, 'chips_ahoy',   'monkey123',     'charles.hoy@mail.example',      'Charles Hoy',       7800.0,0,0,'2026-03-01 08:00:00'),
  (8, 'novak.m',      'dragon99',      'marco.novak@mail.example',      'Marco Novak',       2100.0,0,0,'2026-03-10 12:00:00'),
  (9, 'ace_diamond',  '3fc0a7acf087f549ac2b266baf94b8b1','james.carter@mail.example',     'James Carter',     55400.0,0,1,'2026-01-12 08:30:00'),
  (10,'red_velvet',   'e99a18c428cb38d5f260853678922e03','sophia.martinez@mail.example',  'Sophia Martinez',   3200.0,0,0,'2026-01-14 11:00:00'),
  (11,'cash_flow',    'eb0a191797624dd3a48fa681d3061212','derek.hughes@mail.example',     'Derek Hughes',     72800.0,0,1,'2026-01-16 09:15:00'),
  (12,'the_count',    '3bf1114a986ba87ed28fc1b5884fc2f8','victor.romano@mail.example',    'Victor Romano',     9100.0,0,0,'2026-01-18 14:00:00'),
  (13,'royal_flush',  '37b4e2d82900d5e94b8da524fbeb33c0','nathan.blake@mail.example',     'Nathan Blake',     61500.0,0,1,'2026-01-20 10:30:00'),
  (14,'bet_master',   'a906449d5769fa7361d7ecc6aa3f6d28','carlos.reyes@mail.example',     'Carlos Reyes',      4600.0,0,0,'2026-01-22 13:45:00'),
  (15,'gold_digger',  '8afa847f50a716e64932d995c8e7435a','amanda.collins@mail.example',   'Amanda Collins',    1850.0,0,0,'2026-01-25 15:00:00'),
  (16,'card_shark',   'e10adc3949ba59abbe56e057f20f883e','tyler.brooks@mail.example',     'Tyler Brooks',     14300.0,0,0,'2026-01-28 08:00:00'),
  (17,'roulette_rose','5f4dcc3b5aa765d61d8327deb882cf99','rachel.kim@mail.example',       'Rachel Kim',        8900.0,0,0,'2026-01-30 09:30:00'),
  (18,'jackpot_jim',  '25d55ad283aa400af464c76d713c07ad','james.donovan@mail.example',    'James Donovan',    43000.0,0,1,'2026-02-01 07:00:00'),
  (19,'bluff_king',   'fcea920f7412b5da7be0cf42b8c93759','marcus.webb@mail.example',      'Marcus Webb',       6700.0,0,0,'2026-02-03 10:00:00'),
  (20,'dealer_dan',   '0571749e2ac330a7455809c6b0e7af90','daniel.harper@mail.example',    'Daniel Harper',     2400.0,0,0,'2026-02-05 11:30:00'),
  (21,'full_house',   'd0763edaa9d9bd2a9516280e9044d885','kevin.nguyen@mail.example',     'Kevin Nguyen',      5300.0,0,0,'2026-02-07 12:00:00'),
  (22,'straight_flush','8621ffdbc5698829397d97767ac13db3','ryan.caldwell@mail.example',   'Ryan Caldwell',    11200.0,0,0,'2026-02-09 08:45:00'),
  (23,'wild_card',    'ec0e2603172c73a8b644bb9456c1ff6e','brett.morrison@mail.example',   'Brett Morrison',    3800.0,0,0,'2026-02-11 14:15:00'),
  (24,'aces_high',    '84d961568a65073a3bcf0eb216b2a576','scott.ferguson@mail.example',   'Scott Ferguson',    7100.0,0,0,'2026-02-13 09:00:00'),
  (25,'black_jack99', 'd8578edf8458ce06fbc5bb76a58c5ca4','jason.lee@mail.example',        'Jason Lee',          900.0,0,0,'2026-02-15 10:30:00'),
  (26,'spin_doctor',  '96e79218965eb72c92a549dd5a330112','ethan.price@mail.example',      'Ethan Price',        500.0,0,0,'2026-02-17 13:00:00'),
  (27,'double_down',  '276f8db0b86edaa7fc805516c852c889','michael.torres@mail.example',   'Michael Torres',   16400.0,0,1,'2026-02-19 07:30:00'),
  (28,'bust_boy',     'da443a0ad979d5530df38ca1a74e4f80','liam.porter@mail.example',      'Liam Porter',       1200.0,0,0,'2026-02-21 11:00:00'),
  (29,'all_in_alice', 'ad92694923612da0600d7be498cc2e08','alice.fitzgerald@mail.example', 'Alice Fitzgerald',  4050.0,0,0,'2026-02-23 09:45:00'),
  (30,'shuffle_sam',  '5badcaf789d3d1d09794d8f021f40f0e','samuel.grant@mail.example',     'Samuel Grant',      3300.0,0,0,'2026-02-25 14:30:00'),
  (31,'neon_gambler', '0acf4539a14b3aa27deeb4cbdf6e989f','nate.gibson@mail.example',      'Nate Gibson',       8600.0,0,0,'2026-02-27 08:00:00'),
  (32,'casino_kid',   '6b1b36cbb04b41490bfc0ab2bfa26f86','chris.walsh@mail.example',      'Chris Walsh',       2900.0,0,0,'2026-03-01 10:00:00'),
  (33,'big_spender',  '40be4e59b9a2a2b5dffb918c0e86b3d7','robert.sinclair@mail.example',  'Robert Sinclair',  19700.0,0,1,'2026-03-03 12:00:00'),
  (34,'lucky_seven',  '5fcfd41e547a12215b173ff47fdd3739','thomas.reed@mail.example',      'Thomas Reed',       5500.0,0,0,'2026-03-05 07:45:00'),
  (35,'poker_pete',   'c378985d629e99a4e86213db0cd5e70d','peter.sullivan@mail.example',   'Peter Sullivan',    7200.0,0,0,'2026-03-07 09:15:00'),
  (36,'chip_stack',   'df0349ce110b69f03b4def8012ae4970','andrew.barnes@mail.example',    'Andrew Barnes',     3100.0,0,0,'2026-03-09 11:30:00'),
  (37,'night_rider',  'bee783ee2974595487357e195ef38ca2','patrick.lynch@mail.example',    'Patrick Lynch',     6400.0,0,0,'2026-03-11 08:30:00'),
  (38,'midnight_bet', 'ef6e65efc188e7dffd7335b646a85a21','sean.murphy@mail.example',      'Sean Murphy',       1700.0,0,0,'2026-03-13 13:00:00'),
  (39,'velvet_rick',  'bf779e0933a882808585d19455cd7937','richard.vega@mail.example',     'Richard Vega',      4300.0,0,0,'2026-03-15 10:15:00'),
  (40,'dark_horse',   'aae039d6aa239cfc121357a825210fa3','david.coleman@mail.example',    'David Coleman',     2600.0,0,0,'2026-03-17 14:45:00'),
  (41,'silver_tongue','aa47f8215c6f30a0dcdb2a36a9f4168e','steven.archer@mail.example',   'Steven Archer',     8800.0,0,0,'2026-03-19 09:00:00'),
  (42,'golden_gate',  '1d3d37667a8d7eb02054c6afdf9e2e1c','gary.hammond@mail.example',     'Gary Hammond',      5000.0,0,0,'2026-03-21 11:00:00'),
  (43,'jackpot_jade', 'ef4cdd3117793b9fd593d7488409626d','jade.fischer@mail.example',     'Jade Fischer',     13100.0,0,1,'2026-03-23 08:00:00'),
  (44,'flush_queen',  '4297f44b13955235245b2497399d7a93','lauren.page@mail.example',      'Lauren Page',       3700.0,0,0,'2026-03-25 10:30:00'),
  (45,'aces_wild',    'f379eaf3c831b04de153469d1bec345e','ashley.bowen@mail.example',     'Ashley Bowen',      1450.0,0,0,'2026-03-27 12:45:00'),
  (46,'pocket_kings', '482c811da5d5b4bc6d497ffa98491e38','kyle.preston@mail.example',     'Kyle Preston',      9500.0,0,0,'2026-03-29 07:00:00'),
  (47,'river_card',   '7d0710824ff191f6a0086a7e3891641e','brandon.shaw@mail.example',     'Brandon Shaw',      6200.0,0,0,'2026-03-31 09:30:00'),
  (48,'high_hand',    '5c7686c0284e0875b26de99c1008e998','hunter.ellis@mail.example',     'Hunter Ellis',      4800.0,0,0,'2026-04-02 11:00:00'),
  (49,'blind_bet',    '43b90920409618f188bfc6923f16b9fa','blake.mitchell@mail.example',   'Blake Mitchell',    2300.0,0,0,'2026-04-04 08:15:00'),
  (50,'raise_it',     'd8d3a01ba7e5d44394b6f0a8533f4647','josh.lawson@mail.example',      'Josh Lawson',       1100.0,0,0,'2026-04-06 13:30:00'),
  (51,'double_ace',   '2dccd1ab3e03990aea77359831c85ca2','dean.crawford@mail.example',    'Dean Crawford',     3600.0,0,0,'2026-04-08 10:00:00'),
  (52,'big_blind',    'd5c0607301ad5d5c1528962a83992ac8','brian.owens@mail.example',      'Brian Owens',       7800.0,0,0,'2026-04-10 08:45:00'),
  (53,'chip_leader',  '7c6a180b36896a0a8c02787eeafb0e4c','chris.hoffman@mail.example',    'Chris Hoffman',    35000.0,0,1,'2026-04-12 09:00:00'),
  (54,'fold_master',  'f25a2fc72690b780b2a14e140ef6a9e0','frank.kelley@mail.example',     'Frank Kelley',      2100.0,0,0,'2026-04-14 11:15:00'),
  (55,'blaze_runner', '0d107d09f5bbe40cade3de5c71e9e9b7','ben.ramsey@mail.example',       'Ben Ramsey',        4400.0,0,0,'2026-04-16 07:30:00'),
  (56,'stack_master', 'e65c8afc9951f94fed8873a4c1e31a63','steve.walton@mail.example',     'Steve Walton',      6600.0,0,0,'2026-04-18 10:00:00'),
  (57,'card_counter', 'cc25c0f861a83f5efadc6e1ba9d1269e','carl.newton@mail.example',      'Carl Newton',       1900.0,0,0,'2026-04-20 12:30:00'),
  (58,'nightly_grind','b696aef7776367787253dc2acdd10279','nick.greer@mail.example',       'Nick Greer',        3800.0,0,0,'2026-04-22 09:00:00');

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

CREATE TABLE IF NOT EXISTS _flags (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO _flags VALUES
  (1, 'sqli-promo',       'FLAG{ga_promo_sqli_union}'),
  (2, 'sqli-leaderboard', 'FLAG{ga_leaderboard_sqli_union}');

INSERT OR IGNORE INTO game_history VALUES
  (41,1,'slots',0.0,'win',0.0,'FLAG{ga_idor_suite_exposed}','2026-01-01 00:01:00');

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
