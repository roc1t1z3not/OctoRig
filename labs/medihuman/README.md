# MediHuman

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![Ports](https://img.shields.io/badge/Services-HTTP%20%7C%20SSH%20%7C%20FTP-orange.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A deliberately vulnerable healthcare patient portal exposing medical records, prescriptions, lab results, and appointment data. It also runs SSH and FTP — because hospitals really do have more than one attack surface.

> Do not expose this service on a public network.

---

## What to Try

- The login form injects your input directly into the SQL query. Once inside, the patient search at `/patients` accepts a `?q=` parameter that reflects back into the page and straight into the database.
- Patient records are fetched by integer ID at `/patients/<id>` with no ownership check. How many records can you enumerate?
- The staff detail endpoint at `/admin/staff/<id>` enforces a different — and weaker — check than the main `/admin` panel. Can a regular user reach it?
- Messages at `/messages/<id>` have no ownership check. Whose messages can you read?
- SSH is open on port 2224. The credentials are weak and reused in more than one place.
- FTP is on port 2121. Try connecting without any credentials.
- `/patient-records`, `/staff-only`, and `/mri-archive` are disallowed in `robots.txt`. Worth a look.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start medihuman

# Stop
./octorig.sh stop medihuman
```

The app starts on **http://127.0.0.1:8084**.

---

## Access

| Service | Details |
|---------|---------|
| Web | http://127.0.0.1:8084 |
| SSH | `ssh sysadmin@127.0.0.1 -p 2224` — password: `medihuman123` |
| FTP | `ftp 127.0.0.1 2121` — anonymous login |

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `commonhuman-lab` |

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Landing page |
| `GET /dashboard` | Portal dashboard |
| `GET /patients` | Patient list (searchable) |
| `GET /patients/<id>` | Patient record detail |
| `GET /messages` | Secure messaging inbox |
| `GET /messages/<id>` | Message detail |
| `GET /admin` | Admin panel |
| `GET /admin/staff/<id>` | Staff / patient profile |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
