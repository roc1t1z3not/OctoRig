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

CREATE TABLE IF NOT EXISTS _flags (
    id    INTEGER PRIMARY KEY,
    name  TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);
INSERT OR IGNORE INTO _flags VALUES
  (1, 'sqli-search',  'FLAG{ll_search_sqli_union}'),
  (2, 'sqli-gift',    'FLAG{ll_gift_sqli_bypass}'),
  (3, 'sqli-reviews', 'FLAG{ll_api_path_injection}');

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
  (1,1,3, 'D7,D8',   24.00,'2026-05-22 10:00:00','FLAG{ll_idor_booking_leaked}'),
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
  (4,'CMNH-SCREEN',1337.00,NULL),
  (5,'FILM25',      25.00,NULL),
  (6,'NIGHT15',     15.00,7),
  (7,'PREMIER30',   30.00,12),
  (8,'POPCORN5',     5.00,NULL);

INSERT OR IGNORE INTO users VALUES
  (7, 'grace.johnson',  '3fc0a7acf087f549ac2b266baf94b8b1','grace.johnson@mail.example',  'Grace Johnson',    0, 45.00,'2026-01-15 09:00:00'),
  (8, 'henry.w',        'e99a18c428cb38d5f260853678922e03','henry.w@mail.example',        'Henry Williams',   0,  0.00,'2026-01-18 10:30:00'),
  (9, 'isabella.b',     'eb0a191797624dd3a48fa681d3061212','isabella.b@mail.example',     'Isabella Brown',   0, 22.50,'2026-01-22 14:00:00'),
  (10,'james.d',        '3bf1114a986ba87ed28fc1b5884fc2f8','james.d@mail.example',        'James Davis',      0,  8.50,'2026-01-25 11:00:00'),
  (11,'karen.miller',   '37b4e2d82900d5e94b8da524fbeb33c0','karen.miller@mail.example',   'Karen Miller',     0, 60.00,'2026-01-28 16:00:00'),
  (12,'liam.wilson',    'a906449d5769fa7361d7ecc6aa3f6d28','liam.wilson@mail.example',    'Liam Wilson',      0,  0.00,'2026-02-01 08:00:00'),
  (13,'mia.moore',      '8afa847f50a716e64932d995c8e7435a','mia.moore@mail.example',      'Mia Moore',        0, 34.00,'2026-02-04 13:00:00'),
  (14,'noah.taylor',    'e10adc3949ba59abbe56e057f20f883e','noah.taylor@mail.example',    'Noah Taylor',      0, 17.00,'2026-02-07 09:00:00'),
  (15,'olivia.a',       '5f4dcc3b5aa765d61d8327deb882cf99','olivia.a@mail.example',       'Olivia Anderson',  0,  0.00,'2026-02-10 15:00:00'),
  (16,'peter.thomas',   '25d55ad283aa400af464c76d713c07ad','peter.thomas@mail.example',   'Peter Thomas',     0, 85.50,'2026-02-13 10:00:00'),
  (17,'quinn.j',        'fcea920f7412b5da7be0cf42b8c93759','quinn.j@mail.example',        'Quinn Jackson',    0, 12.00,'2026-02-16 12:00:00'),
  (18,'rachel.white',   '0571749e2ac330a7455809c6b0e7af90','rachel.white@mail.example',   'Rachel White',     0,  0.00,'2026-02-19 08:30:00'),
  (19,'samuel.h',       'd0763edaa9d9bd2a9516280e9044d885','samuel.h@mail.example',       'Samuel Harris',    0, 25.50,'2026-02-22 14:30:00'),
  (20,'tina.m',         '8621ffdbc5698829397d97767ac13db3','tina.m@mail.example',         'Tina Martin',      0, 50.00,'2026-02-25 11:00:00'),
  (21,'ursula.g',       'ec0e2603172c73a8b644bb9456c1ff6e','ursula.g@mail.example',       'Ursula Garcia',    0,  0.00,'2026-02-28 09:00:00'),
  (22,'victor.m',       '84d961568a65073a3bcf0eb216b2a576','victor.m@mail.example',       'Victor Martinez',  0, 34.00,'2026-03-03 16:00:00'),
  (23,'wendy.r',        'd8578edf8458ce06fbc5bb76a58c5ca4','wendy.r@mail.example',        'Wendy Robinson',   0, 17.00,'2026-03-06 10:00:00'),
  (24,'xavier.c',       '96e79218965eb72c92a549dd5a330112','xavier.c@mail.example',       'Xavier Clark',     0,  0.00,'2026-03-09 13:00:00'),
  (25,'yolanda.r',      '276f8db0b86edaa7fc805516c852c889','yolanda.r@mail.example',      'Yolanda Rodriguez',0,  8.50,'2026-03-12 09:30:00'),
  (26,'zachary.l',      'da443a0ad979d5530df38ca1a74e4f80','zachary.l@mail.example',      'Zachary Lewis',    0, 24.00,'2026-03-15 11:00:00'),
  (27,'amber.lee',      'ad92694923612da0600d7be498cc2e08','amber.lee@mail.example',      'Amber Lee',        0,  0.00,'2026-03-18 14:00:00'),
  (28,'brandon.w',      '5badcaf789d3d1d09794d8f021f40f0e','brandon.w@mail.example',      'Brandon Walker',   0, 42.00,'2026-03-21 10:00:00'),
  (29,'chloe.h',        '0acf4539a14b3aa27deeb4cbdf6e989f','chloe.h@mail.example',        'Chloe Hall',       0, 17.00,'2026-03-24 15:00:00'),
  (30,'dylan.a',        '6b1b36cbb04b41490bfc0ab2bfa26f86','dylan.a@mail.example',        'Dylan Allen',      0,  0.00,'2026-03-27 08:00:00'),
  (31,'emma.y',         '40be4e59b9a2a2b5dffb918c0e86b3d7','emma.y@mail.example',         'Emma Young',       0, 36.00,'2026-03-30 13:00:00'),
  (32,'felix.h',        '5fcfd41e547a12215b173ff47fdd3739','felix.h@mail.example',        'Felix Hernandez',  0,  8.50,'2026-04-02 10:00:00'),
  (33,'georgia.k',      'c378985d629e99a4e86213db0cd5e70d','georgia.k@mail.example',      'Georgia King',     0,  0.00,'2026-04-05 14:00:00'),
  (34,'hunter.w',       'df0349ce110b69f03b4def8012ae4970','hunter.w@mail.example',       'Hunter Wright',    0, 60.00,'2026-04-08 09:00:00'),
  (35,'iris.l',         'bee783ee2974595487357e195ef38ca2','iris.l@mail.example',         'Iris Lopez',       0, 12.00,'2026-04-11 11:00:00'),
  (36,'jason.h',        'ef6e65efc188e7dffd7335b646a85a21','jason.h@mail.example',        'Jason Hill',       0,  0.00,'2026-04-14 15:30:00'),
  (37,'kelly.s',        'bf779e0933a882808585d19455cd7937','kelly.s@mail.example',        'Kelly Scott',      0, 25.50,'2026-04-17 10:00:00'),
  (38,'lucas.g',        'aae039d6aa239cfc121357a825210fa3','lucas.g@mail.example',        'Lucas Green',      0, 17.00,'2026-04-20 13:00:00'),
  (39,'maya.a',         'aa47f8215c6f30a0dcdb2a36a9f4168e','maya.a@mail.example',         'Maya Adams',       0,  0.00,'2026-04-23 09:00:00'),
  (40,'nathan.b',       '1d3d37667a8d7eb02054c6afdf9e2e1c','nathan.b@mail.example',       'Nathan Baker',     0, 34.00,'2026-04-26 14:00:00'),
  (41,'nora.g',         'ef4cdd3117793b9fd593d7488409626d','nora.g@mail.example',         'Nora Gonzalez',    0,  8.50,'2026-04-29 11:00:00'),
  (42,'oscar.n',        '4297f44b13955235245b2497399d7a93','oscar.n@mail.example',        'Oscar Nelson',     0,  0.00,'2026-05-01 10:00:00'),
  (43,'paula.c',        'f379eaf3c831b04de153469d1bec345e','paula.c@mail.example',        'Paula Carter',     0, 50.00,'2026-05-03 09:00:00'),
  (44,'ryan.m',         '482c811da5d5b4bc6d497ffa98491e38','ryan.m@mail.example',         'Ryan Mitchell',    0, 12.00,'2026-05-05 14:00:00'),
  (45,'sarah.p',        '7d0710824ff191f6a0086a7e3891641e','sarah.p@mail.example',        'Sarah Perez',      0,  0.00,'2026-05-07 11:00:00'),
  (46,'tyler.r',        '5c7686c0284e0875b26de99c1008e998','tyler.r@mail.example',        'Tyler Roberts',    0, 85.50,'2026-05-09 09:30:00'),
  (47,'uma.t',          '43b90920409618f188bfc6923f16b9fa','uma.t@mail.example',          'Uma Turner',       0, 17.00,'2026-05-11 10:00:00'),
  (48,'vincent.p',      'd8d3a01ba7e5d44394b6f0a8533f4647','vincent.p@mail.example',      'Vincent Phillips', 0,  0.00,'2026-05-12 13:00:00'),
  (49,'walter.c',       '2dccd1ab3e03990aea77359831c85ca2','walter.c@mail.example',       'Walter Campbell',  0, 24.00,'2026-05-13 09:00:00'),
  (50,'xena.p',         'd5c0607301ad5d5c1528962a83992ac8','xena.p@mail.example',         'Xena Parker',      0,  0.00,'2026-05-14 10:00:00'),
  (51,'yasmine.e',      '7c6a180b36896a0a8c02787eeafb0e4c','yasmine.e@mail.example',      'Yasmine Evans',    0, 36.00,'2026-05-14 11:00:00'),
  (52,'zoe.e',          'f25a2fc72690b780b2a14e140ef6a9e0','zoe.e@mail.example',          'Zoe Edwards',      0,  8.50,'2026-05-14 12:00:00'),
  (53,'alan.c',         '0d107d09f5bbe40cade3de5c71e9e9b7','alan.c@mail.example',         'Alan Collins',     0,  0.00,'2026-05-14 13:00:00'),
  (54,'barbara.s',      'e65c8afc9951f94fed8873a4c1e31a63','barbara.s@mail.example',      'Barbara Stewart',  0, 42.00,'2026-05-14 14:00:00'),
  (55,'carl.s',         'cc25c0f861a83f5efadc6e1ba9d1269e','carl.s@mail.example',         'Carl Sanchez',     0, 17.00,'2026-05-14 15:00:00'),
  (56,'diane.m',        'b696aef7776367787253dc2acdd10279','diane.m@mail.example',        'Diane Morris',     0,  0.00,'2026-05-14 16:00:00');

INSERT OR IGNORE INTO bookings VALUES
  (6, 7, 1,'C5,C6',    17.00,'2026-05-22 12:00:00','LML-00006'),
  (7, 8, 6,'E1',       12.00,'2026-05-22 13:30:00','LML-00007'),
  (8, 9, 9,'B2,B3',    24.00,'2026-05-22 14:00:00','LML-00008'),
  (9,10,11,'A4',         8.50,'2026-05-22 15:00:00','LML-00009'),
  (10,11,14,'D1,D2',   17.00,'2026-05-23 08:00:00','LML-00010'),
  (11,12,17,'F3,F4,F5',25.50,'2026-05-23 09:30:00','LML-00011'),
  (12,13, 3,'G1',       12.00,'2026-05-23 10:00:00','LML-00012'),
  (13,14, 5,'H2,H3',   17.00,'2026-05-23 11:00:00','LML-00013'),
  (14,15, 8,'B1',        8.50,'2026-05-23 12:00:00','LML-00014'),
  (15,16,12,'C7,C8',   24.00,'2026-05-23 13:00:00','LML-00015'),
  (16,17,15,'A5,A6',   24.00,'2026-05-23 14:00:00','LML-00016'),
  (17,18, 2,'D4,D5',   17.00,'2026-05-23 15:00:00','LML-00017'),
  (18,19, 7,'E3',        8.50,'2026-05-23 16:00:00','LML-00018'),
  (19,20,10,'B8,B9',   17.00,'2026-05-23 17:00:00','LML-00019'),
  (20,21,13,'F1,F2',   17.00,'2026-05-23 18:00:00','LML-00020'),
  (21,22,16,'G6,G7',   17.00,'2026-05-24 09:00:00','LML-00021'),
  (22,23, 4,'C2,C3,C4',25.50,'2026-05-24 10:00:00','LML-00022'),
  (23,24,18,'D6',       12.00,'2026-05-24 11:00:00','LML-00023'),
  (24,25, 1,'A9,A10',  17.00,'2026-05-24 12:00:00','LML-00024'),
  (25,26, 6,'B11',      12.00,'2026-05-24 13:00:00','LML-00025'),
  (26,27, 9,'C1,C2',   24.00,'2026-05-24 14:00:00','LML-00026'),
  (27,28,11,'D3',        8.50,'2026-05-24 15:00:00','LML-00027'),
  (28,29,14,'E5,E6',   17.00,'2026-05-24 16:00:00','LML-00028'),
  (29,30,17,'F8,F9',   17.00,'2026-05-24 17:00:00','LML-00029'),
  (30,31, 3,'G3,G4',   24.00,'2026-05-24 18:00:00','LML-00030'),
  (31,32, 5,'H7',        8.50,'2026-05-25 09:00:00','LML-00031'),
  (32,33, 8,'A3,A4',   17.00,'2026-05-25 10:00:00','LML-00032'),
  (33,34,12,'B6,B7',   24.00,'2026-05-25 11:00:00','LML-00033'),
  (34,35,15,'C9',       12.00,'2026-05-25 12:00:00','LML-00034'),
  (35,36,18,'D1,D2,D3',36.00,'2026-05-25 13:00:00','LML-00035');

INSERT OR IGNORE INTO reviews VALUES
  (9, 1, 7,5,'One of the best sci-fi films in years. The paradox concept is handled brilliantly.','2026-05-23 10:00:00'),
  (10,2, 8,5,'A heartbreaking and beautiful film. Cried twice. Bell is extraordinary.','2026-05-23 11:00:00'),
  (11,3, 9,4,'Edge-of-your-seat action. The surveillance plot feels frighteningly real.','2026-05-23 12:00:00'),
  (12,4,10,3,'Some effective scares but nothing groundbreaking. Sets the mood well.','2026-05-23 13:00:00'),
  (13,5,11,5,'The chemistry between the leads is electric. Absolutely wonderful.','2026-05-23 14:00:00'),
  (14,1,14,4,'Loved the concept but the middle dragged a bit. The final act was breathtaking.','2026-05-23 18:00:00'),
  (15,2,16,4,'Slow burn but absolutely worth it. The cinematography is stunning.','2026-05-23 19:00:00'),
  (16,3,18,5,'Okafor is a genius. Best action film of the year, no question.','2026-05-23 20:00:00'),
  (17,4,20,4,'Genuinely unsettling. The manor is basically a character of its own.','2026-05-23 21:00:00'),
  (18,5,23,4,'Sweet, charming, and gorgeous to look at. Took my partner and she loved it.','2026-05-23 22:00:00'),
  (19,6,13,4,'The effects are spectacular and Chen keeps the tension high throughout.','2026-05-23 23:00:00'),
  (20,1,22,5,'A masterclass in science fiction. Vasquez is an incredible director.','2026-05-24 10:00:00'),
  (21,2,25,5,'Bell crafts something truly special here. Understated but devastating.','2026-05-24 11:00:00'),
  (22,3,26,4,'Fast-paced and smart. A rare thriller that respects its audience.','2026-05-24 12:00:00'),
  (23,4,28,2,'Too slow for a horror film. The ending was anticlimactic.','2026-05-24 13:00:00'),
  (24,5,29,5,'Nair directs with such sensitivity. A genuinely moving romance.','2026-05-24 14:00:00'),
  (25,6,31,5,'Incredible world-building. The ethical questions it raises stayed with me.','2026-05-24 15:00:00'),
  (26,1,30,3,'Interesting idea but too complicated for its own good. Still enjoyable.','2026-05-24 20:00:00'),
  (27,2,33,4,'Quietly powerful. I was moved by the central performance.','2026-05-24 21:00:00'),
  (28,3,34,3,'Good action but the third act felt rushed. Still very watchable.','2026-05-24 22:00:00'),
  (29,4,36,5,'The best horror film I have seen in years. Do not watch alone.','2026-05-25 07:00:00'),
  (30,5,38,3,'Nice visuals but the plot is very predictable. Good for a casual evening out.','2026-05-25 08:00:00'),
  (31,6,41,4,'Action-packed with a genuinely interesting premise. Would watch again.','2026-05-25 07:30:00'),
  (32,1,37,4,'Gripping from start to finish. The lead actress gives a career-best performance.','2026-05-25 08:00:00'),
  (33,3,40,5,'Watched it twice. The twists in this film are something else.','2026-05-25 09:00:00'),
  (34,6,45,3,'Fun but a bit formulaic. The robot design is brilliant though.','2026-05-25 10:00:00'),
  (35,6,50,5,'Better than I expected. Chen delivers his best work to date.','2026-05-25 11:00:00'),
  (36,6,55,4,'Technical marvel. The fight choreography alone is worth the ticket price.','2026-05-25 12:00:00'),
  (37,2,42,4,'Moving and understated. I was not expecting to enjoy this as much as I did.','2026-05-25 13:00:00'),
  (38,3,48,4,'Tense and intelligent. One of the better action films in recent memory.','2026-05-25 14:00:00');
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
