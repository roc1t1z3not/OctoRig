# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 1 — Horizontal IDOR via integer path segment (i1a–i1e)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import (
    ALICE_TOKEN, BOB_TOKEN,
    USERS, DOCUMENTS, INVOICES, ORDERS, MESSAGES,
    get_session_user,
)
from core.challenges.util import page, tier_badge

bp = Blueprint("horizontal", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               target_id: int | str, api_path: str, method: str = "GET",
               body_example: str = "") -> str:
    badge = tier_badge(1)
    try_section = ""
    if method == "GET":
        try_section = f"""
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token (paste alice's or bob's)</label>
  <input id="tok" value="" placeholder="paste token here">
  <label>Resource ID</label>
  <input id="rid" value="{target_id}" placeholder="{target_id}">
  <button onclick="go()">Send GET</button>
  <div class="result" id="out">—</div>
</div>
<script>
const BASE = window.location.origin;
async function go(){{
  const tok = document.getElementById('tok').value.trim();
  const rid = document.getElementById('rid').value.trim();
  const url = BASE + '{api_path}'.replace('{{id}}', rid);
  const out = document.getElementById('out');
  out.className = 'result'; out.textContent = 'Sending…';
  try{{
    const r = await fetch(url, {{headers: tok ? {{'Authorization':'Bearer '+tok}} : {{}}}});
    const t = await r.text();
    try{{ out.textContent = JSON.stringify(JSON.parse(t), null, 2); }}
    catch{{ out.textContent = t; }}
    out.className = r.ok ? 'result ok' : 'result err';
  }}catch(e){{ out.className='result err'; out.textContent=e.message; }}
}}
document.addEventListener('DOMContentLoaded', async () => {{
  try{{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const bob = d.users.find(u => u.username === 'bob');
    if (bob) document.getElementById('tok').value = bob.token;
  }} catch {{}}
}});
</script>"""
    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 1 — Horizontal IDOR &bull; 100 pts &bull; <code>VAULT{{...}}</code></p>
<div class="card">
  <h2>Description</h2>
  <p>{description}</p>
</div>
<div class="card">
  <h2>Hint</h2>
  <p>{hint}</p>
</div>
<div class="card">
  <h2>Session Tokens</h2>
  <div class="token-row"><span class="token-label">alice</span>
    <span class="token-val" id="alice-tok">loading…</span></div>
  <div class="token-row"><span class="token-label">bob</span>
    <span class="token-val" id="bob-tok">loading…</span></div>
  <p style="margin-top:8px">Or: <code>GET /api/tokens</code></p>
</div>
<div class="card">
  <h2>phaseaccess</h2>
  <pre id="pa-cmd">loading…</pre>
</div>
<div class="card">
  <h2>curl</h2>
  <pre id="curl-cmd">loading…</pre>
</div>
{try_section}
<script>
(async () => {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '/api/tokens');
    const d = await r.json();
    const alice = d.users.find(u=>u.username==='alice');
    const bob   = d.users.find(u=>u.username==='bob');
    if (alice) document.getElementById('alice-tok').textContent = alice.token;
    if (bob)   document.getElementById('bob-tok').textContent   = bob.token;
    const AT = alice ? alice.token : '<alice_token>';
    const BT = bob   ? bob.token   : '<bob_token>';
    const EP = BASE + '{api_path}'.replace('{{id}}', '{target_id}');
    document.getElementById('pa-cmd').textContent =
      'phaseaccess \\\\\\n  -u "' + EP + '" \\\\\\n' +
      '  -H "Authorization: Bearer ' + AT + '" --label-a alice \\\\\\n' +
      '  --header-b "Authorization: Bearer ' + BT + '" --label-b bob';
    document.getElementById('curl-cmd').textContent =
      '# Authenticate as bob, access alice\\'s resource:\\n' +
      'curl -H "Authorization: Bearer ' + BT + '" \\\\\\n     ' + EP;
  }} catch(e) {{ console.error(e); }}
}})();
</script>
""")


# ── Challenge pages ───────────────────────────────────────────────────────────

@bp.get("/challenges/horizontal/i1a")
def i1a_page():
    return make_response(_chal_page(
        "i1a", "Profile Reader",
        "The user profile endpoint accepts any valid session token and returns whatever "
        "user ID is in the path. Authentication is checked; ownership is not.",
        "Authenticate as bob (user_id=2) and request alice's profile (user_id=1).",
        target_id=1, api_path="/challenges/horizontal/i1a/users/{id}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/horizontal/i1b")
def i1b_page():
    return make_response(_chal_page(
        "i1b", "Document Fetch",
        "A document storage API. Any authenticated user can fetch any document by ID — "
        "the server never checks whether the document belongs to them.",
        "Alice owns doc_id=101. Authenticate as bob and request document 101.",
        target_id=101, api_path="/challenges/horizontal/i1b/documents/{id}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/horizontal/i1c")
def i1c_page():
    return make_response(_chal_page(
        "i1c", "Invoice View",
        "An invoicing API that returns full invoice details, including bank account "
        "numbers, for any invoice ID passed in the path.",
        "Alice's invoice is inv_id=1001. Request it while authenticated as bob.",
        target_id=1001, api_path="/challenges/horizontal/i1c/invoices/{id}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/horizontal/i1d")
def i1d_page():
    return make_response(_chal_page(
        "i1d", "Order Details",
        "An e-commerce order endpoint that leaks shipping address and card details "
        "for any order ID, regardless of who made the request.",
        "Alice's order is ord_id=2001. Request it as bob.",
        target_id=2001, api_path="/challenges/horizontal/i1d/orders/{id}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/horizontal/i1e")
def i1e_page():
    return make_response(_chal_page(
        "i1e", "Message Thread",
        "A private messaging API. Message IDs are sequential integers and there is "
        "no ownership check on retrieval.",
        "Alice has a private message at msg_id=3001. Request it as bob.",
        target_id=3001, api_path="/challenges/horizontal/i1e/messages/{id}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.get("/challenges/horizontal/i1a/users/<int:uid>")
def i1a_api(uid: int):
    if not get_session_user():
        return jsonify(_401), 401
    user = USERS.get(uid)
    if not user:
        return jsonify(_404), 404
    return jsonify(user)


@bp.get("/challenges/horizontal/i1b/documents/<int:doc_id>")
def i1b_api(doc_id: int):
    if not get_session_user():
        return jsonify(_401), 401
    doc = DOCUMENTS.get(doc_id)
    if not doc:
        return jsonify(_404), 404
    return jsonify(doc)


@bp.get("/challenges/horizontal/i1c/invoices/<int:inv_id>")
def i1c_api(inv_id: int):
    if not get_session_user():
        return jsonify(_401), 401
    inv = INVOICES.get(inv_id)
    if not inv:
        return jsonify(_404), 404
    return jsonify(inv)


@bp.get("/challenges/horizontal/i1d/orders/<int:ord_id>")
def i1d_api(ord_id: int):
    if not get_session_user():
        return jsonify(_401), 401
    order = ORDERS.get(ord_id)
    if not order:
        return jsonify(_404), 404
    return jsonify(order)


@bp.get("/challenges/horizontal/i1e/messages/<int:msg_id>")
def i1e_api(msg_id: int):
    if not get_session_user():
        return jsonify(_401), 401
    msg = MESSAGES.get(msg_id)
    if not msg:
        return jsonify(_404), 404
    return jsonify(msg)
