# VaultGate IDOR Range

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![Challenges](https://img.shields.io/badge/Challenges-26-orange.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab%209-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

Dedicated IDOR training range — 26 challenges across 8 categories: horizontal IDOR via path, POST body, and query params; obfuscated references (UUID, base64, hex, MD5); vertical privilege escalation; HTTP method bypass; parameter pollution; mass assignment; and JWT tampering. **18,400 total points.**

> Do not expose this service on a public network.

---

## Challenges

### Tier 1 — Horizontal IDOR (Integer Path) · 5 challenges · 500 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `i1a` | Profile Reader | Integer user_id in path | 100 |
| `i1b` | Document Fetch | Integer doc_id in path | 100 |
| `i1c` | Invoice View | Integer inv_id in path | 100 |
| `i1d` | Order Details | Integer ord_id in path | 100 |
| `i1e` | Message Thread | Integer msg_id in path | 100 |

### Tier 2 — Obfuscated Object References · 4 challenges · 1,200 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `i2a` | UUID Profile | Deterministic UUID (md5-derived) | 300 |
| `i2b` | Base64 Note | Base64-encoded integer | 300 |
| `i2c` | Hashed File ID | MD5-hashed integer | 300 |
| `i2d` | Hex Receipt | Hex-encoded integer | 300 |

### Tier 3 — IDOR via POST Body / Query Param · 4 challenges · 2,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `i3a` | Body Message Read | Integer ID in POST body | 500 |
| `i3b` | Query Report | Integer ID in query param | 500 |
| `i3c` | Export Resource | resource_id in POST body | 500 |
| `i3d` | Record Lookup | record_id in query param | 500 |

### Tier 4 — Vertical IDOR · 3 challenges · 2,400 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `v1a` | Admin User List | Missing role check on admin endpoint | 800 |
| `v1b` | Admin Settings | Internal config exposed to any auth user | 800 |
| `v1c` | Staff Invoice | Staff resource reachable by regular user | 800 |

### Tier 5 — HTTP Method Bypass · 3 challenges · 3,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `m1a` | Delete Bypass | DELETE handler unguarded | 1,000 |
| `m1b` | PUT Bypass | PUT handler unguarded | 1,000 |
| `m1c` | PATCH Bypass | PATCH handler unguarded | 1,000 |

### Tier 6 — Parameter Pollution · 2 challenges · 2,400 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `p1a` | Duplicate Query Param | Duplicate query param — last-value wins | 1,200 |
| `p1b` | JSON Duplicate Key | Duplicate JSON key — last-value wins | 1,200 |

### Tier 7 — Mass Assignment · 2 challenges · 2,400 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `a1a` | Role Elevation | role field accepted from body | 1,200 |
| `a1b` | Owner Override | user_id accepted from body | 1,200 |

### Tier 8 — JWT Tampering · 3 challenges · 4,500 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `j1a` | Algorithm None | JWT — alg:none bypass | 1,500 |
| `j1b` | Weak Secret | JWT — weak HS256 secret (`secret`) | 1,500 |
| `j1c` | Role Claim | JWT — role claim escalation | 1,500 |

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start vaultgate

# Stop (preserves scoreboard volume)
./octorig.sh stop vaultgate

# Wipe scoreboard and restart clean
./octorig.sh reset vaultgate
```

The app starts on **http://127.0.0.1:17478**.

---

## API

VaultGate is API-first — all challenges are driven by JSON endpoints. Collect a token, then use it as a Bearer header on every challenge request.

```bash
# Get all tokens (no auth needed — part of the range design)
GET /api/tokens

# Log in to get your own token
POST /api/login
{"username": "alice", "password": "password123"}

# List all challenges
GET /api/challenges

# Submit a flag
POST /api/submit-flag
{"player": "you", "challenge_id": "i1a", "flag": "VAULT{...}"}
```

Challenge endpoints follow the pattern:

```bash
/challenges/{category}/{id}            # HTML explanation page
/challenges/{category}/{id}/{resource} # Vulnerable JSON API endpoint
```

---

## Flag Format

All flags follow the pattern:

```text
VAULT{<challenge_id>_<short_description>}
```

Example: `VAULT{i1a_profile_idor}`

---

## License

Licensed under the [AGPLv3](../../LICENSE).
