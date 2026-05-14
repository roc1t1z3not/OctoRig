# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 4 — Vertical IDOR (v1a–v1c)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response

from core.db.appdb import USERS, ADMIN_SETTINGS, STAFF_INVOICES, get_session_user
from core.challenges.util import page, tier_badge

bp = Blueprint("vertical", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_403 = {"error": "Forbidden — admin role required"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               api_path: str, target_id: str = "") -> str:
    badge = tier_badge(4)
    id_row = (f'<label>Resource ID</label>'
              f'<input id="rid" value="{target_id}">' if target_id else "")
    url_js = (f"BASE + '{api_path}'.replace('{{id}}', document.getElementById('rid').value.trim())"
              if target_id else f"BASE + '{api_path}'")
    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 4 — Vertical IDOR &bull; 800 pts</p>
<div class="card"><h2>Description</h2><p>{description}</p></div>
<div class="card"><h2>Hint</h2><p>{hint}</p></div>
<div class="card">
  <h2>phaseaccess</h2>
  <pre id="pa">loading…</pre>
</div>
<div class="card">
  <h2>curl</h2>
  <pre id="curl">loading…</pre>
</div>
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token (use any regular-user token)</label>
  <input id="tok" placeholder="paste token here">
  {id_row}
  <button onclick="go()">Send GET</button>
  <div class="result" id="out">—</div>
</div>
<script>
(async () => {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const alice = d.users.find(u=>u.username==='alice');
    const bob   = d.users.find(u=>u.username==='bob');
    if (bob) document.getElementById('tok').value = bob.token;
    const AT = alice ? alice.token : '<alice_token>';
    const BT = bob   ? bob.token   : '<bob_token>';
    const EP = BASE + '{api_path}'.replace('{{id}}', '{target_id}');
    document.getElementById('pa').textContent =
      'phaseaccess \\\\\\n  -u "' + EP + '" \\\\\\n' +
      '  -H "Authorization: Bearer ' + AT + '" --label-a alice \\\\\\n' +
      '  --header-b "Authorization: Bearer ' + BT + '" --label-b bob';
    document.getElementById('curl').textContent =
      'curl -H "Authorization: Bearer ' + BT + '" \\\\\\n     "' + EP + '"';
  }} catch(e) {{ console.error(e); }}
}})();
async function go() {{
  const BASE = window.location.origin;
  const tok = document.getElementById('tok').value.trim();
  const url = {url_js};
  const out = document.getElementById('out');
  out.className = 'result'; out.textContent = 'Sending…';
  try {{
    const r = await fetch(url, {{headers: tok ? {{'Authorization':'Bearer '+tok}} : {{}}}});
    const t = await r.text();
    try {{ out.textContent = JSON.stringify(JSON.parse(t), null, 2); }}
    catch {{ out.textContent = t; }}
    out.className = r.ok ? 'result ok' : 'result err';
  }} catch(e) {{ out.className='result err'; out.textContent=e.message; }}
}}
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/vertical/v1a")
def v1a_page():
    return make_response(_chal_page(
        "v1a", "Admin User List",
        "An admin-only endpoint that returns all users including admin accounts. "
        "The endpoint checks authentication but not the user's role.",
        "GET /admin/users with any valid session token — no admin role required.",
        api_path="/challenges/vertical/v1a/admin/users",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/vertical/v1b")
def v1b_page():
    return make_response(_chal_page(
        "v1b", "Admin Settings",
        "An internal configuration endpoint that exposes database passwords and API keys. "
        "Intended for admins only, but the role check is missing.",
        "GET /admin/settings with bob's regular user token.",
        api_path="/challenges/vertical/v1b/admin/settings",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/vertical/v1c")
def v1c_page():
    return make_response(_chal_page(
        "v1c", "Staff Invoice",
        "A staff-tier endpoint serving executive invoices. Regular users can reach it "
        "because the middleware only checks for a valid session, not for staff role.",
        "GET /staff/invoices/99001 with a regular user token.",
        api_path="/challenges/vertical/v1c/staff/invoices/{id}",
        target_id="99001",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.get("/challenges/vertical/v1a/admin/users")
def v1a_api():
    # BUG: no role check — any authenticated user can list all users
    if not get_session_user():
        return jsonify(_401), 401
    return jsonify(list(USERS.values()))


@bp.get("/challenges/vertical/v1b/admin/settings")
def v1b_api():
    # BUG: no role check — config exposed to any authenticated user
    if not get_session_user():
        return jsonify(_401), 401
    return jsonify(ADMIN_SETTINGS)


@bp.get("/challenges/vertical/v1c/staff/invoices/<int:inv_id>")
def v1c_api(inv_id: int):
    # BUG: only checks auth, not staff/admin role
    if not get_session_user():
        return jsonify(_401), 401
    inv = STAFF_INVOICES.get(inv_id)
    if not inv:
        return jsonify(_404), 404
    return jsonify(inv)
