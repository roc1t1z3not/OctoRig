# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Tier 8 — JWT Tampering (j1a–j1c)."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import JWT_SECRET, JWT_USERS, JWT_ROLE_FLAG
from core.challenges.util import page, tier_badge

bp = Blueprint("jwt_chals", __name__)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def _b64url_enc(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def issue_jwt(user_id: int, username: str, role: str) -> str:
    header  = _b64url_enc(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_enc(json.dumps({"sub": str(user_id), "username": username,
                                      "role": role}).encode())
    sig_input = f"{header}.{payload}".encode()
    sig = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
    return f"{header}.{payload}.{_b64url_enc(sig)}"


def _verify_jwt_alg_none(token: str) -> dict | None:
    """j1a: accepts alg:none — no signature verification."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header  = json.loads(_b64url_dec(parts[0]))
        payload = json.loads(_b64url_dec(parts[1]))
        alg = header.get("alg", "").lower()
        if alg == "none":
            return payload  # VULNERABLE: skips verification
        if alg == "hs256":
            sig_input = f"{parts[0]}.{parts[1]}".encode()
            expected = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
            actual = _b64url_dec(parts[2])
            if not hmac.compare_digest(expected, actual):
                return None
            return payload
        return None
    except Exception:
        return None


def _verify_jwt_hs256(token: str) -> dict | None:
    """j1b/j1c: only HS256, but with weak secret 'secret'."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header  = json.loads(_b64url_dec(parts[0]))
        payload = json.loads(_b64url_dec(parts[1]))
        if header.get("alg", "").lower() != "hs256":
            return None
        sig_input = f"{parts[0]}.{parts[1]}".encode()
        expected = hmac.new(JWT_SECRET.encode(), sig_input, hashlib.sha256).digest()
        actual = _b64url_dec(parts[2])
        if not hmac.compare_digest(expected, actual):
            return None
        return payload
    except Exception:
        return None


def _bearer_jwt(verifier) -> dict | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    return verifier(auth[7:].strip())


def _chal_page(cid: str, title: str, description: str, hint: str,
               login_path: str, api_path: str, attack_note: str) -> str:
    badge = tier_badge(8)
    return page(f"{cid}: {title}", f"""
<h1>{title} <small style="font-size:.7rem;color:#8b949e">[{cid}]</small> {badge}</h1>
<p class="meta">Tier 8 — JWT Tampering &bull; 1500 pts</p>
<div class="card"><h2>Description</h2><p>{description}</p></div>
<div class="card"><h2>Hint</h2><p>{hint}</p></div>
<div class="card">
  <h2>Setup — get a JWT</h2>
  <p>POST to <code>{login_path}</code> with <code>{{"username":"bob","password":"bob"}}</code>
  to receive a signed JWT. Inspect and tamper it.</p>
  <pre id="jwt-out">—</pre>
  <button onclick="getJWT()">Get JWT for bob</button>
</div>
<div class="card">
  <h2>Attack</h2>
  <p>{attack_note}</p>
</div>
<div class="card">
  <h2>Try forged token</h2>
  <label>Forged JWT</label>
  <textarea id="forged" rows="4" placeholder="paste forged JWT here"></textarea>
  <button onclick="tryForged()">Send to {api_path}</button>
  <div class="result" id="out">—</div>
</div>
<script>
(async () => {{
  const BASE = window.location.origin;
}})();
async function getJWT() {{
  const BASE = window.location.origin;
  try {{
    const r = await fetch(BASE + '{login_path}', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{username:'bob',password:'bob'}}),
    }});
    const d = await r.json();
    document.getElementById('jwt-out').textContent = JSON.stringify(d, null, 2);
    if (d.token) document.getElementById('forged').value = d.token;
  }} catch(e) {{ document.getElementById('jwt-out').textContent = e.message; }}
}}
async function tryForged() {{
  const BASE = window.location.origin;
  const tok = document.getElementById('forged').value.trim();
  const out = document.getElementById('out');
  out.className = 'result'; out.textContent = 'Sending…';
  try {{
    const r = await fetch(BASE + '{api_path}', {{
      headers: {{'Authorization':'Bearer '+tok}},
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

@bp.get("/challenges/jwt/j1a")
def j1a_page():
    return make_response(_chal_page(
        "j1a", "Algorithm None",
        "The JWT verification code accepts the 'none' algorithm, skipping signature "
        "verification entirely. Forge a token claiming sub:1 (alice) with alg:none.",
        "Decode the JWT header+payload (base64url). Set alg to 'none' in the header. "
        "Set sub to '1'. Re-encode header.payload. with an empty third segment.",
        login_path="/challenges/jwt/j1a/login",
        api_path="/challenges/jwt/j1a/profile",
        attack_note="1. Get bob's JWT. "
                    "2. Decode: <code>base64url_decode(header)</code>, change <code>alg</code> to <code>\"none\"</code>. "
                    "3. Decode payload, change <code>sub</code> to <code>\"1\"</code>. "
                    "4. Re-encode: <code>new_header.new_payload.</code> (empty sig). "
                    "5. Send as Authorization: Bearer.",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/jwt/j1b")
def j1b_page():
    return make_response(_chal_page(
        "j1b", "Weak Secret",
        "The JWT is signed with HS256 using the secret 'secret'. Crack the signature, "
        "then forge a token with sub:99 to access admin data.",
        "The signing secret is 'secret'. Use jwt_tool, hashcat, or script it: "
        "sign a new payload with sub=99 using HMAC-SHA256('secret', header.payload).",
        login_path="/challenges/jwt/j1b/login",
        api_path="/challenges/jwt/j1b/data",
        attack_note="1. Get bob's JWT (sub=2). "
                    "2. Crack with: <code>hashcat -a 0 -m 16500 jwt.txt wordlist.txt</code> or try 'secret' directly. "
                    "3. Forge new JWT with sub=99 (admin) signed with 'secret'. "
                    "4. Send forged token to <code>/j1b/data</code>.",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/challenges/jwt/j1c")
def j1c_page():
    return make_response(_chal_page(
        "j1c", "Role Claim",
        "The admin panel checks the 'role' claim in the JWT. The same weak secret "
        "('secret') is used — forge a token with role:admin.",
        "Same weak secret as j1b. Modify the payload: set role to 'admin'. "
        "Re-sign with 'secret' and send to /j1c/admin.",
        login_path="/challenges/jwt/j1c/login",
        api_path="/challenges/jwt/j1c/admin",
        attack_note="1. Get bob's JWT (role=user). "
                    "2. Change the role claim to <code>admin</code>. "
                    "3. Re-sign with <code>'secret'</code>. "
                    "4. Send to <code>/j1c/admin</code>.",
    ), 200, {"Content-Type": "text/html; charset=utf-8"})


# ── Login endpoints (issue JWTs) ──────────────────────────────────────────────

def _jwt_login():
    body = request.get_json(silent=True) or {}
    username = body.get("username", "")
    password = body.get("password", "")
    user_map = {
        "alice": (1, "alice", "user"),
        "bob":   (2, "bob",   "user"),
        "carol": (3, "carol", "user"),
    }
    entry = user_map.get(username)
    if not entry or entry[1] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    uid, uname, role = entry
    token = issue_jwt(uid, uname, role)
    return jsonify({"token": token, "user_id": uid, "username": uname, "role": role})


@bp.post("/challenges/jwt/j1a/login")
def j1a_login():
    return _jwt_login()


@bp.post("/challenges/jwt/j1b/login")
def j1b_login():
    return _jwt_login()


@bp.post("/challenges/jwt/j1c/login")
def j1c_login():
    return _jwt_login()


# ── Vulnerable API endpoints ──────────────────────────────────────────────────

@bp.get("/challenges/jwt/j1a/profile")
def j1a_api():
    """Accepts alg:none — forge sub:1 to get alice's data."""
    payload = _bearer_jwt(_verify_jwt_alg_none)
    if not payload:
        return jsonify({"error": "Invalid or missing JWT"}), 401
    try:
        uid = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid sub claim"}), 400
    user = JWT_USERS.get(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@bp.get("/challenges/jwt/j1b/data")
def j1b_api():
    """Signed with weak secret 'secret' — crack and forge sub:99."""
    payload = _bearer_jwt(_verify_jwt_hs256)
    if not payload:
        return jsonify({"error": "Invalid or missing JWT"}), 401
    try:
        uid = int(payload.get("sub", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid sub claim"}), 400
    user = JWT_USERS.get(uid)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@bp.get("/challenges/jwt/j1c/admin")
def j1c_api():
    """Checks role=admin in JWT — forge role claim."""
    payload = _bearer_jwt(_verify_jwt_hs256)
    if not payload:
        return jsonify({"error": "Invalid or missing JWT"}), 401
    if payload.get("role") != "admin":
        return jsonify({"error": "Forbidden — admin role required in JWT"}), 403
    return jsonify({
        "admin_panel": True,
        "message": "Welcome to the admin panel.",
        "flag": JWT_ROLE_FLAG,
        "users": list(JWT_USERS.values()),
    })
