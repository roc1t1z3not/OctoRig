from ._types import LabDefinition

WORLD_LABS: list[LabDefinition] = [  # type: ignore[assignment]
    {
        "id": 1,
        "slug": "rewindrange",
        "name": "Rewind",
        "description": "Retro video and games store. SQLi, XSS, IDOR, weak SSH/FTP credentials.",
        "category": "world",
        "container_names": ["octorig-rewindrange"],
        "images": {"app": "octorig-rewindrange:latest"},
        "build_contexts": {"app": "labs/rewindrange"},
        "start_order": ["app"],
        "network_name": "octorig-rewindrange-net",
        "subnet": "172.28.1.0/24",
        "app_ip": "172.28.1.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.1.2"},
            {"key": "SSH", "value": "ssh staff@172.28.1.2 (password: dragon)"},
            {"key": "FTP", "value": "ftp 172.28.1.2 (anonymous)"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "rw-recon-robots",
                "title": "What's Off-Limits?",
                "description": (
                    "Every web server has a way to tell search engines what *not* to index. "
                    "Find the right file, follow where it leads, and you'll end up somewhere "
                    "the store would rather keep private.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "information-disclosure"],
                "skills": ["passive recon", "directory enumeration"],
                "points": 50,
                "flags": [
                    {"value": "FLAG{rw_manager_office_found}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Search engines are told what to ignore — that instruction list is itself public.", "cost": 0},
                    {"order_num": 2, "content": "The file lives at a standard path in the web root. Follow each path it lists.", "cost": 25},
                    {"order_num": 3, "content": "Visit /robots.txt, then browse to each Disallow path as a logged-in user.", "cost": 50},
                ],
            },
            {
                "slug": "rw-sqli-browse-union",
                "title": "Browse & Conquer",
                "description": (
                    "The browsing experience on Rewind Range is built on a query that "
                    "trusts user input a little too much. One of the filter parameters "
                    "deserves a closer look — what you find there may reach further than "
                    "the product catalogue.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sql-injection", "union", "sqlite", "data-extraction"],
                "skills": ["UNION SELECT", "SQLite schema enumeration", "column-count detection"],
                "points": 300,
                "flags": [
                    {"value": "FLAG{rw_union_select_from_flags}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The category or genre filter on the browse page is worth inspecting. Try an unusual character.", "cost": 0},
                    {"order_num": 2, "content": "Column count matters. Use ORDER BY to count them before extending the query.", "cost": 25},
                    {"order_num": 3, "content": "SELECT name FROM sqlite_master WHERE type='table' lists all tables in the database.", "cost": 75},
                ],
            },
            {
                "slug": "rw-sqli-login-bypass",
                "title": "Bypass the Velvet Rope",
                "description": (
                    "You don't have admin credentials. You might not need them.\n\n"
                    "Rewind Range's login form makes a decision based on what you submit. "
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "sqli",
                "tags": ["sql-injection", "authentication-bypass", "sqlite"],
                "skills": ["SQLi auth bypass", "tautology injection"],
                "points": 100,
                "flags": [
                    {"value": "FLAG{rw_admin_login_bypassed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "What does the server do when you put a quote character in the username field?", "cost": 0},
                    {"order_num": 2, "content": "SQL comment sequences can neutralise parts of a query.", "cost": 50},
                    {"order_num": 3, "content": "Try username: admin'-- with any password.", "cost": 100},
                ],
            },
            {
                "slug": "rw-sqli-cred-dump",
                "title": "Dump the Membership List",
                "description": (
                    "Rewind Range keeps a membership list. Once you've found your way "
                    "into the database, there's more to collect than product data — "
                    "the users table holds secrets its customers never intended to share.\n\n"
                    "Find the admin's password and wrap it in `FLAG{}`.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sql-injection", "union", "sqlite", "credential-dump"],
                "skills": ["UNION SELECT", "credential extraction"],
                "points": 250,
                "flags": [
                    {"value": "FLAG{123456789}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "You already found an injection point. What other tables exist in this database?", "cost": 0},
                    {"order_num": 2, "content": "There is a users table. Columns include username and password.", "cost": 50},
                    {"order_num": 3, "content": "The admin's password is stored in plaintext. Extract it and wrap it in FLAG{}.", "cost": 75},
                ],
            },
            {
                "slug": "rw-xss-reflected-search",
                "title": "Search and Destroy",
                "description": (
                    "Whatever you search for, Rewind Range echoes it back on the results "
                    "page. The question is whether it echoes *only* what you typed.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "xss",
                "tags": ["xss", "reflected", "javascript"],
                "skills": ["reflected XSS", "basic payload construction"],
                "points": 100,
                "flags": [
                    {"value": "FLAG{rw_reflected_xss_fired}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Does the search input appear verbatim on the results page? Try some HTML.", "cost": 0},
                    {"order_num": 2, "content": "HTML tags in the query — do they render, or get escaped?", "cost": 50},
                    {"order_num": 3, "content": "Try: /search?q=<script>alert(1)</script> — the flag will appear in the page.", "cost": 75},
                ],
            },
            {
                "slug": "rw-xss-stored-feedback",
                "title": "Leave Your Mark",
                "description": (
                    "Happy customers leave feedback. \n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "xss",
                "tags": ["xss", "stored", "session-hijacking", "javascript"],
                "skills": ["stored XSS", "cookie exfiltration", "session hijacking"],
                "points": 350,
                "flags": [
                    {"value": "FLAG{rw_stored_xss_admin_pwned}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "There is a feedback form. Submit something unusual and think about who reads it and how.", "cost": 0},
                    {"order_num": 2, "content": "If the admin's browser renders your submission, and the admin has a cookie you want...", "cost": 50},
                    {"order_num": 3, "content": "The admin reviews feedback at /admin/feedback. Their session cookie is not HttpOnly.", "cost": 100},
                ],
            },
            {
                "slug": "rw-idor-inbox",
                "title": "You've Got Mail",
                "description": (
                    "Rewind Range has a private messaging feature. Messages are fetched "
                    "by number — but whose messages can you actually read?\n\n"
                    "Log in as any regular user and find out.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "access-control", "enumeration"],
                "skills": ["IDOR", "sequential ID enumeration"],
                "points": 150,
                "flags": [
                    {"value": "FLAG{rw_idor_inbox_read}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in and find the inbox URL. The message ID is in the path.", "cost": 0},
                    {"order_num": 2, "content": "Try different message IDs. The server may not check who the message belongs to.", "cost": 50},
                    {"order_num": 3, "content": "Log in as alice (password: iloveyou). Try /inbox/1, /inbox/7 and nearby IDs.", "cost": 75},
                ],
            },
            {
                "slug": "rw-idor-rental-api",
                "title": "Someone Else's Rental",
                "description": (
                    "Rewind Range has a REST API for rental orders. Each order has an ID. "
                    "As an authenticated user, how many orders can you actually access?\n\n"
                    "Explore the API and see what turns up in records that aren't yours.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind, requires auth)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "idor",
                "tags": ["idor", "bola", "api", "access-control"],
                "skills": ["API IDOR", "Burp Intruder / ffuf", "JSON parsing"],
                "points": 250,
                "flags": [
                    {"value": "FLAG{rw_api_idor_rentals}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Authenticate and look for a rental orders endpoint in the API.", "cost": 0},
                    {"order_num": 2, "content": "Try different order IDs. Does the API only return your own?", "cost": 50},
                    {"order_num": 3, "content": "GET /api/v1/rentals/<id> as any logged-in user. Check a few IDs for a memo field.", "cost": 75},
                ],
            },
            {
                "slug": "rw-session-forge",
                "title": "Rewind the Cookie",
                "description": (
                    "Session cookies are signed, not encrypted. The signature is only as "
                    "strong as the secret behind it — and secrets sometimes find their "
                    "way into source code.\n\n"
                    "Craft a session that says you're the admin and walk through a door "
                    "you were never given a key to.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "web",
                "tags": ["session", "flask", "cookie-forgery", "crypto"],
                "skills": ["Flask session internals", "itsdangerous", "cookie signing"],
                "points": 500,
                "flags": [
                    {"value": "FLAG{rw_session_forged_as_admin}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Flask session cookies are signed with a SECRET_KEY. What if you could find it?", "cost": 0},
                    {"order_num": 2, "content": "The source code is available in the lab. Look for the secret key in app.py.", "cost": 75},
                    {"order_num": 3, "content": "Use flask-unsign: --sign --cookie '{\"user_id\": 1}' --secret '<key>'", "cost": 100},
                ],
            },
            {
                "slug": "rw-py-sqli-script",
                "title": "Script the Injector",
                "description": (
                    "Clicking through a web form is slow. The same input that surprises the "
                    "database can be sent programmatically — faster, quieter, and repeatable. "
                    "Craft a Python script that talks directly to the server and pulls back "
                    "something the UI was never meant to show you.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "sql-injection", "automation"],
                "skills": ["requests", "HTTP parameter injection", "response parsing"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{rw_python_sqli_automated}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "A script that loops and changes one parameter per request can cover ground no human can match.", "cost": 0},
                    {"order_num": 2, "content": "The browse page accepts a filter parameter in the query string. Send your requests there.", "cost": 50},
                    {"order_num": 3, "content": "Try appending to the filter value and watch what the response body contains.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 2,
        "slug": "tradefloor",
        "name": "TradeFloor",
        "description": "Stock trading portal. SQLi, IDOR, race conditions, weak SSH/FTP credentials.",
        "category": "world",
        "container_names": ["octorig-tradefloor"],
        "images": {"app": "octorig-tradefloor:latest"},
        "build_contexts": {"app": "labs/tradefloor"},
        "start_order": ["app"],
        "network_name": "octorig-tradefloor-net",
        "subnet": "172.28.2.0/24",
        "app_ip": "172.28.2.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.2.2"},
            {"key": "SSH", "value": "ssh tradeops@172.28.2.2"},
            {"key": "FTP", "value": "ftp 172.28.2.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "tf-recon-robots",
                "title": "Off the Books",
                "description": (
                    "Every exchange has areas it doesn't want indexed. TradeFloor is "
                    "no different — there's a public file that hints at paths the "
                    "operators would prefer you didn't visit.\n\n"
                    "Find one of those paths and access it as a logged-in user.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "information-disclosure", "bac"],
                "skills": ["passive recon", "broken access control"],
                "points": 50,
                "flags": [
                    {"value": "FLAG{tf_fund_manager_found}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Web servers publish a list of paths they'd prefer crawlers ignored. That list is public.", "cost": 0},
                    {"order_num": 2, "content": "Some of the restricted paths don't actually enforce authentication.", "cost": 50},
                ],
            },
            {
                "slug": "tf-sqli-market-union",
                "title": "Inside the Order Book",
                "description": (
                    "The market search feature accepts a ticker query. Try entering "
                    "something the search wasn't designed to handle — some inputs "
                    "travel further than just the product catalogue.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sql-injection", "union", "sqlite", "data-extraction"],
                "skills": ["UNION SELECT", "SQLite schema enumeration", "column-count detection"],
                "points": 300,
                "flags": [
                    {"value": "FLAG{tf_union_select_from_flags}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Enter an unusual character in the ticker search and observe the response.", "cost": 0},
                    {"order_num": 2, "content": "Column count must match before extending a query. Use ORDER BY to determine it.", "cost": 25},
                    {"order_num": 3, "content": "SELECT name FROM sqlite_master WHERE type='table' reveals what else is stored.", "cost": 75},
                ],
            },
            {
                "slug": "tf-sqli-api-token",
                "title": "Token Without a Password",
                "description": (
                    "TradeFloor's REST API issues tokens via a login endpoint. "
                    "The credential check has a flaw — the right username might "
                    "bypass the need for a password entirely.\n\n"
                    "Obtain an admin token, then call a privileged endpoint.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "sqli",
                "tags": ["sql-injection", "authentication-bypass", "api", "jwt"],
                "skills": ["SQLi auth bypass", "JWT", "API testing"],
                "points": 100,
                "flags": [
                    {"value": "FLAG{tf_api_token_injected}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The API token endpoint is at /api/token. Try a POST with unusual username values.", "cost": 0},
                    {"order_num": 2, "content": "What if the username contained a character that changes how the query is interpreted?", "cost": 50},
                    {"order_num": 3, "content": "Once you have an admin token, look for a privileged API endpoint that returns the flag.", "cost": 75},
                ],
            },
            {
                "slug": "tf-sqli-cred-dump",
                "title": "Membership Leaked",
                "description": (
                    "You've found a way into the database. There's more stored there "
                    "than market data — and not everything is encrypted.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sql-injection", "union", "sqlite", "credential-dump"],
                "skills": ["UNION SELECT", "credential extraction"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{tf_users_table_dumped}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "You already have an injection point. What other tables exist?", "cost": 0},
                    {"order_num": 2, "content": "Enumerate with sqlite_master. Look for a users or members table.", "cost": 50},
                    {"order_num": 3, "content": "The _flags table has a row called sqli-creds containing the answer.", "cost": 75},
                ],
            },
            {
                "slug": "tf-xss-reflected-market",
                "title": "Ticker Injection",
                "description": (
                    "The market search field echoes your query back on the results page. "
                    "How faithfully does it reproduce what you type?\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "xss",
                "tags": ["xss", "reflected", "javascript"],
                "skills": ["reflected XSS", "basic payload construction"],
                "points": 100,
                "flags": [
                    {"value": "FLAG{tf_reflected_xss_fired}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Enter some HTML into the search field. Does the page reflect it back?", "cost": 0},
                    {"order_num": 2, "content": "If your HTML renders, can you go further? The flag is in the browser's cookie jar.", "cost": 50},
                    {"order_num": 3, "content": "A script that reads document.cookie will find it.", "cost": 75},
                ],
            },
            {
                "slug": "tf-idor-order-detail",
                "title": "Someone Else's Trade",
                "description": (
                    "Trade orders each have an ID. As a logged-in user, you can view "
                    "your own orders — but are they truly *your* orders?\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "access-control", "enumeration"],
                "skills": ["IDOR", "sequential ID enumeration"],
                "points": 150,
                "flags": [
                    {"value": "FLAG{tf_idor_order_memo}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in and find the order detail URL. The ID is in the path.", "cost": 0},
                    {"order_num": 2, "content": "Try other IDs. The server may hand back orders belonging to different users.", "cost": 50},
                    {"order_num": 3, "content": "Check the admin's orders. A memo field on one of them contains the flag.", "cost": 75},
                ],
            },
            {
                "slug": "tf-bac-admin-view",
                "title": "The Compliance Desk",
                "description": (
                    "TradeFloor's admin panel has a per-user detail view. Being logged "
                    "in might be enough to reach it — try navigating there as a "
                    "regular user.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "web",
                "tags": ["broken-access-control", "bac", "idor", "vertical-privesc"],
                "skills": ["broken access control", "URL enumeration"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{tf_bac_admin_user_detail}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Admin routes are under /admin/. Log in as any user and explore.", "cost": 0},
                    {"order_num": 2, "content": "The user detail page takes an ID. User IDs are sequential integers.", "cost": 50},
                    {"order_num": 3, "content": "Try /admin/users/1 while logged in as alice.p.", "cost": 75},
                ],
            },
            {
                "slug": "tf-jwt-alg-none",
                "title": "Trust Nobody, Sign Nothing",
                "description": (
                    "TradeFloor's API uses tokens. The way the server verifies them "
                    "is worth examining — specifically, what the token itself says "
                    "about how it should be verified.\n\n"
                    "Forge an admin token and call a privileged endpoint.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "web",
                "tags": ["jwt", "alg-none", "authentication", "api"],
                "skills": ["JWT internals", "algorithm confusion", "API testing"],
                "points": 450,
                "flags": [
                    {"value": "FLAG{tf_jwt_alg_none_bypassed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Decode your JWT (base64url). What's in the header? Pay attention to the alg field.", "cost": 0},
                    {"order_num": 2, "content": "The server reads the algorithm from the token itself. What happens if you change it?", "cost": 75},
                    {"order_num": 3, "content": "Set alg to 'none', drop the signature, add role: admin to the payload. Call GET /api/admin/report as Bearer.", "cost": 100},
                ],
            },
            {
                "slug": "tf-py-idor-sweep",
                "title": "Portfolio Sweep",
                "description": (
                    "Profiles are numbered. Each number belongs to someone — or it should. "
                    "Write a Python script that walks the sequence and notices when a record "
                    "surfaces that the current session has no business seeing.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "idor", "automation", "api"],
                "skills": ["requests", "session handling", "sequential enumeration"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{tf_python_idor_swept}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "A loop over sequential numbers can reveal what manual clicking cannot.", "cost": 0},
                    {"order_num": 2, "content": "The portfolio endpoint is under /api/. Authenticated requests return different data than anonymous ones.", "cost": 50},
                    {"order_num": 3, "content": "Log in first with requests.Session(), then iterate /api/portfolio/<id> and inspect each response.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 3,
        "slug": "goldenace",
        "name": "GoldenAce",
        "description": "Online casino. SQLi, XSS, privilege escalation, FTP backdoor, weak SSH.",
        "category": "world",
        "container_names": ["octorig-goldenace"],
        "images": {"app": "octorig-goldenace:latest"},
        "build_contexts": {"app": "labs/goldenace"},
        "start_order": ["app"],
        "network_name": "octorig-goldenace-net",
        "subnet": "172.28.3.0/24",
        "app_ip": "172.28.3.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.3.2"},
            {"key": "SSH", "value": "ssh casinoops@172.28.3.2 (password: sunshine)"},
            {"key": "FTP", "value": "ftp 172.28.3.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "ga-recon-robots",
                "title": "House Rules",
                "description": "Every casino has areas off-limits to regular guests. The web equivalent of a staff-only door is well-known — and what's listed behind it doesn't always require a key.",
                "difficulty": "easy",
                "category": "recon",
                "points": 50,
                "challenge_type": "flag",
                "estimated_minutes": 5,
                "tags": ["recon"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Web servers publish a list of paths they'd prefer crawlers ignored. That list is itself public.", "cost": 0},
                    {"order_num": 2, "content": "Some of the restricted paths don't actually require authentication. Try each one.", "cost": 25},
                ],
            },
            {
                "slug": "ga-sqli-promo",
                "title": "Free Chips",
                "description": "The promo redemption desk accepts codes. Some codes may do more than redeem credits — try entering something the field wasn't designed for.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["sqli", "union", "sqlite"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "What happens when you put special characters in the promo code field?", "cost": 0},
                    {"order_num": 2, "content": "The injection takes you to the database. Use sqlite_master to see what tables exist.", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT against a hidden table. Column count must match the original query.", "cost": 75},
                ],
            },
            {
                "slug": "ga-sqli-leaderboard",
                "title": "Rigged Rankings",
                "description": "The leaderboard has a search. Your input ends up in more than one place — try something you wouldn't normally type as a player name.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["sqli", "union", "reflected-xss"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Enter an unusual character in the search. What does the response tell you about how it's processed?", "cost": 0},
                    {"order_num": 2, "content": "The query uses a LIKE clause. What happens when you close it early?", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT to pivot into a hidden table. Match the column count of the users query.", "cost": 75},
                ],
            },
            {
                "slug": "ga-xss-chat",
                "title": "Dealer's Message",
                "description": "The live casino chat is open to all registered players. What you post is visible to everyone who loads the room — including what you didn't intend to post.",
                "difficulty": "easy",
                "category": "xss",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["xss", "stored", "cookies"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Post a message with some HTML in it. Does the chat render it?", "cost": 0},
                    {"order_num": 2, "content": "If HTML renders, so does JavaScript. The page sets a cookie when it loads.", "cost": 50},
                    {"order_num": 3, "content": "Not all cookies have the HttpOnly flag. Some are readable from JavaScript.", "cost": 75},
                ],
            },
            {
                "slug": "ga-idor-suite",
                "title": "Wrong Room",
                "description": "Player suites display a full game history. The room number is in the URL — is it verified against your session?",
                "difficulty": "easy",
                "category": "idor",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["idor", "access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Room numbers are sequential integers in the URL.", "cost": 0},
                    {"order_num": 2, "content": "Start from room 1. Game history memos sometimes contain more than scores.", "cost": 50},
                ],
            },
            {
                "slug": "ga-biz-negative-bet",
                "title": "The House Loses",
                "description": "The slot machine accepts your bet via a form. The server processes what you send — but does it validate it?",
                "difficulty": "medium",
                "category": "web",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["business-logic", "parameter-tampering"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Intercept the bet submission. What fields are in the POST body?", "cost": 0},
                    {"order_num": 2, "content": "The bet field accepts numbers. Explore its boundaries — in both directions.", "cost": 50},
                ],
            },
            {
                "slug": "ga-bac-admin",
                "title": "Staff Only",
                "description": "The admin panel is behind a door marked staff only. As a registered player, try walking through it.",
                "difficulty": "easy",
                "category": "web",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["bac", "access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Register a regular account and navigate to /admin.", "cost": 0},
                    {"order_num": 2, "content": "The flag is displayed on the admin panel page.", "cost": 25},
                ],
            },
            {
                "slug": "ga-bac-high-rollers",
                "title": "VIP Lounge",
                "description": "Somewhere on this site there's a restricted area for high-rollers. The path is hinted at in a familiar file. Being registered might be enough to get in.",
                "difficulty": "easy",
                "category": "web",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["bac", "access-control", "recon"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "The path to the VIP area is listed in a file crawlers are told to avoid.", "cost": 0},
                    {"order_num": 2, "content": "Log in as any user and request the path directly.", "cost": 25},
                ],
            },
            {
                "slug": "ga-promo-reuse",
                "title": "Double Down",
                "description": "The promo system hands out rewards. What happens if you try to collect more than once?",
                "difficulty": "medium",
                "category": "web",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["business-logic", "promo-abuse"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Redeem a valid promo code. Now try redeeming it again with the same account.", "cost": 0},
                    {"order_num": 2, "content": "The system tracks total redemptions across all users, but not per-user redemptions.", "cost": 50},
                ],
            },
            {
                "slug": "ga-py-logic-abuse",
                "title": "House Edge",
                "description": (
                    "The house always wins — unless you move faster than the rules allow. "
                    "There's a sequence of calls that can leave your balance in a state the "
                    "server didn't intend. A Python script can issue them in the right order, "
                    "at the right speed.\n\n"
                    "**Target:** `http://172.28.3.2` (start Lab 3 — GoldenAce)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "business-logic", "race-condition"],
                "skills": ["requests", "session handling", "concurrency", "state manipulation"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{ga_python_logic_edge}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Two actions that should be mutually exclusive can both succeed if they arrive close enough together.", "cost": 0},
                    {"order_num": 2, "content": "Look at the bet and withdraw endpoints. What happens if both fire before the balance updates?", "cost": 50},
                    {"order_num": 3, "content": "Use threading.Thread or concurrent.futures to send requests in parallel within the same session.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 4,
        "slug": "humanbank",
        "name": "HumanBank",
        "description": "Banking portal. SQLi, IDOR, auth bypass, Redis cache, SSH private keys.",
        "category": "world",
        "container_names": ["octorig-humanbank"],
        "images": {"app": "octorig-humanbank:latest"},
        "build_contexts": {"app": "labs/humanbank"},
        "start_order": ["app"],
        "network_name": "octorig-humanbank-net",
        "subnet": "172.28.4.0/24",
        "app_ip": "172.28.4.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21, "redis": 6379},
        "access_info": [
            {"key": "URL", "value": "http://172.28.4.2"},
            {"key": "SSH", "value": "ssh bankops@172.28.4.2"},
            {"key": "Redis", "value": "redis-cli -h 172.28.4.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "hb-recon-audit-log",
                "title": "Open Books",
                "description": (
                    "An internal diagnostics endpoint was deployed and never locked down. "
                    "It responds to anyone who asks — no session required. "
                    "The raw financial history of the entire bank is there for the taking.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "openapi", "unauthenticated", "information-disclosure"],
                "skills": ["API enumeration", "OpenAPI spec reading"],
                "points": 50,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{hb_recon_audit_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The API publishes a machine-readable description of every endpoint it exposes.", "cost": 0},
                    {"order_num": 2, "content": "One of the paths listed contains audit information. Try accessing it without a session cookie.", "cost": 25},
                ],
            },
            {
                "slug": "hb-sqli-login",
                "title": "Master Key",
                "description": (
                    "The login screen accepts your name and passphrase. "
                    "What if the passphrase weren't the deciding factor? "
                    "A carefully chosen username might make the decision for you.\n\n"
                    "Once inside as admin, check the admin profile — "
                    "there is a field the bank keeps very close to its chest.\n\n"
                    "**Target:** `http://172.28.4.2/login` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "sqli",
                "tags": ["sqli", "login-bypass", "sqlite", "auth"],
                "skills": ["SQL injection", "authentication bypass"],
                "points": 100,
                "estimated_minutes": 15,
                "flags": [
                    {"value": "FLAG{hb_sqli_login_bypassed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "What happens when you put special characters in the username field?", "cost": 0},
                    {"order_num": 2, "content": "A single quote in the username causes an error. What if you also added a comment character after the username?", "cost": 50},
                    {"order_num": 3, "content": "Username: `admin'--`, any password. After login, the flag is in `/profile` under the admin's address field.", "cost": 75},
                ],
            },
            {
                "slug": "hb-sqli-search",
                "title": "Transaction Miner",
                "description": (
                    "The transaction search takes your query and goes hunting. "
                    "What it brings back might surprise you — especially if you ask "
                    "it to go looking somewhere it wasn't designed to reach.\n\n"
                    "**Target:** `http://172.28.4.2/search` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sqli", "union", "sqlite", "search"],
                "skills": ["UNION SELECT", "SQLite schema enumeration"],
                "points": 250,
                "estimated_minutes": 25,
                "flags": [
                    {"value": "FLAG{hb_sqli_search_union}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Try entering unusual characters in the search box. Does the response change?", "cost": 0},
                    {"order_num": 2, "content": "The database has more tables than the app shows you. SQLite keeps a schema table you can query.", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT into the `_flags` table. Match the 7-column count of the original query.", "cost": 75},
                ],
            },
            {
                "slug": "hb-sqli-txn-memo",
                "title": "Filter Bypass",
                "description": (
                    "The transaction list accepts filter fields — memo, type, date range. "
                    "Each one goes straight into the query logic. "
                    "The database knows more than transaction history.\n\n"
                    "**Target:** `http://172.28.4.2/accounts/1/transactions` "
                    "(start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sqli", "union", "sqlite", "filter"],
                "skills": ["UNION SELECT", "filter parameter injection"],
                "points": 200,
                "estimated_minutes": 20,
                "flags": [
                    {"value": "FLAG{hb_sqli_txn_dump}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Try putting unusual characters in the `memo` filter. What does the server respond with?", "cost": 0},
                    {"order_num": 2, "content": "The memo filter wraps your input in a LIKE clause. Closing it early opens the door to appending your own query.", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT into the `_flags` table from the memo param. The original query returns 6 columns.", "cost": 75},
                ],
            },
            {
                "slug": "hb-idor-accounts",
                "title": "Everyone's Balance",
                "description": (
                    "Banking works on the assumption that you can only see your own accounts. "
                    "But what if the account list page didn't share that assumption?\n\n"
                    "One account in the system belongs to an entity that shouldn't be visible "
                    "to regular customers. Its transaction history has a memo worth reading.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "accounts", "banking"],
                "skills": ["IDOR", "object-level access control"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{hb_idor_cmnh_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in as any user. Browse to the accounts list — does it only show your own?", "cost": 0},
                    {"order_num": 2, "content": "Look for an account with an unusual holder name. Its transactions contain a flag in an internal memo.", "cost": 25},
                ],
            },
            {
                "slug": "hb-idor-ticket",
                "title": "Someone Else's Ticket",
                "description": (
                    "Support tickets are assigned a number when filed. "
                    "Does the system verify that the number you're requesting belongs to you?\n\n"
                    "An internal ticket was created by bank staff and was never meant "
                    "to be seen by customers. Find it.\n\n"
                    "**Target:** `http://172.28.4.2/tickets/` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "tickets", "enumeration"],
                "skills": ["IDOR", "horizontal privilege escalation"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{hb_idor_ticket_read}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Ticket IDs are sequential numbers. Try visiting a ticket that isn't yours.", "cost": 0},
                    {"order_num": 2, "content": "Internal support tickets were created before any customer accounts. Try the earliest IDs.", "cost": 25},
                ],
            },
            {
                "slug": "hb-bac-admin-api",
                "title": "Teller Without a Badge",
                "description": (
                    "There's an API endpoint meant for administrators only. "
                    "The door asks if you have a key — not whether the key is the right one. "
                    "Any customer who walks in authenticated might find the vault wide open.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "web",
                "tags": ["bac", "broken-access-control", "api", "privilege-escalation"],
                "skills": ["broken access control", "API testing"],
                "points": 150,
                "estimated_minutes": 15,
                "flags": [
                    {"value": "FLAG{hb_bac_api_admin_bypass}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The API spec lists every endpoint. Look for paths under an `/admin/` prefix.", "cost": 0},
                    {"order_num": 2, "content": "Log in as any regular customer and call an admin endpoint. Inspect the JSON response carefully.", "cost": 25},
                ],
            },
            {
                "slug": "hb-bac-user-detail",
                "title": "Admin Panel Without the Admin",
                "description": (
                    "The admin area has a page that shows detailed user profiles. "
                    "It checks that you're logged in — but not who you're logged in as.\n\n"
                    "Any registered customer can walk straight in. "
                    "The first user account has something stored in a field that should never be public.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "web",
                "tags": ["bac", "broken-access-control", "admin-panel"],
                "skills": ["broken access control", "vertical privilege escalation"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{hb_bac_admin_detail_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Look for an admin section in the API spec or robots.txt. Try navigating there while logged in as a regular user.", "cost": 0},
                    {"order_num": 2, "content": "The admin user-detail path takes a user ID. User ID 1 is the admin. The flag is in the profile data.", "cost": 50},
                ],
            },
            {
                "slug": "hb-xss-stored-ticket",
                "title": "Support Ticket Hijack",
                "description": (
                    "The bank's support ticket system stores everything customers submit "
                    "and displays it to staff in the admin panel. "
                    "What gets stored, gets rendered — and the admin panel isn't as safe as it looks.\n\n"
                    "Leave something in a ticket that will run when the admin reads it.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "xss",
                "tags": ["xss", "stored-xss", "cookie-theft", "admin-panel"],
                "skills": ["stored XSS", "cookie exfiltration", "session hijacking"],
                "points": 300,
                "estimated_minutes": 30,
                "flags": [
                    {"value": "FLAG{hb_xss_admin_cookie_stolen}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Try submitting HTML in a ticket body. Does the admin panel render it?", "cost": 0},
                    {"order_num": 2, "content": "The admin ticket view renders content without escaping. JavaScript submitted in a ticket runs when an admin views it.", "cost": 50},
                    {"order_num": 3, "content": "Log in as admin (hint: the login form has its own flaw) and visit the ticket list. `document.cookie` will have the flag.", "cost": 100},
                ],
            },
            {
                "slug": "hb-py-sqli-dump",
                "title": "Account Drain",
                "description": (
                    "The bank's data doesn't stay locked when the query is written carelessly. "
                    "A Python script can do in seconds what a proxy intercept does one request "
                    "at a time — chain the steps together and the vault opens itself.\n\n"
                    "**Target:** `http://172.28.4.2` (start Lab 4 — HumanBank)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "sql-injection", "automation", "credential-dump"],
                "skills": ["requests", "session handling", "SQLi chaining", "response parsing"],
                "points": 225,
                "flags": [
                    {"value": "FLAG{hb_python_sqli_chained}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "One endpoint lets you in without the right password. Another leaks more than it should once you're authenticated.", "cost": 0},
                    {"order_num": 2, "content": "The account search endpoint accepts user input that reaches the query directly.", "cost": 50},
                    {"order_num": 3, "content": "Use a single requests.Session() — first post to /login with the bypass, then query /accounts/search with your payload.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 5,
        "slug": "medihuman",
        "name": "MediHuman",
        "description": "Healthcare portal. SQLi, IDOR, auth bypass, weak SSH/FTP credentials.",
        "category": "world",
        "container_names": ["octorig-medihuman"],
        "images": {"app": "octorig-medihuman:latest"},
        "build_contexts": {"app": "labs/medihuman"},
        "start_order": ["app"],
        "network_name": "octorig-medihuman-net",
        "subnet": "172.28.5.0/24",
        "app_ip": "172.28.5.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.5.2"},
            {"key": "SSH", "value": "ssh mediadmin@172.28.5.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "mh-recon-openapi",
                "title": "Open Spec",
                "description": (
                    "The portal publishes a complete map of itself — every endpoint, "
                    "every parameter — without requiring a login. "
                    "Read it carefully. Developers sometimes leave notes in places they assume nobody will look.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "openapi", "unauthenticated", "information-disclosure"],
                "skills": ["API enumeration", "OpenAPI spec reading"],
                "points": 50,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{mh_recon_openapi_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Most REST APIs publish their schema at a well-known path. No authentication needed.", "cost": 0},
                    {"order_num": 2, "content": "Scan the JSON for any non-standard extension fields — keys that start with `x-`.", "cost": 25},
                ],
            },
            {
                "slug": "mh-sqli-login",
                "title": "Doctor's Orders",
                "description": (
                    "The login screen trusts what you give it. "
                    "A username crafted to speak directly to the database might "
                    "bypass the password check entirely.\n\n"
                    "Once inside as admin, check the HTTP response from the admin panel — "
                    "the server reveals more than just the page.\n\n"
                    "**Target:** `http://172.28.5.2/login` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "sqli",
                "tags": ["sqli", "login-bypass", "sqlite", "auth"],
                "skills": ["SQL injection", "authentication bypass", "HTTP response headers"],
                "points": 100,
                "estimated_minutes": 15,
                "flags": [
                    {"value": "FLAG{mh_sqli_login_bypassed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Try unusual characters in the username field. Notice any difference in how the server responds?", "cost": 0},
                    {"order_num": 2, "content": "A quote character breaks the query. A comment character after the username silences the rest.", "cost": 50},
                    {"order_num": 3, "content": "Username: `admin'--`, any password. After logging in, check the HTTP response headers on `/admin`.", "cost": 75},
                ],
            },
            {
                "slug": "mh-sqli-patient-search",
                "title": "Records Request",
                "description": (
                    "The patient search accepts a name and queries the database. "
                    "What the database returns depends entirely on how you frame the question.\n\n"
                    "The system stores more than patient names.\n\n"
                    "**Target:** `http://172.28.5.2/patients` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sqli", "union", "sqlite", "phi", "healthcare"],
                "skills": ["UNION SELECT", "SQLite schema enumeration"],
                "points": 250,
                "estimated_minutes": 25,
                "flags": [
                    {"value": "FLAG{mh_sqli_patient_search_union}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Put a special character in the search. Does the error tell you how the query is structured?", "cost": 0},
                    {"order_num": 2, "content": "The database schema is readable if you know where to look. What tables does SQLite expose by default?", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT into a hidden table. The original query returns 9 columns — match that count.", "cost": 75},
                ],
            },
            {
                "slug": "mh-idor-lab-result",
                "title": "Classified Test Result",
                "description": (
                    "Lab results are accessed by ID. The portal verifies you're "
                    "authenticated — but not that the result belongs to you.\n\n"
                    "One result in the system was filed by an external party "
                    "and should never have been accessible to patients. "
                    "The notes field tells a different story.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "phi", "healthcare", "lab-results"],
                "skills": ["IDOR", "object-level access control"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{mh_idor_lab_result_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in as any user. Browse lab result IDs. Does the system restrict which records you can see?", "cost": 0},
                    {"order_num": 2, "content": "There are more results in the database than are shown in your patient dashboard.", "cost": 25},
                ],
            },
            {
                "slug": "mh-idor-prescription",
                "title": "Second Opinion",
                "description": (
                    "Prescription records are stored by ID. "
                    "The system trusts that you'll only ask for your own — "
                    "but it doesn't enforce it.\n\n"
                    "There is a prescription in the system that belongs to someone else. "
                    "The notes field carries something that shouldn't be there.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "idor",
                "tags": ["idor", "bola", "phi", "prescriptions"],
                "skills": ["IDOR", "horizontal privilege escalation"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{mh_idor_prescription_read}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in as any user. Try accessing prescriptions by their ID number.", "cost": 0},
                    {"order_num": 2, "content": "Your own prescription might not be ID 1. Try IDs you weren't assigned.", "cost": 25},
                ],
            },
            {
                "slug": "mh-bac-admin-export",
                "title": "Patient Data Export",
                "description": (
                    "The admin section has a data export that dumps every patient record "
                    "in the system. The door is labelled admin-only — "
                    "but the bouncer just checks if you exist, not who you are.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "web",
                "tags": ["bac", "broken-access-control", "api", "phi", "data-exposure"],
                "skills": ["broken access control", "API testing", "PHI exposure"],
                "points": 150,
                "estimated_minutes": 15,
                "flags": [
                    {"value": "FLAG{mh_bac_admin_export_bypass}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The API spec lists admin paths. Try calling one while logged in as a regular patient.", "cost": 0},
                    {"order_num": 2, "content": "The export endpoint returns JSON with all patient records — and one extra field.", "cost": 25},
                ],
            },
            {
                "slug": "mh-bac-staff-detail",
                "title": "Admin Profile Leak",
                "description": (
                    "Staff profiles are tucked behind an admin path. "
                    "The lock on the door checks whether you're logged in — "
                    "not whether you're staff.\n\n"
                    "The first staff member's profile has a field that doesn't belong there.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "web",
                "tags": ["bac", "broken-access-control", "admin-panel", "vertical-privesc"],
                "skills": ["broken access control", "vertical privilege escalation"],
                "points": 100,
                "estimated_minutes": 10,
                "flags": [
                    {"value": "FLAG{mh_bac_staff_detail_exposed}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Log in as any user. Look for an admin staff path — the API spec will list it.", "cost": 0},
                    {"order_num": 2, "content": "Request staff ID 1. The profile data includes a field that shouldn't be visible to patients.", "cost": 25},
                ],
            },
            {
                "slug": "mh-xss-reflected",
                "title": "Search & Destroy",
                "description": (
                    "The patient search echoes your search term back on the results page. "
                    "It reads it in, and it reads it back out — without checking what it contains.\n\n"
                    "There is a cookie set on this page that is readable from the browser.\n\n"
                    "**Target:** `http://172.28.5.2/patients` "
                    "(start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "xss",
                "tags": ["xss", "reflected-xss", "cookie-theft", "search"],
                "skills": ["reflected XSS", "cookie exfiltration", "Jinja2 | safe"],
                "points": 150,
                "estimated_minutes": 20,
                "flags": [
                    {"value": "FLAG{mh_xss_reflected_patients}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Try putting some HTML in the search field. Does the page render it?", "cost": 0},
                    {"order_num": 2, "content": "If HTML renders, JavaScript runs too. The page sets a session cookie that isn't flagged HttpOnly.", "cost": 50},
                    {"order_num": 3, "content": "Read `document.cookie` from your script. The session cookie value is the flag.", "cost": 75},
                ],
            },
            {
                "slug": "mh-mass-assign",
                "title": "Appointment Escalation",
                "description": (
                    "The appointment system lets you update your own bookings. "
                    "It accepts a JSON body and trusts you to only send fields "
                    "that belong to you.\n\n"
                    "Some fields are never shown in the patient form — but the server "
                    "will accept them anyway.\n\n"
                    "**Target:** `http://172.28.5.2/api/v1/appointments/1` "
                    "(start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "web",
                "tags": ["mass-assignment", "api", "privilege-escalation", "bola"],
                "skills": ["mass assignment", "REST API manipulation", "BOLA"],
                "points": 300,
                "estimated_minutes": 30,
                "flags": [
                    {"value": "FLAG{mh_mass_assign_escalated}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Intercept a PUT request to the appointments endpoint. What fields does the server actually accept?", "cost": 0},
                    {"order_num": 2, "content": "Try adding fields that control who the appointment is assigned to — fields not present in the patient-facing form.", "cost": 50},
                    {"order_num": 3, "content": "Including `doctor_id` or `patient_id` in the PUT body triggers the flag in the JSON response.", "cost": 75},
                ],
            },
            {
                "slug": "mh-py-idor-enum",
                "title": "Record Scraper",
                "description": (
                    "Patient records are fetched by ID. The IDs are sequential. "
                    "Not every ID belongs to you — but the server doesn't always check. "
                    "Script a sweep and see whose records surface.\n\n"
                    "**Target:** `http://172.28.5.2` (start Lab 5 — MediHuman)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "idor", "automation", "healthcare"],
                "skills": ["requests", "session handling", "sequential enumeration", "JSON parsing"],
                "points": 200,
                "flags": [
                    {"value": "FLAG{mh_python_idor_scraped}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "An authenticated user can only view their own records — in theory.", "cost": 0},
                    {"order_num": 2, "content": "The lab results endpoint accepts a record ID in the URL path. Try a range of IDs.", "cost": 50},
                    {"order_num": 3, "content": "GET /api/records/<id> with your session cookie. The flag appears in the JSON body of a record that isn't yours.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 6,
        "slug": "netpulse",
        "name": "NetPulse",
        "description": "ISP management portal. SQLi, IDOR, server-side template flaws, SSH/FTP.",
        "category": "world",
        "container_names": ["octorig-netpulse"],
        "images": {"app": "octorig-netpulse:latest"},
        "build_contexts": {"app": "labs/netpulse"},
        "start_order": ["app"],
        "network_name": "octorig-netpulse-net",
        "subnet": "172.28.6.0/24",
        "app_ip": "172.28.6.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.6.2"},
            {"key": "SSH", "value": "ssh netops@172.28.6.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "np-recon-billing-db",
                "title": "Off the Books",
                "description": "An internal endpoint was left exposed during a rushed deployment. It requires no login and speaks freely to anyone who requests it. Internal invoices are there for the taking.",
                "challenge_type": "flag",
                "category": "recon",
                "difficulty": "easy",
                "points": 50,
                "tags": ["unauthenticated", "information-disclosure"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Web servers often publish a file telling crawlers which paths to avoid. That list can be revealing.", "cost": 0},
                    {"order_num": 2, "content": "One of the disallowed paths serves raw JSON without requiring authentication. Look through the records.", "cost": 25},
                ],
            },
            {
                "slug": "np-sqli-login",
                "title": "Ghost Credentials",
                "description": "The login form accepts a username and password. The check that validates them might be easier to sidestep than it appears — especially if you phrase your username carefully.",
                "challenge_type": "flag",
                "category": "sqli",
                "difficulty": "easy",
                "points": 100,
                "tags": ["authentication", "boolean-based"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try entering unusual characters in the username. Does the error change?", "cost": 0},
                    {"order_num": 2, "content": "A quote in the username changes the query structure. A comment character ends it early.", "cost": 50},
                    {"order_num": 3, "content": "After logging in as admin, check the HTTP response headers on the admin panel page.", "cost": 75},
                ],
            },
            {
                "slug": "np-sqli-board-search",
                "title": "Thread Unraveled",
                "description": "The community board has a search box. Your query travels further than the forum posts — the database has more to offer if you ask the right way.",
                "challenge_type": "flag",
                "category": "sqli",
                "difficulty": "medium",
                "points": 250,
                "tags": ["union-based", "sqlite"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try entering a single quote in the search. What does the response tell you?", "cost": 0},
                    {"order_num": 2, "content": "The database stores more than posts. Enumerate the schema to find what else is there.", "cost": 50},
                    {"order_num": 3, "content": "Use UNION SELECT — match the column count, then target the internal flags table.", "cost": 75},
                ],
            },
            {
                "slug": "np-idor-user",
                "title": "Wrong Account",
                "description": "The user API returns account details by ID. You are logged in — but does that mean you can only see yourself?",
                "challenge_type": "flag",
                "category": "idor",
                "difficulty": "easy",
                "points": 100,
                "tags": ["api", "horizontal-privilege-escalation"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "The API spec lists a users endpoint. Try accessing IDs other than your own.", "cost": 0},
                    {"order_num": 2, "content": "The first user created in the system usually has the lowest ID.", "cost": 25},
                ],
            },
            {
                "slug": "np-idor-ticket",
                "title": "Internal Dispatch",
                "description": "Support tickets are accessed by number. The system verifies you're logged in — not that the ticket is yours.",
                "challenge_type": "flag",
                "category": "idor",
                "difficulty": "easy",
                "points": 100,
                "tags": ["api", "information-disclosure"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Browse to the tickets API. What happens when you try IDs you didn't create?", "cost": 0},
                    {"order_num": 2, "content": "Internal ops tickets were created before customer accounts. Try lower IDs.", "cost": 25},
                ],
            },
            {
                "slug": "np-bac-admin-config",
                "title": "Backdoor Config",
                "description": "The admin area has a configuration endpoint. The path is listed in a file you should check early. Getting in may be easier than you'd expect.",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "easy",
                "points": 150,
                "tags": ["broken-access-control", "api"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Check robots.txt or the API spec for admin paths.", "cost": 0},
                    {"order_num": 2, "content": "Try accessing an admin path while logged in as a regular user. The check may only verify you have a session.", "cost": 50},
                ],
            },
            {
                "slug": "np-ssti-template",
                "title": "Preview Flaw",
                "description": "The notification system lets admins preview message templates before sending. The preview renders content on the server side — and the render context is richer than the feature implies.",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "hard",
                "points": 450,
                "tags": ["ssti", "jinja2", "broken-access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try submitting `{{ 7*7 }}` in the preview body. If the result is 49, the server is evaluating your input.", "cost": 0},
                    {"order_num": 2, "content": "The preview endpoint doesn't verify admin role — any logged-in user can reach it.", "cost": 50},
                    {"order_num": 3, "content": "The server exposes its configuration object in the template context. Look for the flag there.", "cost": 75},
                ],
            },
            {
                "slug": "np-cmdi-dnslookup",
                "title": "Diagnostic Override",
                "description": "The network tools section has a hostname lookup feature. It runs a system command in the background. What happens when the hostname isn't a hostname?",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "medium",
                "points": 350,
                "tags": ["command-injection", "rce"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "What separates one shell command from another? Try those characters in the hostname field.", "cost": 0},
                    {"order_num": 2, "content": "The tool runs a DNS lookup command. Appending a shell separator lets you run something else after it.", "cost": 50},
                    {"order_num": 3, "content": "The flag is in a file at the root of the filesystem. Read it with `cat`.", "cost": 75},
                ],
            },
            {
                "slug": "np-xss-reflected-board",
                "title": "Open Mic Night",
                "description": "The community board search reflects your search term back in the response. The page also sets a cookie that isn't protected from client-side access.",
                "challenge_type": "flag",
                "category": "xss",
                "difficulty": "easy",
                "points": 150,
                "tags": ["reflected", "cookie-theft"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try entering some HTML in the search. Does the page render it?", "cost": 0},
                    {"order_num": 2, "content": "If HTML renders, JavaScript does too. The page sets a cookie that JavaScript can read.", "cost": 50},
                    {"order_num": 3, "content": "Read `document.cookie` from your script. The cookie value is the flag.", "cost": 75},
                ],
            },
            {
                "slug": "np-py-ssti",
                "title": "Template Tap",
                "description": (
                    "A portal feature lets operators compose messages with dynamic placeholders. "
                    "The engine that fills those placeholders in is more powerful than the "
                    "interface suggests. A well-placed expression can reach well beyond the "
                    "intended output.\n\n"
                    "**Target:** `http://172.28.6.2` (start Lab 6 — NetPulse)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "python",
                "tags": ["python", "scripting", "ssti", "jinja2", "automation"],
                "skills": ["requests", "SSTI", "template expression crafting"],
                "points": 250,
                "flags": [
                    {"value": "FLAG{np_python_ssti_tapped}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Template engines have a syntax for expressions. Some let expressions do more than format strings.", "cost": 0},
                    {"order_num": 2, "content": "The diagnostics notification preview endpoint passes your input into a render call. Try an arithmetic expression first to confirm.", "cost": 50},
                    {"order_num": 3, "content": "POST your expression as the template_body field to /api/admin/notify/preview and inspect the rendered output.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 7,
        "slug": "limelight",
        "name": "Limelight",
        "description": "Cinema booking system. SQLi, IDOR, logic flaws, AWS creds in SSH home.",
        "category": "world",
        "container_names": ["octorig-limelight"],
        "images": {"app": "octorig-limelight:latest"},
        "build_contexts": {"app": "labs/limelight"},
        "start_order": ["app"],
        "network_name": "octorig-limelight-net",
        "subnet": "172.28.7.0/24",
        "app_ip": "172.28.7.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.7.2"},
            {"key": "SSH", "value": "ssh cinemaops@172.28.7.2 (password: abc123)"},
            {"key": "FTP", "value": "ftp 172.28.7.2 (user: cinemaops / abc123)"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "ll-recon-robots",
                "title": "Curtain Call",
                "description": "Before the main feature begins, someone left instructions for web crawlers. Read the disallowed lines — one of those paths hands back more than it should to any logged-in visitor.",
                "difficulty": "easy",
                "category": "recon",
                "points": 50,
                "challenge_type": "flag",
                "estimated_minutes": 5,
                "tags": ["recon"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Every web server's first secret lives at a well-known path in the root.", "cost": 0},
                    {"order_num": 2, "content": "One of the disallowed paths responds to authenticated users with internal status information and something extra.", "cost": 25},
                ],
            },
            {
                "slug": "ll-sqli-search",
                "title": "Search and Destroy",
                "description": "The film catalogue search takes your query and asks the database. What it returns depends on how you phrase the question.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["sqli", "union", "sqlite"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try unusual characters in the search. Does the error reveal how your input is being used?", "cost": 0},
                    {"order_num": 2, "content": "The search wraps your input in a string comparison. Closing that string lets you append your own query.", "cost": 50},
                    {"order_num": 3, "content": "Use UNION SELECT — match the column count of the movies query and pivot to the schema tables.", "cost": 75},
                ],
            },
            {
                "slug": "ll-sqli-gift",
                "title": "Redeem Yourself",
                "description": "Gift cards are validated by code. The redemption form accepts your code and checks it against the database. What if the code contained more than a card number?",
                "difficulty": "medium",
                "category": "sqli",
                "points": 250,
                "challenge_type": "flag",
                "estimated_minutes": 25,
                "tags": ["sqli", "union", "sqlite"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try putting a special character in the gift code field. What does the response look like?", "cost": 0},
                    {"order_num": 2, "content": "The code field goes straight into a WHERE clause. Enumerate the database schema to find what other tables exist.", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT into a hidden table. Match the column count of the gift card query.", "cost": 75},
                ],
            },
            {
                "slug": "ll-sqli-api-reviews",
                "title": "Critical Review",
                "description": "A JSON endpoint returns film reviews by ID. The ID segment travels from the URL into the query without a stop in between.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["sqli", "api", "path-injection"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Check /openapi.json — the spec lists every available route including newer v1 endpoints.", "cost": 0},
                    {"order_num": 2, "content": "The review endpoint uses an f-string SQL query. The path parameter is the injection point.", "cost": 50},
                ],
            },
            {
                "slug": "ll-xss-stored-review",
                "title": "Standing Ovation",
                "description": "The review system stores and renders submitted text without sanitisation. A payload posted on any film page executes in the browser of every subsequent visitor.",
                "difficulty": "easy",
                "category": "xss",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["xss", "stored", "cookies"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Review text is rendered with no output encoding. A script tag in a review runs for every visitor.", "cost": 0},
                    {"order_num": 2, "content": "Check what cookies are present when the movie page loads. Not all of them carry the HttpOnly flag.", "cost": 25},
                ],
            },
            {
                "slug": "ll-idor-booking",
                "title": "Not Your Seat",
                "description": "Booking confirmation pages verify only that you are logged in — not that the booking is yours. Sequential integers, no access control.",
                "difficulty": "easy",
                "category": "idor",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["idor", "access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Booking IDs are sequential integers. Start from 1.", "cost": 0},
                    {"order_num": 2, "content": "The confirmation code field on the first booking contains something unusual.", "cost": 25},
                ],
            },
            {
                "slug": "ll-bac-admin-panel",
                "title": "Staff Entrance",
                "description": "The administration panel verifies that a session exists. It does not verify whether the session holder is supposed to be there.",
                "difficulty": "easy",
                "category": "web",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["bac", "access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Register a regular account and navigate to the path listed in robots.txt.", "cost": 0},
                ],
            },
            {
                "slug": "ll-ssti-announce",
                "title": "The Projectionist's Script",
                "description": "The announcement editor lets you preview your message before publishing. The preview is rendered on the server — and the render context may know more than the message author.",
                "difficulty": "hard",
                "category": "web",
                "points": 450,
                "challenge_type": "flag",
                "estimated_minutes": 35,
                "tags": ["ssti", "jinja2", "flask"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try submitting `{{ 7*7 }}` in the preview body. If you see 49, the server is evaluating your input.", "cost": 0},
                    {"order_num": 2, "content": "The server-side context exposes internal application state. What objects are available in the template?", "cost": 75},
                ],
            },
            {
                "slug": "ll-mass-assign-privesc",
                "title": "Rewrite the Credits",
                "description": "Profile updates accept fields straight from the POST body with no filtering. Sending fields that were never shown in the form can change more than a display name.",
                "difficulty": "medium",
                "category": "web",
                "points": 250,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["mass-assignment", "privilege-escalation"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "The profile form shows display_name, email, and password — but the endpoint accepts every user column.", "cost": 0},
                    {"order_num": 2, "content": "After updating your own profile with extra fields, an authenticated API endpoint will unlock. Check /api/v1/.", "cost": 50},
                ],
            },
            {
                "slug": "ll-gift-admin-noauth",
                "title": "Unlocked Vault",
                "description": "An administrative endpoint for managing gift cards was deployed without any authentication requirement. The path is hinted from a familiar file.",
                "difficulty": "easy",
                "category": "web",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 5,
                "tags": ["bac", "unauthenticated", "recon"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "robots.txt lists several disallowed paths. One of them needs no credentials at all.", "cost": 0},
                ],
            },
            {
                "slug": "ll-py-bulk-book",
                "title": "Bulk Booker",
                "description": (
                    "Seats are finite. The booking logic enforces that limit — but only if "
                    "requests arrive one at a time. A Python script can send many at once. "
                    "What happens to the seat count when the server can't keep up?\n\n"
                    "**Target:** `http://172.28.7.2` (start Lab 7 — Limelight)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "python",
                "tags": ["python", "scripting", "race-condition", "business-logic", "concurrency"],
                "skills": ["requests", "threading", "session handling", "race condition exploitation"],
                "points": 300,
                "flags": [
                    {"value": "FLAG{ll_python_race_booked}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "The seat limit is checked at read time. What if two writes land before either check completes?", "cost": 0},
                    {"order_num": 2, "content": "The booking endpoint is POST /api/bookings. The seat_count check happens in the request handler, not a transaction.", "cost": 50},
                    {"order_num": 3, "content": "Fire 10+ booking requests for the same fully-booked show in parallel threads sharing one session. Inspect the responses — one may carry the flag.", "cost": 100},
                ],
            },
        ],
    },
    {
        "id": 8,
        "slug": "subverse",
        "name": "SubVerse",
        "description": "Reddit-like community forum. SQLi, XSS, IDOR, CSRF, SSTI, command injection, mass assignment, file upload, SSH/FTP.",
        "category": "world",
        "container_names": ["octorig-subverse"],
        "images": {"app": "octorig-subverse:latest"},
        "build_contexts": {"app": "labs/subverse"},
        "start_order": ["app"],
        "network_name": "octorig-subverse-net",
        "subnet": "172.28.18.0/24",
        "app_ip": "172.28.18.2",
        "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
        "access_info": [
            {"key": "URL", "value": "http://172.28.18.2"},
            {"key": "SSH", "value": "ssh sysadmin@172.28.18.2 (password: subverse2024)"},
            {"key": "FTP", "value": "ftp 172.28.18.2 (anonymous)"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [
            {
                "slug": "sv-recon-robots",
                "title": "Hidden Community",
                "description": "SubVerse hosts communities for all kinds of groups. Not all of them are listed publicly. A file the site publishes for crawlers hints at where the private ones live.",
                "challenge_type": "flag",
                "category": "recon",
                "difficulty": "easy",
                "points": 50,
                "tags": ["information-disclosure"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Check the standard file that web crawlers are expected to read before indexing a site.", "cost": 0},
                    {"order_num": 2, "content": "One of the disallowed paths is a community that isn't linked from anywhere. Visit it and read the announcements.", "cost": 25},
                ],
            },
            {
                "slug": "sv-sqli-login",
                "title": "Ghost Credentials",
                "description": "The login form asks for a username and password. There may be a way to make the password check irrelevant — depending on how you craft the username.",
                "challenge_type": "flag",
                "category": "sqli",
                "difficulty": "easy",
                "points": 100,
                "tags": ["authentication", "boolean-based"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try entering a special character in the username. What does the server respond with?", "cost": 0},
                    {"order_num": 2, "content": "A quote character breaks the authentication query. A comment character ends the query before the password check.", "cost": 50},
                    {"order_num": 3, "content": "After gaining access as admin, inspect the HTTP response headers on the admin panel.", "cost": 75},
                ],
            },
            {
                "slug": "sv-sqli-search-union",
                "title": "Search Party",
                "description": "The post search takes your query and finds matching content. The database stores more than forum posts — and how you phrase the query affects what comes back.",
                "challenge_type": "flag",
                "category": "sqli",
                "difficulty": "medium",
                "points": 250,
                "tags": ["union-based", "sqlite"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try unusual characters in the search box. Does the error reveal anything about how the query works?", "cost": 0},
                    {"order_num": 2, "content": "The database has internal tables not visible through the UI. You can enumerate them.", "cost": 50},
                    {"order_num": 3, "content": "UNION SELECT — determine the column count, then target the internal flags table.", "cost": 75},
                ],
            },
            {
                "slug": "sv-idor-message",
                "title": "Someone's DM",
                "description": "Direct messages are stored by ID. The endpoint retrieves them by that ID. It verifies you're logged in — but whose message it is, it does not check.",
                "challenge_type": "flag",
                "category": "idor",
                "difficulty": "easy",
                "points": 100,
                "tags": ["api", "information-disclosure"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Browse to the messages endpoint. Try IDs you didn't send or receive.", "cost": 0},
                    {"order_num": 2, "content": "Early messages in the system were sent between admin accounts. Low IDs may contain sensitive information.", "cost": 25},
                ],
            },
            {
                "slug": "sv-idor-draft-post",
                "title": "Unpublished",
                "description": "Before a post goes live, it lives as a draft. Draft posts aren't linked in the UI — but if you know the path, and you're logged in, the server will show you.",
                "challenge_type": "flag",
                "category": "idor",
                "difficulty": "easy",
                "points": 100,
                "tags": ["information-disclosure", "broken-access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Draft posts have their own URL pattern. Log in and explore the post path — there may be a draft sub-path.", "cost": 0},
                    {"order_num": 2, "content": "Try iterating post IDs on the draft path. Some posts were never published but are still accessible.", "cost": 25},
                ],
            },
            {
                "slug": "sv-mass-assign-escalate",
                "title": "Power Up",
                "description": "The profile editor lets you update your display name and bio. The server processes whatever fields you send — not just the ones shown in the form.",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "medium",
                "points": 250,
                "tags": ["mass-assignment", "privilege-escalation"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Intercept the profile update request. Are there fields the server accepts that aren't in the HTML form?", "cost": 0},
                    {"order_num": 2, "content": "Try including fields related to account standing or permissions in the POST body.", "cost": 50},
                    {"order_num": 3, "content": "Including `role=admin` in the profile edit POST escalates your account. Then visit the admin secret endpoint.", "cost": 75},
                ],
            },
            {
                "slug": "sv-ssti-announce",
                "title": "The Announcement",
                "description": "Community moderators can preview announcements before publishing. The preview renders on the server — and the rendering context is more capable than a text formatter should be.",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "hard",
                "points": 450,
                "tags": ["ssti", "jinja2", "broken-access-control"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try submitting `{{ 7*7 }}` in the announcement preview. If the response shows 49, the server evaluates your input.", "cost": 0},
                    {"order_num": 2, "content": "The preview endpoint checks login but not role. Any registered user can submit a preview.", "cost": 50},
                    {"order_num": 3, "content": "The server exposes its application config in the template context. The flag is stored there.", "cost": 75},
                ],
            },
            {
                "slug": "sv-cmdi-preview-link",
                "title": "Preview Exploit",
                "description": "When you share a link in a post, the site fetches a preview. Somewhere between your input and the network request, the URL is processed in a way that may allow more than fetching.",
                "challenge_type": "flag",
                "category": "web",
                "difficulty": "medium",
                "points": 350,
                "tags": ["command-injection", "rce"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Try submitting a URL with shell metacharacters in it. What does the server return?", "cost": 0},
                    {"order_num": 2, "content": "The URL is passed to a shell command. Characters that separate shell commands can break out of the URL argument.", "cost": 50},
                    {"order_num": 3, "content": "The flag is in a file at the root of the server filesystem. Use a command to read it.", "cost": 75},
                ],
            },
            {
                "slug": "sv-xss-stored-bio",
                "title": "Bio Hazard",
                "description": "User bios are displayed on public profile pages. The profile page also sets a session cookie. Is the bio display safe to include arbitrary text?",
                "challenge_type": "flag",
                "category": "xss",
                "difficulty": "easy",
                "points": 200,
                "tags": ["stored", "cookie-theft"],
                "skills": [],
                "flags": [],
                "hints": [
                    {"order_num": 1, "content": "Edit your profile bio. Try including some HTML. Does your profile page render it?", "cost": 0},
                    {"order_num": 2, "content": "If HTML renders in the bio, JavaScript does too. The profile page sets a session cookie.", "cost": 50},
                    {"order_num": 3, "content": "The session cookie on this page is not HttpOnly — JavaScript can read it with `document.cookie`.", "cost": 75},
                ],
            },
            {
                "slug": "sv-py-cmdi",
                "title": "Command Drone",
                "description": (
                    "Somewhere in this forum a field passes its value straight into an OS-level "
                    "call. A browser makes that awkward to exploit — a Python script does not. "
                    "Construct the right payload, send it programmatically, and read what the "
                    "server hands back.\n\n"
                    "**Target:** `http://172.28.18.2` (start Lab 8 — SubVerse)"
                ),
                "challenge_type": "flag",
                "difficulty": "hard",
                "category": "python",
                "tags": ["python", "scripting", "command-injection", "rce", "automation"],
                "skills": ["requests", "session handling", "command injection", "shell metacharacters"],
                "points": 300,
                "flags": [
                    {"value": "FLAG{sv_python_cmdi_droned}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Find a feature that sends data off-server on your behalf. The value you supply may reach a shell.", "cost": 0},
                    {"order_num": 2, "content": "The link-preview endpoint passes your URL into a system call. Shell separators can append a second command.", "cost": 50},
                    {"order_num": 3, "content": "POST to /api/posts with a crafted url field. Add a separator and a read command. The flag lives at /flag.txt on the host.", "cost": 100},
                ],
            },
        ],
    },
]
