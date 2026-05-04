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
<div class="ui-card">
  <h2>Login Wall <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2b]</span></h2>
  <p class="subtitle">A staff portal login. Enter credentials to authenticate.</p>
  <form method="POST" action="/challenges/my2/login">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
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
<div class="ui-card">
  <h2>Second Sight <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2d]</span></h2>
  <p class="subtitle">Search for a user, then read their inbox. The flag travels between two requests.</p>
  <form method="GET" action="/challenges/my2/search">
    <div class="field"><label>Search username</label><input name="user" type="text" value="admin" autocomplete="off"></div>
    <button class="btn" type="submit">Search</button>
  </form>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
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
<div class="ui-card">
  <h2>API Whisperer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4b]</span></h2>
  <p class="subtitle">A JSON API that looks up users by ID. Edit the body and fire the request.</p>
  <form method="POST" action="/challenges/my4/api/user" enctype="application/x-www-form-urlencoded">
    <div class="field"><label>user_id</label><input name="user_id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">POST /challenges/my4/api/user</button>
  </form>
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
<div class="ui-card">
  <h2>Cookie Monster <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4e]</span></h2>
  <p class="subtitle">
    The profile endpoint reads your <code>session_id</code> cookie to look you up.
  </p>
  <p style="font-size:.8rem;color:var(--muted)">
    Current <code>session_id</code>: <code>{current}</code>
  </p>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
    The injectable surface is the <code>session_id</code> cookie sent to
    <a href="/challenges/my4/profile">/challenges/my4/profile</a>.
    Use <code>--cookie-params session_id</code> with your scanner.
  </p>
  <a href="/challenges/my4/profile" class="btn" style="display:inline-block;margin-top:8px">Fetch profile &rsaquo;</a>
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
<div class="ui-card">
  <h2>PG POST Form <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg3b]</span></h2>
  <p class="subtitle">A PostgreSQL-backed staff login. The password field maps to the email column.</p>
  <form method="POST" action="/challenges/pg/login">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password (email)</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
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
<div class="ui-card">
  <h2>PG Echo Chamber <span style="font-size:.75rem;color:var(--muted);font-weight:400">[pg2f]</span></h2>
  <p class="subtitle">Update a profile bio. The stored value is later read back verbatim.</p>
  <form method="POST" action="/challenges/pg/profile">
    <div class="field"><label>Username</label><input name="username" type="text" value="alice" autocomplete="off"></div>
    <div class="field"><label>Bio</label><input name="bio" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Save profile</button>
  </form>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
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
<div class="ui-card">
  <h2>Lite Login <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2e]</span></h2>
  <p class="subtitle">A SQLite-backed login form. Enter credentials to authenticate.</p>
  <form method="POST" action="/challenges/sq/login">
    <div class="field"><label>Username</label><input name="username" type="text" value="admin" autocomplete="off"></div>
    <div class="field"><label>Password</label><input name="password" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Log in</button>
  </form>
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
<div class="ui-card">
  <h2>Lite Echo <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2h]</span></h2>
  <p class="subtitle">Update a profile bio. The stored value is later read back verbatim.</p>
  <form method="POST" action="/challenges/sq/profile">
    <div class="field"><label>Username</label><input name="username" type="text" value="alice" autocomplete="off"></div>
    <div class="field"><label>Bio</label><input name="bio" type="text" value="" autocomplete="off"></div>
    <button class="btn" type="submit">Save profile</button>
  </form>
  <p style="font-size:.8rem;color:var(--muted);margin-top:8px">
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
<div class="ui-card">
  <h2>Lite Whisperer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2i]</span></h2>
  <p class="subtitle">A SQLite member lookup that reads from a JSON body. The ID is embedded raw.</p>
  <form method="POST" action="/challenges/sq/api/member" enctype="application/x-www-form-urlencoded">
    <div class="field"><label>member_id</label><input name="member_id" type="text" value="1" autocomplete="off"></div>
    <button class="btn" type="submit">POST /challenges/sq/api/member</button>
  </form>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
"""
    return _page(" — sq2i: Lite Whisperer", content)
