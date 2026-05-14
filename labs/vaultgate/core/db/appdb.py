# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Static data store, token auth, and shared constants for VaultGate."""
from __future__ import annotations

import base64
import hashlib
import uuid as _uuid

from flask import request

_SALT = "vaultgate-salt-2026"


# ── Token / credential helpers ────────────────────────────────────────────────

def _tok(uid: int, uname: str) -> str:
    return hashlib.sha256(f"vaultgate-{uid}-{uname}-{_SALT}".encode()).hexdigest()[:24]


def _profile_uuid(uid: int) -> str:
    raw = hashlib.md5(f"vaultgate-profile-{uid}".encode()).digest()
    return str(_uuid.UUID(bytes=raw))


def _note_b64(note_id: int) -> str:
    return base64.b64encode(f"note:{note_id}".encode()).decode()


def _file_hash(file_id: int) -> str:
    return hashlib.md5(f"file-{file_id}".encode()).hexdigest()


def _receipt_hex(receipt_id: int) -> str:
    return hex(receipt_id)[2:]


# ── Tokens ────────────────────────────────────────────────────────────────────

ALICE_TOKEN = _tok(1, "alice")
BOB_TOKEN   = _tok(2, "bob")
CAROL_TOKEN = _tok(3, "carol")
ADMIN_TOKEN = _tok(99, "admin")

TOKENS: dict[str, dict] = {
    ALICE_TOKEN: {"user_id": 1,  "username": "alice", "role": "user"},
    BOB_TOKEN:   {"user_id": 2,  "username": "bob",   "role": "user"},
    CAROL_TOKEN: {"user_id": 3,  "username": "carol", "role": "user"},
    ADMIN_TOKEN: {"user_id": 99, "username": "admin", "role": "admin"},
}

# password == username (lab only)
_CREDS: dict[str, tuple[str, int]] = {
    "alice": ("alice", 1),
    "bob":   ("bob",   2),
    "carol": ("carol", 3),
    "admin": ("admin", 99),
}


def login(username: str, password: str) -> dict | None:
    entry = _CREDS.get(username)
    if entry and entry[0] == password:
        uid = entry[1]
        uname = username
        return {"token": _tok(uid, uname), "user_id": uid, "username": uname,
                "role": TOKENS[_tok(uid, uname)]["role"]}
    return None


# ── Data — Tier 1: Horizontal IDOR (integer path IDs) ────────────────────────

USERS: dict[int, dict] = {
    1:  {"user_id": 1,  "username": "alice", "email": "alice@vault.local",
         "role": "user",  "phone": "+1-555-0101", "ssn": "123-45-6789",
         "flag": "VAULT{i1a_profile_idor}"},
    2:  {"user_id": 2,  "username": "bob",   "email": "bob@vault.local",
         "role": "user",  "phone": "+1-555-0102", "ssn": "987-65-4321"},
    3:  {"user_id": 3,  "username": "carol", "email": "carol@vault.local",
         "role": "user",  "phone": "+1-555-0103", "ssn": "456-78-9012"},
    99: {"user_id": 99, "username": "admin", "email": "admin@vault.local",
         "role": "admin", "phone": "+1-555-0099", "ssn": "000-00-0000",
         "flag": "VAULT{v1a_vertical_admin_users}"},
}

DOCUMENTS: dict[int, dict] = {
    101: {"doc_id": 101, "user_id": 1, "classification": "RESTRICTED",
          "title": "Q1 Strategy (CONFIDENTIAL)",
          "content": "Alice's internal strategy — not for distribution.",
          "flag": "VAULT{i1b_document_idor}"},
    102: {"doc_id": 102, "user_id": 1, "title": "Personal Notes",
          "content": "Alice's personal notes."},
    201: {"doc_id": 201, "user_id": 2, "title": "Bob's Report",
          "content": "Bob's work report."},
    301: {"doc_id": 301, "user_id": 3, "title": "Carol's Draft",
          "content": "Carol's draft document."},
}

INVOICES: dict[int, dict] = {
    1001: {"inv_id": 1001, "user_id": 1, "amount": 4250.00,
           "description": "Alice's consulting invoice",
           "bank_account": "IBAN-GB29-NWBK-6016-1331-9268-19",
           "flag": "VAULT{i1c_invoice_idor}"},
    1002: {"inv_id": 1002, "user_id": 1, "amount": 1100.00,
           "description": "Alice's expense reimbursement"},
    2001: {"inv_id": 2001, "user_id": 2, "amount": 750.00,
           "description": "Bob's subscription invoice"},
    3001: {"inv_id": 3001, "user_id": 3, "amount": 3200.00,
           "description": "Carol's project invoice"},
}

ORDERS: dict[int, dict] = {
    2001: {"ord_id": 2001, "user_id": 1, "item": "Enterprise License",
           "status": "paid", "address": "123 Alice St, SF CA 94105",
           "card_last4": "1234", "flag": "VAULT{i1d_order_idor}"},
    2002: {"ord_id": 2002, "user_id": 1, "item": "Support Package",
           "status": "pending"},
    3001: {"ord_id": 3001, "user_id": 2, "item": "Starter Plan",
           "status": "active"},
    4001: {"ord_id": 4001, "user_id": 3, "item": "Pro Plan",
           "status": "active"},
}

MESSAGES: dict[int, dict] = {
    3001: {"msg_id": 3001, "from_user": "admin", "to_user_id": 1,
           "subject": "Account Reset",
           "body": "Your temporary password is: TmpPass#8821",
           "flag": "VAULT{i1e_message_idor}"},
    3002: {"msg_id": 3002, "from_user": "admin", "to_user_id": 1,
           "subject": "Welcome", "body": "Welcome to VaultGate!"},
    4001: {"msg_id": 4001, "from_user": "admin", "to_user_id": 2,
           "subject": "Bob welcome", "body": "Hi Bob, welcome aboard!"},
    5001: {"msg_id": 5001, "from_user": "admin", "to_user_id": 3,
           "subject": "Carol welcome", "body": "Hi Carol!"},
}

# ── Data — Tier 2: Obfuscated IDs ────────────────────────────────────────────

ALICE_PROFILE_UUID = _profile_uuid(1)
BOB_PROFILE_UUID   = _profile_uuid(2)

PROFILES: dict[str, dict] = {
    ALICE_PROFILE_UUID: {"uuid": ALICE_PROFILE_UUID, "user_id": 1,
                         "display_name": "Alice A.", "bio": "Security researcher",
                         "salary": 120000, "flag": "VAULT{i2a_uuid_profile_idor}"},
    BOB_PROFILE_UUID:   {"uuid": BOB_PROFILE_UUID, "user_id": 2,
                         "display_name": "Bob B.", "bio": "Developer",
                         "salary": 80000},
}

ALICE_NOTE_B64 = _note_b64(101)
BOB_NOTE_B64   = _note_b64(201)

NOTES: dict[str, dict] = {
    ALICE_NOTE_B64: {"note_id": 101, "user_id": 1,
                     "content": "Lab admin creds: admin / Sup3rS3cret!2026",
                     "flag": "VAULT{i2b_base64_note_idor}"},
    BOB_NOTE_B64:   {"note_id": 201, "user_id": 2,
                     "content": "Bob's shopping list: milk, eggs, bread"},
}

ALICE_FILE_HASH = _file_hash(101)
BOB_FILE_HASH   = _file_hash(201)

FILES: dict[str, dict] = {
    ALICE_FILE_HASH: {"file_id": 101, "user_id": 1,
                      "filename": "credentials.txt",
                      "content": "alice_api_key=sk-IDOR2026-alice-private",
                      "flag": "VAULT{i2c_hash_file_idor}"},
    BOB_FILE_HASH:   {"file_id": 201, "user_id": 2,
                      "filename": "notes.txt",
                      "content": "Bob's file content"},
}

ALICE_RECEIPT_HEX = _receipt_hex(4001)
BOB_RECEIPT_HEX   = _receipt_hex(5001)

RECEIPTS: dict[str, dict] = {
    ALICE_RECEIPT_HEX: {"receipt_id": 4001, "user_id": 1, "amount": 9999.00,
                        "merchant": "ALICE-CORP-LTD",
                        "card_number": "4111111111111111",
                        "flag": "VAULT{i2d_hex_receipt_idor}"},
    BOB_RECEIPT_HEX:   {"receipt_id": 5001, "user_id": 2, "amount": 49.99,
                        "merchant": "EXAMPLE-SHOP"},
}

# ── Data — Tier 3: Body / Query-param IDOR ────────────────────────────────────

BODY_MESSAGES: dict[int, dict] = {
    7001: {"msg_id": 7001, "user_id": 1,
           "content": "Meet at the server room at 21:00 — bring the root key.",
           "flag": "VAULT{i3a_body_message_idor}"},
    7002: {"msg_id": 7002, "user_id": 2,
           "content": "Hey Bob, lunch at noon?"},
}

REPORTS: dict[int, dict] = {
    8001: {"report_id": 8001, "user_id": 1,
           "title": "Annual Security Audit",
           "data": "Critical: 3 highs, 7 mediums. VPN creds: vpn/Al1c3Pass",
           "flag": "VAULT{i3b_query_report_idor}"},
    8002: {"report_id": 8002, "user_id": 2,
           "title": "Bob's Monthly Report",
           "data": "Sales numbers look good."},
}

EXPORTS: dict[int, dict] = {
    9001: {"resource_id": 9001, "user_id": 1,
           "data": "alice_salary=120000\nalice_bonus=30000\nalice_ssn=123-45-6789",
           "flag": "VAULT{i3c_export_idor}"},
    9002: {"resource_id": 9002, "user_id": 2,
           "data": "bob_salary=80000"},
}

RECORDS: dict[int, dict] = {
    10001: {"record_id": 10001, "user_id": 1,
            "data": "Alice's health record — blood type A+, DOB: 1990-03-15",
            "flag": "VAULT{i3d_lookup_idor}"},
    10002: {"record_id": 10002, "user_id": 2,
            "data": "Bob's health record — blood type O+"},
}

# ── Data — Tier 4: Vertical IDOR ──────────────────────────────────────────────

ADMIN_SETTINGS: dict = {
    "db_password": "Passw0rd!",
    "smtp_password": "mail-secret-2026",
    "api_key": "sk-admin-VAULT-2026-internal",
    "debug_mode": False,
    "flag": "VAULT{v1b_vertical_admin_settings}",
}

STAFF_INVOICES: dict[int, dict] = {
    99001: {"inv_id": 99001, "user_id": 99, "amount": 500000.00,
            "description": "Executive compensation Q1",
            "recipient": "admin@vault.local",
            "flag": "VAULT{v1c_vertical_staff_invoice}"},
    99002: {"inv_id": 99002, "user_id": 99, "amount": 25000.00,
            "description": "Board consulting fee"},
}

# ── Data — Tier 5: Method Bypass ──────────────────────────────────────────────

METHOD_RECORDS: dict[int, dict] = {
    11001: {"record_id": 11001, "user_id": 1,
            "data": "Alice's confidential record",
            "flag": "VAULT{m1a_method_delete_bypass}"},
    11002: {"record_id": 11002, "user_id": 2, "data": "Bob's record"},
}

METHOD_PROFILES: dict[int, dict] = {
    12001: {"profile_id": 12001, "user_id": 1,
            "data": "Alice's restricted profile data",
            "flag": "VAULT{m1b_method_put_bypass}"},
    12002: {"profile_id": 12002, "user_id": 2, "data": "Bob's profile"},
}

METHOD_ENTRIES: dict[int, dict] = {
    13001: {"entry_id": 13001, "user_id": 1,
            "data": "Alice's entry data",
            "flag": "VAULT{m1c_method_patch_bypass}"},
    13002: {"entry_id": 13002, "user_id": 2, "data": "Bob's entry"},
}

# ── Data — Tier 6: Param Pollution ────────────────────────────────────────────

POLL_DATA: dict[int, dict] = {
    1: {"user_id": 1, "username": "alice",
        "private_data": "Alice's private dashboard data",
        "flag": "VAULT{p1a_param_pollution}"},
    2: {"user_id": 2, "username": "bob",
        "private_data": "Bob's dashboard data"},
}

JSON_DATA: dict[int, dict] = {
    1: {"user_id": 1, "username": "alice",
        "secret": "alice_secret_2026",
        "flag": "VAULT{p1b_json_duplicate_key}"},
    2: {"user_id": 2, "username": "bob",
        "secret": "bob_secret_2026"},
}

# ── Data — Tier 7: Mass Assignment ────────────────────────────────────────────

MA_ROLE_FLAG  = "VAULT{a1a_mass_assign_role}"
MA_OWNER_FLAG = "VAULT{a1b_mass_assign_owner}"

# ── Data — Tier 8: JWT Tampering ─────────────────────────────────────────────

JWT_SECRET = "secret"

JWT_USERS: dict[int, dict] = {
    1:  {"user_id": 1,  "username": "alice", "role": "user",
         "private_data": "Alice's JWT-protected private data",
         "flag": "VAULT{j1a_jwt_alg_none}"},
    2:  {"user_id": 2,  "username": "bob",   "role": "user",
         "private_data": "Bob's JWT data"},
    99: {"user_id": 99, "username": "admin", "role": "admin",
         "private_data": "Admin secret dashboard data",
         "flag": "VAULT{j1b_jwt_weak_secret}"},
}

JWT_ROLE_FLAG = "VAULT{j1c_jwt_role_claim}"


# ── Auth helper ───────────────────────────────────────────────────────────────

def get_session_user() -> dict | None:
    """Return session user dict from Bearer token header or vault_token cookie."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
    else:
        token = request.cookies.get("vault_token", "").strip()
    return TOKENS.get(token)
