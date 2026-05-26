# Limelight

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

The popcorn smells real. The vulnerabilities are too. Limelight is a deliberately vulnerable cinema booking platform where you can browse films, select seats, write reviews, and redeem gift cards — and where almost every feature has a flaw waiting to be found.

> Do not expose this service on a public network.

---

## What to Try

- The search bar at `/movies?q=` drops your input straight into a LIKE query. There's no parameterisation. The results page also echoes your query back unescaped — one request, two vulnerabilities.
- Movie reviews are stored raw and rendered with no output encoding. Post a payload on any film's page and wait for someone else to load it.
- Booking references are sequential integers at `/booking/<id>`. Is there any check that the booking belongs to you?
- The API at `/api/booking/<id>` and `/api/user/<id>` require no authentication at all. Start from 1 and keep going.
- Profile editing at `/profile/<user_id>` checks that you're logged in — but not that the profile is yours. The `is_admin` and `balance` fields are also accepted in the POST body without restriction.
- Gift card redemption at `/gift` passes the code directly into the SQL query. No parameterisation.
- The `/admin` panel checks for a session but never verifies whether you're actually an admin. Any authenticated user can reach it.
- The announcement editor at `/admin/announce` renders your input through Flask's `render_template_string`. Type `{{ 7*7 }}` and see what comes back.
- Login accepts a `?next=` redirect parameter with no validation. Where can you send someone after they authenticate?
- Ticket price is submitted as a hidden field from the seat-selection form. The server uses whatever value arrives in the POST — try editing it before you submit.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start limelight

# Stop
./octorig.sh stop limelight
```

The app starts on **http://172.28.7.2**.

---

## Access

| Service | Details |
|---------|---------|
| Web | http://172.28.7.2 |
| SSH | `ssh cinemaops@172.28.7.2` |
| FTP | `ftp 172.28.7.2` |

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `commonhuman-lab` |

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Now showing homepage |
| `GET /movies` | Browse and search films |
| `GET /movie/<id>` | Film detail, showtimes, and reviews |
| `GET /book/<showing_id>` | Seat selection map |
| `GET /booking/<id>` | View a booking (IDOR) |
| `GET /bookings` | My bookings |
| `GET /profile/<user_id>` | User profile (IDOR, mass assignment) |
| `GET /gift` | Gift card redemption (SQLi) |
| `GET /admin` | Admin panel (broken access control) |
| `GET /admin/announce` | Announcement editor (SSTI) |
| `GET /api/booking/<id>` | Booking API — no auth required |
| `GET /api/user/<id>` | User API — no auth required |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
