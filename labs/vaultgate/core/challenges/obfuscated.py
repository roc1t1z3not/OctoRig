# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 2 — Horizontal IDOR with obfuscated object references (i2a–i2d)."""
from __future__ import annotations

from flask import Blueprint, jsonify, make_response

from core.db.appdb import (
    ALICE_PROFILE_UUID, BOB_PROFILE_UUID,
    ALICE_NOTE_B64, BOB_NOTE_B64,
    ALICE_FILE_HASH, BOB_FILE_HASH,
    ALICE_RECEIPT_HEX, BOB_RECEIPT_HEX,
    PROFILES, NOTES, FILES, RECEIPTS,
    get_session_user,
)
from core.challenges.util import page, tier_badge

bp = Blueprint("obfuscated", __name__)

_401 = {"error": "Unauthorized — send Authorization: Bearer <token>"}
_404 = {"error": "Not found"}


def _chal_page(cid: str, title: str, description: str, hint: str,
               alice_id: str, bob_id: str, api_path_tpl: str,
               id_note: str = "") -> str:
    badge = tier_badge(2)
    alice_url_id = alice_id
    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 2 — Obfuscated IDs &bull; 300 pts</p>
<div class="card">
  <h2>Description</h2>
  <p>{description}</p>
</div>
<div class="card">
  <h2>Hint</h2>
  <p>{hint}</p>
</div>
<div class="card">
  <h2>Resource IDs</h2>
  <table>
    <tr><th>User</th><th>Obfuscated ID</th></tr>
    <tr><td>alice (owner)</td><td><code>{alice_id}</code></td></tr>
    <tr><td>bob</td><td><code>{bob_id}</code></td></tr>
  </table>
  {f'<p style="margin-top:8px">{id_note}</p>' if id_note else ''}
</div>
<div class="card">
  <h2>phaseaccess</h2>
  <pre id="pa-cmd">loading…</pre>
</div>
<div class="card">
  <h2>curl</h2>
  <pre id="curl-cmd">loading…</pre>
</div>
<div class="card">
  <h2>Try it</h2>
  <label>Bearer token</label>
  <input id="tok" placeholder="paste token here">
  <label>Obfuscated ID</label>
  <input id="oid" value="{alice_url_id}">
  <button onclick="go()">Send GET</button>
  <div class="result" id="out">—</div>
</div>
<script>
const API_TPL = '{api_path_tpl}';
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
    const EP = BASE + API_TPL.replace('{{oid}}', encodeURIComponent('{alice_url_id}'));
    document.getElementById('pa-cmd').textContent =
      'phaseaccess \\\\\\n  -u "' + EP + '" \\\\\\n' +
      '  -H "Authorization: Bearer ' + AT + '" --label-a alice \\\\\\n' +
      '  --header-b "Authorization: Bearer ' + BT + '" --label-b bob';
    document.getElementById('curl-cmd').textContent =
      'curl -H "Authorization: Bearer ' + BT + '" \\\\\\n     ' + EP;
  }} catch(e) {{ console.error(e); }}
}})();
async function go() {{
  const BASE = window.location.origin;
  const tok = document.getElementById('tok').value.trim();
  const oid = document.getElementById('oid').value.trim();
  const url = BASE + API_TPL.replace('{{oid}}', encodeURIComponent(oid));
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

@bp.get("/challenges/obfuscated/i2a")
def i2a_page():
    return make_response(_chal_page(
        "i2a", "UUID Profile",
        "Profile UUIDs look random but are generated deterministically from the user ID "
        "using md5('vaultgate-profile-{user_id}') formatted as a UUID.",
        "Compute the UUID for user_id=1 (alice) using Python: "
        "import hashlib, uuid; str(uuid.UUID(bytes=hashlib.md5(b'vaultgate-profile-1').digest()))",
        alice_id=ALICE_PROFILE_UUID, bob_id=BOB_PROFILE_UUID,
        api_path_tpl="/challenges/obfuscated/i2a/profiles/{oid}",
        id_note="Alice's UUID is deterministic — no brute-force needed once the pattern is known.",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/obfuscated/i2b")
def i2b_page():
    return make_response(_chal_page(
        "i2b", "Base64 Note",
        "Note IDs are base64 encodings of strings like 'note:101'. The encoding hides "
        "the integer but doesn't prevent enumeration.",
        "Alice's note is note:101 → base64: bm90ZToxMDE= (try it: "
        "python3 -c \"import base64; print(base64.b64encode(b'note:101').decode())\")",
        alice_id=ALICE_NOTE_B64, bob_id=BOB_NOTE_B64,
        api_path_tpl="/challenges/obfuscated/i2b/notes/{oid}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/obfuscated/i2c")
def i2c_page():
    return make_response(_chal_page(
        "i2c", "Hashed File ID",
        "File IDs are MD5 hashes of the string 'file-{integer}'. The hash obscures "
        "the original value but the function is known.",
        "Alice's file is file-101 → md5: "
        "python3 -c \"import hashlib; print(hashlib.md5(b'file-101').hexdigest())\"",
        alice_id=ALICE_FILE_HASH, bob_id=BOB_FILE_HASH,
        api_path_tpl="/challenges/obfuscated/i2c/files/{oid}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/obfuscated/i2d")
def i2d_page():
    return make_response(_chal_page(
        "i2d", "Hex Receipt",
        "Receipt IDs are hex-encoded integers. The encoding is trivially reversible — "
        "convert the hex string back to decimal or just compute hex(receipt_id).",
        "Alice's receipt is receipt_id=4001 → hex(4001) = 'fa1'. "
        "Bob's is receipt_id=5001 → hex(5001) = '1389'.",
        alice_id=ALICE_RECEIPT_HEX, bob_id=BOB_RECEIPT_HEX,
        api_path_tpl="/challenges/obfuscated/i2d/receipts/{oid}",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.get("/challenges/obfuscated/i2a/profiles/<uuid_str>")
def i2a_api(uuid_str: str):
    if not get_session_user():
        return jsonify(_401), 401
    profile = PROFILES.get(uuid_str)
    if not profile:
        return jsonify(_404), 404
    return jsonify(profile)


@bp.get("/challenges/obfuscated/i2b/notes/<b64_id>")
def i2b_api(b64_id: str):
    if not get_session_user():
        return jsonify(_401), 401
    note = NOTES.get(b64_id)
    if not note:
        return jsonify(_404), 404
    return jsonify(note)


@bp.get("/challenges/obfuscated/i2c/files/<hash_id>")
def i2c_api(hash_id: str):
    if not get_session_user():
        return jsonify(_401), 401
    f = FILES.get(hash_id)
    if not f:
        return jsonify(_404), 404
    return jsonify(f)


@bp.get("/challenges/obfuscated/i2d/receipts/<hex_id>")
def i2d_api(hex_id: str):
    if not get_session_user():
        return jsonify(_401), 401
    receipt = RECEIPTS.get(hex_id)
    if not receipt:
        return jsonify(_404), 404
    return jsonify(receipt)
