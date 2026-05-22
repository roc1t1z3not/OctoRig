import os
import sqlite3
from flask import g

DATABASE = '/data/netpulse.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password      TEXT NOT NULL,
    email         TEXT NOT NULL,
    full_name     TEXT DEFAULT '',
    is_admin      INTEGER DEFAULT 0,
    bio           TEXT DEFAULT '',
    phone         TEXT DEFAULT '',
    address       TEXT DEFAULT '',
    plan          TEXT DEFAULT 'Dial-Up 56K',
    data_used_mb  INTEGER DEFAULT 0,
    data_limit_mb INTEGER DEFAULT 500
);

CREATE TABLE IF NOT EXISTS invoices (
    id             INTEGER PRIMARY KEY,
    user_id        INTEGER NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    amount         REAL NOT NULL,
    due_date       TEXT NOT NULL,
    issued_date    TEXT NOT NULL,
    paid           INTEGER DEFAULT 0,
    description    TEXT DEFAULT ''
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

CREATE TABLE IF NOT EXISTS board_threads (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS board_replies (
    id         INTEGER PRIMARY KEY,
    thread_id  INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notification_templates (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    subject     TEXT NOT NULL,
    body        TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS reset_tokens (
    id         INTEGER PRIMARY KEY,
    user_id    INTEGER NOT NULL,
    token      TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used       INTEGER DEFAULT 0
);

INSERT OR IGNORE INTO users VALUES
  (1,'admin','commonhuman-lab','admin@netpulse.local','NetPulse Admin',1,'','555-0100','NetPulse HQ, Server Room B','ISDN 128K',0,999999),
  (2,'dave.norton','password1','dave@example.com','Dave Norton',0,'Avid Usenet reader and IRC regular.','+1 503 555 0201','18 Maple Ave, Portland OR','Dial-Up 56K',312,500),
  (3,'sue.chang','ilovecats','sue@example.com','Sue Chang',0,'','','77 Oak Street, Seattle WA','Dial-Up 56K',420,500),
  (4,'mike.reed','baseball99','mike@example.com','Mike Reed',0,'Webmaster of mikesite.net.','','9 Cedar Lane, Austin TX','ISDN 64K',88,1000),
  (5,'jan.white','fluffy99','jan@example.com','Jan White',0,'','','31 Birch Road, Denver CO','Dial-Up 56K',498,500),
  (6,'carl.stone','qwerty12','carl@example.com','Carl Stone',0,'Power user. Runs a local BBS.','','66 Pine Court, Miami FL','ISDN 128K',201,1000),
  (7,'kim.lee','sunshine','kim@example.com','Kim Lee',0,'','','12 Elm Drive, Chicago IL','Dial-Up 56K',3,500);

INSERT OR IGNORE INTO invoices VALUES
  (1, 2,'NP-0001-FEB',  19.99,'1998-03-01','1998-02-01',1,'Dial-Up 56K — February 1998'),
  (2, 2,'NP-0001-MAR',  19.99,'1998-04-01','1998-03-01',1,'Dial-Up 56K — March 1998'),
  (3, 2,'NP-0001-APR',  19.99,'1998-05-01','1998-04-01',1,'Dial-Up 56K — April 1998'),
  (4, 2,'NP-0001-MAY',  19.99,'1998-06-01','1998-05-01',0,'Dial-Up 56K — May 1998'),
  (5, 3,'NP-0002-FEB',  19.99,'1998-03-01','1998-02-01',1,'Dial-Up 56K — February 1998'),
  (6, 3,'NP-0002-MAR',  19.99,'1998-04-01','1998-03-01',1,'Dial-Up 56K — March 1998'),
  (7, 3,'NP-0002-APR',  19.99,'1998-05-01','1998-04-01',1,'Dial-Up 56K — April 1998'),
  (8, 3,'NP-0002-MAY',  19.99,'1998-06-01','1998-05-01',0,'Dial-Up 56K — May 1998'),
  (9, 4,'NP-0003-FEB',  29.99,'1998-03-01','1998-02-01',1,'ISDN 64K — February 1998'),
  (10,4,'NP-0003-MAR',  29.99,'1998-04-01','1998-03-01',1,'ISDN 64K — March 1998'),
  (11,4,'NP-0003-APR',  29.99,'1998-05-01','1998-04-01',1,'ISDN 64K — April 1998'),
  (12,4,'NP-0003-MAY',  29.99,'1998-06-01','1998-05-01',0,'ISDN 64K — May 1998'),
  (13,5,'NP-0004-FEB',  19.99,'1998-03-01','1998-02-01',1,'Dial-Up 56K — February 1998'),
  (14,5,'NP-0004-MAR',  19.99,'1998-04-01','1998-03-01',1,'Dial-Up 56K — March 1998'),
  (15,5,'NP-0004-APR',  19.99,'1998-05-01','1998-04-01',1,'Dial-Up 56K — April 1998'),
  (16,5,'NP-0004-MAY',  19.99,'1998-06-01','1998-05-01',0,'Dial-Up 56K — May 1998'),
  (17,6,'NP-0005-FEB',  49.99,'1998-03-01','1998-02-01',1,'ISDN 128K — February 1998'),
  (18,6,'NP-0005-MAR',  49.99,'1998-04-01','1998-03-01',1,'ISDN 128K — March 1998'),
  (19,6,'NP-0005-APR',  49.99,'1998-05-01','1998-04-01',1,'ISDN 128K — April 1998'),
  (20,6,'NP-0005-MAY',  49.99,'1998-06-01','1998-05-01',0,'ISDN 128K — May 1998'),
  (21,7,'NP-0006-FEB',  19.99,'1998-03-01','1998-02-01',1,'Dial-Up 56K — February 1998'),
  (22,7,'NP-0006-MAR',  19.99,'1998-04-01','1998-03-01',0,'Dial-Up 56K — March 1998'),
  (23,7,'NP-0006-APR',  19.99,'1998-05-01','1998-04-01',0,'Dial-Up 56K — April 1998'),
  (24,7,'NP-0006-MAY',  19.99,'1998-06-01','1998-05-01',0,'Dial-Up 56K — May 1998'),
  (25,1,'NP-ADMIN-FEB', 0.00,'1998-03-01','1998-02-01',1,'Staff account — ISDN 128K — February 1998'),
  (26,1,'NP-ADMIN-MAR', 0.00,'1998-04-01','1998-03-01',1,'Staff account — ISDN 128K — March 1998'),
  (27,1,'NP-ADMIN-APR', 0.00,'1998-05-01','1998-04-01',1,'Staff account — ISDN 128K — April 1998'),
  (28,1,'NP-ADMIN-MAY', 0.00,'1998-06-01','1998-05-01',1,'Staff account — ISDN 128K — May 1998');

INSERT OR IGNORE INTO support_tickets VALUES
  (1,2,'Connection drops after 30 minutes','Every evening my connection gets cut after exactly 30 minutes. I have to redial and it reconnects fine. This has been happening for two weeks. Is there a session timeout configured on your servers?','closed','1998-05-02'),
  (2,3,'Cannot connect after 6pm','I cannot connect at all between 6pm and 9pm. I get a busy signal every time. I have tried all three access numbers. My connection during the day is fine. Please advise.','closed','1998-05-08'),
  (3,4,'Website hosting — can I upgrade?','I am currently on ISDN 64K and I run a small website hosted on my own machine. The pages are loading slowly for visitors. Is it possible to upgrade to ISDN 128K without changing my invoice date?','open','1998-05-11'),
  (4,5,'Data limit nearly exceeded','My usage bar shows I am almost at 500MB. I do not understand how I have used this much. I have only been reading email and some Usenet groups. Can you show me a breakdown?','open','1998-05-13'),
  (5,6,'Static IP address request','I need a static IP address for running a local server. I understand there is an additional fee. Please confirm availability and pricing.','closed','1998-05-18'),
  (6,7,'New account — cannot get modem to dial','I just signed up and followed the setup guide but my modem will not dial. It says NO CARRIER. I am using a US Robotics 56K Sportster. Windows 98. Please help.','closed','1998-05-20'),
  (7,2,'Overcharged on March invoice','I was billed $24.99 on my March invoice but my plan is $19.99. Please investigate and issue a refund for the difference.','closed','1998-04-03'),
  (8,4,'Email quota — how do I check it?','How much mailbox space does my account include? I am getting bounce errors when people try to send me attachments. Is there a webmail interface I can use to clear old messages?','open','1998-05-15'),
  (9,3,'Modem keeps disconnecting mid-download','I am trying to download a large file from FTP and my connection drops every 20 minutes or so. I am using a 56K US Robotics modem. Is there a way to resume interrupted downloads?','open','1998-05-17'),
  (10,6,'Need reverse DNS entry for mail server','I have set up a sendmail server on my static IP and am getting rejections from other mail servers because my IP has no reverse DNS record. Can you add a PTR record pointing to mail.stonenet.local?','open','1998-05-21'),
  (11,1,'Billing system migration — test accounts needed','Planning to migrate the billing DB to the new Postgres instance next weekend. Need three test accounts created with dummy credit card data so QA can verify the charge flow. Please assign them to the test subnet.','closed','1998-04-28'),
  (12,1,'Server room UPS replacement — schedule downtime','The UPS in Server Room B is due for replacement on Saturday 9 May. Estimated downtime: 2am–4am. Need to notify affected ISDN customers 48 hours in advance. Can ops send the standard maintenance email template?','closed','1998-05-07'),
  (13,1,'Access log rotation — disk space alert','The access logs on np-web-01 are not rotating correctly. /var/log is at 94% capacity. I have checked logrotate.conf and the path looks correct. Can someone from ops take a look before we hit 100%?','open','1998-05-20');

INSERT OR IGNORE INTO ticket_replies VALUES
  (1,1,1,'Hi Dave, we have removed the 30-minute session timeout from your account. This was a legacy setting applied to older accounts. You should now be able to maintain a continuous connection. Let us know if the issue recurs.',1,'1998-05-04'),
  (2,2,1,'Hi Sue, we have identified a capacity issue on the 6pm–9pm access pool. We have added four additional dial-in lines effective from today. Please try connecting again this evening and let us know if the issue continues.',1,'1998-05-10'),
  (3,2,3,'Thank you — I was able to connect fine last night. The new lines have made a big difference. Marking this resolved.',0,'1998-05-11'),
  (4,5,1,'Hi Carl, a static IP is available on your ISDN 128K plan at no additional charge. Your assigned IP is 212.54.18.92. We have updated your account and the IP will be active within 2 hours. Reverse DNS can be configured on request.',1,'1998-05-19'),
  (5,5,6,'Perfect — the IP is working and I have updated my server configs. Could you also set up a PTR record pointing to bbs.stonenet.local?',0,'1998-05-20'),
  (6,5,1,'PTR record added. Allow up to 24 hours for DNS propagation.',1,'1998-05-21'),
  (7,6,1,'Hi Kim, your modem model is supported. The most common cause of NO CARRIER is an incorrect dial string. In your dial-up connection settings, add a comma after the area code to insert a pause: 0,1800NET555. This usually resolves the issue with PBX lines.',1,'1998-05-21'),
  (8,7,1,'Hi Dave, we identified a billing system error that applied the wrong rate to 47 accounts in March. A credit of $5.00 has been applied to your account and will appear on your May invoice.',1,'1998-04-05'),
  (9,7,2,'Thank you for the quick resolution. The credit is showing on my account.',0,'1998-04-06'),
  (10,11,1,'Three test accounts created: test-qa-01 through test-qa-03 on subnet 10.99.0.0/24. Dummy card data seeded. Assigned to billing_test group in the admin panel.',1,'1998-04-29'),
  (11,12,1,'Maintenance window confirmed for Sat 9 May 02:00–04:00. Notification email queued for Thursday 7 May 06:00 to all affected ISDN accounts. Estimated 47 customer notifications.',1,'1998-05-07');

INSERT OR IGNORE INTO board_threads VALUES
  (1, 2,'Best IRC networks in 1998?',              'I have been using EFnet for years but heard Undernet is less laggy. Anyone have recommendations? Looking for good tech channels mostly.','1998-05-01'),
  (2, 3,'Free web hosting recommendations',        'I want to put up a personal homepage but do not want to pay. Has anyone used GeoCities or Tripod? What are the size limits?','1998-05-05'),
  (3, 4,'How do I get my IP address?',             'I need my current IP to configure my server software but winipcfg keeps showing 0.0.0.0. Any ideas?','1998-05-08'),
  (4, 6,'ISDN splitter — self-install tips',       'Got my ISDN line installed but the splitter the engineer left looks different from the one in the setup guide. Has anyone self-installed one of these?','1998-05-12'),
  (5, 5,'Usenet: best newsgroups for tech help?',  'Looking for active newsgroups for Windows 98 help. comp.os.ms-windows.* seems dead. Any suggestions?','1998-05-14'),
  (6, 7,'Anyone else using mIRC scripts?',         'I wrote a small mIRC script to auto-respond to CTCP version requests with a fake client string. Anyone else doing stuff like this? Would love to trade scripts.','1998-05-15'),
  (7, 4,'What FTP software do you use?',           'I have been using WS_FTP LE but it keeps crashing on large transfers. CuteFTP looks good but it is not free. Anyone have a recommendation for a stable free FTP client?','1998-05-16'),
  (8, 3,'Windows 98 vs NT 4 for home use?',        'My brother keeps telling me to install NT 4 instead of Windows 98 because it is more stable. I just want to browse the web and play games. Is it worth the hassle?','1998-05-17'),
  (9, 2,'Netscape vs Internet Explorer — which?',  'I know this is controversial but I genuinely want to hear opinions. I have been on Netscape 4 since it came out but IE 4 seems faster lately. What are people using?','1998-05-18'),
  (10,6,'Setting up a personal mail server',       'I am running sendmail on Linux and want to host my own email. I have a static IP from NetPulse. Anyone done this? Main questions are: do I need my own domain, and how do I handle spam filtering?','1998-05-19'),
  (11,5,'Modem init string for better speeds',     'My 56K modem rarely connects above 44K. I read that tweaking the modem initialisation string in dial-up networking can improve things. Has anyone found a good init string for the Sportster 56K?','1998-05-20'),
  (12,4,'Running a web server on ISDN — tips?',    'I have Apache 1.3 running on my Windows 98 machine with the ISDN line. It works but goes down whenever I reboot. Anyone using a more stable setup for a personal site that gets light traffic?','1998-05-21');

INSERT OR IGNORE INTO board_replies VALUES
  (1, 1,4,'EFnet is huge but yes, very laggy. I switched to DALnet for smaller channels and it is much more stable. Try ##programming on there.','1998-05-02'),
  (2, 1,6,'irc.freenode.net is great for technical stuff. Less drama than EFnet too.','1998-05-03'),
  (3, 1,3,'I tried Undernet last week. Much faster than EFnet. #linux-help there is very active.','1998-05-04'),
  (4, 2,2,'GeoCities gives you 11MB free but goes down a lot. Tripod is more reliable in my experience.','1998-05-06'),
  (5, 2,5,'Angelfire is also worth trying. I have had my page up there for six months without any issues. 5MB limit though.','1998-05-07'),
  (6, 2,7,'I use xoom.com — 50MB free and no pop-up banners on every page like GeoCities.','1998-05-08'),
  (7, 3,1,'Open a command prompt and type winipcfg then click the dropdown to select your modem adapter rather than the default.','1998-05-09'),
  (8, 3,6,'If you have a static IP from NetPulse it will always be the same. Check your dial-up connection properties under TCP/IP settings too.','1998-05-10'),
  (9, 4,2,'I self-installed mine. The key thing is to make sure the filter is before the phone socket, not after. The guide diagram is backwards.','1998-05-13'),
  (10,4,3,'I had the same issue. Ring NetPulse support — they talked me through it in about 10 minutes. The engineer should have installed it for you anyway.','1998-05-14'),
  (11,5,4,'alt.windows98 and microsoft.public.win98.general are both still fairly active. The Microsoft newsgroups are better for official answers.','1998-05-15'),
  (12,5,6,'comp.os.ms-windows.nt.admin.networking has good content even if the name suggests NT — lots of the advice applies to 98 too.','1998-05-16'),
  (13,6,4,'Nice idea. I have a script that plays a sound when someone says my nick and auto-kicks anyone who says certain words. Happy to share.','1998-05-16'),
  (14,6,2,'I use a script to log all channel messages to a file. Useful for reading back after I disconnect. Send me a /msg if you want it.','1998-05-17'),
  (15,7,3,'SmartFTP is free and very stable. I switched from WS_FTP about three months ago and it has never crashed on me.','1998-05-17'),
  (16,7,5,'FileZilla was just released last month. Open source and free. I have only used it briefly but it looks promising.','1998-05-18'),
  (17,8,4,'NT 4 is overkill for home use. The hardware requirements are higher and most games will not run on it properly. Stick with 98.','1998-05-18'),
  (18,8,6,'NT 4 is rock solid but your brother is right that setup is more involved. Unless you need the stability for a server it is not worth it at home.','1998-05-19'),
  (19,9,4,'I switched to IE 4 two months ago. It renders most sites better and Outlook Express is actually a decent mail client.','1998-05-19'),
  (20,9,5,'Netscape has better Java support. If you use any Java applets stay on Netscape. Otherwise IE is fine.','1998-05-20'),
  (21,9,3,'I use both depending on the site. Some sites are coded specifically for IE and look broken in Netscape. The browser wars are genuinely annoying.','1998-05-20'),
  (22,10,2,'You will need a domain if you want a proper email address. Register one at Network Solutions — about $70 for two years. Then set up MX records pointing to your IP.','1998-05-20'),
  (23,10,4,'For spam filtering on sendmail look into procmail. It is a pain to configure but very powerful once it is set up.','1998-05-21'),
  (24,11,4,'Try ATZ&F&C1&D2S11=55S0=0 as your init string. The S11=55 speeds up the dialling tone recognition. Made a difference on my Sportster.','1998-05-21'),
  (25,12,7,'I run Apache on Linux for exactly this reason. Put a cheap 486 in the corner running Slackware — it just stays up indefinitely.','1998-05-22');

INSERT OR IGNORE INTO notification_templates VALUES
  (1,'welcome','Welcome to NetPulse!','Dear {{ user.full_name }},\n\nWelcome to NetPulse Internet Services. Your account is now active.\n\nUsername: {{ user.username }}\nPlan: {{ user.plan }}\n\nPlease keep your password safe. If you need help, contact our helpdesk.\n\nNetPulse Support Team','Sent when a new account is created'),
  (2,'invoice','Your NetPulse invoice is ready','Dear {{ user.full_name }},\n\nYour invoice for {{ invoice.description }} is now available.\n\nAmount Due: ${{ invoice.amount }}\nDue Date: {{ invoice.due_date }}\n\nPlease contact us if you have any questions.\n\nNetPulse Billing Department','Sent when a new invoice is issued'),
  (3,'suspend','Account suspension notice','Dear {{ user.full_name }},\n\nYour NetPulse account has been temporarily suspended due to non-payment.\n\nTo restore service, please settle your outstanding balance.\n\nNetPulse Accounts','Sent when an account is suspended for non-payment');
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
