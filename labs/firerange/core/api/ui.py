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
# t2b — Login Wall (MySQL POST login)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my2b/ui")
def t2b_ui():
    content = """
<div class="ui-card">
  <h2>Login Wall <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2b]</span></h2>
  <p class="subtitle">A staff portal login. Enter credentials to authenticate.</p>
  <div class="field"><label>Username</label><input id="u" type="text" value="admin" autocomplete="off"></div>
  <div class="field"><label>Password</label><input id="p" type="text" value="" autocomplete="off"></div>
  <button class="btn" onclick="doLogin()">Log in</button>
  <pre class="response-box" id="resp"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doLogin() {
  const fd = new FormData();
  fd.append('username', document.getElementById('u').value);
  fd.append('password', document.getElementById('p').value);
  const r = await fetch('/challenges/my2/login', {method:'POST', body:fd});
  const box = document.getElementById('resp');
  box.style.display = 'block';
  box.textContent = JSON.stringify(await r.json(), null, 2);
}
</script>
"""
    return _page(" — my2b: Login Wall", content)


# ---------------------------------------------------------------------------
# t2d — Second Sight (search + inbox viewer)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my2d/ui")
def t2d_ui():
    content = """
<div class="ui-card">
  <h2>Second Sight <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my2d]</span></h2>
  <p class="subtitle">Search for a user, then read their inbox. The flag travels between two requests.</p>
  <div class="field"><label>Search username</label><input id="u" type="text" value="admin" autocomplete="off"></div>
  <button class="btn" onclick="doSearch()">Search &amp; Read Inbox</button>
  <pre class="response-box" id="resp-search"></pre>
  <pre class="response-box" id="resp-inbox"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doSearch() {
  const user = document.getElementById('u').value;
  const r1 = await fetch('/challenges/my2/search?user=' + encodeURIComponent(user));
  const s = document.getElementById('resp-search');
  s.style.display = 'block';
  s.textContent = 'Search: ' + JSON.stringify(await r1.json(), null, 2);
  const r2 = await fetch('/challenges/my2/inbox');
  const i = document.getElementById('resp-inbox');
  i.style.display = 'block';
  i.textContent = 'Inbox: ' + JSON.stringify(await r2.json(), null, 2);
}
</script>
"""
    return _page(" — my2d: Second Sight", content)


# ---------------------------------------------------------------------------
# t4b — API Whisperer (JSON body POST)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my4b/ui")
def t4b_ui():
    content = """
<div class="ui-card">
  <h2>API Whisperer <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4b]</span></h2>
  <p class="subtitle">A JSON API that looks up users by ID. Edit the body and fire the request.</p>
  <div class="field">
    <label>Request body (JSON)</label>
    <textarea id="body">{"user_id": 1}</textarea>
  </div>
  <button class="btn" onclick="doPost()">POST /challenges/my4/api/user</button>
  <pre class="response-box" id="resp"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doPost() {
  let body;
  try { body = document.getElementById('body').value; JSON.parse(body); }
  catch(e) { alert('Invalid JSON: ' + e.message); return; }
  const r = await fetch('/challenges/my4/api/user', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: body,
  });
  const box = document.getElementById('resp');
  box.style.display = 'block';
  box.textContent = JSON.stringify(await r.json(), null, 2);
}
</script>
"""
    return _page(" — my4b: API Whisperer", content)


# ---------------------------------------------------------------------------
# t4e — Cookie Monster (session_id cookie profile)
# ---------------------------------------------------------------------------

@bp.get("/challenges/my4e/ui")
def t4e_ui():
    current = request.cookies.get("session_id", "sess_def456")
    content = f"""
<div class="ui-card">
  <h2>Cookie Monster <span style="font-size:.75rem;color:var(--muted);font-weight:400">[my4e]</span></h2>
  <p class="subtitle">
    The profile endpoint reads your <code>session_id</code> cookie to look you up.
    Set a cookie value below and fetch the profile.
  </p>
  <div class="field">
    <label>session_id cookie value</label>
    <input id="sid" type="text" value="{current}" autocomplete="off">
  </div>
  <button class="btn" onclick="doFetch()">Fetch profile</button>
  <pre class="response-box" id="resp"></pre>
  <p style="font-size:.75rem;color:var(--muted);margin-top:12px">
    The cookie is set in your browser then sent with the request.
    Your scanner should inject the cookie header directly.
  </p>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doFetch() {{
  const val = document.getElementById('sid').value;
  document.cookie = 'session_id=' + encodeURIComponent(val) + '; path=/';
  const r = await fetch('/challenges/my4/profile');
  const box = document.getElementById('resp');
  box.style.display = 'block';
  box.textContent = JSON.stringify(await r.json(), null, 2);
}}
</script>
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
  <div class="field"><label>Username</label><input id="u" type="text" value="admin" autocomplete="off"></div>
  <div class="field"><label>Password (email)</label><input id="p" type="text" value="" autocomplete="off"></div>
  <button class="btn" onclick="doLogin()">Log in</button>
  <pre class="response-box" id="resp"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doLogin() {
  const fd = new FormData();
  fd.append('username', document.getElementById('u').value);
  fd.append('password', document.getElementById('p').value);
  const r = await fetch('/challenges/pg/login', {method:'POST', body:fd});
  const box = document.getElementById('resp');
  box.style.display = 'block';
  box.textContent = JSON.stringify(await r.json(), null, 2);
}
</script>
"""
    return _page(" — pg3b: PG POST Form", content)


# ---------------------------------------------------------------------------
# sq2e — Lite Login (SQLite POST login)
# ---------------------------------------------------------------------------

@bp.get("/challenges/sq2e/ui")
def sq2e_ui():
    content = """
<div class="ui-card">
  <h2>Lite Login <span style="font-size:.75rem;color:var(--muted);font-weight:400">[sq2e]</span></h2>
  <p class="subtitle">A SQLite-backed login form. Enter credentials to authenticate.</p>
  <div class="field"><label>Username</label><input id="u" type="text" value="admin" autocomplete="off"></div>
  <div class="field"><label>Password</label><input id="p" type="text" value="" autocomplete="off"></div>
  <button class="btn" onclick="doLogin()">Log in</button>
  <pre class="response-box" id="resp"></pre>
  <a class="back-link" href="/">&#8592; Back to challenges</a>
</div>
<script>
async function doLogin() {
  const fd = new FormData();
  fd.append('username', document.getElementById('u').value);
  fd.append('password', document.getElementById('p').value);
  const r = await fetch('/challenges/sq/login', {method:'POST', body:fd});
  const box = document.getElementById('resp');
  box.style.display = 'block';
  box.textContent = JSON.stringify(await r.json(), null, 2);
}
</script>
"""
    return _page(" — sq2e: Lite Login", content)
