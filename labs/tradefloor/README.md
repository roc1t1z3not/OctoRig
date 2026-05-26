# TradeFloor

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

It's 1999. The dot-com bubble hasn't burst yet, and TradeFloor hasn't heard of CSRF tokens, parameterised queries, or output encoding. A deliberately vulnerable Y2K-era stock trading terminal where live ticking prices share a page with stored XSS, cross-site request forgery, and SQL injection.

> Do not expose this service on a public network.

---

## What to Try

- The trade form at `/trade` has no CSRF token. Can you craft an external page that silently places a buy order on behalf of a logged-in victim?
- The `?symbol=` pre-fill parameter on `/trade` is concatenated directly into a SQL query before the POST even happens. One quote and a comment go a long way.
- The trade memo field is stored raw and rendered without escaping on the order detail page. What fires in the admin's browser the next time they view it?
- The `/filings` search reflects `?q=` into both the query and the HTML simultaneously — injection and XSS in the same parameter.
- Portfolio holdings are fetched by ID. Is there an ownership check stopping you from viewing another trader's positions?
- `/trading-engine`, `/settlement`, and `/compliance-logs` are disallowed in `robots.txt`. Worth a look.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start tradefloor

# Stop
./octorig.sh stop tradefloor
```

The app starts on **http://172.28.2.2**.

---

## Access

| Service | Details |
|---------|---------|
| Web | http://172.28.2.2 |
| SSH | `ssh trader@172.28.2.2` |
| FTP | `ftp 172.28.2.2` |

| Account | Username | Password |
|---------|----------|----------|
| Admin | `admin` | `commonhuman-lab` |

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Trading dashboard |
| `GET /trade` | Place a trade |
| `GET /portfolio` | Portfolio holdings |
| `GET /filings` | Company filing search |
| `GET /filings/<id>` | Filing detail |
| `GET /watchlist` | Watchlist |
| `GET /alerts` | Price alerts |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
