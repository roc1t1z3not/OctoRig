# HumanBank

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A deliberately vulnerable online banking application packed with real-world auth flaws, broken access control, and injection vulnerabilities. Manage accounts, wire transfers, and support tickets — or own them all.

> Do not expose this service on a public network.

---

## What to Try

- The login form trusts user input directly in the SQL query. A single quote and a comment can bypass the password check — and the error messages tell you whether a username exists before you've guessed the password.
- Password reset tokens are computed, not random: `md5(username + epoch_seconds)`. If you know the username and roughly when the reset was requested, you can forge the link.
- Browse to `/accounts` while logged in as a regular user. Does it show only your own account?
- Support tickets have sequential integer IDs at `/tickets/<id>`. Does the server check that the ticket belongs to you?
- The transaction filter on `/accounts/<id>/transactions` accepts `memo`, `type`, `date_from`, and `date_to` — all injected raw into the query.
- `/vault`, `/wire-transfers`, and `/audit-log` are hidden from crawlers. What's inside?

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start humanbank

# Stop
./octorig.sh stop humanbank
```

The app starts on **http://127.0.0.1:8083**.

---

## Access

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `commonhuman-lab` |

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Landing page |
| `GET /dashboard` | Account dashboard |
| `GET /accounts` | Account list |
| `GET /accounts/<id>` | Account detail |
| `GET /accounts/<id>/transactions` | Transaction history (filterable) |
| `GET /tickets` | Support tickets |
| `GET /tickets/<id>` | Ticket detail |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
