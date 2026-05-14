# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 3 — IDOR via POST body or query parameter (i3a–i3d)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import BODY_MESSAGES, REPORTS, EXPORTS, RECORDS, get_session_user
from core.challenges.util import page, tier_badge

bp = Blueprint("body", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               method: str, api_path: str, alice_id: int,
               body_example: str = "", query_key: str = "") -> str:
    badge = tier_badge(3)
    if method == "POST":
        try_html = f"""
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>JSON body</label>
  <textarea id="body" rows="3">{body_example}</textarea>
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
  }} catch {{}}
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
</script>"""
    else:
        try_html = f"""
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>Resource ID (<code>{query_key}</code>)</label>
  <input id="rid" value="{alice_id}">
  <button onclick="go()">Send GET</button>
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
  }} catch {{}}
}})();
async function go() {{
  const BASE = window.location.origin;
  const tok = document.getElementById('tok').value.trim();
  const rid = document.getElementById('rid').value.trim();
  const url = BASE + '{api_path}?' + new URLSearchParams({{'{query_key}': rid}});
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

    cmd_method = "POST" if method == "POST" else "GET"
    if method == "POST":
        curl_js = (
            "document.getElementById('curl').textContent = "
            "'curl -s -X POST \\\\\\n"
            "  -H \"Content-Type: application/json\" \\\\\\n"
            "  -H \"Authorization: Bearer ' + BT + '\" \\\\\\n"
            f"  -d \\'{body_example}\\' \\\\\\n"
            "  \"' + EP + '\"';"
        )
    else:
        curl_js = (
            "document.getElementById('curl').textContent = "
            f"'curl -H \"Authorization: Bearer \\' + BT + \\'\" \\\\\\n"
            f"     \"\\' + EP + '?{query_key}={alice_id}\"';"
        )

    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 3 — Body / Param IDOR &bull; 500 pts</p>
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
{try_html}
<script>
(async () => {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const alice = d.users.find(u=>u.username==='alice');
    const bob   = d.users.find(u=>u.username==='bob');
    const AT = alice ? alice.token : '<alice_token>';
    const BT = bob   ? bob.token   : '<bob_token>';
    const EP = BASE + '{api_path}';
    document.getElementById('pa').textContent =
      'phaseaccess \\\\\\n  -u "' + EP + '" \\\\\\n  -X {cmd_method} \\\\\\n' +
      '  -H "Authorization: Bearer ' + AT + '" --label-a alice \\\\\\n' +
      '  --header-b "Authorization: Bearer ' + BT + '" --label-b bob';
    {curl_js}
  }} catch(e) {{ console.error(e); }}
}})();
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/body/i3a")
def i3a_page():
    return make_response(_chal_page(
        "i3a", "Body Message Read",
        "A POST endpoint that reads a private message. The message_id is supplied in "
        "the JSON request body and is not validated against the authenticated session.",
        "POST {\"message_id\": 7001} with bob's token to read alice's private message.",
        method="POST", api_path="/challenges/body/i3a/messages/read",
        alice_id=7001, body_example='{"message_id": 7001}',
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/body/i3b")
def i3b_page():
    return make_response(_chal_page(
        "i3b", "Query Report",
        "A report endpoint that accepts report_id as a query parameter. Any authenticated "
        "user can retrieve any report — the server doesn't check ownership.",
        "GET /report?report_id=8001 as bob to retrieve alice's audit report.",
        method="GET", api_path="/challenges/body/i3b/report",
        alice_id=8001, query_key="report_id",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/body/i3c")
def i3c_page():
    return make_response(_chal_page(
        "i3c", "Export Resource",
        "A data export endpoint. The caller supplies resource_id in the POST body and "
        "the server exports the matching record without an ownership check.",
        "POST {\"resource_id\": 9001} as bob to export alice's payroll data.",
        method="POST", api_path="/challenges/body/i3c/export",
        alice_id=9001, body_example='{"resource_id": 9001}',
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/body/i3d")
def i3d_page():
    return make_response(_chal_page(
        "i3d", "Record Lookup",
        "A record lookup endpoint using a record_id query parameter. Health records are "
        "returned for any valid ID without checking the requester's ownership.",
        "GET /lookup?record_id=10001 as bob to retrieve alice's health record.",
        method="GET", api_path="/challenges/body/i3d/lookup",
        alice_id=10001, query_key="record_id",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.post("/challenges/body/i3a/messages/read")
def i3a_api():
    if not get_session_user():
        return jsonify(_401), 401
    body = request.get_json(silent=True) or {}
    msg_id = body.get("message_id")
    if not isinstance(msg_id, int):
        return jsonify({"error": "message_id (integer) required"}), 400
    msg = BODY_MESSAGES.get(msg_id)
    if not msg:
        return jsonify(_404), 404
    return jsonify(msg)


@bp.get("/challenges/body/i3b/report")
def i3b_api():
    if not get_session_user():
        return jsonify(_401), 401
    try:
        report_id = int(request.args.get("report_id", ""))
    except (ValueError, TypeError):
        return jsonify({"error": "report_id (integer) required"}), 400
    report = REPORTS.get(report_id)
    if not report:
        return jsonify(_404), 404
    return jsonify(report)


@bp.post("/challenges/body/i3c/export")
def i3c_api():
    if not get_session_user():
        return jsonify(_401), 401
    body = request.get_json(silent=True) or {}
    resource_id = body.get("resource_id")
    if not isinstance(resource_id, int):
        return jsonify({"error": "resource_id (integer) required"}), 400
    export = EXPORTS.get(resource_id)
    if not export:
        return jsonify(_404), 404
    return jsonify(export)


@bp.get("/challenges/body/i3d/lookup")
def i3d_api():
    if not get_session_user():
        return jsonify(_401), 401
    try:
        record_id = int(request.args.get("record_id", ""))
    except (ValueError, TypeError):
        return jsonify({"error": "record_id (integer) required"}), 400
    record = RECORDS.get(record_id)
    if not record:
        return jsonify(_404), 404
    return jsonify(record)
