# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import sqlite3
from flask import g

DB_PATH = '/data/subverse.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            username     TEXT UNIQUE NOT NULL,
            email        TEXT,
            password_hash TEXT NOT NULL,
            role         TEXT DEFAULT 'user',
            karma        INTEGER DEFAULT 0,
            bio          TEXT DEFAULT '',
            avatar       TEXT DEFAULT '',
            created_at   TEXT,
            reset_token  TEXT
        );

        CREATE TABLE IF NOT EXISTS communities (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT UNIQUE NOT NULL,
            description  TEXT DEFAULT '',
            created_by   INTEGER,
            member_count INTEGER DEFAULT 0,
            announcement TEXT DEFAULT '',
            created_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS community_members (
            user_id      INTEGER,
            community_id INTEGER,
            role         TEXT DEFAULT 'member',
            joined_at    TEXT,
            PRIMARY KEY (user_id, community_id)
        );

        CREATE TABLE IF NOT EXISTS posts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            body         TEXT DEFAULT '',
            user_id      INTEGER,
            community_id INTEGER,
            score        INTEGER DEFAULT 0,
            status       TEXT DEFAULT 'published',
            flair        TEXT DEFAULT '',
            created_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            body       TEXT NOT NULL,
            user_id    INTEGER,
            post_id    INTEGER,
            parent_id  INTEGER,
            score      INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS votes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER,
            target_type TEXT,
            target_id   INTEGER,
            value       INTEGER,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id    INTEGER,
            recipient_id INTEGER,
            subject      TEXT,
            body         TEXT DEFAULT '',
            read         INTEGER DEFAULT 0,
            created_at   TEXT
        );

        CREATE TABLE IF NOT EXISTS mod_log (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            community_id INTEGER,
            mod_id       INTEGER,
            action       TEXT,
            target_id    INTEGER,
            reason       TEXT DEFAULT '',
            created_at   TEXT
        );
    """)

    # MD5 hashes: commonhuman-lab, password1, letmein, sunshine1, baseball99, iloveyou, monkey123, dragon99
    db.executescript("""
        INSERT OR IGNORE INTO users (id, username, email, password_hash, role, karma, bio, created_at) VALUES
          (1, 'admin',       'admin@subverse.local',        '36b809e24478355e344545720ea7e090', 'admin',     9999, 'Site administrator.',   '2025-01-01 00:00:00'),
          (2, 'mod_alice',   'alice@subverse.local',        '7c6a180b36896a0a8c02787eeafb0e4c', 'moderator', 4500, 'Community moderator.',  '2025-01-05 08:00:00'),
          (3, 'mod_bob',     'bob@subverse.local',          '0d107d09f5bbe40cade3de5c71e9e9b7', 'moderator', 3200, 'Tech mod.',             '2025-01-06 09:00:00'),
          (4, 'sv_dan',      'dan.foster@mail.example',     'd5c0607301ad5d5c1528962a83992ac8', 'user',       850, 'Just a regular poster.','2025-02-10 12:00:00'),
          (5, 'pixel_kate',  'kate.p@mail.example',         'e65c8afc9951f94fed8873a4c1e31a63', 'user',       420, 'I like cats and code.', '2025-02-14 15:30:00'),
          (6, 'tech_marcus', 'marcus.t@mail.example',       'f25a2fc72690b780b2a14e140ef6a9e0', 'user',       720, 'Security researcher.',  '2025-02-20 11:00:00'),
          (7, 'sara_q',      'sara.q@mail.example',         'cc25c0f861a83f5efadc6e1ba9d1269e', 'user',       310, '',                      '2025-03-01 09:45:00'),
          (8, 'ghost_user',  'ghost@mail.example',          'b696aef7776367787253dc2acdd10279', 'user',        55, 'Just lurking.',         '2025-03-15 20:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO communities (id, name, description, created_by, member_count, announcement, created_at) VALUES
          (1, 'technology', 'Tech news, tools, and discussion.',              1, 1842, '', '2025-01-01 00:00:00'),
          (2, 'security',   'Cybersecurity, CTFs, and hacking.',              1,  934, '', '2025-01-01 00:00:00'),
          (3, 'offtopic',   'Everything that doesn''t fit elsewhere.',        2,  612, '', '2025-01-02 00:00:00'),
          (4, 'news',       'World news and current events.',                 2, 2341, '', '2025-01-02 00:00:00'),
          (5, 'hidden',     'Private staff community — moderators only.',     1,    3, '', '2025-01-01 00:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO community_members (user_id, community_id, role, joined_at) VALUES
          (1, 1, 'moderator', '2025-01-01 00:00:00'), (1, 2, 'moderator', '2025-01-01 00:00:00'),
          (1, 5, 'moderator', '2025-01-01 00:00:00'), (2, 1, 'moderator', '2025-01-05 08:00:00'),
          (2, 3, 'moderator', '2025-01-05 08:00:00'), (2, 5, 'moderator', '2025-01-05 08:00:00'),
          (3, 2, 'moderator', '2025-01-06 09:00:00'), (3, 4, 'moderator', '2025-01-06 09:00:00'),
          (4, 1, 'member',    '2025-02-10 12:00:00'), (4, 2, 'member',    '2025-02-11 13:00:00'),
          (5, 1, 'member',    '2025-02-14 15:30:00'), (5, 3, 'member',    '2025-02-14 16:00:00'),
          (6, 2, 'member',    '2025-02-20 11:00:00'), (6, 1, 'member',    '2025-02-21 10:00:00'),
          (7, 3, 'member',    '2025-03-01 09:45:00'), (7, 4, 'member',    '2025-03-02 10:00:00'),
          (8, 1, 'member',    '2025-03-15 20:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO posts (id, title, body, user_id, community_id, score, status, flair, created_at) VALUES
          (1,  'Rust is eating Python''s lunch in systems tooling',
                'Hot take: the new wave of Rust-based CLI tools (ripgrep, fd, bat, exa) are so much faster that Python tools will be relegated to scripting glue within 5 years. Discuss.',
                4, 1, 312, 'published', 'Discussion', '2025-04-01 10:00:00'),
          (2,  'Anyone else using Neovim full-time in 2025?',
                'Switched from VS Code six months ago and haven''t looked back. Treesitter + LSP + lazy.nvim is actually a joy. What plugins are you using?',
                6, 1, 189, 'published', 'Tools', '2025-04-02 09:30:00'),
          (3,  'CVE-2025-3141: Critical RCE in libexpat — patch now',
                'A critical heap overflow in libexpat (versions < 2.7.1) allows remote code execution via a malformed XML entity. CVSS 9.8. Most Linux distros have pushed patches.',
                3, 2, 547, 'published', 'Alert', '2025-04-03 08:00:00'),
          (4,  'SQL injection still #1 in OWASP Top 10 — why?',
                'It''s 2025 and SQLi is still the most common critical finding in web app audits. Parameterised queries have been the answer since the 90s. Why do developers keep getting this wrong?',
                6, 2, 233, 'published', 'Discussion', '2025-04-04 14:00:00'),
          (5,  'Found a flask app storing passwords in plaintext',
                'During a pentest this week I found a Flask app storing user passwords in plain text in SQLite. The admin password was "commonhuman-lab". Filed the report. Check your /data/ directories folks.',
                3, 2,  88, 'published', 'Story', '2025-04-05 11:00:00'),
          (6,  'Weekend plans?',
                'Going hiking up in the mountains this weekend. Anyone else escaping the screen for a couple of days?',
                7, 3,  42, 'published', '', '2025-04-06 17:00:00'),
          (7,  'What''s everyone reading right now?',
                'Just finished "The Pragmatic Programmer" for the third time. Still finding new things in it. Recommendations for the next book?',
                5, 3,  61, 'published', '', '2025-04-07 20:00:00'),
          (8,  'Tech layoffs continue into Q2 2025',
                'Three major cloud providers announced another round of layoffs this week, totalling 12,000 jobs. The restructuring is said to focus on shifting headcount to AI divisions.',
                2, 4, 891, 'published', 'Tech', '2025-04-08 07:00:00'),
          (9,  'EU passes landmark AI regulation act',
                'The European Parliament passed the AI Act with 523 votes in favour. High-risk AI systems will require mandatory audits and human oversight. Full text linked.',
                3, 4, 634, 'published', 'Policy', '2025-04-09 08:30:00'),
          (10, 'Docker vs Podman in 2025 — which do you use?',
                'With Podman going rootless by default and Docker Desktop licensing changes, I''ve seen a lot of teams switching. What''s your team running in production?',
                4, 1, 156, 'published', 'Discussion', '2025-04-10 11:00:00'),
          (11, 'Beginner''s guide to Burp Suite I wrote up',
                'I put together a comprehensive intro to Burp Suite Community for beginners. Covers proxy setup, repeater, intruder basics, and decoder. Feedback welcome.',
                6, 2,  99, 'published', 'Guide', '2025-04-11 14:30:00'),
          (12, 'My home lab setup — 2025 edition',
                'Updated my homelab this year: Proxmox on three nodes, TrueNAS for storage, Pi-hole + Unbound for DNS. Happy to answer questions.',
                4, 1, 204, 'published', 'Homelab', '2025-04-12 16:00:00'),
          (13, 'Anyone else doing HackTheBox / TryHackMe?',
                'I''ve been working through the HTB Starting Point series. Great intro to enumeration and basic exploitation. What machines are you working on?',
                5, 2,  77, 'published', 'Training', '2025-04-13 18:00:00'),
          (14, 'Hot take: YAML is a terrible config language',
                'Indentation-sensitive, inconsistent booleans, surprise type coercions. TOML or even JSON would be better for most config use cases. Fight me.',
                8, 1, 445, 'published', 'Hot Take', '2025-04-14 09:00:00'),
          (15, 'Cloudflare outage post-mortem published',
                'Cloudflare published their post-mortem for last month''s 90-minute global outage. Root cause was a misconfigured BGP route that propagated globally. Good read.',
                2, 4, 312, 'published', 'Incident', '2025-04-15 10:00:00'),
          (16, 'Wireguard setup guide for self-hosters',
                'Step-by-step guide to setting up a Wireguard VPN server on a $5 VPS. Covers key generation, peer config, and routing.',
                6, 1, 188, 'published', 'Guide', '2025-04-16 12:00:00'),
          (17, 'The best terminal emulators in 2025',
                'Alacritty, Kitty, WezTerm, and the new Ghostty — benchmarks and comparisons. GPU-accelerated terminals are now basically the standard.',
                4, 1, 134, 'published', 'Tools', '2025-04-17 14:00:00'),
          (18, 'SSRF attack demo — from internal metadata to RCE',
                'Recorded a full SSRF exploitation chain: internal metadata service → cloud credentials → S3 bucket listing → RCE via CI/CD webhook. Write-up in comments.',
                3, 2, 421, 'published', 'Research', '2025-04-18 11:00:00'),
          (19, 'Favourite terminal one-liners?',
                'Mine: `find . -name "*.log" -mtime +30 -delete` and `jq ''.[] | select(.status=="error")'' errors.json`. Post yours.',
                7, 1, 267, 'published', '', '2025-04-19 15:00:00'),
          (20, 'Is Go still worth learning in 2025?',
                'With Rust taking over systems programming and Python still dominating scripting/ML, where does Go fit? I think K8s and cloud tooling keep it relevant. Thoughts?',
                6, 1, 143, 'published', 'Discussion', '2025-04-20 10:00:00'),
          (21, 'Breaking: major social media platform suffers data breach',
                '350 million user records exposed including hashed passwords and private messages. Company notified users via email. Regulators investigating.',
                2, 4, 1240, 'published', 'Breaking', '2025-04-21 06:00:00'),
          (22, 'Climate summit reaches carbon agreement',
                'World leaders signed a new carbon reduction treaty today, committing to 50% emission cuts by 2035. Analysts are cautiously optimistic.',
                3, 4, 456, 'published', 'World', '2025-04-22 07:30:00'),
          (23, 'Tips for staying productive working from home?',
                'Three years in and I''m still struggling with the afternoon slump. What routines or tools have actually worked for you?',
                5, 3,  93, 'published', '', '2025-04-23 13:00:00'),
          (24, 'Coffee shop recommendations for remote workers in Berlin',
                'Looking for places with fast wifi and outlets that don''t kick you out after 2 hours. Mitte / Kreuzberg preferred.',
                7, 3,  38, 'published', '', '2025-04-24 11:00:00'),
          (25, 'Understanding JWT algorithm confusion attacks',
                'Quick breakdown of the alg:none attack and RS256→HS256 confusion. Both are still found in real apps. Code examples and mitigations included.',
                3, 2, 318, 'published', 'Research', '2025-04-25 09:00:00'),
          (26, 'Zero-trust network architecture — practical implementation',
                'Moved our org to zero-trust last year. Here''s what actually worked and what the vendors don''t tell you.',
                6, 2, 204, 'published', 'Guide', '2025-04-26 14:00:00'),
          (27, 'Python 3.14 performance improvements are real',
                'PEP 703 (no-GIL) is landing in 3.14 experimental. Early benchmarks on CPU-bound tasks show 2-4x improvements on multi-core. Game changer for scientific computing.',
                4, 1, 376, 'published', 'News', '2025-04-27 10:00:00'),
          (28, 'Ask SubVerse: best resources for learning AppSec?',
                'Career pivot from dev to AppSec. I have a strong Python background. Where should I start — PortSwigger Web Academy, TCM Security, or somewhere else?',
                5, 2, 112, 'published', 'Ask SV', '2025-04-28 15:30:00'),
          (29, 'Self-hosted alternatives to common SaaS tools',
                'Replaced Notion with Obsidian + Syncthing, Slack with Mattermost, and Google Analytics with Plausible. Total monthly cost: $12 VPS. Here''s the full list.',
                4, 1, 529, 'published', 'Self-hosted', '2025-04-29 12:00:00'),
          (30, 'DRAFT: Admin password rotation — DO NOT POST',
                'INTERNAL DRAFT — This post should not be visible to regular users.\n\nNew admin password will be changed to: subverse2025admin\nEffective date: next Monday 09:00 UTC\nDo not share this information outside of the moderation team.',
                1, 5,   0, 'draft',     '', '2025-04-30 08:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO comments (id, body, user_id, post_id, parent_id, score, created_at) VALUES
          (1,  'Completely agree on ripgrep. 40x faster than grep for my use case. The Rust ecosystem is maturing fast.',             6, 1, NULL, 87, '2025-04-01 11:00:00'),
          (2,  'Hot take rejected. Python has the ecosystem, Rust has the learning curve. They''ll coexist for decades.',             5, 1, NULL, 43, '2025-04-01 12:00:00'),
          (3,  'Both can be true. Rust for performance-critical tooling, Python for glue and automation.',                            4, 1, 2,   29, '2025-04-01 13:00:00'),
          (4,  'Neovim user here. My setup: LazyVim base config + Harpoon for navigation + Telescope + nvim-dap for debugging.',      4, 2, NULL, 61, '2025-04-02 10:00:00'),
          (5,  'Still on VS Code but the Vim extension is getting better. Baby steps.',                                              7, 2, NULL, 22, '2025-04-02 11:00:00'),
          (6,  'Patched on Ubuntu already. Debian stable still waiting. If you''re running anything exposed to untrusted XML, patch now.',3, 3, NULL,134, '2025-04-03 09:00:00'),
          (7,  'This affects anything using libexpat directly: Python''s xml.etree, PHP''s libxml, and a bunch of C apps.',           6, 3, NULL, 98, '2025-04-03 10:00:00'),
          (8,  'Because ORMs make it feel like you don''t need to think about SQL. Then someone hand-writes a query for performance and skips sanitisation.',4, 4, NULL, 77, '2025-04-04 15:00:00'),
          (9,  'Framework defaults save you but the moment you step outside them you''re on your own.',                              5, 4, NULL, 54, '2025-04-04 16:00:00'),
          (10, 'The DB was also accessible from the web root. You could curl /data/subverse.db and get the whole thing. Check your FTP server too — sometimes backups are left there.',1, 5, NULL, 41, '2025-04-05 12:00:00'),
          (11, 'Classic. Found the same thing last year. /data/*.db exposed via nginx misconfiguration.',                            3, 5, NULL, 38, '2025-04-05 13:00:00'),
          (12, 'Sounds great! Where are you going?',                                                                                5, 6, NULL, 12, '2025-04-06 18:00:00'),
          (13, '"The Phoenix Project" if you haven''t read it. Great for understanding DevOps culture alongside technical skills.',   4, 7, NULL, 44, '2025-04-07 21:00:00'),
          (14, '"Staff Engineer" by Will Larson is excellent for senior IC career paths.',                                           6, 7, NULL, 31, '2025-04-07 22:00:00'),
          (15, 'The AI pivot is real. I know two ML engineers who got pulled from cloud teams into LLM work last quarter.',          4, 8, NULL, 88, '2025-04-08 08:00:00'),
          (16, 'Running Podman in production for 18 months now. Rootless + systemd integration is solid. No regrets.',              6,10, NULL, 67, '2025-04-10 12:00:00'),
          (17, 'Docker Desktop licensing was the push we needed to finally migrate to Podman.',                                     4,10, NULL, 45, '2025-04-10 13:00:00'),
          (18, 'Good guide. Would add: always use the passive mode for intruder if you''re rate-limited.',                          3,11, NULL, 22, '2025-04-11 15:30:00'),
          (19, 'Three-node Proxmox cluster! What''s your replication setup? ZFS mirror or Ceph?',                                   5,12, NULL, 39, '2025-04-12 17:00:00'),
          (20, 'ZFS mirror for now. Will add Ceph when I get a 4th node.',                                                         4,12, 19,  28, '2025-04-12 18:00:00'),
          (21, 'YAML is a pox. I''m on the TOML side. The fact that `no` and `false` and `off` all mean boolean false is a crime.',8,14, NULL,112, '2025-04-14 10:00:00'),
          (22, 'Counterpoint: YAML is readable when used for simple config. The problem is people trying to do logic in it.',       7,14, NULL, 34, '2025-04-14 11:00:00'),
          (23, 'PortSwigger Web Academy is the best free AppSec resource I''ve found. Do every lab, not just the easy ones.',       3,28, NULL, 56, '2025-04-28 16:00:00'),
          (24, 'TCM Security Practical Bug Bounty is great for methodology. Pair it with Web Academy for the technical depth.',     6,28, NULL, 41, '2025-04-28 17:00:00'),
          (25, 'The SSRF write-up is in my blog. Link in bio.',                                                                     3,18, NULL,118, '2025-04-18 12:00:00'),
          (26, 'Great post. Would add: check for SSRF in webhook URLs, image upload endpoints, and PDF generators.',               6,18, NULL, 87, '2025-04-18 13:00:00'),
          (27, 'WezTerm all the way. Lua config, GPU-accelerated, and multiplexer built in.',                                      4,17, NULL, 44, '2025-04-17 15:00:00'),
          (28, 'Ghostty is finally in stable. The performance on macOS is insane.',                                                 6,17, NULL, 38, '2025-04-17 16:00:00'),
          (29, 'The no-GIL change is opt-in in 3.14. Still experimental but the benchmarks are promising.',                        3,27, NULL, 61, '2025-04-27 11:00:00'),
          (30, 'Zero-trust is the right direction but the tooling is still fragmented. Which vendor did you go with?',             4,26, NULL, 29, '2025-04-26 15:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO messages (id, sender_id, recipient_id, subject, body, read, created_at) VALUES
          (1, 1, 2, 'Site secret key — DO NOT SHARE',
              'Alice, storing this here for the record. Flask SECRET_KEY: subverse-2026-xK9mQp7\nDB is at /data/subverse.db\nDo not share outside the team.',
              0, '2025-04-01 00:00:00'),
          (2, 2, 4, 'Welcome to SubVerse',
              'Hi sv_dan, welcome to the community! Let us know if you have any questions.',
              1, '2025-04-10 12:00:00'),
          (3, 3, 6, 'Your report on CVE-2025-3141',
              'Hey tech_marcus, great post on the CVE. Would you be interested in writing a longer breakdown for the security community?',
              1, '2025-04-03 14:00:00'),
          (4, 1, 3, 'Mod action required — post #30',
              'Bob, post #30 is a draft that got indexed somehow. Please review and ensure it is not visible to the public. The password rotation details cannot leak.',
              0, '2025-04-30 09:00:00'),
          (5, 4, 5, 'Your homelab post',
              'Kate, saw your comment on my homelab post. Happy to answer any Proxmox questions!',
              1, '2025-04-12 19:00:00'),
          (6, 6, 3, 'JWT research collab',
              'Bob, I''ve been working on an extension to the alg:none research. Want to co-author a post?',
              0, '2025-04-25 10:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO mod_log (id, community_id, mod_id, action, target_id, reason, created_at) VALUES
          (1, 2, 3, 'remove_post',  99,  'Spam — unrelated product advertisement.',              '2025-03-10 10:00:00'),
          (2, 1, 2, 'ban_user',    999,  'Repeated rule violations after two warnings.',          '2025-03-15 14:00:00'),
          (3, 3, 2, 'remove_post', 998,  'Off-topic and inflammatory.',                           '2025-03-20 11:00:00'),
          (4, 2, 3, 'pin_post',      3,  'Important security advisory — pinned for visibility.', '2025-04-03 08:05:00'),
          (5, 1, 2, 'remove_comment',21, 'Targeted harassment.',                                 '2025-04-14 12:00:00'),
          (6, 4, 3, 'pin_post',     21,  'Breaking news — pinned.',                              '2025-04-21 06:05:00'),
          (7, 5, 1, 'add_moderator', 2,  'Alice promoted to staff community mod.',               '2025-01-05 08:00:00');
    """)

    db.commit()
    db.close()
