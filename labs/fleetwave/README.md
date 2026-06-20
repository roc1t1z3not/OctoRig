<!-- Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not -->
# FleetWave — Fleet & Delivery Management

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

**Author of this lab:** roc1t1z3not — https://github.com/roc1t1z3not

FleetWave is a deliberately vulnerable logistics / delivery fleet-management SaaS — an internal dispatcher console (DHL-internal-dashboard vibe) for shipments, depots, driver rosters, freight-credit billing, and carrier status checks. Nearly every operational feature trusts its input.

> Do not route real freight or expose this on a public network.

---

## What to Try

- **Recon** — anonymous FTP drops a nightly WMS backup manifest in `pub/`.
- **SQLi (login)** — the sign-in username is interpolated raw; `admin'--` bypasses the password. The `/admin` response carries an `X-Admin-Flag` header.
- **SQLi (search)** — `/shipments/search` injects your term into a `LIKE` clause; UNION into the `_flags` table (4 columns).
- **IDOR (shipment)** — `/shipments/<id>` has no ownership check; walk the ids.
- **IDOR (depot manifest)** — `/depots/<id>` exposes restricted manifest notes, ignoring the `depot_access` table entirely.
- **BAC** — `/admin/driver-roster` (driver PII) checks only that you're logged in, not that you're an admin.
- **Stored XSS** — a delivery-issue report note is rendered unescaped in `/admin/review`; the admin cookie isn't HttpOnly.
- **Mass assignment** — `POST /profile` as JSON accepts a `role` field → escalate to admin.
- **Business logic** — `/billing` freight-credit transfers accept negative, unbounded amounts → inflate your own balance.
- **SSRF → command injection** — admin-only `/api/admin/carrier-check` fetches any URL; point it at the loopback-only `/api/internal/manifest-export`, whose `format` param is a shell-injection sink (the insane chain).

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start fleetwave

# Stop
./octorig.sh stop fleetwave
```

The app starts on **http://172.28.21.2**.

---

## Access

| Service | Details |
|---------|---------|
| Web | http://172.28.21.2 |
| SSH | `ssh fw-ops@172.28.21.2` |
| FTP | `ftp 172.28.21.2` |

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `fleet-master-2026` |
| Demo dispatcher | `demo` | `demo` |

Passwords are stored as unsalted MD5 (crackable); the app MD5s the submitted password before comparison, so the username SQLi still stands.

---

## License

Licensed under the [AGPLv3](../../LICENSE).
