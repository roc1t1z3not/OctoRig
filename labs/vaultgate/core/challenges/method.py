# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 5 — HTTP method bypass (m1a–m1c)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import METHOD_RECORDS, METHOD_PROFILES, METHOD_ENTRIES, get_session_user
from core.challenges.util import page, tier_badge

bp = Blueprint("method", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_403 = {"error": "Forbidden — you do not own this resource"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               bypass_method: str, api_path: str, alice_id: int,
               body_note: str = "") -> str:
    badge = tier_badge(5)
    bm = bypass_method
    try_html = f"""
<div class="card">
  <h2>Try it — {bm} (the bypass)</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>Resource ID</label>
  <input id="rid" value="{alice_id}">
  {'<label>Body (JSON, can be empty)</label><textarea id="body" rows="2">{}</textarea>' if bm in ('PUT','PATCH') else ''}
  <button onclick="go()">Send {bm}</button>
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
  const url = BASE + '{api_path}'.replace('{{id}}', rid);
  const out = document.getElementById('out');
  out.className = 'result'; out.textContent = 'Sending…';
  {'const bodyEl = document.getElementById("body"); const bodyVal = bodyEl ? bodyEl.value.trim() : "{}";' if bm in ('PUT','PATCH') else 'const bodyVal = null;'}
  try {{
    const opts = {{ method: '{bm}', headers: tok ? {{'Authorization':'Bearer '+tok}} : {{}} }};
    {'opts.headers["Content-Type"] = "application/json"; opts.body = bodyVal || "{}";' if bm in ('PUT','PATCH') else ''}
    const r = await fetch(url, opts);
    const t = await r.text();
    try {{ out.textContent = JSON.stringify(JSON.parse(t), null, 2); }}
    catch {{ out.textContent = t; }}
    out.className = r.ok ? 'result ok' : 'result err';
  }} catch(e) {{ out.className='result err'; out.textContent=e.message; }}
}}
</script>"""

    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 5 — Method Bypass &bull; 1000 pts</p>
<div class="card"><h2>Description</h2><p>{description}</p></div>
<div class="card"><h2>Hint</h2><p>{hint}</p></div>
<div class="card">
  <h2>Endpoint</h2>
  <table>
    <tr><th>Method</th><th>Path</th><th>Result</th></tr>
    <tr><td><code>GET</code></td><td><code>{api_path.replace('{id}', str(alice_id))}</code></td><td>403 Forbidden</td></tr>
    <tr><td><code>{bm}</code></td><td><code>{api_path.replace('{id}', str(alice_id))}</code></td><td>200 + flag &#x2717;</td></tr>
  </table>
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
    const bob = d.users.find(u=>u.username==='bob');
    const BT = bob ? bob.token : '<bob_token>';
    const EP = BASE + '{api_path}'.replace('{{id}}', '{alice_id}');
    {'document.getElementById(\'curl\').textContent = \'curl -X ' + bm + ' -H "Authorization: Bearer \' + BT + \'" \\\\\\n     \\\\\\\n  -H "Content-Type: application/json" -d \'{}\'\\\\\\n     "\' + EP + \'"\';' if bm in ('PUT','PATCH') else 'document.getElementById(\'curl\').textContent = \'curl -X ' + bm + ' -H "Authorization: Bearer \' + BT + \'" \\\\\\n     "\' + EP + \'"\';'}
  }} catch(e) {{ console.error(e); }}
}})();
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/method/m1a")
def m1a_page():
    return make_response(_chal_page(
        "m1a", "Delete Bypass",
        "GET /records/{id} is protected and returns 403 Forbidden. The DELETE handler "
        "on the same path skips the ownership check entirely.",
        "Try DELETE /records/11001 as bob — the auth guard only runs on GET.",
        bypass_method="DELETE",
        api_path="/challenges/method/m1a/records/{id}",
        alice_id=11001,
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/method/m1b")
def m1b_page():
    return make_response(_chal_page(
        "m1b", "PUT Bypass",
        "GET /profiles/{id} returns 403 for non-owners. The PUT handler on the same "
        "path was added later and never received the ownership check.",
        "PUT /profiles/12001 with any JSON body as bob to get the flag.",
        bypass_method="PUT",
        api_path="/challenges/method/m1b/profiles/{id}",
        alice_id=12001,
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/method/m1c")
def m1c_page():
    return make_response(_chal_page(
        "m1c", "PATCH Bypass",
        "GET /entries/{id} is access-controlled. PATCH on the same endpoint was added "
        "for partial updates and the authorization check was forgotten.",
        "PATCH /entries/13001 as bob — send any JSON body.",
        bypass_method="PATCH",
        api_path="/challenges/method/m1c/entries/{id}",
        alice_id=13001,
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

# m1a — GET guarded, DELETE unguarded
@bp.get("/challenges/method/m1a/records/<int:rid>")
def m1a_get(rid: int):
    caller = get_session_user()
    if not caller:
        return jsonify(_401), 401
    record = METHOD_RECORDS.get(rid)
    if not record:
        return jsonify(_404), 404
    # Proper ownership check on GET
    if record["user_id"] != caller["user_id"]:
        return jsonify(_403), 403
    return jsonify(record)


@bp.delete("/challenges/method/m1a/records/<int:rid>")
def m1a_delete(rid: int):
    if not get_session_user():
        return jsonify(_401), 401
    record = METHOD_RECORDS.get(rid)
    if not record:
        return jsonify(_404), 404
    # BUG: no ownership check on DELETE
    return jsonify({"deleted": True, "record": record})


# m1b — GET guarded, PUT unguarded
@bp.get("/challenges/method/m1b/profiles/<int:pid>")
def m1b_get(pid: int):
    caller = get_session_user()
    if not caller:
        return jsonify(_401), 401
    profile = METHOD_PROFILES.get(pid)
    if not profile:
        return jsonify(_404), 404
    if profile["user_id"] != caller["user_id"]:
        return jsonify(_403), 403
    return jsonify(profile)


@bp.put("/challenges/method/m1b/profiles/<int:pid>")
def m1b_put(pid: int):
    if not get_session_user():
        return jsonify(_401), 401
    profile = METHOD_PROFILES.get(pid)
    if not profile:
        return jsonify(_404), 404
    # BUG: no ownership check on PUT
    body = request.get_json(silent=True) or {}
    return jsonify({"updated": True, "profile": profile, "changes": body})


# m1c — GET guarded, PATCH unguarded
@bp.get("/challenges/method/m1c/entries/<int:eid>")
def m1c_get(eid: int):
    caller = get_session_user()
    if not caller:
        return jsonify(_401), 401
    entry = METHOD_ENTRIES.get(eid)
    if not entry:
        return jsonify(_404), 404
    if entry["user_id"] != caller["user_id"]:
        return jsonify(_403), 403
    return jsonify(entry)


@bp.route("/challenges/method/m1c/entries/<int:eid>", methods=["PATCH"])
def m1c_patch(eid: int):
    if not get_session_user():
        return jsonify(_401), 401
    entry = METHOD_ENTRIES.get(eid)
    if not entry:
        return jsonify(_404), 404
    # BUG: no ownership check on PATCH
    body = request.get_json(silent=True) or {}
    return jsonify({"patched": True, "entry": entry, "changes": body})
