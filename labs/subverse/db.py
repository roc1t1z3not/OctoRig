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

        CREATE TABLE IF NOT EXISTS _flags (
            name  TEXT PRIMARY KEY,
            value TEXT
        );

        INSERT OR IGNORE INTO _flags VALUES ('sqli-search', 'FLAG{sv_sqli_search_union}');
    """)

    # MD5 hashes — plaintext passwords (all in rockyou.txt):
    #  1:admin         commonhuman-lab → 36b809e24478355e344545720ea7e090
    #  2:mod_alice      password1       → 7c6a180b36896a0a8c02787eeafb0e4c
    #  3:mod_bob        letmein         → 0d107d09f5bbe40cade3de5c71e9e9b7
    #  4:cipher_dev     sunshine1       → d5c0607301ad5d5c1528962a83992ac8
    #  5:rootkit_rose   baseball99      → e65c8afc9951f94fed8873a4c1e31a63
    #  6:nullptr_       iloveyou        → f25a2fc72690b780b2a14e140ef6a9e0
    #  7:hexdump_hero   monkey123       → cc25c0f861a83f5efadc6e1ba9d1269e
    #  8:ghost_signal   dragon99        → b696aef7776367787253dc2acdd10279
    #  9:terminal_kai   hacktheplanet   → 1b3231655cebb7a1f783eddf27d254ca
    # 10:sudo_sarah     qwerty123       → 865d6c4a566268abf14e5da76c71bff9
    # 11:packet_pete    password        → 5f4dcc3b5aa765d61d8327deb882cf99
    # 12:devsec_dia     123456          → e10adc3949ba59abbe56e057f20f883e
    # 13:shellcode_sam  master          → 9a0364b9e99bb480dd25e1f0284c8555
    # 14:xor_xena       princess        → 8afa847f50a716e64932d995c8e7435a
    # 15:fuzzr_felix    dragon          → 8621ffdbc5698829397d97767ac13db3
    # 16:netcat_neo     abc123          → e99a18c428cb38d5f260853678922e03
    # 17:bytesmith      monkey          → d0763edaa9d9bd2a9516280e9044d885
    # 18:vuln_viv       shadow          → 67aeea294e1cb515236c73ac6e6eaa93
    # 19:traceroute_ty  qwerty          → d8578edf8458ce06fbc5bb76a58c5ca4
    # 20:asm_archer     superman        → 84d961568a65073a3bcf0eb216b2a576
    db.executescript("""
        INSERT OR IGNORE INTO users (id, username, email, password_hash, role, karma, bio, created_at) VALUES
          (1,  'admin',         'admin@subverse.local',          '36b809e24478355e344545720ea7e090', 'admin',      9999, 'Site administrator. I keep the lights on.',                              '2025-01-01 00:00:00'),
          (2,  'mod_alice',     'alice@subverse.local',          '7c6a180b36896a0a8c02787eeafb0e4c', 'moderator',  4812, 'Community moderator. Blue team by day, CTF player by night.',            '2025-01-05 08:00:00'),
          (3,  'mod_bob',       'bob@subverse.local',            '0d107d09f5bbe40cade3de5c71e9e9b7', 'moderator',  3541, 'Security researcher. I find bugs so you don''t have to.',               '2025-01-06 09:00:00'),
          (4,  'cipher_dev',    'cipher@mail.example',           'd5c0607301ad5d5c1528962a83992ac8', 'user',        967, 'Rust evangelist. Homelab hoarder. Ex-sysadmin.',                         '2025-02-10 12:00:00'),
          (5,  'rootkit_rose',  'rose.r@mail.example',           'e65c8afc9951f94fed8873a4c1e31a63', 'user',        731, 'Pentester in training. Loves CTFs and bad puns.',                        '2025-02-14 15:30:00'),
          (6,  'nullptr_',      'null@mail.example',             'f25a2fc72690b780b2a14e140ef6a9e0', 'user',        889, 'Low-level systems. C/Asm/Rust. If it runs on bare metal I want in.',     '2025-02-20 11:00:00'),
          (7,  'hexdump_hero',  'hex@mail.example',              'cc25c0f861a83f5efadc6e1ba9d1269e', 'user',        512, 'Malware analyst and reverse engineer. Runs Linux on everything.',         '2025-03-01 09:45:00'),
          (8,  'ghost_signal',  'ghost@mail.example',            'b696aef7776367787253dc2acdd10279', 'user',         88, 'Just lurking. Learning web security.',                                   '2025-03-15 20:00:00'),
          (9,  'terminal_kai',  'kai.t@mail.example',            '1b3231655cebb7a1f783eddf27d254ca', 'user',        344, 'DevOps. k8s, Terraform, Ansible. I automate everything I touch.',        '2025-03-20 10:00:00'),
          (10, 'sudo_sarah',    'sarah.sudo@mail.example',       '865d6c4a566268abf14e5da76c71bff9', 'user',        278, 'Cloud security. AWS cert hunter. Loves serverless and hates YAML.',      '2025-04-01 09:00:00'),
          (11, 'packet_pete',   'pete.p@mail.example',           '5f4dcc3b5aa765d61d8327deb882cf99', 'user',        193, 'Network engineer. Wireshark addict. If it has a MAC address I care.',    '2025-04-05 10:00:00'),
          (12, 'devsec_dia',    'dia.d@mail.example',            'e10adc3949ba59abbe56e057f20f883e', 'user',        441, 'DevSecOps. Shifting security left one pipeline at a time.',              '2025-04-08 11:00:00'),
          (13, 'shellcode_sam', 'sam.sc@mail.example',           '9a0364b9e99bb480dd25e1f0284c8555', 'user',        302, 'Exploit dev and CTF enjoyer. x86-64 or nothing.',                        '2025-04-10 09:00:00'),
          (14, 'xor_xena',      'xena.x@mail.example',           '8afa847f50a716e64932d995c8e7435a', 'user',        215, 'Crypto and protocol analysis. Making XOR great again.',                  '2025-04-12 14:00:00'),
          (15, 'fuzzr_felix',   'felix.fz@mail.example',         '8621ffdbc5698829397d97767ac13db3', 'user',        167, 'Fuzzing enthusiast. AFL++, libFuzzer, and too much coffee.',             '2025-04-15 08:00:00'),
          (16, 'netcat_neo',    'neo.nc@mail.example',           'e99a18c428cb38d5f260853678922e03', 'user',        389, 'Pentester. Everything is a shell if you are brave enough.',             '2025-04-18 10:00:00'),
          (17, 'bytesmith',     'byte.s@mail.example',           'd0763edaa9d9bd2a9516280e9044d885', 'user',        122, 'Firmware dev and embedded systems hacker. JTAG is my debugger.',         '2025-04-20 12:00:00'),
          (18, 'vuln_viv',      'viv.v@mail.example',            '67aeea294e1cb515236c73ac6e6eaa93', 'user',        267, 'Vulnerability researcher. Bug bounty hunter. n-day collector.',          '2025-04-22 09:00:00'),
          (19, 'traceroute_ty', 'ty.tr@mail.example',            'd8578edf8458ce06fbc5bb76a58c5ca4', 'user',         99, 'Network security and threat hunting. Logs tell all stories.',            '2025-04-25 11:00:00'),
          (20, 'asm_archer',    'archer.asm@mail.example',       '84d961568a65073a3bcf0eb216b2a576', 'user',        178, 'Assembly programmer. Writing shellcode since it was called shellcode.',   '2025-04-28 08:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO communities (id, name, description, created_by, member_count, announcement, created_at) VALUES
          (1, 'technology', 'Tech news, tools, and discussion for builders and tinkerers.',               1, 2841, '', '2025-01-01 00:00:00'),
          (2, 'security',   'Cybersecurity, CTFs, exploit dev, and defensive techniques.',                1, 1203, '', '2025-01-01 00:00:00'),
          (3, 'offtopic',   'Everything that doesn''t fit elsewhere. Be excellent to each other.',        2,  847, '', '2025-01-02 00:00:00'),
          (4, 'news',       'World news, tech industry events, and current affairs.',                     2, 3122, '', '2025-01-02 00:00:00'),
          (5, 'devops',     'Infrastructure, CI/CD, containers, and cloud — the boring stuff that keeps it all running.', 3, 1074, '', '2025-01-10 00:00:00'),
          (6, 'reverseeng', 'Reverse engineering, malware analysis, binary exploitation, and low-level wizardry.',        3,  618, '', '2025-01-12 00:00:00'),
          (7, 'hidden',     'Private staff community — moderators only.',                                 1,    3, 'FLAG{sv_recon_hidden_community} — Staff area. If you are reading this and you are not a moderator, you found a bug. Good work. Visit /commonhuman.', '2025-01-01 00:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO community_members (user_id, community_id, role, joined_at) VALUES
          (1, 1, 'moderator', '2025-01-01 00:00:00'), (1, 2, 'moderator', '2025-01-01 00:00:00'),
          (1, 7, 'moderator', '2025-01-01 00:00:00'), (2, 1, 'moderator', '2025-01-05 08:00:00'),
          (2, 3, 'moderator', '2025-01-05 08:00:00'), (2, 7, 'moderator', '2025-01-05 08:00:00'),
          (3, 2, 'moderator', '2025-01-06 09:00:00'), (3, 4, 'moderator', '2025-01-06 09:00:00'),
          (3, 5, 'moderator', '2025-01-10 00:00:00'), (3, 6, 'moderator', '2025-01-12 00:00:00'),
          (4, 1, 'member', '2025-02-10 12:00:00'), (4, 2, 'member', '2025-02-11 13:00:00'),
          (4, 5, 'member', '2025-02-12 09:00:00'), (5, 2, 'member', '2025-02-14 15:30:00'),
          (5, 3, 'member', '2025-02-14 16:00:00'), (5, 6, 'member', '2025-02-15 10:00:00'),
          (6, 1, 'member', '2025-02-20 11:00:00'), (6, 2, 'member', '2025-02-21 10:00:00'),
          (6, 6, 'member', '2025-02-22 08:00:00'), (7, 6, 'member', '2025-03-01 09:45:00'),
          (7, 2, 'member', '2025-03-02 10:00:00'), (7, 3, 'member', '2025-03-03 11:00:00'),
          (8, 1, 'member', '2025-03-15 20:00:00'), (8, 2, 'member', '2025-03-16 19:00:00'),
          (9, 5, 'member', '2025-03-20 10:00:00'), (9, 1, 'member', '2025-03-21 09:00:00'),
          (10, 2, 'member', '2025-04-01 09:00:00'), (10, 4, 'member', '2025-04-02 10:00:00'),
          (11, 1, 'member', '2025-04-05 10:00:00'), (11, 4, 'member', '2025-04-06 09:00:00'),
          (12, 2, 'member', '2025-04-08 11:00:00'), (12, 5, 'member', '2025-04-09 10:00:00'),
          (13, 2, 'member', '2025-04-10 09:00:00'), (13, 6, 'member', '2025-04-11 08:00:00'),
          (14, 2, 'member', '2025-04-12 14:00:00'), (14, 6, 'member', '2025-04-13 13:00:00'),
          (15, 2, 'member', '2025-04-15 08:00:00'), (15, 6, 'member', '2025-04-16 07:00:00'),
          (16, 2, 'member', '2025-04-18 10:00:00'), (16, 1, 'member', '2025-04-19 09:00:00'),
          (17, 6, 'member', '2025-04-20 12:00:00'), (17, 1, 'member', '2025-04-21 11:00:00'),
          (18, 2, 'member', '2025-04-22 09:00:00'), (18, 4, 'member', '2025-04-23 08:00:00'),
          (19, 4, 'member', '2025-04-25 11:00:00'), (19, 2, 'member', '2025-04-26 10:00:00'),
          (20, 6, 'member', '2025-04-28 08:00:00'), (20, 2, 'member', '2025-04-29 07:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO posts (id, title, body, user_id, community_id, score, status, flair, created_at) VALUES
          (1,  'Rust is eating Python''s lunch in systems tooling',
                'Hot take: the new wave of Rust-based CLI tools (ripgrep, fd, bat, exa) are so much faster that Python tools will be relegated to scripting glue within 5 years. Discuss.',
                4, 1, 312, 'published', 'Discussion', '2025-04-01 10:00:00'),
          (2,  'Anyone else using Neovim full-time in 2025?',
                'Switched from VS Code six months ago and haven''t looked back. Treesitter + LSP + lazy.nvim is actually a joy to use. What plugins are you running?',
                6, 1, 189, 'published', 'Tools', '2025-04-02 09:30:00'),
          (3,  'CVE-2025-3141: Critical RCE in libexpat — patch now',
                'A critical heap overflow in libexpat (versions < 2.7.1) allows remote code execution via a malformed XML entity. CVSS 9.8. Most Linux distros have pushed patches — update your systems.',
                3, 2, 547, 'published', 'Alert', '2025-04-03 08:00:00'),
          (4,  'SQL injection still #1 in OWASP Top 10 — why in 2025?',
                'It''s 2025 and SQLi is still the most common critical finding in web app audits. Parameterised queries have been the answer since the 90s. Why do developers keep getting this wrong?',
                6, 2, 233, 'published', 'Discussion', '2025-04-04 14:00:00'),
          (5,  'Found a Flask app storing passwords in plaintext',
                'During a pentest this week I found a Flask app storing user passwords in plain text in SQLite. The admin password was "commonhuman-lab". Filed the report. Reminder: check your /data/ directories and FTP servers for backup files.',
                3, 2,  88, 'published', 'Story', '2025-04-05 11:00:00'),
          (6,  'Weekend plans — escaping the screen?',
                'Going hiking up in the mountains this weekend. Anyone else trying to detox from the terminal for a couple of days?',
                7, 3,  42, 'published', '', '2025-04-06 17:00:00'),
          (7,  'What are you reading right now?',
                'Just finished "The Pragmatic Programmer" for the third time and still finding new things. Recommendations for the next book — technical or otherwise?',
                5, 3,  61, 'published', '', '2025-04-07 20:00:00'),
          (8,  'Tech layoffs continue into Q2 2025',
                'Three major cloud providers announced another round of layoffs this week, totalling 12,000 jobs. The restructuring is said to focus on shifting headcount to AI divisions.',
                2, 4, 891, 'published', 'Industry', '2025-04-08 07:00:00'),
          (9,  'EU passes landmark AI regulation act',
                'The European Parliament passed the AI Act with 523 votes in favour. High-risk AI systems will require mandatory audits and human oversight. Full enforcement begins 2026.',
                3, 4, 634, 'published', 'Policy', '2025-04-09 08:30:00'),
          (10, 'Docker vs Podman in 2025 — migration stories',
                'With Podman going rootless by default and Docker Desktop licensing changes I have seen a lot of teams switching. What did your migration look like? Any gotchas?',
                4, 5, 156, 'published', 'Discussion', '2025-04-10 11:00:00'),
          (11, 'Beginner''s guide to Burp Suite I wrote up',
                'Comprehensive intro to Burp Suite Community for beginners. Covers proxy setup, repeater, intruder basics, and decoder. Feedback welcome.',
                16, 2,  99, 'published', 'Guide', '2025-04-11 14:30:00'),
          (12, 'My homelab setup — 2025 edition',
                'Updated my homelab: Proxmox on three nodes, TrueNAS Scale for storage, Pi-hole + Unbound for DNS, Traefik for reverse proxy. Running about 40 Docker services.',
                4, 1, 204, 'published', 'Homelab', '2025-04-12 16:00:00'),
          (13, 'Working through HackTheBox Starting Point — tips?',
                'I''ve been doing the HTB Starting Point series. Great for enumeration and basic exploitation fundamentals. What machines should I tackle next?',
                5, 2,  77, 'published', 'Training', '2025-04-13 18:00:00'),
          (14, 'Hot take: YAML is a terrible config language',
                'Indentation-sensitive, inconsistent boolean handling, surprise type coercions. TOML or even JSON would be better for most use cases. Fight me.',
                8, 1, 445, 'published', 'Hot Take', '2025-04-14 09:00:00'),
          (15, 'Cloudflare outage post-mortem published',
                'Root cause: misconfigured BGP route that propagated globally before being caught. Good read on their detection pipeline and response timeline.',
                2, 4, 312, 'published', 'Incident', '2025-04-15 10:00:00'),
          (16, 'WireGuard setup guide for self-hosters',
                'Step-by-step guide to WireGuard VPN on a $5 VPS. Covers key generation, peer config, routing, and split-tunnel vs full-tunnel. Tested on Debian 12.',
                6, 1, 188, 'published', 'Guide', '2025-04-16 12:00:00'),
          (17, 'Best terminal emulators in 2025 — benchmarks',
                'Alacritty, Kitty, WezTerm, and Ghostty compared. GPU-accelerated terminals are now basically the standard. Benchmarks on throughput and latency included.',
                4, 1, 134, 'published', 'Tools', '2025-04-17 14:00:00'),
          (18, 'SSRF exploitation chain: metadata → cloud creds → RCE',
                'Full SSRF exploitation walkthrough: internal metadata service → cloud credentials → S3 bucket listing → RCE via CI/CD webhook trigger.',
                3, 2, 421, 'published', 'Research', '2025-04-18 11:00:00'),
          (19, 'Favourite terminal one-liners?',
                'Mine: `find . -name "*.log" -mtime +30 -delete` and `jq ''.[] | select(.status=="error")'' errors.json`. Drop yours in the comments.',
                7, 1, 267, 'published', '', '2025-04-19 15:00:00'),
          (20, 'Is Go still worth learning in 2025?',
                'With Rust taking over systems programming and Python dominating ML, where does Go fit? Kubernetes and cloud tooling keeps it relevant. Thoughts?',
                6, 1, 143, 'published', 'Discussion', '2025-04-20 10:00:00'),
          (21, 'Breaking: 350M user records exposed in social platform breach',
                'Records include hashed passwords, private messages, and phone numbers. Threat actor claims data was exfiltrated via an unsecured internal API endpoint.',
                2, 4, 1240, 'published', 'Breaking', '2025-04-21 06:00:00'),
          (22, 'Climate summit reaches binding carbon agreement',
                'World leaders signed a new carbon reduction treaty today, committing to 50% emission cuts by 2035. Enforcement mechanism differs from Paris — actual trade penalties this time.',
                3, 4, 456, 'published', 'World', '2025-04-22 07:30:00'),
          (23, 'Tips for staying productive WFH — three years in',
                'Three years remote and I''m still fighting the afternoon slump. What routines or tools have actually helped you stay focused?',
                5, 3,  93, 'published', '', '2025-04-23 13:00:00'),
          (24, 'Understanding JWT algorithm confusion attacks',
                'Quick breakdown of the alg:none attack and RS256 to HS256 confusion. Both are still found in production apps in 2025. Code examples and mitigation checklist included.',
                3, 2, 318, 'published', 'Research', '2025-04-24 09:00:00'),
          (25, 'Zero-trust architecture: what the vendors don''t tell you',
                'Moved our org to zero-trust last year. The sales pitch is clean; the reality is painful. Here''s what actually broke and where we ended up.',
                6, 2, 204, 'published', 'Guide', '2025-04-25 14:00:00'),
          (26, 'Python 3.14 free-threaded mode benchmarks',
                'PEP 703 (no-GIL) experimental mode in Python 3.14 is showing 2-4x improvements on CPU-bound multi-threaded workloads. Game changer for data pipelines.',
                4, 1, 376, 'published', 'News', '2025-04-26 10:00:00'),
          (27, 'Ask SubVerse: best resources for breaking into AppSec?',
                'Career pivot from Python dev to AppSec. Strong programming background, decent Linux skills. Where do I start? Budget is limited.',
                5, 2, 112, 'published', 'Ask SV', '2025-04-27 15:30:00'),
          (28, 'Self-hosted SaaS replacements — full stack for $12/mo',
                'Replaced Notion with Obsidian + Syncthing, Slack with Mattermost, Google Analytics with Plausible, and Zoom with Jitsi. One $12 VPS. Full config notes.',
                4, 1, 529, 'published', 'Self-hosted', '2025-04-28 12:00:00'),
          (29, 'Kubernetes the hard way — still worth it in 2025?',
                'Kelsey Hightower''s guide teaches you how the pieces fit together at a level that k3s and managed clusters paper over. Did it last month on bare VMs. Worth every painful hour.',
                9, 5, 287, 'published', 'Guide', '2025-04-29 10:00:00'),
          (30, 'GitHub Actions vs GitLab CI vs Drone — comparison 2025',
                'Evaluation of three CI/CD platforms for our migration. Scoring on: YAML ergonomics, secrets management, self-hosted runner support, cost, and debugging experience.',
                9, 5, 198, 'published', 'Discussion', '2025-04-30 11:00:00'),
          (31, 'Reverse engineering an IoT firmware image — walkthrough',
                'Extracted firmware via UART, unpacked squashfs, found hardcoded credentials and an undocumented telnet backdoor. Full methodology from binwalk to root shell.',
                7, 6, 534, 'published', 'Walkthrough', '2025-05-01 09:00:00'),
          (32, 'Intro to ELF binary analysis with radare2',
                'Walkthrough of r2 on a stripped x86-64 ELF: find main, recover function names with aaa, set breakpoints, and patch a simple license check. Beginner-friendly.',
                7, 6, 312, 'published', 'Guide', '2025-05-02 14:00:00'),
          (33, 'Heap exploitation primitives — use-after-free on glibc 2.39',
                'Deep dive into UAF exploitation on modern glibc. Covers tcache poisoning, safe-linking bypass, and reliable arbitrary write. Tested on Ubuntu 24.04 LTS.',
                6, 6, 441, 'published', 'Research', '2025-05-03 10:00:00'),
          (34, 'Terraform state management at scale',
                'Managing Terraform state across 40+ environments: remote state locking, workspace sprawl, module versioning, and why you need Atlantis or similar in production.',
                9, 5, 167, 'published', 'Story', '2025-05-04 11:00:00'),
          (35, 'Cloud cost optimization: cut our AWS bill by 60%',
                'Went from $28k/mo to $11k/mo over six months. Biggest wins: Reserved Instances, S3 Intelligent Tiering, CloudFront caching, and killing zombie resources.',
                10, 5, 723, 'published', 'Story', '2025-05-05 09:30:00'),
          (36, 'Open source LLMs are closing the gap fast',
                'Llama 3.3, Mistral Large, and Qwen 2.5 performing surprisingly close to GPT-4 on coding benchmarks. Running locally on a consumer GPU is now actually viable.',
                4, 4, 891, 'published', 'AI', '2025-05-06 08:00:00'),
          (37, 'Governments mandating memory-safe languages for critical systems',
                'NSA, CISA, and ENISA issued guidance pushing agencies toward memory-safe languages for new development. C/C++ legacy systems need migration plans.',
                3, 4, 567, 'published', 'Policy', '2025-05-07 07:30:00'),
          (38, 'Show SubVerse: terminal Pomodoro timer in Rust',
                'After getting tired of browser tab timers I built a minimal Pomodoro timer in Rust with a TUI. 450 lines, no async runtime, works in tmux. Source on GitHub.',
                4, 1, 234, 'published', 'Show SV', '2025-05-08 16:00:00'),
          (39, 'What''s your OpSec setup for your personal threat model?',
                'Curious what people here actually use day-to-day. I''m on Qubes OS, Signal, Mullvad, and FIDO2 keys everywhere. Looking for gaps I might have missed.',
                5, 2, 189, 'published', 'Ask SV', '2025-05-09 14:00:00'),
          (40, 'Coffee shop recommendations for remote workers in Berlin',
                'Looking for places with fast wifi, outlets, and staff who won''t kick you out after two coffees. Mitte or Kreuzberg preferred.',
                7, 3,  38, 'published', '', '2025-05-10 11:00:00'),
          (41, 'IaC security scanning: tfsec, Checkov, and Terrascan compared',
                'Ran all three scanners against our production Terraform repo. Comparison of false positive rate, rule coverage, CI integration, and remediation guidance.',
                10, 5, 143, 'published', 'Tools', '2025-05-11 10:00:00'),
          (42, 'Unpacking obfuscated PowerShell malware step by step',
                'Analysed an Emotet dropper from a phishing campaign. Walked through four layers of base64, string reversal, and XOR obfuscation before getting to the payload stager.',
                7, 6, 388, 'published', 'Walkthrough', '2025-05-12 09:00:00'),
          (43, 'We moved our monolith to k8s — here''s what broke',
                'Six-month migration from bare-metal monolith to Kubernetes. Database connection pooling, session state, file uploads, cron jobs — each had a surprise.',
                9, 5, 456, 'published', 'Story', '2025-05-13 11:00:00'),
          (44, 'Minimal Linux from scratch: booting a 1.2MB kernel + init',
                'Built a minimal bootable Linux system: custom kernel config, a 300-line C init, and a squashfs root. Blog post series on the full process.',
                6, 1, 312, 'published', 'Deep Dive', '2025-05-14 14:00:00'),
          (45, 'Fuzzing 101: getting started with AFL++ on a real target',
                'Walked through setting up AFL++ on a real open-source project, from instrumented build to first crash. Triage, minimisation, and reporting workflow included.',
                15, 2, 244, 'published', 'Guide', '2025-05-15 10:00:00'),
          (46, 'Shodan for defenders — finding your exposed assets first',
                'Most orgs discover their external exposure from bug bounty reports. Here is how to use Shodan and Censys to audit your own perimeter before someone else does.',
                18, 2, 312, 'published', 'Guide', '2025-05-16 09:00:00'),
          (47, 'Custom shellcode loader in C — evading signature detection',
                'Built a shellcode loader that decrypts and executes payload in memory, avoiding common AV signatures. Process injection via QueueUserAPC. Educational walkthrough.',
                20, 6, 278, 'published', 'Research', '2025-05-17 11:00:00'),
          (48, 'Packet capture analysis workflow — from PCAP to indicators',
                'My workflow for turning raw packet captures into threat intel: Wireshark filters, tshark one-liners, Zeek parsing, and enriching IPs via threat feeds.',
                11, 2, 167, 'published', 'Workflow', '2025-05-18 10:00:00'),
          (49, 'SAST tools comparison: CodeQL, Semgrep, and SonarQube',
                'Ran all three against the same vulnerable-by-design codebase. Precision vs recall tradeoffs, false positive rates, and CI integration notes.',
                12, 5, 198, 'published', 'Tools', '2025-05-19 11:00:00'),
          (50, 'DRAFT: Admin password rotation — DO NOT POST',
                'INTERNAL DRAFT — This post should not be visible to regular users.\n\nNew admin password will be changed to: subverse2025admin\nEffective date: next Monday 09:00 UTC\nDo not share this information outside of the moderation team.\n\nFLAG{sv_idor_draft_post_read}',
                1, 7,   0, 'draft', '', '2025-05-20 08:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO comments (id, body, user_id, post_id, parent_id, score, created_at) VALUES
          -- Post 1: Rust vs Python
          (1,  'Completely agree on ripgrep. 40x faster than grep for my use case. The Rust ecosystem is maturing fast.',              6,  1, NULL, 87, '2025-04-01 11:00:00'),
          (2,  'Hot take rejected. Python has the ecosystem, Rust has the learning curve. They will coexist for decades.',             5,  1, NULL, 43, '2025-04-01 12:00:00'),
          (3,  'Both can be true. Rust for performance-critical tooling, Python for glue and automation.',                             4,  1,    2, 29, '2025-04-01 13:00:00'),
          (4,  'uv and ruff are Rust-based Python tooling and they are genuinely game-changing. Best of both worlds.',               11,  1, NULL, 35, '2025-04-01 14:00:00'),
          -- Post 2: Neovim
          (5,  'My config: LazyVim base + Harpoon for navigation + Telescope + nvim-dap for debugging. No regrets.',                  4,  2, NULL, 61, '2025-04-02 10:00:00'),
          (6,  'Still on VS Code but the Neovim extension keeps me from fully committing. Baby steps.',                              14,  2, NULL, 22, '2025-04-02 11:00:00'),
          (7,  'The moment you muscle-memory your way through a motion it clicks. Give it 2 weeks of pain and you will not go back.', 7,  2, NULL, 44, '2025-04-02 12:00:00'),
          -- Post 3: libexpat CVE
          (8,  'Patched on Ubuntu 24.04 via apt already. Debian stable still waiting. Patch now if you expose untrusted XML.',        3,  3, NULL,134, '2025-04-03 09:00:00'),
          (9,  'This affects Python xml.etree, PHP libxml, and any C app that links libexpat directly.',                              6,  3, NULL, 98, '2025-04-03 10:00:00'),
          (10, 'CVSS 9.8 in the default package list of most distros. Going to be exploited in the wild within days.',               5,  3, NULL, 71, '2025-04-03 11:00:00'),
          -- Post 4: SQLi
          (11, 'ORMs make it feel like you never need to think about SQL. Then someone writes a raw query for performance.',          4,  4, NULL, 77, '2025-04-04 15:00:00'),
          (12, 'Framework defaults protect you but the moment you step outside them you are on your own.',                           5,  4, NULL, 54, '2025-04-04 16:00:00'),
          (13, 'The SQLi finding that still gets me: string formatting inside a stored procedure. Devs thought the DB layer was safe.',3, 4, NULL, 66, '2025-04-04 17:00:00'),
          -- Post 5: plaintext passwords
          (14, 'The DB was also accessible from the web root. Check your FTP server too — database backups sometimes end up there.',  1,  5, NULL, 41, '2025-04-05 12:00:00'),
          (15, 'Classic. Found the same last year — /data/*.db via an nginx alias that was one character too broad.',                 3,  5, NULL, 38, '2025-04-05 13:00:00'),
          -- Post 10: Docker vs Podman
          (16, 'Running Podman in production for 18 months. Rootless + systemd integration is solid.',                               6, 10, NULL, 67, '2025-04-10 12:00:00'),
          (17, 'Docker Desktop licensing was the final push we needed to migrate.',                                                   4, 10, NULL, 45, '2025-04-10 13:00:00'),
          (18, 'Podman compose is still rougher than docker-compose for local dev. That is the one holdback.',                       9, 10, NULL, 31, '2025-04-10 14:00:00'),
          -- Post 12: homelab
          (19, 'Three-node Proxmox cluster — ZFS mirror or Ceph for replication?',                                                   5, 12, NULL, 39, '2025-04-12 17:00:00'),
          (20, 'ZFS mirror for now. Will add Ceph when budget allows for a fourth node.',                                            4, 12,   19, 28, '2025-04-12 18:00:00'),
          -- Post 14: YAML hot take
          (21, 'YAML is a pox. The fact that `no`, `false`, and `off` all parse as boolean false is a crime.',                       8, 14, NULL,112, '2025-04-14 10:00:00'),
          (22, 'YAML is readable for simple config. The problem is people using it as a programming language.',                      7, 14, NULL, 34, '2025-04-14 11:00:00'),
          (23, 'TOML is YAML but sane. Fight me back.',                                                                              6, 14, NULL, 88, '2025-04-14 12:00:00'),
          -- Post 18: SSRF
          (24, 'The full SSRF write-up for this chain is on my blog. Link in bio.',                                                  3, 18, NULL,118, '2025-04-18 12:00:00'),
          (25, 'Worth adding: SSRF via PDF generators is criminally underrated as an attack vector.',                                6, 18, NULL, 87, '2025-04-18 13:00:00'),
          (26, 'The metadata to creds chain is so reliable on AWS IMDSv1 it should be considered a design flaw.',                    5, 18, NULL, 54, '2025-04-18 14:00:00'),
          -- Post 24: JWT
          (27, 'The alg:none trick still works against libraries that do not validate the header algorithm server-side.',             4, 24, NULL, 71, '2025-04-24 10:00:00'),
          (28, 'RS256 to HS256 confusion is subtler and catches implementors who only test the happy path.',                         7, 24, NULL, 48, '2025-04-24 11:00:00'),
          -- Post 27: AppSec career
          (29, 'PortSwigger Web Academy is the best free AppSec resource I have found. Do every lab including expert-level.',        3, 27, NULL, 56, '2025-04-27 16:00:00'),
          (30, 'TCM Security Practical Bug Bounty is excellent for methodology. Pair it with Web Academy.',                          6, 27, NULL, 41, '2025-04-27 17:00:00'),
          (31, 'OSCP is worth it for the mindset training. Start with HTB and HTB Academy first to decide if it clicks.',            5, 27, NULL, 33, '2025-04-27 18:00:00'),
          -- Post 29: k8s the hard way
          (32, 'Did this in 2023 and it permanently changed how I debug cluster issues. Everyone who runs k8s in prod should.',      10, 29, NULL, 67, '2025-04-29 11:00:00'),
          (33, 'You cannot really understand why etcd matters until you have watched a split-brain kill your cluster.',               4, 29, NULL, 44, '2025-04-29 12:00:00'),
          -- Post 31: IoT firmware
          (34, 'Found the same thing on a smart plug last year — telnet on port 23 with root and no password.',                      5, 31, NULL, 89, '2025-05-01 10:00:00'),
          (35, 'Binwalk plus Jefferson for JFFS2 is my standard starting point.',                                                    6, 31, NULL, 61, '2025-05-01 11:00:00'),
          (36, 'I always check for FTP services on IoT devices. Found default credentials on three devices in the same product line.',17, 31, NULL, 44, '2025-05-01 12:00:00'),
          -- Post 33: heap exploitation
          (37, 'Safe-linking bypass on glibc 2.35+ broke a lot of old techniques. The delta encoding on tcache next pointers is clever.', 7, 33, NULL, 77, '2025-05-03 11:00:00'),
          (38, 'These techniques need ASLR defeated first. Any chance of a follow-up on stack leak primitives?',                     5, 33, NULL, 55, '2025-05-03 12:00:00'),
          (39, 'The format string leak into heap is the primitive I usually reach for first on amd64.',                             20, 33, NULL, 48, '2025-05-03 13:00:00'),
          -- Post 35: AWS cost
          (40, 'Reserved Instances cut our compute by 40%. Convincing finance to commit upfront was the real challenge.',            9, 35, NULL, 88, '2025-05-05 10:30:00'),
          (41, 'S3 Intelligent Tiering took us from $3k/mo to $800/mo on storage. Should have done it two years earlier.',          10, 35, NULL, 72, '2025-05-05 11:00:00'),
          -- Post 38: Rust Pomodoro
          (42, 'Have you considered desktop notifications via libnotify? The timer is useless if you are in a flow state.',          6, 38, NULL, 34, '2025-05-08 17:00:00'),
          (43, 'Planning to add it in v0.2 with the notify-rust crate. Also adding a config file so lengths are not hardcoded.',    4, 38,   42, 22, '2025-05-08 18:00:00'),
          -- Post 42: PowerShell malware
          (44, 'Four layers of obfuscation and the payload was still just a Cobalt Strike beacon. Loaders are commoditised now.',    3, 42, NULL, 66, '2025-05-12 10:00:00'),
          (45, 'The XOR key recovery step is interesting — any chance of sharing the script you used to automate that?',            5, 42, NULL, 44, '2025-05-12 11:00:00'),
          -- Post 43: monolith to k8s
          (46, 'PgBouncer in transaction mode broke every advisory lock we used. That one hurt.',                                    9, 43, NULL, 55, '2025-05-13 12:00:00'),
          (47, 'The cron job problem is underrated. Everyone says use a k8s CronJob but the failure semantics are completely different.', 10, 43, NULL, 41, '2025-05-13 13:00:00'),
          -- Post 44: minimal Linux
          (48, 'This is the kind of content SubVerse was made for.',                                                                 8, 44, NULL, 77, '2025-05-14 15:00:00'),
          (49, 'Did you use syslinux or GRUB for the bootloader? I spent three days fighting GRUB config.',                         5, 44, NULL, 53, '2025-05-14 16:00:00'),
          (50, 'GRUB2 with a minimal grub.cfg — about 8 lines. The hardest part was getting initramfs unpacking order right.',      6, 44,   49, 39, '2025-05-14 17:00:00'),
          -- Post 45: fuzzing
          (51, 'AFL++ persistent mode is the real game-changer. 10-50x throughput compared to fork mode on most targets.',          15, 45, NULL, 61, '2025-05-15 11:00:00'),
          (52, 'Good intro. When you are ready, look at coverage-guided fuzzing with libFuzzer + AddressSanitizer for deeper finds.', 3, 45, NULL, 44, '2025-05-15 12:00:00'),
          -- Post 46: Shodan
          (53, 'The number of orgs that discover open Elasticsearch instances via Shodan before Shodan discovers them for the attacker is depressingly low.', 19, 46, NULL, 67, '2025-05-16 10:00:00'),
          (54, 'Combine with BBOT for automated subdomain enum and you have a decent continuous attack surface monitoring setup.',   18, 46, NULL, 55, '2025-05-16 11:00:00'),
          -- Post 47: shellcode loader
          (55, 'QueueUserAPC is detectable by most EDRs at this point. NtMapViewOfSection is the current preferred injection technique.', 13, 47, NULL, 71, '2025-05-17 12:00:00'),
          (56, 'Good write-up but be careful about the ethics framing here. Evasion research is dual-use and context matters.',     12, 47, NULL, 44, '2025-05-17 13:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO messages (id, sender_id, recipient_id, subject, body, read, created_at) VALUES
          (1, 1, 2, 'Site secret key — DO NOT SHARE',
              'Alice, storing this here for the record. Flask SECRET_KEY: subverse-2026-xK9mQp7\nDB is at /data/subverse.db\nDo not share outside the team.\nFLAG{sv_idor_message_read}',
              0, '2025-04-01 00:00:00'),
          (2, 2, 4, 'Welcome to SubVerse, cipher_dev',
              'Hi cipher_dev, welcome to the community! Looks like you have been posting great content already. Let us know if you have any questions.',
              1, '2025-04-10 12:00:00'),
          (3, 3, 6, 'Your CVE-2025-3141 post',
              'Hey nullptr_, great write-up on the libexpat CVE. Would you be interested in writing a longer technical breakdown for sv/security? We could pin it.',
              1, '2025-04-03 14:00:00'),
          (4, 1, 3, 'Mod action required — post #50',
              'Bob, post #50 is a draft that got indexed somehow. Please review and ensure it is not visible to the public. The password rotation details cannot leak.',
              0, '2025-05-20 09:00:00'),
          (5, 4, 5, 'Re: homelab Proxmox question',
              'rootkit_rose, happy to answer Proxmox questions! ZFS on Linux is stable but memory-hungry — budget 1GB RAM per TB of pool capacity.',
              1, '2025-04-12 19:00:00'),
          (6, 6, 3, 'Heap exploitation collab post',
              'Bob, I have been expanding the UAF research to cover GLIBC 2.40 changes. Want to co-author a follow-up for sv/reverseeng?',
              0, '2025-05-03 15:00:00'),
          (7, 9, 10, 'IaC scanner results',
              'sudo_sarah, saw your comment on the IaC security post. Did you find a way to suppress the S3 block-public-access false positives in Checkov?',
              1, '2025-05-11 11:00:00'),
          (8, 2, 8, 'Your account — welcome',
              'Hey ghost_signal, just checking in — you have been quiet lately. The sv/security community is very welcoming to learners. Jump in!',
              0, '2025-05-14 10:00:00'),
          (9, 15, 13, 'AFL++ corpus minimisation question',
              'shellcode_sam, loved your shellcode loader post. Separate topic: do you have a good workflow for minimising AFL corpora before sharing them?',
              1, '2025-05-16 09:00:00'),
          (10, 18, 16, 'Shodan monitoring automation',
              'netcat_neo, I built a small Python script that wraps the Shodan API and alerts on new results for our IP ranges. Want me to share it?',
              0, '2025-05-17 10:00:00');
    """)

    db.executescript("""
        INSERT OR IGNORE INTO mod_log (id, community_id, mod_id, action, target_id, reason, created_at) VALUES
          (1,  2, 3, 'remove_post',     99,  'Spam — unrelated product advertisement.',                  '2025-03-10 10:00:00'),
          (2,  1, 2, 'ban_user',       999,  'Repeated rule violations after two formal warnings.',      '2025-03-15 14:00:00'),
          (3,  3, 2, 'remove_post',    998,  'Off-topic and inflammatory. Third offence.',               '2025-03-20 11:00:00'),
          (4,  2, 3, 'pin_post',         3,  'Important security advisory — pinned for visibility.',    '2025-04-03 08:05:00'),
          (5,  1, 2, 'remove_comment',  21,  'Targeted harassment. User warned previously.',             '2025-04-14 12:00:00'),
          (6,  4, 3, 'pin_post',        21,  'Breaking news — pinned to top of sv/news.',               '2025-04-21 06:05:00'),
          (7,  7, 1, 'add_moderator',    2,  'Alice promoted to staff community moderator.',             '2025-01-05 08:00:00'),
          (8,  6, 3, 'pin_post',        31,  'Excellent firmware RE walkthrough — pinned.',              '2025-05-01 09:05:00'),
          (9,  5, 3, 'remove_post',    997,  'Vendor spam disguised as a tutorial.',                    '2025-05-10 13:00:00'),
          (10, 2, 2, 'pin_post',        33,  'High-quality heap exploitation research — pinned.',        '2025-05-03 10:05:00');
    """)

    # ── CommonHuman easter egg layer ──────────────────────────────────────────
    # User 21: commonhuman_ — password "octopus" (MD5: fcf1eed8596699624167416a1e7e122e)
    # Karma 1337. Bio hints at /commonhuman. Discoverable via SQLi, IDOR, or
    # robots.txt → /community/hidden → post 52.
    db.executescript("""
        INSERT OR IGNORE INTO users (id, username, email, password_hash, role, karma, bio, created_at) VALUES
          (21, 'commonhuman_', 'lab@commonhuman.example',
               'fcf1eed8596699624167416a1e7e122e',
               'moderator', 1337,
               'I built this place. If you are reading this you found something. Try /commonhuman',
               '2025-01-01 00:00:00');
    """)

    # Community memberships for commonhuman_
    db.executescript("""
        INSERT OR IGNORE INTO community_members (user_id, community_id, role, joined_at) VALUES
          (21, 1, 'member',    '2025-01-01 00:00:00'),
          (21, 2, 'moderator', '2025-01-01 00:00:00'),
          (21, 3, 'member',    '2025-01-01 00:00:00'),
          (21, 7, 'moderator', '2025-01-01 00:00:00');
    """)

    # Posts 51-53: the in-app easter egg content
    # Post 51: sv/security — public post explaining OctoRig (the "CommonHuman-Lab game" equivalent)
    # Post 52: sv/hidden  — internal staff note (IDOR target, discoverable via robots.txt hint)
    # Post 53: sv/offtopic — humorous wink at the player
    db.executescript("""
        INSERT OR IGNORE INTO posts (id, title, body, user_id, community_id, score, status, flair, created_at) VALUES
          (51,
           'OctoRig — the lab platform running this site',
           'Hi SubVerse.\n\nThis site is part of OctoRig — an open-source deliberately vulnerable web application suite built for security training. Every route on this platform has something intentionally broken about it.\n\nA non-exhaustive list of what to look for:\n\n- Login form: SQL injection on both username and password fields\n- Search bar: reflected user input — no sanitisation, returns all rows with a classic payload\n- Post bodies and comments: stored XSS via Jinja2 | safe filter\n- User bios: same — stored XSS, rendered on the profile page\n- Voting: GET-based CSRF — triggerable from any page with a simple img tag\n- Profile edit: mass assignment — role= and karma= are processed from the form body even though they are not in the HTML\n- File uploads: extension check only, no MIME validation — upload a .php named .jpg\n- Community announcements: Jinja2 render_template_string on user input — full SSTI\n- Link preview: subprocess with shell=True and your URL — classic command injection\n- Messages: IDOR — /messages/<id> has no ownership check\n- Draft posts: IDOR — /post/<id>/draft only checks login, not who owns the draft\n- Mod log: IDOR — any logged-in user can read it\n- Password reset: predictable token — md5(username + str(epoch // 3600))\n- Open redirect: /login?next= — not validated\n- Debug mode: app.run(debug=True) — Werkzeug console on unhandled exceptions\n- FTP: anonymous access — interesting files in /pub/\n- SSH: sysadmin / subverse2024 — check .bash_history and .env\n\nIf you found this post without moderator access, you already exploited something.\n\nThe platform is open source. If it has been useful for your training or teaching:\nhttps://github.com/CommonHuman-Lab\n\nAnd when you are ready: /commonhuman',
           21, 2, 42, 'published', 'Meta', '2025-01-02 10:00:00'),

          (52,
           'Staff: platform maintenance checklist — INTERNAL',
           'Internal reference for the moderation team.\n\nSubVerse intentional vulnerability inventory (for lab documentation):\n\n[WEB]\n- SQLi: login, search (/search?q=), communities list, /api/search\n- Stored XSS: post body, comment body, user bio\n- Reflected XSS: search results page (/search?q=)\n- IDOR: /messages/<id>, /post/<id>/draft, /community/<name>/modlog\n- CSRF: vote endpoints use GET with no token\n- Mass assignment: /profile/edit accepts role= karma= from POST body\n- File upload: avatar — extension check only\n- SSTI: /admin/community/<name>/announce — POST-only auth check missing, render_template_string on input\n- Command injection: /post/preview-link — shell=True subprocess\n- Open redirect: /login?next= not validated\n- Broken auth: reset token = md5(username + epoch // 3600)\n- Info disclosure: debug=True, robots.txt, /api/internal returns password hashes\n\n[SSH]\nUser: sysadmin / subverse2024\nArtifacts: /app/.env (secret key), /home/sysadmin/.bash_history, /home/sysadmin/.ssh/id_rsa\n\n[FTP]\nAnonymous access. Files in /pub/:\n- db_backup_2024.sql (MD5 hashes — crack with hashcat + rockyou)\n- deploy_notes.txt (SSH credentials)\n- users_export.csv (PII)\n\n[IDOR targets]\n- Message id=1: admin -> mod_alice, contains Flask SECRET_KEY\n- Post id=50: draft, contains admin password rotation details\n- Post id=52: this document (staff-only, no enforcement)\n\nPlatform: https://github.com/CommonHuman-Lab\nEaster egg route: /commonhuman',
           1, 7, 3, 'published', 'Internal', '2025-01-01 12:00:00'),

          (53,
           'PSA: yes, this entire site is intentionally broken',
           'Just wanted to put this out there in case anyone has been wondering why the voting works from an img tag, why the search bar echoes your input raw, or why the profile edit form accepts a role= field that is not in the HTML.\n\nAll of it is on purpose. This is a training platform.\n\nIf you found this post organically — nice work. If you found it because you ran a SQL injection against the search and got every row back — even better.\n\nSee you at /commonhuman.',
           21, 3, 88, 'published', 'Meta', '2025-01-03 09:00:00');
    """)

    # Comments seeding organic discussion around the easter egg posts
    db.executescript("""
        INSERT OR IGNORE INTO comments (id, body, user_id, post_id, parent_id, score, created_at) VALUES
          -- Post 51: OctoRig explanation
          (57, 'Confirmed the SQLi on login within about 30 seconds. Classic single-quote test. Nice lab.',
               5, 51, NULL, 29, '2025-01-02 11:00:00'),
          (58, 'The SSTI in the announcement editor is my favourite touch. render_template_string on user input in 2025.',
               3, 51, NULL, 34, '2025-01-02 12:00:00'),
          (59, 'Found the FTP anonymous access before I even touched the web app. The db_backup_2024.sql had everything I needed.',
               16, 51, NULL, 41, '2025-01-02 13:00:00'),
          (60, 'The mass assignment on profile edit is sneaky. role=admin is not in the form but the backend processes it anyway.',
               6, 51, NULL, 27, '2025-01-02 14:00:00'),
          (61, 'Shell injection via the link preview — curl with shell=True and single-quote injection. Textbook.',
               7, 51, NULL, 22, '2025-01-02 15:00:00'),
          (62, 'Already cracked mod_alice and mod_bob hashes from the FTP backup. password1 and letmein. Both in rockyou top 100.',
               13, 51, NULL, 19, '2025-01-02 16:00:00'),
          -- Post 52: internal staff note (discoverable via IDOR on hidden community)
          (63, 'This checklist is thorough. Pinning for the moderation team.',
               2, 52, NULL, 2, '2025-01-01 13:00:00'),
          (64, 'Should we add the weak reset token timing window? 1-hour epoch bucket is very guessable.',
               3, 52, NULL, 1, '2025-01-01 14:00:00'),
          (65, 'Good catch — adding it. Also noting that /api/internal returns password hashes to any authenticated user.',
               1, 52,   64, 1, '2025-01-01 15:00:00'),
          -- Post 53: offtopic PSA
          (66, 'I found this post via SQL injection. The irony is not lost on me.',
               5, 53, NULL, 44, '2025-01-03 10:00:00'),
          (67, 'Okay the img tag CSRF on voting is genuinely funny. One image embed and everyone who views the page upvotes your post.',
               4, 53, NULL, 38, '2025-01-03 11:00:00'),
          (68, 'The /commonhuman route is a nice touch. Took me a while to find it — robots.txt eventually gave it away.',
               8, 53, NULL, 31, '2025-01-03 12:00:00'),
          (69, 'Spent an hour on the IDOR chain before realising the message endpoint had zero ownership checks. Classic.',
               18, 53, NULL, 26, '2025-01-03 13:00:00');
    """)

    # Messages referencing the easter egg
    db.executescript("""
        INSERT OR IGNORE INTO messages (id, sender_id, recipient_id, subject, body, read, created_at) VALUES
          (11, 21, 1, 'Lab is live',
               'All vulnerabilities are confirmed in place. The OctoRig post is up in sv/security. FTP anonymous access is working. SSH creds are set.\n\nRemind the team: post #50 is the IDOR draft target and message #1 has the secret key.\n\nEaster egg at /commonhuman is ready.',
               1, '2025-01-01 08:00:00'),
          (12, 1, 21, 'Re: Lab is live',
               'Confirmed. Good work. The staff checklist in sv/hidden (post #52) covers everything. Let me know if any vuln behaviour needs adjusting after student feedback.\n\nRemember the password for commonhuman_ is something in rockyou. Keep it crackable.',
               1, '2025-01-01 09:00:00');
    """)

    # Mod log entries for commonhuman_
    db.executescript("""
        INSERT OR IGNORE INTO mod_log (id, community_id, mod_id, action, target_id, reason, created_at) VALUES
          (11, 7, 1,  'add_moderator', 21, 'commonhuman_ added as platform architect — full staff access.',   '2025-01-01 00:00:00'),
          (12, 2, 21, 'pin_post',      51, 'Platform info post — pinned to top of sv/security.',             '2025-01-02 10:05:00'),
          (13, 2, 21, 'pin_post',       3, 'CVE advisory and platform info both pinned.',                    '2025-01-02 10:06:00');
    """)

    db.commit()
    db.close()
    with open('/flag_cmdi.txt', 'w') as f:
        f.write('FLAG{sv_cmdi_preview_rce}\n')
