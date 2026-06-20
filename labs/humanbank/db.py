import os
import random
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
    iban           TEXT UNIQUE DEFAULT '',
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

CREATE TABLE IF NOT EXISTS _flags (name TEXT PRIMARY KEY, value TEXT);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS tan_codes (
    id       INTEGER PRIMARY KEY,
    user_id  INTEGER NOT NULL,
    position INTEGER NOT NULL,
    pin      TEXT    NOT NULL,
    used     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transfer_limits (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE,
    daily_limit REAL    DEFAULT 1000.0,
    limit_start TEXT,
    limit_end   TEXT
);

CREATE TABLE IF NOT EXISTS payment_requests (
    id           INTEGER PRIMARY KEY,
    requester_id INTEGER NOT NULL,
    target_id    INTEGER NOT NULL,
    from_account INTEGER NOT NULL,
    to_account   INTEGER NOT NULL,
    amount       REAL    NOT NULL,
    memo         TEXT    DEFAULT '',
    pin          TEXT    NOT NULL,
    status       TEXT    DEFAULT 'pending',
    created_at   TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    type       TEXT    NOT NULL,
    title      TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    link       TEXT    DEFAULT '',
    read       INTEGER DEFAULT 0,
    created_at TEXT    NOT NULL
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@humanbank.local','HumanBank Admin',1,'FLAG{hb_bac_admin_detail_exposed}','555-0100','FLAG{hb_sqli_login_bypassed}'),
  (2,'alice.wang','sunshine1','alice@example.com','Alice Wang',0,'Passionate about personal finance and travel.','+1 503 555 0201','14 Cedar Ave, Portland OR'),
  (3,'bob.harris','baseball99','bob@example.com','Bob Harris',0,'','','42 Oak Street, Seattle WA'),
  (4,'carol.lee','iloveyou','carol@example.com','Carol Lee',0,'Coffee addict. Saving for a house.','','88 Pine Road, Austin TX'),
  (5,'dan.murphy','letmein','dan@example.com','Dan Murphy',0,'','','22 Elm Drive, Denver CO'),
  (6,'eva.santos','monkey123','eva@example.com','Eva Santos',0,'Freelance designer. Multiple income streams.','','9 Birch Lane, Miami FL'),
  (7,'frank.kim','dragon99','frank@example.com','Frank Kim',0,'','','77 Maple Court, Chicago IL'),
  (8,'c.human','commonhuman-lab','accounts@commonhuman.local','CommonHuman Labs',0,'Categorisation not possible.','','Unknown');

INSERT OR IGNORE INTO accounts VALUES
  (1, 2,'HB-0001','','checking', 4823.50,'2024-01-15'),
  (2, 2,'HB-0002','','savings', 12400.00,'2024-01-15'),
  (3, 3,'HB-0003','','checking',   875.25,'2024-03-02'),
  (4, 3,'HB-0004','','savings',  3200.00,'2024-03-02'),
  (5, 4,'HB-0005','','checking',  2100.00,'2024-06-18'),
  (6, 4,'HB-0006','','savings',   8500.00,'2024-06-18'),
  (7, 5,'HB-0007','','checking',   560.00,'2025-01-10'),
  (8, 5,'HB-0008','','savings',   1200.00,'2025-01-10'),
  (9, 6,'HB-0009','','checking',  9345.80,'2023-11-05'),
  (10,6,'HB-0010','','savings',  24000.00,'2023-11-05'),
  (11,7,'HB-0011','','checking',  1870.00,'2025-04-22'),
  (12,7,'HB-0012','','savings',   5000.00,'2025-04-22'),
  (13,8,'HB-CMNH','','checking',1337000.00,'2026-01-01');

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

INSERT OR IGNORE INTO users VALUES
  (9, 'grace.johnson',    '3fc0a7acf087f549ac2b266baf94b8b1','grace.johnson@example.com',    'Grace Johnson',    0,'Avid reader and home gardener.',         '+1 206 555 0301','5 Maple Ave, Seattle WA'),
  (10,'henry.williams',   'e99a18c428cb38d5f260853678922e03','henry.williams@example.com',   'Henry Williams',   0,'',                                       '+1 312 555 0201','18 Oak Street, Chicago IL'),
  (11,'isabella.brown',   'eb0a191797624dd3a48fa681d3061212','isabella.brown@example.com',   'Isabella Brown',   0,'Small business owner. Keeping finances simple.','','34 Birch Road, Phoenix AZ'),
  (12,'james.davis',      '3bf1114a986ba87ed28fc1b5884fc2f8','james.davis@example.com',      'James Davis',      0,'',                                       '+1 702 555 0401','67 Desert Drive, Las Vegas NV'),
  (13,'karen.miller',     '37b4e2d82900d5e94b8da524fbeb33c0','karen.miller@example.com',     'Karen Miller',     0,'Retired teacher. Managing retirement savings.','+1 615 555 0311','22 Elm Court, Nashville TN'),
  (14,'liam.wilson',      'a906449d5769fa7361d7ecc6aa3f6d28','liam.wilson@example.com',      'Liam Wilson',      0,'','','9 Pine Street, Boston MA'),
  (15,'mia.moore',        '8afa847f50a716e64932d995c8e7435a','mia.moore@example.com',        'Mia Moore',        0,'Artist and freelance photographer.',     '+1 323 555 0411','104 Sunset Blvd, Los Angeles CA'),
  (16,'noah.taylor',      'e10adc3949ba59abbe56e057f20f883e','noah.taylor@example.com',      'Noah Taylor',      0,'','','55 River Road, Portland OR'),
  (17,'olivia.anderson',  '5f4dcc3b5aa765d61d8327deb882cf99','olivia.anderson@example.com',  'Olivia Anderson',  0,'Nurse. Saving for my kids'' college fund.','+1 404 555 0211','71 Peachtree St, Atlanta GA'),
  (18,'peter.thomas',     '25d55ad283aa400af464c76d713c07ad','peter.thomas@example.com',     'Peter Thomas',     0,'',                                       '+1 214 555 0301','33 Commerce Way, Dallas TX'),
  (19,'quinn.jackson',    'fcea920f7412b5da7be0cf42b8c93759','quinn.jackson@example.com',    'Quinn Jackson',    0,'','','88 Cedar Lane, Minneapolis MN'),
  (20,'rachel.white',     '0571749e2ac330a7455809c6b0e7af90','rachel.white@example.com',     'Rachel White',     0,'Marketing professional. Side hustle in e-commerce.','+1 503 555 0401','41 Broadway Ave, Portland OR'),
  (21,'samuel.harris',    'd0763edaa9d9bd2a9516280e9044d885','samuel.harris@example.com',    'Samuel Harris',    0,'','','15 Harbor View, San Diego CA'),
  (22,'tina.martin',      '8621ffdbc5698829397d97767ac13db3','tina.martin@example.com',      'Tina Martin',      0,'Accountant. Meticulous with every dollar.','+1 303 555 0511','28 Mountain Rd, Denver CO'),
  (23,'ursula.garcia',    'ec0e2603172c73a8b644bb9456c1ff6e','ursula.garcia@example.com',    'Ursula Garcia',    0,'',                                       '+1 305 555 0211','5 Ocean Drive, Miami FL'),
  (24,'victor.martinez',  '84d961568a65073a3bcf0eb216b2a576','victor.martinez@example.com',  'Victor Martinez',  0,'','','60 Industrial Blvd, Houston TX'),
  (25,'wendy.robinson',   'd8578edf8458ce06fbc5bb76a58c5ca4','wendy.robinson@example.com',   'Wendy Robinson',   0,'Stay-at-home parent managing household budget.','+1 612 555 0601','19 Lake Street, St Paul MN'),
  (26,'xavier.clark',     '96e79218965eb72c92a549dd5a330112','xavier.clark@example.com',     'Xavier Clark',     0,'','','44 Tech Park Drive, San Jose CA'),
  (27,'yolanda.rodriguez','276f8db0b86edaa7fc805516c852c889','yolanda.rodriguez@example.com','Yolanda Rodriguez', 0,'Server. Building my first savings.',     '+1 505 555 0311','12 Mesa Ave, Albuquerque NM'),
  (28,'zachary.lewis',    'da443a0ad979d5530df38ca1a74e4f80','zachary.lewis@example.com',    'Zachary Lewis',    0,'',                                       '+1 513 555 0501','77 River Bend, Cincinnati OH'),
  (29,'amber.lee',        'ad92694923612da0600d7be498cc2e08','amber.lee@example.com',        'Amber Lee',        0,'','','31 Cherry Blossom Way, San Francisco CA'),
  (30,'brandon.walker',   '5badcaf789d3d1d09794d8f021f40f0e','brandon.walker@example.com',   'Brandon Walker',   0,'Construction worker. Saving for a truck.','+1 615 555 0701','8 Union Street, Memphis TN'),
  (31,'chloe.hall',       '0acf4539a14b3aa27deeb4cbdf6e989f','chloe.hall@example.com',       'Chloe Hall',       0,'','','56 Park Lane, Charlotte NC'),
  (32,'dylan.allen',      '6b1b36cbb04b41490bfc0ab2bfa26f86','dylan.allen@example.com',      'Dylan Allen',      0,'IT technician. Building an emergency fund.','+1 206 555 0801','90 Capitol Hill, Seattle WA'),
  (33,'emma.young',       '40be4e59b9a2a2b5dffb918c0e86b3d7','emma.young@example.com',       'Emma Young',       0,'',                                       '+1 617 555 0311','4 Beacon Street, Boston MA'),
  (34,'felix.hernandez',  '5fcfd41e547a12215b173ff47fdd3739','felix.hernandez@example.com',  'Felix Hernandez',  0,'','','62 Sunset Ave, El Paso TX'),
  (35,'georgia.king',     'c378985d629e99a4e86213db0cd5e70d','georgia.king@example.com',     'Georgia King',     0,'Realtor. Lots of commissions, more expenses.','+1 404 555 0801','23 Magnolia Drive, Atlanta GA'),
  (36,'hunter.wright',    'df0349ce110b69f03b4def8012ae4970','hunter.wright@example.com',    'Hunter Wright',    0,'','','37 Frontier Road, Oklahoma City OK'),
  (37,'iris.lopez',       'bee783ee2974595487357e195ef38ca2','iris.lopez@example.com',       'Iris Lopez',       0,'Graduate student. Watching every penny.','+1 512 555 0411','16 University Ave, Austin TX'),
  (38,'jason.hill',       'ef6e65efc188e7dffd7335b646a85a21','jason.hill@example.com',       'Jason Hill',       0,'','','48 Ridgeline Dr, Denver CO'),
  (39,'kelly.scott',      'bf779e0933a882808585d19455cd7937','kelly.scott@example.com',      'Kelly Scott',      0,'Hair salon owner. Mix of personal and business.','+1 813 555 0311','9 Clearwater Blvd, Tampa FL'),
  (40,'lucas.green',      'aae039d6aa239cfc121357a825210fa3','lucas.green@example.com',      'Lucas Green',      0,'',                                       '+1 314 555 0211','55 Gateway Arch Rd, St Louis MO'),
  (41,'maya.adams',       'aa47f8215c6f30a0dcdb2a36a9f4168e','maya.adams@example.com',       'Maya Adams',       0,'','','27 Harbor Blvd, Baltimore MD'),
  (42,'nathan.baker',     '1d3d37667a8d7eb02054c6afdf9e2e1c','nathan.baker@example.com',     'Nathan Baker',     0,'Baker. Balancing passion with practicality.','+1 503 555 0911','3 Artisan Way, Portland OR'),
  (43,'nora.gonzalez',    'ef4cdd3117793b9fd593d7488409626d','nora.gonzalez@example.com',    'Nora Gonzalez',    0,'','','72 Palm Drive, San Antonio TX'),
  (44,'oscar.nelson',     '4297f44b13955235245b2497399d7a93','oscar.nelson@example.com',     'Oscar Nelson',     0,'',                                       '+1 612 555 0211','18 Forest Ave, Minneapolis MN'),
  (45,'paula.carter',     'f379eaf3c831b04de153469d1bec345e','paula.carter@example.com',     'Paula Carter',     0,'Administrative assistant. Two kids in school.','','34 Suburban Drive, Columbus OH'),
  (46,'ryan.mitchell',    '482c811da5d5b4bc6d497ffa98491e38','ryan.mitchell@example.com',    'Ryan Mitchell',    0,'',                                       '+1 415 555 0611','100 Market Street, San Francisco CA'),
  (47,'sarah.perez',      '7d0710824ff191f6a0086a7e3891641e','sarah.perez@example.com',      'Sarah Perez',      0,'','','45 Spring Garden, Philadelphia PA'),
  (48,'tyler.roberts',    '5c7686c0284e0875b26de99c1008e998','tyler.roberts@example.com',    'Tyler Roberts',    0,'Truck driver. Long haul across the midwest.','+1 402 555 0211','11 Interstate Way, Omaha NE'),
  (49,'uma.turner',       '43b90920409618f188bfc6923f16b9fa','uma.turner@example.com',       'Uma Turner',       0,'','','67 Vineyard Road, Napa CA'),
  (50,'vincent.phillips', 'd8d3a01ba7e5d44394b6f0a8533f4647','vincent.phillips@example.com', 'Vincent Phillips',  0,'',                                       '+1 206 555 0111','83 Eastside Ave, Seattle WA'),
  (51,'walter.campbell',  '2dccd1ab3e03990aea77359831c85ca2','walter.campbell@example.com',  'Walter Campbell',  0,'Retired military. Simple banking needs.','','25 Veterans Pkwy, Fayetteville NC'),
  (52,'xena.parker',      'd5c0607301ad5d5c1528962a83992ac8','xena.parker@example.com',      'Xena Parker',      0,'',                                       '+1 702 555 0811','40 Strip Blvd, Las Vegas NV'),
  (53,'yasmine.evans',    '7c6a180b36896a0a8c02787eeafb0e4c','yasmine.evans@example.com',    'Yasmine Evans',    0,'Fashion buyer. Travels frequently for work.','','15 Fashion Ave, New York NY'),
  (54,'zoe.edwards',      'f25a2fc72690b780b2a14e140ef6a9e0','zoe.edwards@example.com',      'Zoe Edwards',      0,'',                                       '+1 310 555 0711','88 Wilshire Blvd, Los Angeles CA'),
  (55,'alan.collins',     '0d107d09f5bbe40cade3de5c71e9e9b7','alan.collins@example.com',     'Alan Collins',     0,'','','30 Warehouse Row, Nashville TN'),
  (56,'barbara.stewart',  'e65c8afc9951f94fed8873a4c1e31a63','barbara.stewart@example.com',  'Barbara Stewart',  0,'School principal. Planning early retirement.','+1 602 555 0311','55 Desert View, Phoenix AZ'),
  (57,'carl.sanchez',     'cc25c0f861a83f5efadc6e1ba9d1269e','carl.sanchez@example.com',     'Carl Sanchez',     0,'','','19 Border Street, El Paso TX'),
  (58,'diane.morris',     'b696aef7776367787253dc2acdd10279','diane.morris@example.com',     'Diane Morris',     0,'Veterinarian. Loves animals, hates spreadsheets.','+1 651 555 0411','77 Lakeview Drive, St Paul MN');

-- Contractor account. Cross-lab credential-reuse pivot target for VaultSync's
-- vs-credential-reuse-pivot challenge — this password is only discoverable by
-- reading j.reyes' VaultSync vault (item id 11, planted in labs/vaultsync/db.py),
-- not by anything inside this lab on its own.
INSERT OR IGNORE INTO users VALUES
  (59,'j.reyes','correct1','j.reyes@contractor.example','Jordan Reyes',0,'Contractor — temporary access for the Q2 ledger migration. FLAG{vs_credential_reuse_pivot}','','c/o IT Contracting Pool');

INSERT OR IGNORE INTO accounts VALUES
  (14, 9,'HB-0014','','checking',  3450.00,'2022-03-15'),
  (15, 9,'HB-0015','','savings',   8200.00,'2022-03-15'),
  (16,10,'HB-0016','','checking',  1875.50,'2022-07-22'),
  (17,10,'HB-0017','','savings',   4100.00,'2022-07-22'),
  (18,11,'HB-0018','','checking',  6240.00,'2022-09-10'),
  (19,11,'HB-0019','','savings',  15800.00,'2022-09-10'),
  (20,12,'HB-0020','','checking',   924.75,'2022-11-30'),
  (21,12,'HB-0021','','savings',   2300.00,'2022-11-30'),
  (22,13,'HB-0022','','checking',  5120.00,'2022-12-05'),
  (23,13,'HB-0023','','savings',  18500.00,'2022-12-05'),
  (24,14,'HB-0024','','checking',  2380.00,'2023-01-18'),
  (25,14,'HB-0025','','savings',   6750.00,'2023-01-18'),
  (26,15,'HB-0026','','checking',  4915.25,'2023-02-14'),
  (27,15,'HB-0027','','savings',  11000.00,'2023-02-14'),
  (28,16,'HB-0028','','checking',   738.50,'2023-04-08'),
  (29,16,'HB-0029','','savings',   1800.00,'2023-04-08'),
  (30,17,'HB-0030','','checking',  3600.00,'2023-05-20'),
  (31,17,'HB-0031','','savings',   9400.00,'2023-05-20'),
  (32,18,'HB-0032','','checking',  8250.00,'2023-06-11'),
  (33,18,'HB-0033','','savings',  22000.00,'2023-06-11'),
  (34,19,'HB-0034','','checking',  1140.00,'2023-07-29'),
  (35,19,'HB-0035','','savings',   3000.00,'2023-07-29'),
  (36,20,'HB-0036','','checking',  2890.50,'2023-08-15'),
  (37,20,'HB-0037','','savings',   7600.00,'2023-08-15'),
  (38,21,'HB-0038','','checking',   512.00,'2023-09-03'),
  (39,21,'HB-0039','','savings',   1200.00,'2023-09-03'),
  (40,22,'HB-0040','','checking',  4380.00,'2023-10-17'),
  (41,22,'HB-0041','','savings',  12000.00,'2023-10-17'),
  (42,23,'HB-0042','','checking',  2060.00,'2023-11-22'),
  (43,23,'HB-0043','','savings',   5300.00,'2023-11-22'),
  (44,24,'HB-0044','','checking',  7800.00,'2023-12-01'),
  (45,24,'HB-0045','','savings',  19500.00,'2023-12-01'),
  (46,25,'HB-0046','','checking',  3215.00,'2024-01-09'),
  (47,25,'HB-0047','','savings',   8800.00,'2024-01-09'),
  (48,26,'HB-0048','','checking',   950.00,'2024-02-14'),
  (49,26,'HB-0049','','savings',   2100.00,'2024-02-14'),
  (50,27,'HB-0050','','checking',  1680.50,'2024-03-28'),
  (51,27,'HB-0051','','savings',   4000.00,'2024-03-28'),
  (52,28,'HB-0052','','checking',  5500.00,'2024-04-11'),
  (53,28,'HB-0053','','savings',  14200.00,'2024-04-11'),
  (54,29,'HB-0054','','checking',  2340.00,'2024-05-07'),
  (55,29,'HB-0055','','savings',   6500.00,'2024-05-07'),
  (56,30,'HB-0056','','checking',   875.00,'2024-06-19'),
  (57,30,'HB-0057','','savings',   2000.00,'2024-06-19'),
  (58,31,'HB-0058','','checking',  3900.00,'2024-07-03'),
  (59,31,'HB-0059','','savings',  10200.00,'2024-07-03'),
  (60,32,'HB-0060','','checking',  1425.75,'2024-08-21'),
  (61,32,'HB-0061','','savings',   3700.00,'2024-08-21'),
  (62,33,'HB-0062','','checking',  6800.00,'2024-09-14'),
  (63,33,'HB-0063','','savings',  17000.00,'2024-09-14'),
  (64,34,'HB-0064','','checking',  2175.00,'2024-10-02'),
  (65,34,'HB-0065','','savings',   5800.00,'2024-10-02'),
  (66,35,'HB-0066','','checking',  4620.50,'2024-10-30'),
  (67,35,'HB-0067','','savings',  13400.00,'2024-10-30'),
  (68,36,'HB-0068','','checking',  1050.00,'2024-11-15'),
  (69,36,'HB-0069','','savings',   2500.00,'2024-11-15'),
  (70,37,'HB-0070','','checking',  3280.00,'2024-12-04'),
  (71,37,'HB-0071','','savings',   8100.00,'2024-12-04'),
  (72,38,'HB-0072','','checking',  9100.00,'2025-01-13'),
  (73,38,'HB-0073','','savings',  24500.00,'2025-01-13'),
  (74,39,'HB-0074','','checking',  2740.00,'2025-02-08'),
  (75,39,'HB-0075','','savings',   7200.00,'2025-02-08'),
  (76,40,'HB-0076','','checking',  1380.50,'2025-03-22'),
  (77,40,'HB-0077','','savings',   3400.00,'2025-03-22'),
  (78,41,'HB-0078','','checking',  5040.00,'2025-04-05'),
  (79,41,'HB-0079','','savings',  14800.00,'2025-04-05'),
  (80,42,'HB-0080','','checking',  2915.00,'2025-04-30'),
  (81,42,'HB-0081','','savings',   7500.00,'2025-04-30'),
  (82,43,'HB-0082','','checking',   865.00,'2025-05-18'),
  (83,43,'HB-0083','','savings',   1950.00,'2025-05-18'),
  (84,44,'HB-0084','','checking',  3730.00,'2025-06-11'),
  (85,44,'HB-0085','','savings',   9600.00,'2025-06-11'),
  (86,45,'HB-0086','','checking',  1200.00,'2025-07-07'),
  (87,45,'HB-0087','','savings',   2800.00,'2025-07-07'),
  (88,46,'HB-0088','','checking',  7450.00,'2025-07-29'),
  (89,46,'HB-0089','','savings',  20000.00,'2025-07-29'),
  (90,47,'HB-0090','','checking',  2560.00,'2025-08-14'),
  (91,47,'HB-0091','','savings',   6300.00,'2025-08-14'),
  (92,48,'HB-0092','','checking',  4180.00,'2025-09-03'),
  (93,48,'HB-0093','','savings',  11500.00,'2025-09-03'),
  (94,49,'HB-0094','','checking',  1835.50,'2025-10-16'),
  (95,49,'HB-0095','','savings',   4400.00,'2025-10-16'),
  (96,50,'HB-0096','','checking',  3420.00,'2025-11-08'),
  (97,50,'HB-0097','','savings',   8700.00,'2025-11-08'),
  (98,51,'HB-0098','','checking',   940.00,'2025-12-01'),
  (99,51,'HB-0099','','savings',   2250.00,'2025-12-01'),
  (100,52,'HB-0100','','checking', 5870.00,'2025-12-20'),
  (101,52,'HB-0101','','savings', 15200.00,'2025-12-20'),
  (102,53,'HB-0102','','checking', 2290.50,'2026-01-07'),
  (103,53,'HB-0103','','savings',  6100.00,'2026-01-07'),
  (104,54,'HB-0104','','checking', 4660.00,'2026-01-28'),
  (105,54,'HB-0105','','savings', 12500.00,'2026-01-28'),
  (106,55,'HB-0106','','checking', 1750.00,'2026-02-11'),
  (107,55,'HB-0107','','savings',  4300.00,'2026-02-11'),
  (108,56,'HB-0108','','checking', 8320.00,'2026-03-04'),
  (109,56,'HB-0109','','savings', 21000.00,'2026-03-04'),
  (110,57,'HB-0110','','checking', 2110.00,'2026-03-25'),
  (111,57,'HB-0111','','savings',  5400.00,'2026-03-25'),
  (112,58,'HB-0112','','checking', 6090.50,'2026-04-09'),
  (113,58,'HB-0113','','savings', 16300.00,'2026-04-09');

INSERT OR IGNORE INTO transactions VALUES
  (27, 14,'credit',3200.00,'Payroll — May 2026',        'Rainier Software LLC',         '2026-05-30'),
  (28, 14,'debit', 1400.00,'Rent — June 2026',           'Greenwood Properties',         '2026-06-01'),
  (29, 16,'credit',4100.00,'Payroll — May 2026',         'Midwest Consulting Group',     '2026-05-30'),
  (30, 16,'debit', 1800.00,'Mortgage — June 2026',       'First National Bank',          '2026-06-01'),
  (31, 18,'credit',5200.00,'Invoice #INV-2204',          'Brown & Associates LLC',       '2026-05-28'),
  (32, 18,'debit',  299.00,'Annual software licence',    'Adobe Systems Inc',            '2026-05-29'),
  (33, 20,'credit',2800.00,'Monthly salary — May',       'Vegas Hospitality Group',      '2026-05-31'),
  (34, 20,'debit', 1100.00,'Rent — June 2026',           'Desert Sun Rentals',           '2026-06-01'),
  (35, 22,'credit',2400.00,'Pension payment — May',      'Tennessee Teachers Fund',      '2026-05-30'),
  (36, 22,'debit',   95.00,'Electricity — May',          'Nashville Power Co',           '2026-05-28'),
  (37, 24,'credit',3600.00,'Payroll — May 2026',         'BostonTech Inc',               '2026-05-30'),
  (38, 24,'debit', 1650.00,'Rent — June 2026',           'Beacon Hill Rentals',          '2026-06-01'),
  (39, 26,'credit',2100.00,'Photography invoice',        'Studio Collective LA',         '2026-05-25'),
  (40, 26,'debit', 1900.00,'Rent — June 2026',           'Sunset Properties LLC',        '2026-06-01'),
  (41, 28,'credit',2950.00,'Payroll — May 2026',         'Pacific Logistics Inc',        '2026-05-31'),
  (42, 28,'debit',  900.00,'Rent — June 2026',           'Portland Rentals Group',       '2026-06-01'),
  (43, 30,'credit',4200.00,'Salary — May 2026',          'Piedmont Health System',       '2026-05-30'),
  (44, 30,'debit', 1350.00,'Mortgage — June 2026',       'SunTrust Mortgage',            '2026-06-01'),
  (45, 32,'credit',7500.00,'Monthly salary — May',       'Apex Financial Corp',          '2026-05-31'),
  (46, 32,'debit', 2100.00,'Mortgage — June 2026',       'Wells Fargo Home Loans',       '2026-06-01'),
  (47, 34,'credit',3100.00,'Payroll — May 2026',         'North Star Retail Group',      '2026-05-30'),
  (48, 34,'debit', 1250.00,'Rent — June 2026',           'Twin Cities Rentals',          '2026-06-01'),
  (49, 36,'credit',3400.00,'Salary — May 2026',          'Albuquerque Restaurant Group', '2026-05-31'),
  (50, 36,'debit',  950.00,'Rent — June 2026',           'Mesa View Apartments',         '2026-06-01'),
  (51, 38,'credit',4800.00,'Payroll — May 2026',         'Great Lakes Engineering',      '2026-05-30'),
  (52, 38,'debit', 1700.00,'Car loan — June',            'Chase Auto Finance',           '2026-06-01'),
  (53, 40,'credit',3750.00,'Payroll — May 2026',         'Bay Area Staffing Co',         '2026-05-31'),
  (54, 40,'debit', 2200.00,'Rent — June 2026',           'SF Market Properties',         '2026-06-01'),
  (55, 42,'credit',2600.00,'Payroll — May 2026',         'Memphis Build & Repair',       '2026-05-30'),
  (56, 42,'debit',  480.00,'Tool supplies',              'Home Depot',                   '2026-05-29'),
  (57, 44,'credit',3300.00,'Payroll — May 2026',         'Carolina Healthcare LLC',      '2026-05-31'),
  (58, 44,'debit', 1150.00,'Rent — June 2026',           'Pinehurst Rentals',            '2026-06-01'),
  (59, 46,'credit',5100.00,'Payroll — May 2026',         'PNW Technology Group',         '2026-05-30'),
  (60, 46,'debit', 1600.00,'Rent — June 2026',           'Capitol Hill Properties',      '2026-06-01'),
  (61, 48,'credit',4000.00,'Payroll — May 2026',         'Boston Financial LLC',         '2026-05-31'),
  (62, 48,'debit', 1850.00,'Rent — June 2026',           'Fenway Park Rentals',          '2026-06-01'),
  (63, 50,'credit',2200.00,'Payroll — May 2026',         'Border City Services Inc',     '2026-05-30'),
  (64, 50,'debit',  650.00,'Groceries — May',            'El Rancho Supermarket',        '2026-05-28'),
  (65, 52,'credit',6800.00,'Commission — April sale',    'Atlanta Premier Realty',       '2026-05-15'),
  (66, 52,'debit', 2050.00,'Rent — June 2026',           'Buckhead Apartments',          '2026-06-01'),
  (67, 54,'credit',2900.00,'Payroll — May 2026',         'Oklahoma City Utilities',      '2026-05-31'),
  (68, 54,'debit', 1000.00,'Rent — June 2026',           'Frontier Rentals LLC',         '2026-06-01'),
  (69, 56,'credit',1800.00,'Monthly stipend',            'UT Austin Financial Aid',      '2026-05-20'),
  (70, 56,'debit',  820.00,'Rent — June 2026',           'Campus Housing LLC',           '2026-06-01'),
  (71, 58,'credit',8900.00,'Payroll — May 2026',         'Rocky Mountain Logistics',     '2026-05-31'),
  (72, 58,'debit', 2300.00,'Mortgage — June 2026',       'Colorado Mortgage Group',      '2026-06-01'),
  (73, 60,'credit',4500.00,'Business income — May',      'Kelly''s Hair & Beauty LLC',   '2026-05-30'),
  (74, 60,'debit',  780.00,'Salon supplies',             'Sally Beauty Supply',          '2026-05-27'),
  (75, 62,'credit',3500.00,'Payroll — May 2026',         'Gateway Financial Partners',   '2026-05-31'),
  (76, 62,'debit', 1300.00,'Rent — June 2026',           'St Louis Loft Rentals',        '2026-06-01'),
  (77, 64,'credit',3800.00,'Payroll — May 2026',         'Chesapeake Bay Corp',          '2026-05-30'),
  (78, 64,'debit', 1500.00,'Rent — June 2026',           'Harbor View Apartments',       '2026-06-01'),
  (79, 66,'credit',5600.00,'Monthly sales revenue',      'Nathan''s Artisan Bakery',     '2026-05-28'),
  (80, 66,'debit', 1200.00,'Ingredient supplies',        'Portland Food Distributors',   '2026-05-26'),
  (81, 68,'credit',2750.00,'Payroll — May 2026',         'Alamo City Services',          '2026-05-31'),
  (82, 68,'debit', 1050.00,'Rent — June 2026',           'River Walk Apartments',        '2026-06-01'),
  (83, 70,'credit',3600.00,'Payroll — May 2026',         'Twin Pines Group Inc',         '2026-05-30'),
  (84, 70,'debit', 1200.00,'Rent — June 2026',           'Lakes District Rentals',       '2026-06-01'),
  (85, 72,'credit',3100.00,'Payroll — May 2026',         'Heartland Insurance Co',       '2026-05-31'),
  (86, 72,'debit',  850.00,'Childcare — June',           'Sunshine Daycare Center',      '2026-06-01'),
  (87, 74,'credit',9200.00,'Payroll — May 2026',         'Golden Gate Capital LLC',      '2026-05-30'),
  (88, 74,'debit', 2500.00,'Rent — June 2026',           'SOMA Properties SF',           '2026-06-01'),
  (89, 76,'credit',3200.00,'Payroll — May 2026',         'Philadelphia Healthcare',      '2026-05-31'),
  (90, 76,'debit', 1200.00,'Rent — June 2026',           'Old City Apartments',          '2026-06-01'),
  (91, 78,'credit',5800.00,'Trucking income — May',      'Heartland Freight LLC',        '2026-05-30'),
  (92, 78,'debit', 1100.00,'Diesel fuel — May',          'Pilot Flying J',               '2026-05-29'),
  (93, 80,'credit',3400.00,'Payroll — May 2026',         'Napa Valley Resorts',          '2026-05-31'),
  (94, 80,'debit', 1400.00,'Rent — June 2026',           'Vineyard View Rentals',        '2026-06-01'),
  (95, 82,'credit',4100.00,'Payroll — May 2026',         'Northwest Tech Solutions',     '2026-05-30'),
  (96, 82,'debit',  820.00,'Health insurance premium',   'Blue Cross Blue Shield',       '2026-06-01'),
  (97, 84,'credit',2300.00,'Pension — May 2026',         'US Military Retirement Fund',  '2026-05-31'),
  (98, 84,'debit',  210.00,'Utilities — May',            'Fayetteville City Power',      '2026-05-28'),
  (99, 86,'credit',3800.00,'Payroll — May 2026',         'Las Vegas Grand Hotel',        '2026-05-30'),
  (100,86,'debit', 1600.00,'Rent — June 2026',           'Nevada Desert Apartments',     '2026-06-01'),
  (101,88,'credit',6200.00,'Salary — May 2026',          'Nordstrom Corporate',          '2026-05-31'),
  (102,88,'debit', 2800.00,'Rent — June 2026',           'Manhattan Luxury Rentals',     '2026-06-01'),
  (103,90,'credit',3500.00,'Payroll — May 2026',         'Wilshire Medical Group',       '2026-05-30'),
  (104,90,'debit', 1750.00,'Rent — June 2026',           'Brentwood Apartments',         '2026-06-01'),
  (105,92,'credit',3000.00,'Payroll — May 2026',         'Music City Enterprises',       '2026-05-31'),
  (106,92,'debit', 1100.00,'Rent — June 2026',           'Nashville Midtown Lofts',      '2026-06-01'),
  (107,94,'credit',7500.00,'Salary — May 2026',          'Camelback School District',    '2026-05-30'),
  (108,94,'debit', 2000.00,'Mortgage — June 2026',       'Phoenix Federal Credit Union', '2026-06-01'),
  (109,96,'credit',2700.00,'Payroll — May 2026',         'Lone Star Border Co',          '2026-05-31'),
  (110,96,'debit',  980.00,'Rent — June 2026',           'Rio Grande Apartments',        '2026-06-01'),
  (111,98,'credit',5200.00,'Payroll — May 2026',         'Twin City Veterinary Clinic',  '2026-05-30'),
  (112,98,'debit',  450.00,'Clinic supplies',            'VetSource Medical',            '2026-05-29'),
  (113,100,'credit',3800.00,'Payroll — May 2026',        'Nevada Gaming Corp',           '2026-05-30'),
  (114,100,'debit',1600.00,'Rent — June 2026',           'Las Vegas Strip Apartments',   '2026-06-01'),
  (115,102,'credit',6200.00,'Salary — May 2026',         'Vogue Magazine Editorial',     '2026-05-31'),
  (116,102,'debit',3200.00,'Rent — June 2026',           'Manhattan Upper West Side',    '2026-06-01'),
  (117,104,'credit',3500.00,'Payroll — May 2026',        'Westside Medical Center',      '2026-05-30'),
  (118,104,'debit',1750.00,'Rent — June 2026',           'Brentwood Luxury Rentals',     '2026-06-01'),
  (119,106,'credit',2900.00,'Payroll — May 2026',        'Country Music Network',        '2026-05-31'),
  (120,106,'debit', 980.00,'Rent — June 2026',           'Nashville East Rentals',       '2026-06-01'),
  (121,108,'credit',7500.00,'Salary — May 2026',         'Scottsdale Academy',           '2026-05-30'),
  (122,108,'debit',2200.00,'Mortgage — June 2026',       'Arizona Federal Mortgage',     '2026-06-01'),
  (123,110,'credit',2800.00,'Payroll — May 2026',        'Southwest Border Services',    '2026-05-31'),
  (124,110,'debit', 900.00,'Rent — June 2026',           'El Paso Sunland Apartments',   '2026-06-01'),
  (125,112,'credit',5400.00,'Payroll — May 2026',        'Great Plains Vet Clinic',      '2026-05-30'),
  (126,112,'debit', 480.00,'Clinic supplies',            'Merck Animal Health',          '2026-05-29');

INSERT OR IGNORE INTO support_tickets VALUES
  (8, 9,'Login issue from new device','I recently got a new laptop and cannot log into my account. I have been entering the correct password but keep getting an error. Please help me regain access.','open','2026-05-02'),
  (9,12,'Wire transfer limit increase request','I need to wire $15,000 to my contractor for home renovation. The system is showing my daily limit as $5,000. Can this be temporarily raised for this payment?','open','2026-05-08'),
  (10,15,'Suspicious ATM withdrawal','I noticed a $400 cash withdrawal from an ATM I do not recognise. I have not used an ATM in over a month. Please freeze my account and investigate.','open','2026-05-12'),
  (11,18,'Bank statements for mortgage application','I am applying for a home loan and need 6 months of statements showing my salary credits. Please send to peter.thomas@example.com or provide a secure download link.','open','2026-05-15'),
  (12,21,'Debit card stopped working','My card was declined at the supermarket today despite sufficient balance. I also tried it online and got an error. I need this resolved urgently.','open','2026-05-18'),
  (13,25,'Direct debit charged twice','My monthly broadband payment of $89 was taken twice this month. I need the duplicate refunded and the mandate reviewed.','closed','2026-05-05'),
  (14,30,'Question about savings interest rate','I have been a customer for over two years and my savings account is still on 0.5%. Are there better rates available for existing customers?','open','2026-05-20'),
  (15,35,'Account locked — cannot log in','When I try to log in I receive an error that my account is locked. I have not done anything unusual. Please unlock my account.','open','2026-05-21'),
  (16,42,'Unexpected monthly fee','I noticed a $12 maintenance fee on my checking statement. I was not informed of this charge when I opened the account. Please refund and waive this fee.','closed','2026-05-14'),
  (17,50,'Update mailing address','I have moved and need to update my address to: 83 Eastside Ave, Seattle WA 98101. Please also direct future statements there.','open','2026-05-22');

INSERT OR IGNORE INTO _flags VALUES
  ('sqli-search', 'FLAG{hb_sqli_search_union}'),
  ('sqli-txn',    'FLAG{hb_sqli_txn_dump}');

INSERT OR IGNORE INTO transactions VALUES
  (127,13,'credit',0.01,'FLAG{hb_recon_audit_exposed}','INTERNAL AUDIT','2026-01-01');

INSERT OR IGNORE INTO transactions VALUES
  (128,13,'debit',0.01,'FLAG{hb_idor_cmnh_exposed}','INTERNAL AUDIT','2026-01-02');

INSERT OR IGNORE INTO support_tickets VALUES
  (18,1,'Internal Security Audit Note','Quarterly penetration test complete. Auditors confirmed critical IDOR on ticket endpoint. FLAG{hb_idor_ticket_read}','closed','2026-05-01');

INSERT OR IGNORE INTO ticket_replies VALUES
  (3, 8, 1,'Hi Grace, we have sent a one-time security code to your registered email. Use it to verify your new device on the login page. Contact us again if the issue persists.',1,'2026-05-03'),
  (4, 9,12,'Thank you. I will split the payment into three transfers over three days. Please let me know if there is a faster option available.',0,'2026-05-09'),
  (5,11, 1,'Hi Peter, six months of statements have been sent as password-protected PDFs to peter.thomas@example.com. The password is your date of birth in DDMMYYYY format. Please confirm receipt.',1,'2026-05-16'),
  (6,13, 1,'Hi Wendy, we confirmed the duplicate direct debit and have raised a $89 refund to your account. It should appear within 2 business days. The mandate has been corrected.',1,'2026-05-07'),
  (7,16, 1,'Hi Nathan, the $12 fee has been refunded and a maintenance fee waiver applied for the next 12 months. We apologise for the inconvenience.',1,'2026-05-15');

INSERT OR IGNORE INTO documents VALUES
  (5, 9,'grace_johnson_passport.pdf',          'doc_005.pdf','id',       '2026-05-02'),
  (6,10,'henry_williams_statement_q1.pdf',     'doc_006.pdf','statement','2026-05-05'),
  (7,13,'karen_miller_statement_apr2026.pdf',  'doc_007.pdf','statement','2026-05-15'),
  (8,15,'mia_moore_drivers_licence.pdf',       'doc_008.pdf','id',       '2026-05-12'),
  (9,18,'peter_thomas_statements_6m.pdf',      'doc_009.pdf','statement','2026-05-16'),
  (10,22,'tina_martin_tax_return_2025.pdf',    'doc_010.pdf','tax',      '2026-05-03'),
  (11,30,'brandon_walker_statement_q1.pdf',    'doc_011.pdf','statement','2026-05-20'),
  (12,35,'georgia_king_national_id.pdf',       'doc_012.pdf','id',       '2026-05-21'),
  (13,42,'nathan_baker_business_licence.pdf',  'doc_013.pdf','business', '2026-05-18'),
  (14,56,'barbara_stewart_pension_stmt.pdf',   'doc_014.pdf','statement','2026-05-22');
"""


def _iban_for(account_id):
    # OC = fictional OctoBank country code, OCTO = bank identifier, 0001 = branch
    bban = f'OCTO0001{account_id:08d}'
    numeric = ''
    for c in (bban + 'OC00'):
        numeric += str(ord(c) - 55) if c.isalpha() else c
    check = 98 - (int(numeric) % 97)
    return f'OC{check:02d}{bban}'


def gen_tan_codes(user_id):
    rng = random.Random(user_id * 7919 + 13)
    pool = list(range(10, 100))
    rng.shuffle(pool)
    return [(user_id, pos, str(pool[pos - 1]), 0) for pos in range(1, 77)]


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
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)

    # Populate IBANs for all seeded accounts
    rows = conn.execute("SELECT id FROM accounts WHERE iban = '' OR iban IS NULL").fetchall()
    for r in rows:
        conn.execute("UPDATE accounts SET iban = ? WHERE id = ?", (_iban_for(r['id']), r['id']))

    # Generate TAN codes for all seeded users (ids 1–58)
    for uid in range(1, 59):
        for code in gen_tan_codes(uid):
            conn.execute(
                "INSERT OR IGNORE INTO tan_codes (user_id, position, pin, used) VALUES (?, ?, ?, ?)",
                code
            )

    # Default transfer limits for all seeded users
    for uid in range(1, 59):
        conn.execute(
            "INSERT OR IGNORE INTO transfer_limits (user_id, daily_limit) VALUES (?, 1000.0)",
            (uid,)
        )

    conn.commit()
    conn.close()
