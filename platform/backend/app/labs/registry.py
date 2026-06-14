"""
Lab registry — authoritative Python source for all 18 OctoRig labs.

Mirrors the LABS array in octorig.sh (lines 54-72) but adds the full
Docker orchestration metadata needed by DockerRuntimeService.

Each entry is a LabDefinition TypedDict. The keys map 1-to-1 to the
LabTemplate SQLAlchemy model so sync_registry() can upsert them directly.

Labs that ship with challenges define them inline via the optional
`challenges` key. sync_registry() upserts those into the platform DB so
they appear in /challenges immediately, no separate seed step needed.
"""
from typing import NotRequired, TypedDict


class FlagDef(TypedDict):
    value: str
    flag_type: str          # "static" | "dynamic" | "regex"
    case_sensitive: bool


class HintDef(TypedDict):
    order_num: int
    content: str
    cost: int               # 0 = free hint


class ChallengeDef(TypedDict):
    slug: str
    title: str
    description: str
    challenge_type: str     # "flag" | "web" | "container" etc.
    difficulty: str         # "easy" | "medium" | "hard" | "insane"
    category: str
    tags: list[str]
    skills: list[str]
    points: int
    flags: list[FlagDef]
    hints: NotRequired[list[HintDef]]


class LabDefinition(TypedDict):
    id: int
    slug: str
    name: str
    description: str
    category: str           # "world" | "firerange" | "thirdparty"
    container_names: list[str]
    images: dict[str, str]  # role → image tag
    build_contexts: dict[str, str]  # role → path relative to OctoRig repo root
    start_order: list[str]  # roles in the order containers must start
    network_name: str
    subnet: str
    app_ip: str
    exposed_ports: dict[str, int]   # service name → port number
    access_info: list[dict[str, str]]  # [{"key": "URL", "value": "..."}]
    volume_names: list[str]
    env_vars: dict[str, str]
    requires_privileged: bool
    challenges: NotRequired[list[ChallengeDef]]


LAB_REGISTRY: list[LabDefinition] = [  # type: ignore[assignment]
    # ------------------------------------------------------------------ #
    # World scenarios (1–8) — realistic apps, Flask + SSH + FTP           #
    # ------------------------------------------------------------------ #
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
            # ── Recon ──────────────────────────────────────────────────────
            {
                "slug": "rw-recon-robots",
                "title": "Rewind: What's Off-Limits?",
                "description": (
                    "Every web server has a way to tell search engines what *not* to index. "
                    "Rewind Range is no exception — and the things it wants crawlers to ignore "
                    "are worth a look.\n\n"
                    "Find the right file, follow where it leads, and you'll end up somewhere "
                    "the store would rather keep private.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "robots.txt", "information-disclosure"],
                "skills": ["passive recon", "directory enumeration"],
                "points": 50,
                "flags": [
                    {"value": "FLAG{rw_manager_office_found}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Start at http://172.28.1.2/robots.txt", "cost": 0},
                ],
            },
            # ── SQL Injection ───────────────────────────────────────────────
            {
                "slug": "rw-sqli-browse-union",
                "title": "Rewind: Browse & Conquer",
                "description": (
                    "The browsing experience on Rewind Range is built on a query that "
                    "trusts user input a little too much. One of the filter parameters "
                    "goes straight into the SQL — no escaping, no parameterisation.\n\n"
                    "Extend that query to reach data the application never intended to "
                    "show you. The database has more tables than the product catalogue.\n\n"
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
                    {"order_num": 1, "content": "Determine column count first: ORDER BY 1, ORDER BY 2, … until an error.", "cost": 0},
                    {"order_num": 2, "content": "SELECT * FROM products returns 10 columns. Match that count in your UNION.", "cost": 25},
                    {"order_num": 3, "content": "SELECT name FROM sqlite_master WHERE type='table' to list all tables.", "cost": 50},
                ],
            },
            {
                "slug": "rw-sqli-login-bypass",
                "title": "Rewind: Bypass the Velvet Rope",
                "description": (
                    "You don't have admin credentials. You don't need them.\n\n"
                    "Rewind Range's login form builds its authentication query the old-fashioned "
                    "way — by gluing strings together. A well-placed quote and a comment can "
                    "make any query return true.\n\n"
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
                    {"order_num": 1, "content": "Classic: username = admin'-- and any password.", "cost": 0},
                ],
            },
            {
                "slug": "rw-sqli-cred-dump",
                "title": "Rewind: Dump the Membership List",
                "description": (
                    "Rewind Range keeps a membership list. Usernames, email addresses, "
                    "and — because it was 2003 when this app was written — plaintext passwords.\n\n"
                    "The same injection point you used to pull hidden data can reach the "
                    "users table too. Find the admin's password and wrap it in `FLAG{}`.\n\n"
                    "**Target:** `http://172.28.1.2` (start Lab 1 — Rewind)"
                ),
                "challenge_type": "flag",
                "difficulty": "medium",
                "category": "sqli",
                "tags": ["sql-injection", "union", "sqlite", "credential-dump"],
                "skills": ["UNION SELECT", "credential extraction"],
                "points": 250,
                "flags": [
                    # Value matches the seeded admin password in db.py
                    {"value": "FLAG{123456789}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Target the `users` table. Columns include username and password.", "cost": 25},
                ],
            },
            # ── XSS ────────────────────────────────────────────────────────
            {
                "slug": "rw-xss-reflected-search",
                "title": "Rewind: Search and Destroy",
                "description": (
                    "Whatever you search for, Rewind Range helpfully echoes it back on "
                    "the results page. The kind of helpful that skips HTML encoding.\n\n"
                    "Make the page execute something it wasn't asked to run, and the flag "
                    "will confirm it worked.\n\n"
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
                    {"order_num": 1, "content": "Try: /search?q=<script>alert(1)</script>", "cost": 0},
                ],
            },
            {
                "slug": "rw-xss-stored-feedback",
                "title": "Rewind: Leave Your Mark",
                "description": (
                    "Happy customers leave feedback. Admins read it.\n\n"
                    "The store has a way to submit comments, and whoever reviews them does "
                    "so in a browser with elevated privileges. If the content isn't sanitised "
                    "before it's rendered, you can make the reviewer's browser work for you.\n\n"
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
                    {"order_num": 1, "content": "Visit /admin/feedback (requires admin session) to see the flag.", "cost": 0},
                    {"order_num": 2, "content": "The admin cookie is named `session`. Forge it or steal it via XSS.", "cost": 50},
                ],
            },
            # ── IDOR ────────────────────────────────────────────────────────
            {
                "slug": "rw-idor-inbox",
                "title": "Rewind: You've Got Mail",
                "description": (
                    "Rewind Range has a private messaging feature. Messages are stored "
                    "with a number, and the app fetches them by that number alone — "
                    "without checking whether the message belongs to you.\n\n"
                    "Log in as any regular user and start counting. Someone important "
                    "left a message you weren't supposed to read.\n\n"
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
                    {"order_num": 1, "content": "Log in as alice (password: iloveyou), then try /inbox/1, /inbox/7…", "cost": 0},
                ],
            },
            {
                "slug": "rw-idor-rental-api",
                "title": "Rewind: Someone Else's Rental",
                "description": (
                    "Rewind Range has a REST API for rental orders. Each order has an ID, "
                    "and the API will hand back the full record — customer name, email, "
                    "everything — to any authenticated user who asks.\n\n"
                    "It never verifies that the order belongs to you. Explore the API, "
                    "enumerate some records, and you'll find something hidden in someone "
                    "else's order.\n\n"
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
                    {"order_num": 1, "content": "Send an authenticated GET to /api/v1/rentals/5 as alice.", "cost": 0},
                ],
            },
            # ── Session Forgery ─────────────────────────────────────────────
            {
                "slug": "rw-session-forge",
                "title": "Rewind: Rewind the Cookie",
                "description": (
                    "Session cookies are signed, not encrypted. The signature is only as "
                    "strong as the secret behind it — and secrets have a way of leaking.\n\n"
                    "Find the signing key, craft a session that says you're the admin, "
                    "and walk through a door you were never given a key to.\n\n"
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
                    {"order_num": 1, "content": "The secret key is hardcoded in app.py. Read the source.", "cost": 0},
                    {"order_num": 2, "content": "flask-unsign --sign --cookie '{\"user_id\": 1}' --secret '<key>'", "cost": 50},
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
            # ── Recon ──────────────────────────────────────────────────────
            {
                "slug": "tf-recon-robots",
                "title": "TradeFloor: Off the Books",
                "description": (
                    "Every exchange has areas it doesn't want indexed. TradeFloor is "
                    "no different — the server's crawl exclusion file hints at paths "
                    "the operators would prefer you didn't visit.\n\n"
                    "Find one of those paths, access it as a logged-in user, and "
                    "collect what the response leaks.\n\n"
                    "**Target:** `http://172.28.2.2` (start Lab 2 — TradeFloor)"
                ),
                "challenge_type": "flag",
                "difficulty": "easy",
                "category": "recon",
                "tags": ["recon", "robots.txt", "information-disclosure", "bac"],
                "skills": ["passive recon", "broken access control"],
                "points": 50,
                "flags": [
                    {"value": "FLAG{tf_fund_manager_found}", "flag_type": "static", "case_sensitive": False}
                ],
                "hints": [
                    {"order_num": 1, "content": "Check /robots.txt and pick one of the Disallow paths.", "cost": 0},
                ],
            },
            # ── SQL Injection ───────────────────────────────────────────────
            {
                "slug": "tf-sqli-market-union",
                "title": "TradeFloor: Inside the Order Book",
                "description": (
                    "The market search feature accepts a ticker query and builds its "
                    "SQL by concatenating your input directly into the string.\n\n"
                    "Extend the query with a UNION to reach a table that shouldn't "
                    "be in the product catalogue at all.\n\n"
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
                    {"order_num": 1, "content": "Try closing the LIKE clause: %' UNION SELECT ...", "cost": 0},
                    {"order_num": 2, "content": "market_data has 6 columns. Match that in your UNION.", "cost": 25},
                    {"order_num": 3, "content": "SELECT name FROM sqlite_master WHERE type='table' to find hidden tables.", "cost": 50},
                ],
            },
            {
                "slug": "tf-sqli-api-token",
                "title": "TradeFloor: Token Without a Password",
                "description": (
                    "TradeFloor's REST API issues JWT tokens via a login endpoint. "
                    "The credential check builds its query by string concatenation.\n\n"
                    "Obtain an admin token without knowing the admin's password, "
                    "then call a privileged endpoint to collect the flag.\n\n"
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
                    {"order_num": 1, "content": "POST JSON to /api/token with a username that breaks the SQL.", "cost": 0},
                    {"order_num": 2, "content": "username: admin'-- works if the query is: WHERE username='...' AND password='...'", "cost": 25},
                ],
            },
            {
                "slug": "tf-sqli-cred-dump",
                "title": "TradeFloor: Membership Leaked",
                "description": (
                    "The same injection that gets you a token can reach further. "
                    "TradeFloor's user table stores credentials in the clear — "
                    "names, emails, and passwords that belong on a Post-it note.\n\n"
                    "Dump the users table and collect what's inside.\n\n"
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
                    {"order_num": 1, "content": "The _flags table has a row called sqli-creds.", "cost": 25},
                ],
            },
            # ── XSS ────────────────────────────────────────────────────────
            {
                "slug": "tf-xss-reflected-market",
                "title": "TradeFloor: Ticker Injection",
                "description": (
                    "The market search field reflects your input back on the results "
                    "page without HTML encoding.\n\n"
                    "Inject a script and read `document.cookie` — the flag is "
                    "sitting in a cookie waiting to be stolen.\n\n"
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
                    {"order_num": 1, "content": "The search query parameter is reflected raw in the HTML.", "cost": 0},
                ],
            },
            # ── IDOR ────────────────────────────────────────────────────────
            {
                "slug": "tf-idor-order-detail",
                "title": "TradeFloor: Someone Else's Trade",
                "description": (
                    "Trade orders each have an ID. The order detail page fetches "
                    "the record by that ID alone — no check that it belongs to you.\n\n"
                    "Log in as any user and enumerate order records until you find "
                    "something that wasn't meant for you.\n\n"
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
                    {"order_num": 1, "content": "Log in as alice.p (password: abc1234) and browse to /orders/<id>.", "cost": 0},
                    {"order_num": 2, "content": "The flag is in a memo field on one of the admin's orders.", "cost": 25},
                ],
            },
            # ── Broken Access Control ───────────────────────────────────────
            {
                "slug": "tf-bac-admin-view",
                "title": "TradeFloor: The Compliance Desk",
                "description": (
                    "TradeFloor's admin panel has a per-user detail view. "
                    "The access check on that page only verifies you're logged in — "
                    "it never checks whether you're actually an admin.\n\n"
                    "Reach the admin's user detail page as a regular user and "
                    "collect the flag that confirms you got in.\n\n"
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
                    {"order_num": 1, "content": "Admin routes are under /admin/. Not all of them properly check is_admin.", "cost": 0},
                    {"order_num": 2, "content": "Try /admin/users/1 while logged in as alice.p.", "cost": 25},
                ],
            },
            # ── JWT ─────────────────────────────────────────────────────────
            {
                "slug": "tf-jwt-alg-none",
                "title": "TradeFloor: Trust Nobody, Sign Nothing",
                "description": (
                    "TradeFloor's API uses JWT tokens. The verification code "
                    "reads the algorithm from the token header itself — and it "
                    "accepts a value that skips signature verification entirely.\n\n"
                    "Forge an admin token, call the privileged report endpoint, "
                    "and retrieve the flag from the response.\n\n"
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
                    {"order_num": 1, "content": "Decode a real token (base64url). Look at the header's 'alg' field.", "cost": 0},
                    {"order_num": 2, "content": "Set alg to 'none' and drop the signature. Include role: admin in the payload.", "cost": 50},
                    {"order_num": 3, "content": "Call GET /api/admin/report with your forged token as Bearer.", "cost": 75},
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
                "tags": ["recon", "robots.txt"],
                "hints": [
                    {"order_num": 1, "content": "Start at robots.txt. One of the disallowed paths needs no authentication at all.", "cost": 0},
                ],
            },
            {
                "slug": "ga-sqli-promo",
                "title": "Free Chips",
                "description": "The promo redemption desk feeds your code directly into the database query. Go further than the code field was meant to reach.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["sqli", "union", "sqlite"],
                "hints": [
                    {"order_num": 1, "content": "The promo code field is interpolated directly into a SQL WHERE clause — no parameterisation.", "cost": 0},
                    {"order_num": 2, "content": "UNION SELECT against a hidden table. Use sqlite_master to enumerate table names first.", "cost": 50},
                ],
            },
            {
                "slug": "ga-sqli-leaderboard",
                "title": "Rigged Rankings",
                "description": "The leaderboard search echoes your query into both the SQL and the page output without filtering either. One request, two vulnerabilities.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["sqli", "union", "reflected-xss"],
                "hints": [
                    {"order_num": 1, "content": "The ?q= parameter on /leaderboard is concatenated directly into a LIKE query.", "cost": 0},
                    {"order_num": 2, "content": "UNION SELECT to pivot into a hidden table. Match the column count of the users query.", "cost": 50},
                ],
            },
            {
                "slug": "ga-xss-chat",
                "title": "Dealer's Message",
                "description": "The live casino chat stores and renders every message raw. A script posted in the chat room runs in the browser of every player who loads the page.",
                "difficulty": "easy",
                "category": "xss",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["xss", "stored", "cookies"],
                "hints": [
                    {"order_num": 1, "content": "Messages are rendered with no output encoding. A script tag in the chat executes for every visitor.", "cost": 0},
                    {"order_num": 2, "content": "Check what cookies are set when the chat page loads — not all carry the HttpOnly flag.", "cost": 25},
                ],
            },
            {
                "slug": "ga-idor-suite",
                "title": "Wrong Room",
                "description": "Player suites display a full game history. The room number is an integer in the URL, and the door has no lock that checks whose name is on the booking.",
                "difficulty": "easy",
                "category": "idor",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["idor", "access-control"],
                "hints": [
                    {"order_num": 1, "content": "Suite IDs are sequential integers. Start from 1 — the house always gets suite one.", "cost": 0},
                    {"order_num": 2, "content": "The admin's game history contains an unusual entry in the memo field.", "cost": 25},
                ],
            },
            {
                "slug": "ga-biz-negative-bet",
                "title": "The House Loses",
                "description": "The slot machine trusts the bet amount submitted in the POST body without checking its sign. Maths works in both directions.",
                "difficulty": "medium",
                "category": "web",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["business-logic", "parameter-tampering"],
                "hints": [
                    {"order_num": 1, "content": "The bet field is a hidden form input. Intercept the request and change its value.", "cost": 0},
                    {"order_num": 2, "content": "Try submitting a negative number. Watch what the server logs in the audit trail.", "cost": 25},
                ],
            },
            {
                "slug": "ga-bac-admin",
                "title": "Staff Only",
                "description": "The admin panel gates on a session existing — not on the session belonging to an admin. Any registered player can walk behind the counter.",
                "difficulty": "easy",
                "category": "web",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["bac", "access-control"],
                "hints": [
                    {"order_num": 1, "content": "Register a regular account and visit /admin.", "cost": 0},
                ],
            },
            {
                "slug": "ga-bac-high-rollers",
                "title": "VIP Lounge",
                "description": "A restricted lounge for high-rollers and VIPs is linked from the crawlers-only file. The endpoint checks for a session — but never whether the session holder qualifies.",
                "difficulty": "easy",
                "category": "web",
                "points": 100,
                "challenge_type": "flag",
                "estimated_minutes": 10,
                "tags": ["bac", "access-control", "recon"],
                "hints": [
                    {"order_num": 1, "content": "robots.txt lists a path restricted to high-rollers. Log in as any user and request it directly.", "cost": 0},
                ],
            },
            {
                "slug": "ga-promo-reuse",
                "title": "Double Down",
                "description": "The promo system records each redemption — but never consults that record before accepting another. Redeem the same code twice to prove the gap.",
                "difficulty": "medium",
                "category": "web",
                "points": 150,
                "challenge_type": "flag",
                "estimated_minutes": 15,
                "tags": ["business-logic", "promo-abuse"],
                "hints": [
                    {"order_num": 1, "content": "The system checks max_uses against uses_count, but never checks if you personally have already redeemed the code.", "cost": 0},
                    {"order_num": 2, "content": "Redeem any multi-use promo code (like WELCOME100) twice with the same account.", "cost": 25},
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
            # ── Recon ──────────────────────────────────────────────────────────
            {
                "slug": "hb-recon-audit-log",
                "title": "HumanBank: Open Books",
                "description": (
                    "HumanBank exposes an internal endpoint that was never meant to be "
                    "public. No authentication required — it just responds with the "
                    "raw transaction log for the entire bank.\n\n"
                    "Find the endpoint (the OpenAPI spec at `/openapi.json` is a good "
                    "starting point), call it without logging in, and read the flag "
                    "buried in the transaction memos.\n\n"
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
                    {"order_num": 1, "content": "Check `/openapi.json` for a full list of endpoints.", "cost": 0},
                    {"order_num": 2, "content": "One of the listed paths under `/audit-log` requires no session cookie at all.", "cost": 25},
                ],
            },
            # ── SQL Injection ───────────────────────────────────────────────────
            {
                "slug": "hb-sqli-login",
                "title": "HumanBank: Master Key",
                "description": (
                    "HumanBank's login form builds its SQL query by stitching username "
                    "and password directly into an f-string — no parameterisation, no "
                    "escaping.\n\n"
                    "Comment out the password check with a classic injection payload "
                    "and log in as the admin. Once in, check the admin profile for "
                    "something the bank keeps very close to its chest.\n\n"
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
                    {"order_num": 1, "content": "Try the username field. A single quote followed by `--` comments out the rest of the query.", "cost": 0},
                    {"order_num": 2, "content": "Payload: `admin'--` as the username. Any password.", "cost": 50},
                    {"order_num": 3, "content": "After logging in as admin, check `/profile` — the admin's address field holds the flag.", "cost": 75},
                ],
            },
            {
                "slug": "hb-sqli-search",
                "title": "HumanBank: Transaction Miner",
                "description": (
                    "The transaction search at `/search?q=` drops your input straight "
                    "into a `LIKE` clause with no sanitisation. The database has more "
                    "than just transactions.\n\n"
                    "Use a UNION-based injection to pivot into the internal `_flags` "
                    "table and retrieve the value for `sqli-search`.\n\n"
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
                    {"order_num": 1, "content": "Count the columns first: try `' UNION SELECT NULL--` and add NULLs until the error disappears.", "cost": 0},
                    {"order_num": 2, "content": "The query returns 7 columns. Inject: `' UNION SELECT value,2,3,4,5,6,7 FROM _flags WHERE name='sqli-search'--`", "cost": 75},
                ],
            },
            {
                "slug": "hb-sqli-txn-memo",
                "title": "HumanBank: Filter Bypass",
                "description": (
                    "The transaction list at `/accounts/<id>/transactions` accepts "
                    "filter parameters — `memo`, `type`, `date_from`, `date_to` — and "
                    "concatenates every one of them directly into the SQL WHERE clause.\n\n"
                    "Inject into the `memo` parameter to UNION-select from the internal "
                    "`_flags` table and retrieve the value for `sqli-txn`.\n\n"
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
                    {"order_num": 1, "content": "The `memo` param is injected as: `memo LIKE '%<your input>%'`. Close the LIKE, then UNION.", "cost": 0},
                    {"order_num": 2, "content": "Payload: `?memo=' UNION SELECT name,value,3,4,5,6 FROM _flags WHERE name='sqli-txn'--`", "cost": 75},
                ],
            },
            # ── IDOR ────────────────────────────────────────────────────────────
            {
                "slug": "hb-idor-accounts",
                "title": "HumanBank: Everyone's Balance",
                "description": (
                    "HumanBank's `/accounts` route lists every account in the database "
                    "regardless of who is logged in — no ownership filter at all.\n\n"
                    "Log in as any user, browse to `/accounts`, and find the mysterious "
                    "`HB-CMNH` account. Navigate to its transaction history "
                    "to find the flag hidden in an internal audit memo.\n\n"
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
                    {"order_num": 1, "content": "Register or log in as any user. `/accounts` shows ALL bank accounts.", "cost": 0},
                    {"order_num": 2, "content": "Find account HB-CMNH in the list and click through to its transactions.", "cost": 25},
                ],
            },
            {
                "slug": "hb-idor-ticket",
                "title": "HumanBank: Someone Else's Ticket",
                "description": (
                    "Support tickets at `/tickets/<id>` don't verify that the ticket "
                    "belongs to the logged-in user. The endpoint just looks up by ID "
                    "and returns whatever it finds.\n\n"
                    "Enumerate ticket IDs to find an internal admin-created ticket "
                    "that was never meant to be visible to customers. The flag is in "
                    "the ticket body.\n\n"
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
                    {"order_num": 1, "content": "Try incrementing the ticket ID in the URL. You can access tickets that don't belong to your account.", "cost": 0},
                ],
            },
            # ── Broken Access Control ───────────────────────────────────────────
            {
                "slug": "hb-bac-admin-api",
                "title": "HumanBank: Fake Admin API",
                "description": (
                    "The REST endpoint `/api/v1/admin/users` is supposed to be "
                    "admin-only. The access check reads `if not session.get('user_id')` "
                    "— it verifies you're *logged in*, but never checks `is_admin`.\n\n"
                    "Log in as any regular customer and call the endpoint. The JSON "
                    "response exposes the full user list — and something extra the "
                    "developer left in the payload.\n\n"
                    "**Target:** `http://172.28.4.2/api/v1/admin/users` "
                    "(start Lab 4 — HumanBank)"
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
                    {"order_num": 1, "content": "Register any account. Call `/api/v1/admin/users` with your session cookie. Inspect the JSON response carefully.", "cost": 0},
                ],
            },
            {
                "slug": "hb-bac-user-detail",
                "title": "HumanBank: Admin Panel Without the Admin",
                "description": (
                    "The admin user-detail page at `/admin/users/<id>` checks "
                    "`if not session.get('user_id')` — any logged-in customer can "
                    "access it. No `is_admin` check in sight.\n\n"
                    "Navigate directly to `/admin/users/1` as a regular user. "
                    "The rendered page leaks the admin account's internal profile, "
                    "including a field that was never meant to be public.\n\n"
                    "**Target:** `http://172.28.4.2/admin/users/1` "
                    "(start Lab 4 — HumanBank)"
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
                    {"order_num": 1, "content": "Log in as any user. Navigate to `/admin/users/1`. The admin's bio field contains the flag.", "cost": 0},
                ],
            },
            # ── XSS ────────────────────────────────────────────────────────────
            {
                "slug": "hb-xss-stored-ticket",
                "title": "HumanBank: Support Ticket Hijack",
                "description": (
                    "Support ticket bodies are stored without sanitisation and rendered "
                    "unescaped in the admin panel at `/admin/tickets`. The admin panel "
                    "sets a non-HttpOnly cookie — meaning any JavaScript running on "
                    "that page can read it.\n\n"
                    "Submit a support ticket with an XSS payload. Then log in as admin "
                    "(the login form is also injectable) and visit `/admin/tickets`. "
                    "Your payload fires — `document.cookie` contains the flag.\n\n"
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
                    {"order_num": 1, "content": "Submit a ticket with `<script>document.title=document.cookie</script>` as the body.", "cost": 0},
                    {"order_num": 2, "content": "The admin template renders ticket bodies with `| safe` — no escaping. Log in as admin (use SQLi on the login form) and check `/admin/tickets`.", "cost": 50},
                    {"order_num": 3, "content": "The cookie name is `hb_admin_token`. Its value is the flag.", "cost": 100},
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
        "challenges": [],
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
        "challenges": [],
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
                "tags": ["recon", "robots.txt"],
                "hints": [
                    {"order_num": 1, "content": "Every web server's first secret lives at a well-known path in the root.", "cost": 0},
                    {"order_num": 2, "content": "One of the disallowed paths responds to authenticated users with internal status information and something extra.", "cost": 25},
                ],
            },
            {
                "slug": "ll-sqli-search",
                "title": "Search and Destroy",
                "description": "The film catalogue search hands your input directly to the database. Craft a query that reaches far beyond the movie listings.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 200,
                "challenge_type": "flag",
                "estimated_minutes": 20,
                "tags": ["sqli", "union", "sqlite"],
                "hints": [
                    {"order_num": 1, "content": "The search term lands inside a LIKE clause with no parameterisation — try closing the string.", "cost": 0},
                    {"order_num": 2, "content": "UNION SELECT requires matching column count. Count the columns in the movies table and enumerate tables with sqlite_master.", "cost": 50},
                ],
            },
            {
                "slug": "ll-sqli-gift",
                "title": "Redeem Yourself",
                "description": "Gift card validation passes the submitted code straight into a SQL query. The right injection might redeem something the database was never meant to give away.",
                "difficulty": "medium",
                "category": "sqli",
                "points": 250,
                "challenge_type": "flag",
                "estimated_minutes": 25,
                "tags": ["sqli", "union", "sqlite"],
                "hints": [
                    {"order_num": 1, "content": "The gift card code field is interpolated directly into a WHERE clause.", "cost": 0},
                    {"order_num": 2, "content": "UNION-based injection on the redemption form. Enumerate tables first, then look for a hidden one.", "cost": 50},
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
                "hints": [
                    {"order_num": 1, "content": "Register a regular account and navigate to the path listed in robots.txt.", "cost": 0},
                ],
            },
            {
                "slug": "ll-ssti-announce",
                "title": "The Projectionist's Script",
                "description": "The announcement preview feature passes submitted content directly to a Python template engine at render time. The engine is more powerful than the feature suggests.",
                "difficulty": "hard",
                "category": "web",
                "points": 450,
                "challenge_type": "flag",
                "estimated_minutes": 35,
                "tags": ["ssti", "jinja2", "flask"],
                "hints": [
                    {"order_num": 1, "content": "{{ 7*7 }} is a reliable first test for server-side template injection.", "cost": 0},
                    {"order_num": 2, "content": "Flask's config object is accessible from the template context. What keys are stored in it?", "cost": 75},
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
                "hints": [
                    {"order_num": 1, "content": "robots.txt lists several disallowed paths. One of them needs no credentials at all.", "cost": 0},
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
        "challenges": [],
    },
    # ------------------------------------------------------------------ #
    # Scanner fire-ranges (9–12) — structured challenges for tool testing  #
    # ------------------------------------------------------------------ #
    {
        "id": 9,
        "slug": "breachsql",
        "name": "BreachSQL",
        "description": "57 SQL injection challenges across MySQL, PostgreSQL, and SQLite. Tiered T1–T5.",
        "category": "firerange",
        "container_names": [
            "octorig-breachsql-db",
            "octorig-breachsql-pg",
            "octorig-breachsql-app",
        ],
        "images": {
            "db": "mysql:8.0",
            "pg": "postgres:16-alpine",
            "app": "octorig-breachsql:latest",
        },
        "build_contexts": {"app": "labs/firerange"},
        "start_order": ["db", "pg", "app"],
        "network_name": "octorig-breachsql-net",
        "subnet": "172.28.8.0/24",
        "app_ip": "172.28.8.2",
        "exposed_ports": {"http": 80},
        "access_info": [
            {"key": "URL", "value": "http://172.28.8.2"},
            {"key": "Challenges", "value": "GET /api/challenges"},
            {"key": "Submit flag", "value": "POST /api/submit-flag"},
            {"key": "Scoreboard", "value": "GET /scoreboard"},
        ],
        "volume_names": ["octorig-breachsql-scores"],
        "env_vars": {
            "MYSQL_HOST": "octorig-breachsql-db",
            "MYSQL_PORT": "3306",
            "MYSQL_USER": "firerange",
            "MYSQL_PASSWORD": "firerange",
            "MYSQL_DATABASE": "firerange",
            "PG_HOST": "octorig-breachsql-pg",
            "PG_PORT": "5432",
            "PG_USER": "firerange",
            "PG_PASSWORD": "firerange",
            "PG_DATABASE": "firerange",
        },
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 10,
        "slug": "stingxss",
        "name": "StingXSS",
        "description": "40+ XSS challenges: reflected, stored, DOM, blind, WAF bypass, CSP, GraphQL, WebSocket.",
        "category": "firerange",
        "container_names": ["octorig-stingxss"],
        "images": {"app": "octorig-stingxss:latest"},
        "build_contexts": {"app": "labs/stingxss"},
        "start_order": ["app"],
        "network_name": "octorig-stingxss-net",
        "subnet": "172.28.9.0/24",
        "app_ip": "172.28.9.2",
        "exposed_ports": {"http": 80},
        "access_info": [
            {"key": "URL", "value": "http://172.28.9.2"},
            {"key": "Challenges", "value": "GET /api/challenges"},
            {"key": "Submit flag", "value": "POST /api/submit-flag"},
            {"key": "XSS beacon", "value": "GET /api/catch?cid=...&player=..."},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 11,
        "slug": "vaultgate",
        "name": "VaultGate",
        "description": "IDOR / BOLA benchmarking: horizontal, obfuscated IDs, JWT tampering, mass assignment.",
        "category": "firerange",
        "container_names": ["octorig-vaultgate"],
        "images": {"app": "octorig-vaultgate:latest"},
        "build_contexts": {"app": "labs/vaultgate"},
        "start_order": ["app"],
        "network_name": "octorig-vaultgate-net",
        "subnet": "172.28.10.0/24",
        "app_ip": "172.28.10.2",
        "exposed_ports": {"http": 80},
        "access_info": [
            {"key": "URL", "value": "http://172.28.10.2"},
            {"key": "Challenges", "value": "GET /api/challenges"},
            {"key": "Submit flag", "value": "POST /api/submit-flag"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 12,
        "slug": "vaultriprange",
        "name": "VaultRip Range",
        "description": "Credential harvesting lab. SSH services with intentionally weak/exposed secrets.",
        "category": "firerange",
        "container_names": ["octorig-vaultriprange"],
        "images": {"app": "octorig-vaultriprange:latest"},
        "build_contexts": {"app": "labs/vaultriprange"},
        "start_order": ["app"],
        "network_name": "octorig-vaultriprange-net",
        "subnet": "172.28.11.0/24",
        "app_ip": "172.28.11.2",
        "exposed_ports": {"ssh": 22},
        "access_info": [
            {"key": "SSH", "value": "ssh admin@172.28.11.2"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    # ------------------------------------------------------------------ #
    # Third-party images (13–18) — pulled from Docker Hub                  #
    # ------------------------------------------------------------------ #
    {
        "id": 13,
        "slug": "juiceshop",
        "name": "Juice Shop",
        "description": "OWASP Juice Shop — deliberately insecure Node.js web application.",
        "category": "thirdparty",
        "container_names": ["octorig-juiceshop"],
        "images": {"app": "bkimminich/juice-shop:latest"},
        "build_contexts": {},
        "start_order": ["app"],
        "network_name": "octorig-juiceshop-net",
        "subnet": "172.28.12.0/24",
        "app_ip": "172.28.12.2",
        "exposed_ports": {"http": 3000},
        "access_info": [
            {"key": "URL", "value": "http://172.28.12.2:3000"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 14,
        "slug": "dvwa",
        "name": "DVWA",
        "description": "Damn Vulnerable Web Application. Classic PHP/MySQL training target.",
        "category": "thirdparty",
        "container_names": ["octorig-dvwa"],
        "images": {"app": "ghcr.io/digininja/dvwa:latest"},
        "build_contexts": {},
        "start_order": ["app"],
        "network_name": "octorig-dvwa-net",
        "subnet": "172.28.13.0/24",
        "app_ip": "172.28.13.2",
        "exposed_ports": {"http": 80},
        "access_info": [
            {"key": "URL", "value": "http://172.28.13.2"},
            {"key": "Login", "value": "admin / password"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 15,
        "slug": "metasploitable",
        "name": "Metasploitable2",
        "description": "Classic intentionally vulnerable Linux VM in Docker form. Multi-service.",
        "category": "thirdparty",
        "container_names": ["octorig-metasploitable"],
        "images": {"app": "tleemcjr/metasploitable2:latest"},
        "build_contexts": {},
        "start_order": ["app"],
        "network_name": "octorig-metasploitable-net",
        "subnet": "172.28.14.0/24",
        "app_ip": "172.28.14.2",
        "exposed_ports": {"http": 80, "ftp": 21, "ssh": 22, "telnet": 23},
        "access_info": [
            {"key": "URL", "value": "http://172.28.14.2"},
            {"key": "SSH", "value": "ssh msfadmin@172.28.14.2 (password: msfadmin)"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": True,
        "challenges": [],
    },
    {
        "id": 16,
        "slug": "webgoat",
        "name": "WebGoat",
        "description": "OWASP WebGoat — deliberately insecure Java web application for training.",
        "category": "thirdparty",
        "container_names": ["octorig-webgoat"],
        "images": {"app": "webgoat/webgoat:latest"},
        "build_contexts": {},
        "start_order": ["app"],
        "network_name": "octorig-webgoat-net",
        "subnet": "172.28.15.0/24",
        "app_ip": "172.28.15.2",
        "exposed_ports": {"http": 8080},
        "access_info": [
            {"key": "URL", "value": "http://172.28.15.2:8080/WebGoat"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": False,
        "challenges": [],
    },
    {
        "id": 17,
        "slug": "vulnad",
        "name": "VulnAD",
        "description": "Vulnerable Active Directory environment. Samba4 DC with misconfigured GPOs.",
        "category": "thirdparty",
        "container_names": ["octorig-vulnad"],
        "images": {"app": "octorig-vulnad:latest"},
        "build_contexts": {"app": "labs/vulnad"},
        "start_order": ["app"],
        "network_name": "octorig-vulnad-net",
        "subnet": "172.28.17.0/24",
        "app_ip": "172.28.17.2",
        "exposed_ports": {"ldap": 389, "smb": 445, "kerberos": 88},
        "access_info": [
            {"key": "Domain", "value": "VULNAD.LOCAL"},
            {"key": "DC IP", "value": "172.28.17.2"},
            {"key": "Admin", "value": "Administrator / Passw0rd!"},
        ],
        "volume_names": [],
        "env_vars": {},
        "requires_privileged": True,
        "challenges": [],
    },
]

REGISTRY_BY_SLUG: dict[str, LabDefinition] = {lab["slug"]: lab for lab in LAB_REGISTRY}
REGISTRY_BY_ID: dict[int, LabDefinition] = {lab["id"]: lab for lab in LAB_REGISTRY}
