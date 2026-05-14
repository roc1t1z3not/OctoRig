# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Challenge registry for VaultGate IDOR Range."""
from __future__ import annotations

CHALLENGES: list[dict] = [

    # ── Tier 1 — Horizontal IDOR (integer path segment) ──────────────────────

    dict(challenge_id="i1a", tier=1, title="Profile Reader",
         description="The user profile endpoint accepts any valid session token and returns "
                     "whatever user ID is in the path. Authentication is checked; ownership is not.",
         hint="Log in as alice (user_id=1) and as bob (user_id=2). Request alice's profile "
              "using bob's token: GET /challenges/horizontal/i1a/users/1",
         technique="Horizontal IDOR — integer user_id in path",
         points=100, flag="VAULT{i1a_profile_idor}",
         endpoint="/challenges/horizontal/i1a"),

    dict(challenge_id="i1b", tier=1, title="Document Fetch",
         description="A document storage API. Any authenticated user can fetch any document "
                     "by ID — the server never checks whether the document belongs to them.",
         hint="Alice owns doc_id=101. Authenticate as bob and request document 101.",
         technique="Horizontal IDOR — integer doc_id in path",
         points=100, flag="VAULT{i1b_document_idor}",
         endpoint="/challenges/horizontal/i1b"),

    dict(challenge_id="i1c", tier=1, title="Invoice View",
         description="An invoicing API that returns full invoice details, including bank account "
                     "numbers, for any invoice ID passed in the path.",
         hint="Alice's invoice is inv_id=1001. Request it while authenticated as bob.",
         technique="Horizontal IDOR — integer inv_id in path",
         points=100, flag="VAULT{i1c_invoice_idor}",
         endpoint="/challenges/horizontal/i1c"),

    dict(challenge_id="i1d", tier=1, title="Order Details",
         description="An e-commerce order endpoint that leaks shipping address and card "
                     "details for any order ID, regardless of who made the request.",
         hint="Alice's order is ord_id=2001. Request it as bob.",
         technique="Horizontal IDOR — integer ord_id in path",
         points=100, flag="VAULT{i1d_order_idor}",
         endpoint="/challenges/horizontal/i1d"),

    dict(challenge_id="i1e", tier=1, title="Message Thread",
         description="A private messaging API. Message IDs are sequential integers and "
                     "there is no ownership check on retrieval.",
         hint="Alice has a private message at msg_id=3001. Request it as bob.",
         technique="Horizontal IDOR — integer msg_id in path",
         points=100, flag="VAULT{i1e_message_idor}",
         endpoint="/challenges/horizontal/i1e"),

    # ── Tier 2 — Obfuscated Object References ─────────────────────────────────

    dict(challenge_id="i2a", tier=2, title="UUID Profile",
         description="Profile UUIDs look random but are generated deterministically from "
                     "the user ID using a known hash function. Enumerate to find alice's UUID.",
         hint="The UUID is md5('vaultgate-profile-{user_id}') formatted as a UUID. "
              "Compute it for user_id=1.",
         technique="Horizontal IDOR — deterministic UUID",
         points=300, flag="VAULT{i2a_uuid_profile_idor}",
         endpoint="/challenges/obfuscated/i2a"),

    dict(challenge_id="i2b", tier=2, title="Base64 Note",
         description="Note IDs are base64-encoded strings like 'note:101'. The encoding "
                     "hides the integer but doesn't prevent enumeration.",
         hint="Alice's note is note:101 → base64 encode it to get the path parameter.",
         technique="Horizontal IDOR — base64-encoded integer",
         points=300, flag="VAULT{i2b_base64_note_idor}",
         endpoint="/challenges/obfuscated/i2b"),

    dict(challenge_id="i2c", tier=2, title="Hashed File ID",
         description="File IDs are MD5 hashes of the underlying integer ID. The hash "
                     "obscures the original value but the function is known and reversible by enumeration.",
         hint="Alice's file is file-101. Compute md5('file-101') to get the path parameter.",
         technique="Horizontal IDOR — MD5-hashed integer",
         points=300, flag="VAULT{i2c_hash_file_idor}",
         endpoint="/challenges/obfuscated/i2c"),

    dict(challenge_id="i2d", tier=2, title="Hex Receipt",
         description="Receipt IDs are hex-encoded integers. The encoding is trivially "
                     "reversible — just convert the hex string back to decimal.",
         hint="Alice's receipt is receipt_id=4001. hex(4001) gives the path parameter.",
         technique="Horizontal IDOR — hex-encoded integer",
         points=300, flag="VAULT{i2d_hex_receipt_idor}",
         endpoint="/challenges/obfuscated/i2d"),

    # ── Tier 3 — IDOR via POST Body / Query Param ─────────────────────────────

    dict(challenge_id="i3a", tier=3, title="Body Message Read",
         description="A POST endpoint that reads a private message. The message_id is "
                     "supplied in the JSON request body and is not validated against the session.",
         hint="POST to the endpoint with {\"message_id\": 7001} while authenticated as bob.",
         technique="Horizontal IDOR — integer ID in POST body",
         points=500, flag="VAULT{i3a_body_message_idor}",
         endpoint="/challenges/body/i3a"),

    dict(challenge_id="i3b", tier=3, title="Query Report",
         description="A report download endpoint that takes the report_id as a query "
                     "parameter. Any authenticated user can retrieve any report.",
         hint="Alice's report is report_id=8001. GET /report?report_id=8001 as bob.",
         technique="Horizontal IDOR — integer ID in query param",
         points=500, flag="VAULT{i3b_query_report_idor}",
         endpoint="/challenges/body/i3b"),

    dict(challenge_id="i3c", tier=3, title="Export Resource",
         description="A data export endpoint. The caller supplies resource_id in the "
                     "POST body and the server exports the matching record without an ownership check.",
         hint="POST {\"resource_id\": 9001} as bob to export alice's data.",
         technique="Horizontal IDOR — resource_id in POST body",
         points=500, flag="VAULT{i3c_export_idor}",
         endpoint="/challenges/body/i3c"),

    dict(challenge_id="i3d", tier=3, title="Record Lookup",
         description="A record lookup endpoint using a record_id query parameter. "
                     "Health records are returned for any ID without verifying the requester.",
         hint="Alice's record is record_id=10001. GET /lookup?record_id=10001 as bob.",
         technique="Horizontal IDOR — record_id in query param",
         points=500, flag="VAULT{i3d_lookup_idor}",
         endpoint="/challenges/body/i3d"),

    # ── Tier 4 — Vertical IDOR ────────────────────────────────────────────────

    dict(challenge_id="v1a", tier=4, title="Admin User List",
         description="An admin-only endpoint that returns all users, including admin "
                     "accounts. The endpoint checks authentication but not the user's role.",
         hint="GET /admin/users with any valid session token — no admin role needed.",
         technique="Vertical IDOR — missing role check on admin endpoint",
         points=800, flag="VAULT{v1a_vertical_admin_users}",
         endpoint="/challenges/vertical/v1a"),

    dict(challenge_id="v1b", tier=4, title="Admin Settings",
         description="An internal configuration endpoint that exposes database passwords "
                     "and API keys. Intended for admins only, but the role check is missing.",
         hint="GET /admin/settings with bob's regular user token.",
         technique="Vertical IDOR — internal config exposed to any auth user",
         points=800, flag="VAULT{v1b_vertical_admin_settings}",
         endpoint="/challenges/vertical/v1b"),

    dict(challenge_id="v1c", tier=4, title="Staff Invoice",
         description="A staff-tier endpoint serving executive invoices. Regular users "
                     "can reach it because the middleware only checks for a valid session.",
         hint="GET /staff/invoices/99001 with a regular user token.",
         technique="Vertical IDOR — staff resource reachable by regular user",
         points=800, flag="VAULT{v1c_vertical_staff_invoice}",
         endpoint="/challenges/vertical/v1c"),

    # ── Tier 5 — HTTP Method Bypass ───────────────────────────────────────────

    dict(challenge_id="m1a", tier=5, title="Delete Bypass",
         description="GET /records/{id} is protected and returns 403. The DELETE handler "
                     "on the same path skips the ownership check entirely.",
         hint="Try DELETE /challenges/method/m1a/records/11001 — the auth guard only runs on GET.",
         technique="Method bypass — DELETE handler unguarded",
         points=1000, flag="VAULT{m1a_method_delete_bypass}",
         endpoint="/challenges/method/m1a"),

    dict(challenge_id="m1b", tier=5, title="PUT Bypass",
         description="GET /profiles/{id} returns 403 for non-owners. The PUT handler "
                     "on the same path was added later and never got the ownership check.",
         hint="PUT to /challenges/method/m1b/profiles/12001 with any JSON body as bob.",
         technique="Method bypass — PUT handler unguarded",
         points=1000, flag="VAULT{m1b_method_put_bypass}",
         endpoint="/challenges/method/m1b"),

    dict(challenge_id="m1c", tier=5, title="PATCH Bypass",
         description="GET /entries/{id} is access-controlled. PATCH on the same endpoint "
                     "was added for partial updates and the auth check was forgotten.",
         hint="PATCH /challenges/method/m1c/entries/13001 as bob.",
         technique="Method bypass — PATCH handler unguarded",
         points=1000, flag="VAULT{m1c_method_patch_bypass}",
         endpoint="/challenges/method/m1c"),

    # ── Tier 6 — Parameter Pollution ──────────────────────────────────────────

    dict(challenge_id="p1a", tier=6, title="Duplicate Query Param",
         description="The endpoint reads the last value when the same query parameter "
                     "is sent twice. Send user_id twice — once with your own ID, once with alice's.",
         hint="GET /data?user_id=2&user_id=1 — the server uses request.args.getlist()[-1].",
         technique="HTTP parameter pollution — duplicate query param",
         points=1200, flag="VAULT{p1a_param_pollution}",
         endpoint="/challenges/pollution/p1a"),

    dict(challenge_id="p1b", tier=6, title="JSON Duplicate Key",
         description="Python's json.loads() keeps the last occurrence of a duplicate key. "
                     "Send a JSON body with user_id appearing twice.",
         hint="POST {\"user_id\": 2, \"user_id\": 1} — Python json picks the last value (1).",
         technique="HTTP parameter pollution — duplicate JSON key",
         points=1200, flag="VAULT{p1b_json_duplicate_key}",
         endpoint="/challenges/pollution/p1b"),

    # ── Tier 7 — Mass Assignment ──────────────────────────────────────────────

    dict(challenge_id="a1a", tier=7, title="Role Elevation",
         description="The profile update endpoint passes all request fields directly to "
                     "the update logic. Include a 'role' field to elevate yourself to admin.",
         hint="POST {\"display_name\": \"Hacker\", \"role\": \"admin\"} — the flag appears when role=admin is accepted.",
         technique="Mass assignment — role field accepted from body",
         points=1200, flag="VAULT{a1a_mass_assign_role}",
         endpoint="/challenges/massassign/a1a"),

    dict(challenge_id="a1b", tier=7, title="Owner Override",
         description="A post creation endpoint that binds the user_id from the request "
                     "body instead of from the session. Supply alice's user_id to create a post as her.",
         hint="POST {\"title\": \"...\", \"user_id\": 1} as bob — the post is created as alice.",
         technique="Mass assignment — user_id accepted from body",
         points=1200, flag="VAULT{a1b_mass_assign_owner}",
         endpoint="/challenges/massassign/a1b"),

    # ── Tier 8 — JWT Tampering ────────────────────────────────────────────────

    dict(challenge_id="j1a", tier=8, title="Algorithm None",
         description="The JWT verification code accepts the 'none' algorithm, skipping "
                     "signature verification entirely. Forge a token with alg:none and sub:1.",
         hint="Decode your JWT, change alg to 'none' and sub to '1', remove the signature. "
              "Send the forged token to access alice's data.",
         technique="JWT — alg:none bypass",
         points=1500, flag="VAULT{j1a_jwt_alg_none}",
         endpoint="/challenges/jwt/j1a"),

    dict(challenge_id="j1b", tier=8, title="Weak Secret",
         description="The JWT is signed with HS256 using the secret 'secret'. Crack the "
                     "signature, forge a token with sub:99 to access admin data.",
         hint="The signing secret is 'secret'. Re-sign a token with sub=99 (admin).",
         technique="JWT — weak HS256 secret",
         points=1500, flag="VAULT{j1b_jwt_weak_secret}",
         endpoint="/challenges/jwt/j1b"),

    dict(challenge_id="j1c", tier=8, title="Role Claim",
         description="The admin panel endpoint checks the 'role' claim in the JWT. "
                     "The secret is the same weak one ('secret') — forge role:admin.",
         hint="Decode your JWT, change role to 'admin', re-sign with 'secret'.",
         technique="JWT — role claim escalation",
         points=1500, flag="VAULT{j1c_jwt_role_claim}",
         endpoint="/challenges/jwt/j1c"),
]


def all_challenges() -> list[dict]:
    return CHALLENGES


def challenge_by_id(cid: str) -> dict | None:
    return next((c for c in CHALLENGES if c["challenge_id"] == cid), None)
