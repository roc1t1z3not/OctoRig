# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Manual browser UI pages for select challenges."""
from __future__ import annotations

from flask import Blueprint, make_response, render_template, request

bp = Blueprint("ui", __name__)


def _page(title_suffix: str, content: str):
    return render_template(
        "layout.html",
        block_title=title_suffix,
        block_content=content,
    )


# ---------------------------------------------------------------------------
# my2b — Login Wall (MySQL POST login)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my2b/ui")
def t2b_ui():
    content = """
<div class="ui-card" data-challenge-id="my2b">
  <h2>Login Wall <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2b]</span></h2>
  <p class="subtitle">A staff portal login. Enter credentials to authenticate.</p>
  <form method="POST" action="/challenges/my2/login" data-fetch="resp-my2b">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
  <pre class="response-box" id="resp-my2b"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my2b: Login Wall", content)


# ---------------------------------------------------------------------------
# my2d — Second Sight (search + inbox viewer)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my2d/ui")
def t2d_ui():
    content = """
<div class="ui-card" data-challenge-id="my2d">
  <h2>Second Sight <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2d]</span></h2>
  <p class="subtitle">Search for a user, then read their inbox. The flag travels between two requests.</p>
  <form method="GET" action="/challenges/my2/search" data-fetch="resp-my2d">
    <div class="field"><label>Search username</label><input name="user" type="text" value="admin" autocomplete="off"></div>
    <button class="btn" type="submit">Search</button>
  </form>
  <pre class="response-box" id="resp-my2d"></pre>
  <p style="font-size:.8rem;color:var(--muted);margin-top:12px">
    After searching, read the result at
    <a href="/challenges/my2/inbox">/challenges/my2/inbox</a>.
  </p>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my2d: Second Sight", content)


# ---------------------------------------------------------------------------
# my4b — API Whisperer (JSON body POST)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my4b/ui")
def t4b_ui():
    content = """
<div class="ui-card" data-challenge-id="my4b">
  <h2>API Whisperer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4b]</span></h2>
  <p class="subtitle">A JSON API that looks up users by ID. Edit the body and fire the request.</p>
  <form method="POST" action="/challenges/my4/api/user" enctype="application/x-www-form-urlencoded" data-fetch="resp-my4b">
    <div class="field"><label>user_id</label><input name="user_id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">POST /challenges/my4/api/user</button>
  </form>
  <pre class="response-box" id="resp-my4b"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my4b: API Whisperer", content)


# ---------------------------------------------------------------------------
# my4e — Cookie Monster (session_id cookie profile)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my4e/ui")
def t4e_ui():
    current = request.cookies.get("session_id", "sess_def456")
    content = f"""
<div class="ui-card" data-challenge-id="my4e">
  <h2>Cookie Monster <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4e]</span></h2>
  <p class="subtitle">
    The profile endpoint reads your <code>session_id</code> cookie to look you up.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Current <code>session_id</code>: <code>{current}</code>
  </p>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
    Set the cookie in DevTools (<code>session_id=PAYLOAD</code>) or use
    <code>--cookie "session_id=PAYLOAD"</code> with curl / sqlmap.
  </p>
  <button class="btn" style="margin-top:12px" onclick="fetchEndpoint('/challenges/my4/profile','resp-my4e')">
    Fetch /challenges/my4/profile
  </button>
  <pre class="response-box" id="resp-my4e"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my4e: Cookie Monster", content)


# ---------------------------------------------------------------------------
# pg3b — PG POST Form (PostgreSQL login)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg3b/ui")
def pg3b_ui():
    content = """
<div class="ui-card" data-challenge-id="pg3b">
  <h2>PG POST Form <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg3b]</span></h2>
  <p class="subtitle">A PostgreSQL-backed staff login. The password field maps to the email column.</p>
  <form method="POST" action="/challenges/pg/login" data-fetch="resp-pg3b">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password (email)</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
  <pre class="response-box" id="resp-pg3b"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg3b: PG POST Form", content)


# ---------------------------------------------------------------------------
# pg2f — PG Echo Chamber (second-order, POST profile update)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg2f/ui")
def pg2f_ui():
    content = """
<div class="ui-card" data-challenge-id="pg2f">
  <h2>PG Echo Chamber <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg2f]</span></h2>
  <p class="subtitle">Update a profile bio. The stored value is later read back verbatim.</p>
  <form method="POST" action="/challenges/pg/profile" data-fetch="resp-pg2f">
    <div class="field"><label>Username</label><input name="username" type="text" value="alice" autocomplete="off"></div>
    <div class="field"><label>Bio</label><input name="bio" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Save profile</button>
  </form>
  <pre class="response-box" id="resp-pg2f"></pre>
  <p style="font-size:.8rem;color:var(--muted);margin-top:12px">
    After saving, read the result at
    <a href="/challenges/pg/profile?username=alice">/challenges/pg/profile?username=alice</a>.
  </p>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg2f: PG Echo Chamber", content)


# ---------------------------------------------------------------------------
# sq2e — Lite Login (SQLite POST login)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2e/ui")
def sq2e_ui():
    content = """
<div class="ui-card" data-challenge-id="sq2e">
  <h2>Lite Login <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2e]</span></h2>
  <p class="subtitle">A SQLite-backed login form. Enter credentials to authenticate.</p>
  <form method="POST" action="/challenges/sq/login" data-fetch="resp-sq2e">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
  <pre class="response-box" id="resp-sq2e"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2e: Lite Login", content)


# ---------------------------------------------------------------------------
# sq2h — Lite Echo (second-order, POST profile update)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2h/ui")
def sq2h_ui():
    content = """
<div class="ui-card" data-challenge-id="sq2h">
  <h2>Lite Echo <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2h]</span></h2>
  <p class="subtitle">Update a profile bio. The stored value is later read back verbatim.</p>
  <form method="POST" action="/challenges/sq/profile" data-fetch="resp-sq2h">
    <div class="field"><label>Username</label><input name="username" type="text" value="alice" autocomplete="off"></div>
    <div class="field"><label>Bio</label><input name="bio" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Save profile</button>
  </form>
  <pre class="response-box" id="resp-sq2h"></pre>
  <p style="font-size:.8rem;color:var(--muted);margin-top:12px">
    After saving, read the result at
    <a href="/challenges/sq/profile?username=alice">/challenges/sq/profile?username=alice</a>.
  </p>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2h: Lite Echo", content)


# ---------------------------------------------------------------------------
# sq2i — Lite Whisperer (JSON body POST)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2i/ui")
def sq2i_ui():
    content = """
<div class="ui-card" data-challenge-id="sq2i">
  <h2>Lite Whisperer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2i]</span></h2>
  <p class="subtitle">A SQLite member lookup that reads from a JSON body. The ID is embedded raw.</p>
  <form method="POST" action="/challenges/sq/api/member" enctype="application/x-www-form-urlencoded" data-fetch="resp-sq2i">
    <div class="field"><label>member_id</label><input name="member_id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">POST /challenges/sq/api/member</button>
  </form>
  <pre class="response-box" id="resp-sq2i"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2i: Lite Whisperer", content)


# ---------------------------------------------------------------------------
# my4f — Ghost Writer (MySQL User-Agent header injection)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my4f/ui")
def my4f_ui():
    current_ua = request.headers.get("User-Agent", "Mozilla/5.0")
    content = f"""
<div class="ui-card" data-challenge-id="my4f">
  <h2>Ghost Writer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4f]</span></h2>
  <p class="subtitle">
    A request logger that records the <code>User-Agent</code> header verbatim into the database.
    The injection surface is the header itself — not the URL.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Your current <code>User-Agent</code>: <code>{current_ua}</code>
  </p>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
    Use the <code>?ua=</code> query parameter as a scanner-accessible fallback, or set the
    <code>User-Agent</code> header directly with curl / sqlmap
    (<code>--user-agent</code> / <code>-p ua</code>).
  </p>
  <form method="GET" action="/challenges/my4/agent" data-fetch="resp-my4f">
    <div class="field"><label>?ua= fallback</label><input name="ua" type="text" value="Mozilla/5.0" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/my4/agent</button>
  </form>
  <pre class="response-box" id="resp-my4f"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my4f: Ghost Writer", content)


# ---------------------------------------------------------------------------
# pg3e — PG Ghost Writer (PostgreSQL User-Agent header injection)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg3e/ui")
def pg3e_ui():
    current_ua = request.headers.get("User-Agent", "Mozilla/5.0")
    content = f"""
<div class="ui-card" data-challenge-id="pg3e">
  <h2>PG Ghost Writer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg3e]</span></h2>
  <p class="subtitle">
    A PostgreSQL request logger. The <code>User-Agent</code> header is stored raw and the flag
    lives in the same table.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Your current <code>User-Agent</code>: <code>{current_ua}</code>
  </p>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
    Use the <code>?ua=</code> query parameter as a scanner-accessible fallback, or inject via
    the <code>User-Agent</code> header directly.
  </p>
  <form method="GET" action="/challenges/pg/agent" data-fetch="resp-pg3e">
    <div class="field"><label>?ua= fallback</label><input name="ua" type="text" value="Mozilla/5.0" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/pg/agent</button>
  </form>
  <pre class="response-box" id="resp-pg3e"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg3e: PG Ghost Writer", content)


# ---------------------------------------------------------------------------
# pg3c — PG Cookie (PostgreSQL auth_token cookie injection)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg3c/ui")
def pg3c_ui():
    current = request.cookies.get("auth_token", "tok_default")
    content = f"""
<div class="ui-card" data-challenge-id="pg3c">
  <h2>PG Cookie <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg3c]</span></h2>
  <p class="subtitle">
    A PostgreSQL session endpoint that looks up your account by the <code>auth_token</code> cookie.
    The cookie value is embedded raw into the query.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Current <code>auth_token</code>: <code>{current}</code>
  </p>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
    Set the <code>auth_token</code> cookie in your browser DevTools or use
    <code>--cookie "auth_token=PAYLOAD"</code> with curl / sqlmap.
  </p>
  <button class="btn" style="margin-top:12px" onclick="fetchEndpoint('/challenges/pg/session','resp-pg3c')">
    Fetch /challenges/pg/session
  </button>
  <pre class="response-box" id="resp-pg3c"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg3c: PG Cookie", content)


# ---------------------------------------------------------------------------
# my3a — Sleeping Giant (MySQL time-blind)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my3a/ui")
def my3a_ui():
    content = """
<div class="ui-card" data-challenge-id="my3a">
  <h2>Sleeping Giant <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my3a]</span></h2>
  <p class="subtitle">
    A staff directory with uniform responses. The only signal is how long the server takes to reply.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    The endpoint always returns <code>found: true/false</code>. Use
    <code>IF(condition, SLEEP(N), 0)</code> to leak data one bit at a time.
    Watch the <code>elapsed</code> field in the response.
  </p>
  <form method="GET" action="/challenges/my2/search" data-fetch="resp-my3a">
    <div class="field"><label>name</label><input name="name" type="text" value="admin" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/my2/search</button>
  </form>
  <pre class="response-box" id="resp-my3a"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my3a: Sleeping Giant", content)


# ---------------------------------------------------------------------------
# pg2a — PG Sleep (PostgreSQL time-blind)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg2a/ui")
def pg2a_ui():
    content = """
<div class="ui-card" data-challenge-id="pg2a">
  <h2>PG Sleep <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg2a]</span></h2>
  <p class="subtitle">
    A PostgreSQL employee directory. Every response looks identical — timing is the only channel.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Use <code>'; SELECT CASE WHEN (condition) THEN pg_sleep(N) ELSE pg_sleep(0) END--</code>
    in the <code>name</code> parameter. Watch the <code>elapsed</code> field in the response.
  </p>
  <form method="GET" action="/challenges/pg/employees" data-fetch="resp-pg2a">
    <div class="field"><label>name</label><input name="name" type="text" value="Jane Doe" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/pg/employees</button>
  </form>
  <pre class="response-box" id="resp-pg2a"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg2a: PG Sleep", content)


# ---------------------------------------------------------------------------
# sq2a — Lite Time (SQLite time-blind via randomblob)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2a/ui")
def sq2a_ui():
    content = """
<div class="ui-card" data-challenge-id="sq2a">
  <h2>Lite Time <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2a]</span></h2>
  <p class="subtitle">
    A SQLite file ownership lookup. There is no <code>SLEEP()</code> — but <code>randomblob(N)</code>
    grows expensive as N grows. Time that expense.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Use <code>' AND (SELECT CASE WHEN (condition) THEN randomblob(100000000) ELSE 0 END)--</code>
    in the <code>owner</code> parameter. Watch the <code>elapsed</code> field in the response.
  </p>
  <form method="GET" action="/challenges/sq/files" data-fetch="resp-sq2a">
    <div class="field"><label>owner</label><input name="owner" type="text" value="admin" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/sq/files</button>
  </form>
  <pre class="response-box" id="resp-sq2a"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2a: Lite Time", content)


# ---------------------------------------------------------------------------
# my2e — Group Think (MySQL HAVING / GROUP BY)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my2e/ui")
def my2e_ui():
    content = """
<div class="ui-card" data-challenge-id="my2e">
  <h2>Group Think <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2e]</span></h2>
  <p class="subtitle">
    An analytics summary grouped by department. The <code>dept</code> parameter feeds straight
    into the <code>WHERE</code> and <code>HAVING</code> clauses.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Try error-based payloads or inject into the <code>HAVING</code> clause to enumerate data.
  </p>
  <form method="GET" action="/challenges/my2/groups" data-fetch="resp-my2e">
    <div class="field">
      <label>dept</label>
      <input name="dept" type="text" value="engineering" autocomplete="off">
    </div>
    <button class="btn" type="submit">GET /challenges/my2/groups</button>
  </form>
  <pre class="response-box" id="resp-my2e"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my2e: Group Think", content)


# ---------------------------------------------------------------------------
# pg2d — Aggregate Leak (PostgreSQL HAVING / GROUP BY)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg2d/ui")
def pg2d_ui():
    content = """
<div class="ui-card" data-challenge-id="pg2d">
  <h2>Aggregate Leak <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg2d]</span></h2>
  <p class="subtitle">
    A PostgreSQL department summary. The <code>dept</code> parameter feeds into both the
    <code>WHERE</code> clause and the <code>HAVING</code> aggregate check.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Try injecting <code>engineering' HAVING MIN(id)=1 OR 1=1--</code> or use error-based
    payloads to extract the flag from the same table.
  </p>
  <form method="GET" action="/challenges/pg/groups" data-fetch="resp-pg2d">
    <div class="field">
      <label>dept</label>
      <input name="dept" type="text" value="engineering" autocomplete="off">
    </div>
    <button class="btn" type="submit">GET /challenges/pg/groups</button>
  </form>
  <pre class="response-box" id="resp-pg2d"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg2d: Aggregate Leak", content)


# ---------------------------------------------------------------------------
# my5b — Crawl & Conquer (multi-step crawl flow)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my5b/ui")
def my5b_ui():
    content = """
<div class="ui-card" data-challenge-id="my5b">
  <h2>Crawl &amp; Conquer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my5b]</span></h2>
  <p class="subtitle">
    The endpoint that holds the flag isn't listed anywhere obvious. Find it first, then exploit it.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    The index page links to a dashboard endpoint not shown in the challenge list.
    Once found, the <code>key=</code> parameter is your injection surface.
  </p>
  <ol style="font-size:.8rem;color:var(--muted);line-height:1.8;padding-left:1.2rem">
    <li>Crawl the app from <a href="/">/</a> to discover hidden links.</li>
    <li>Find the dashboard endpoint and its <code>key=</code> parameter.</li>
    <li>Inject into <code>key=</code> to extract the flag.</li>
  </ol>
  <a href="/" class="btn" style="display:inline-block;margin-top:16px">Start at the index &rsaquo;</a>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my5b: Crawl & Conquer", content)


# ---------------------------------------------------------------------------
# sq2g — Master Key (sqlite_master enumeration)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2g/ui")
def sq2g_ui():
    content = """
<div class="ui-card" data-challenge-id="sq2g">
  <h2>Master Key <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2g]</span></h2>
  <p class="subtitle">
    A SQLite item catalogue. A hidden table exists that the API never mentions.
    <code>sqlite_master</code> knows its name.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    The path parameter <code>/sq/item/&lt;id&gt;</code> is your injection surface.
    UNION against <code>sqlite_master</code> to list tables, then read from the hidden one.
  </p>
  <div class="field" style="margin-top:12px">
    <label>item id (injectable path segment)</label>
    <input id="sq2g-id" type="text" value="1" autocomplete="off">
  </div>
  <button class="btn" onclick="fetchEndpoint('/challenges/sq/item/'+encodeURIComponent(document.getElementById('sq2g-id').value),'resp-sq2g')">
    GET /challenges/sq/item/{id}
  </button>
  <pre class="response-box" id="resp-sq2g"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2g: Master Key", content)


# ---------------------------------------------------------------------------
# my3f — Schema Walker (MySQL information_schema enumeration)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my3f/ui")
def my3f_ui():
    content = """
<div class="ui-card" data-challenge-id="my3f">
  <h2>Schema Walker <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my3f]</span></h2>
  <p class="subtitle">
    A MySQL product lookup. A shadow table exists that the app never exposes.
    <code>information_schema.tables</code> will list it.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    The <code>id=</code> parameter is your injection surface. UNION against
    <code>information_schema.tables</code> to enumerate tables, then read from the hidden one.
  </p>
  <form method="GET" action="/challenges/my3/products" data-fetch="resp-my3f">
    <div class="field"><label>id</label><input name="id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/my3/products</button>
  </form>
  <pre class="response-box" id="resp-my3f"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — my3f: Schema Walker", content)


# ---------------------------------------------------------------------------
# pg2e — Catalog Diver (PostgreSQL information_schema enumeration)
# ---------------------------------------------------------------------------

@bp.get("/challenges/pg2e/ui")
def pg2e_ui():
    content = """
<div class="ui-card" data-challenge-id="pg2e">
  <h2>Catalog Diver <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg2e]</span></h2>
  <p class="subtitle">
    A PostgreSQL orders endpoint. A hidden table exists in the schema.
    <code>information_schema.tables</code> works on PostgreSQL too.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    The <code>id=</code> parameter is your injection surface. UNION against
    <code>information_schema.tables</code> to enumerate tables, then extract the flag.
  </p>
  <form method="GET" action="/challenges/pg/orders" data-fetch="resp-pg2e">
    <div class="field"><label>id</label><input name="id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">GET /challenges/pg/orders</button>
  </form>
  <pre class="response-box" id="resp-pg2e"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — pg2e: Catalog Diver", content)
