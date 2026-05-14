# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 6 — Parameter Pollution (p1a–p1b)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import POLL_DATA, JSON_DATA, get_session_user
from core.challenges.util import page, tier_badge

bp = Blueprint("pollution", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               technique_detail: str, api_path: str,
               method: str, body_example: str = "") -> str:
    badge = tier_badge(6)
    if method == "GET":
        try_html = f"""
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>Raw query string (edit to add duplicates)</label>
  <input id="qs" value="user_id=2&amp;user_id=1">
  <button onclick="go()">Send GET</button>
  <div class="result" id="out">—</div>
</div>
<script>
async function go() {{
  const BASE = window.location.origin;
  const tok = document.getElementById('tok').value.trim();
  const qs  = document.getElementById('qs').value.trim();
  const url = BASE + '{api_path}?' + qs;
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
</script>"""
    else:
        try_html = f"""
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>Raw JSON body (with duplicate key)</label>
  <textarea id="body" rows="3">{body_example}</textarea>
  <button onclick="go()">Send POST</button>
  <div class="result" id="out">—</div>
</div>
<script>
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
</script>"""

    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 6 — Param Pollution &bull; 1200 pts</p>
<div class="card"><h2>Description</h2><p>{description}</p></div>
<div class="card"><h2>Hint</h2><p>{hint}</p></div>
<div class="card"><h2>Technique detail</h2><p>{technique_detail}</p></div>
<div class="card">
  <h2>curl</h2>
  <pre id="curl">loading…</pre>
</div>
{try_html}
<script>
(async () => {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const bob = d.users.find(u=>u.username==='bob');
    const BT = bob ? bob.token : '<bob_token>';
    if (bob) document.getElementById('tok').value = bob.token;
    {'document.getElementById(\'curl\').textContent = \'curl -H "Authorization: Bearer \' + BT + \'"\\\\\nURL: ' + api_path + '?user_id=2&user_id=1\';' if method == 'GET' else 'document.getElementById(\'curl\').textContent = \'curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer \' + BT + \'" \\\\\\n  -d \\\'{"user_id": 2, "user_id": 1}\\\' ' + api_path + '\';'}
  }} catch(e) {{ console.error(e); }}
}})();
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/pollution/p1a")
def p1a_page():
    return make_response(_chal_page(
        "p1a", "Duplicate Query Param",
        "The endpoint reads the last value when the same query parameter is sent twice. "
        "Send user_id twice — once with your own ID, once with alice's.",
        "GET /data?user_id=2&user_id=1 — the server uses request.args.getlist('user_id')[-1].",
        "Flask's request.args.get() returns the FIRST duplicate; "
        "request.args.getlist() returns all. This endpoint uses getlist()[-1] — the last value wins.",
        api_path="/challenges/pollution/p1a/data",
        method="GET",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/pollution/p1b")
def p1b_page():
    return make_response(_chal_page(
        "p1b", "JSON Duplicate Key",
        "Python's json.loads() keeps the last occurrence of a duplicate key. "
        "Send a JSON body with user_id appearing twice.",
        "POST {\"user_id\": 2, \"user_id\": 1} — Python's json parser picks the last value.",
        "Most JSON parsers (including Python's) silently accept duplicate keys and keep "
        "the last value. The server binds user_id from the parsed body without deduplication.",
        api_path="/challenges/pollution/p1b/data",
        method="POST",
        body_example='{"user_id": 2, "user_id": 1}',
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.get("/challenges/pollution/p1a/data")
def p1a_api():
    if not get_session_user():
        return jsonify(_401), 401
    # BUG: uses last value from duplicate params
    values = request.args.getlist("user_id")
    if not values:
        return jsonify({"error": "user_id query param required"}), 400
    try:
        uid = int(values[-1])
    except ValueError:
        return jsonify({"error": "user_id must be an integer"}), 400
    data = POLL_DATA.get(uid)
    if not data:
        return jsonify(_404), 404
    return jsonify(data)


@bp.post("/challenges/pollution/p1b/data")
def p1b_api():
    if not get_session_user():
        return jsonify(_401), 401
    body = request.get_json(silent=True) or {}
    uid = body.get("user_id")
    if not isinstance(uid, int):
        return jsonify({"error": "user_id (integer) required"}), 400
    # BUG: uses user_id from body, which can be duplicated in source JSON
    data = JSON_DATA.get(uid)
    if not data:
        return jsonify(_404), 404
    return jsonify(data)
