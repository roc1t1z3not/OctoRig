# BreachSQL Fire Range

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-MySQL%20%7C%20PostgreSQL%20%7C%20SQLite-blue.svg)](.)
[![Challenges](https://img.shields.io/badge/Challenges-57-orange.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

Deliberately vulnerable Flask application — 57 SQL injection challenges across MySQL, PostgreSQL, and SQLite. The primary test target for the [BreachSQL](https://github.com/CommonHuman-Lab/breachsql) scanner. Also usable as a standalone CTF lab.

> Do not expose this service on a public network.

---

## Challenges

57 challenges across 3 backends and 5 difficulty tiers. **47950 total points.**

### MySQL (28 challenges · 22150 pts)

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `my1a` | First Blood | Integer error-based | 100 |
| `my1b` | Secret Stash | UNION 2-column | 100 |
| `my1c` | Double Trouble | Double-quote context error | 100 |
| `my1d` | What's Your Version | UNION / `@@version` | 100 |
| `my2a` | Invisible Gate | Boolean-blind (200 vs 404) | 250 |
| `my2b` | Login Wall | POST login, error + boolean | 250 |
| `my2c` | OR Gate | OR-based boolean-blind | 250 |
| `my2d` | Second Sight | Two-step (inject → read) | 250 |
| `my2e` | Group Think | HAVING / GROUP BY enumeration | 250 |
| `my3a` | Sleeping Giant | Time-blind (`SLEEP()`) | 500 |
| `my3b` | Hidden Corridor | Path-parameter injection | 500 |
| `my3c` | Triple Threat | UNION 3-column | 500 |
| `my3d` | High Five | UNION 5-column | 500 |
| `my3e` | Paren Trap | Boolean-blind, paren context | 500 |
| `my3f` | Schema Walker | `information_schema` enumeration | 500 |
| `my4a` | The Filter | WAF bypass (`--`/`#` stripped) | 1000 |
| `my4b` | API Whisperer | JSON body injection | 1000 |
| `my4c` | Stack Attack | Stacked queries | 1000 |
| `my4d` | Tick Tock | Time-blind, string context | 1000 |
| `my4e` | Cookie Monster | Cookie injection | 1000 |
| `my4f` | Ghost Writer | Header / `?ua=` injection | 1000 |
| `my4g` | No Space No Problem | WAF strips spaces — `/**/` bypass | 1000 |
| `my4h` | Hex Spell | Quote WAF — `0x…` / `CHAR()` bypass | 1000 |
| `my4i` | Burning Cycles | `BENCHMARK()` time-blind, `SLEEP()` blocked | 1000 |
| `my4j` | Case Blind | Case-sensitive keyword blacklist bypass | 1000 |
| `my5a` | Full Chain | Multi-technique, 4 columns | 2500 |
| `my5b` | Crawl & Conquer | Index-linked hidden endpoint | 2500 |
| `my5c` | Broken Words | Keyword-doubling / CONCAT obfuscation | 2500 |

### PostgreSQL (16 challenges · 16500 pts)

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `pg1a` | PG Error | CAST type mismatch | 300 |
| `pg1b` | PG Boolean | Boolean-blind | 300 |
| `pg1c` | Engine Check | UNION / `version()` | 300 |
| `pg2a` | PG Sleep | Time-blind (`pg_sleep()`) | 600 |
| `pg2b` | PG Union | UNION extraction | 600 |
| `pg2c` | PG Stacked | Stacked queries | 600 |
| `pg2d` | Aggregate Leak | HAVING / GROUP BY enumeration | 600 |
| `pg2e` | Catalog Diver | `information_schema` enumeration | 600 |
| `pg2f` | PG Echo Chamber | Second-order injection | 600 |
| `pg3a` | PG Path Param | Path-parameter injection | 1200 |
| `pg3b` | PG POST Form | POST login injection | 1200 |
| `pg3c` | PG Cookie | Cookie injection | 1200 |
| `pg3d` | Dollar Sign | Dollar-quoting WAF bypass | 1200 |
| `pg3e` | PG Ghost Writer | Header injection (`User-Agent` / `?ua=`) | 1200 |
| `pg4a` | PG Legend | Full multi-technique chain | 3000 |
| `pg4b` | Pipe Dream | `\|\|` concat obfuscation vault | 3000 |

### SQLite (13 challenges · 9300 pts)

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `sq1a` | Lite Error | CAST type mismatch | 300 |
| `sq1b` | Lite Boolean | Boolean-blind | 300 |
| `sq1c` | Lite Version | UNION / `sqlite_version()` | 300 |
| `sq2a` | Lite Time | Time-blind (`randomblob()`) | 600 |
| `sq2b` | Lite Union | UNION extraction | 600 |
| `sq2c` | Lite Stacked | Stacked queries | 600 |
| `sq2d` | Lite Path | Path-parameter injection | 600 |
| `sq2e` | Lite Login | POST login injection | 600 |
| `sq2f` | Char by Char | `CHAR()` quote-bypass WAF | 600 |
| `sq2g` | Master Key | `sqlite_master` enumeration | 600 |
| `sq2h` | Lite Echo | Second-order injection | 600 |
| `sq2i` | Lite Whisperer | JSON body injection | 600 |
| `sq3a` | Lite Legend | Full multi-technique chain | 3000 |

---

## Quick Start

The Fire Range is managed by OctoRig

```bash
# From the OctoRig root
./octorig.sh start BreachSQL

# Stop (preserves scoreboard volume)
./octorig.sh stop BreachSQL
```

The app starts on **http://127.0.0.1:17476**.

---

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML challenge index |
| `GET /scoreboard` | HTML scoreboard |
| `GET /api/challenges` | JSON list of all challenges (flags stripped) |
| `GET /api/scoreboard` | JSON scoreboard |
| `POST /api/submit-flag` | Submit a flag — `{"player", "challenge_id", "flag"}` |
| `GET /health` | Health probe — checks all three DB connections |

Challenge endpoints follow the pattern:

```bash
/challenges/my<tier>/<slug>    # MySQL
/challenges/pg/<slug>          # PostgreSQL
/challenges/sq/<slug>          # SQLite
```

---

## Flag Format

All flags follow the pattern:

```text
FIRE{<challenge_id>_<short_description>}
```

Example: `FIRE{my1a_integer_error_based}`

---

## License

Licensed under the [AGPLv3](../../LICENSE).
