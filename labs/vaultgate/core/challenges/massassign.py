# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 7 — Mass Assignment (a1a–a1b)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import USERS, MA_ROLE_FLAG, MA_OWNER_FLAG, get_session_user
from core.challenges.util import page, tier_badge

bp = Blueprint("massassign", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               api_path: str, body_example: str) -> str:
    badge = tier_badge(7)
    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 7 — Mass Assignment &bull; 1200 pts</p>
<div class="card"><h2>Description</h2><p>{description}</p></div>
<div class="card"><h2>Hint</h2><p>{hint}</p></div>
<div class="card">
  <h2>curl</h2>
  <pre id="curl">loading…</pre>
</div>
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token (authenticate as bob)</label>
  <input id="tok" placeholder="paste token here">
  <label>JSON body (add privileged fields)</label>
  <textarea id="body" rows="4">{body_example}</textarea>
  <button onclick="go()">Send POST</button>
  <div class="result" id="out">—</div>
</div>
<script>
(async () => {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const bob = d.users.find(u=>u.username==='bob');
    if (bob) document.getElementById('tok').value = bob.token;
    const BT = bob ? bob.token : '<bob_token>';
    document.getElementById('curl').textContent =
      'curl -s -X POST \\\n' +
      '  -H "Content-Type: application/json" \\\n' +
      '  -H "Authorization: Bearer ' + BT + '" \\\n' +
      "  -d '" + document.getElementById('body').value + "' \\\n" +
      '  "' + BASE + '{api_path}"';
  }} catch(e) {{ console.error(e); }}
}})();
async function go() {{
  const BASE = window.location.origin;
  const tok  = document.getElementById('tok').value.trim();
  const body = document.getElementById('body').value.trim();
  const out  = document.getElementById('out');
  out.className = 'result'; out.textContent = 'Sending…';
  try {{
    const r = await fetch(BASE + '{api_path}', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json',
                 ...(tok ? {{'Authorization':'Bearer '+tok}} : {{}})}},
      body: body,
    }});
    const t = await r.text();
    try {{ out.textContent = JSON.stringify(JSON.parse(t), null, 2); }}
    catch {{ out.textContent = t; }}
    out.className = r.ok ? 'result ok' : 'result err';
  }} catch(e) {{ out.className='result err'; out.textContent=e.message; }}
}}
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/massassign/a1a")
def a1a_page():
    return make_response(_chal_page(
        "a1a", "Role Elevation",
        "The profile update endpoint passes all request fields directly to the update "
        "logic. Include a 'role' field to elevate yourself to admin — the flag appears "
        "in the response when the server accepts the unauthorized role change.",
        "POST {\"display_name\": \"Hacker\", \"role\": \"admin\"} as bob. "
        "The flag appears when role=admin is accepted.",
        api_path="/challenges/massassign/a1a/profile/update",
        body_example='{"display_name": "Hacker", "role": "admin"}',
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/massassign/a1b")
def a1b_page():
    return make_response(_chal_page(
        "a1b", "Owner Override",
        "A post creation endpoint that binds user_id from the request body instead of "
        "from the session. Supply alice's user_id (1) to create content as her — "
        "the flag is returned when the server accepts the injected user_id.",
        "POST {\"title\": \"My Post\", \"user_id\": 1} as bob. "
        "The server creates the post as alice and returns her flag.",
        api_path="/challenges/massassign/a1b/posts/create",
        body_example='{"title": "My Post", "content": "Hello!", "user_id": 1}',
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.post("/challenges/massassign/a1a/profile/update")
def a1a_api():
    caller = get_session_user()
    if not caller:
        return jsonify(_401), 401
    body = request.get_json(silent=True) or {}
    # BUG: all fields from body are merged into the user's effective profile
    merged = {**caller, **body}
    response = {"user_id": caller["user_id"], "username": caller["username"]}
    for field in ("display_name", "bio", "role"):
        if field in body:
            response[field] = body[field]
    # Flag appears when privileged field accepted
    if body.get("role") == "admin" and caller.get("role") != "admin":
        response["flag"] = MA_ROLE_FLAG
        response["note"] = "Role elevation accepted — you are now admin."
    return jsonify(response)


@bp.post("/challenges/massassign/a1b/posts/create")
def a1b_api():
    caller = get_session_user()
    if not caller:
        return jsonify(_401), 401
    body = request.get_json(silent=True) or {}
    # BUG: user_id comes from body instead of session
    author_id = body.get("user_id", caller["user_id"])
    author = USERS.get(author_id, {})
    response = {
        "post_id": 42,
        "title": body.get("title", ""),
        "content": body.get("content", ""),
        "author_id": author_id,
        "author_username": author.get("username", "unknown"),
    }
    if author_id == 1 and caller["user_id"] != 1:
        response["flag"] = MA_OWNER_FLAG
        response["note"] = "Post created as alice — owner override accepted."
    return jsonify(response)
