<!-- Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not -->
# SmartGridOps — Smart City Power Grid Control

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

**Author of this lab:** roc1t1z3not — https://github.com/roc1t1z3not

SmartGridOps is a deliberately vulnerable IoT energy / smart-city SCADA control dashboard. Operators manage distribution **zones**, field **devices** (transformers, reclosers, EV chargers, inverters), smart **meters**, demand-response **energy credits**, and an **MQTT** command bus. Almost every operational feature trusts its input.

> Do not connect this to real grid hardware or expose it on a public network.

---

## What to Try

- **SSRF** — the device status poller at `/devices/poll` fetches any URL server-side and reflects the body. Point it at internal addresses / cloud metadata.
- **Command injection** — `/devices/<id>/reboot` pings the management target via a shell, and `/devices/<id>/config-push` echoes your config through one too. A `;` or `$(...)` runs as the app. (`/flag_cmdi.txt`)
- **Weak auth / hardcoded tokens** — the device API under `/api/device/*` is gated only by a static, fleet-wide `X-Device-Token`. The token (and an admin token) leak via anonymous FTP and the SSH operator home.
- **IDOR** — `/zones/<id>` exposes any zone's restricted note and `/meters/<id>` exposes any customer's meter data, with no ownership check.
- **Business logic** — `/credits` transfers accept negative, unbounded amounts. Move credit "the wrong way" to inflate your own balance.
- **MQTT / IoT injection** — `/mqtt` lets you set the full publish topic. Publishing to another zone's `grid/zone/<n>/cmd` topic or a `#`/`+` wildcard trips the broker ACL audit.
- **Bonus** — the login form is an f-string SQLi and honours an unvalidated `?next=` open redirect.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start smartgridops

# Stop
./octorig.sh stop smartgridops
```

The app starts on **http://172.28.16.2**.

---

## Access

| Service | Details |
|---------|---------|
| Web | http://172.28.16.2 |
| SSH | `ssh gridadmin@172.28.16.2` |
| FTP | `ftp 172.28.16.2` |

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `grid-master-2023` |
| Demo operator | `demo` | `demo` |

15 operator accounts are seeded (1 admin + 14 operators across 15 zones). Passwords are stored as **unsalted MD5** hashes (intentionally weak / crackable); the app MD5s the submitted password before comparison, but the username is still interpolated unsanitised, so the login SQLi stands. Other seeded operator creds include `r.fischer:summer2024`, `a.kowalski:password123`, `n.popova:qwerty2024`, `y.nakamura:feeder123`.

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Control-room home |
| `GET /dashboard` | Grid overview |
| `GET/POST /devices/poll` | Device status poller (SSRF) |
| `POST /devices/<id>/reboot` | Reboot via shell ping (cmd injection) |
| `POST /devices/<id>/config-push` | Config push (cmd injection) |
| `GET /zones/<id>` | Zone detail (IDOR) |
| `GET /meters/<id>` | Meter detail (IDOR) |
| `GET/POST /credits` | Energy credit transfers (business logic) |
| `GET/POST /mqtt` | MQTT command dispatch (topic injection) |
| `GET /api/device/list` | Device API (hardcoded token) |
| `GET /api/admin/operators` | Operator dump (admin token) |
| `GET /admin` | Operator roster (admin only) |
| `GET /robots.txt` | Hints |

---

## Flags

Flags follow the `FLAG{sgo_*}` convention and are planted across the database, files, FTP, and the vulnerable flows (SSRF, command injection, IDOR, business logic, MQTT injection, recon).

---

## License

Licensed under the [AGPLv3](../../LICENSE).
