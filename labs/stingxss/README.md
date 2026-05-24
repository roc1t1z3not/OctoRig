# StingXSS Fire Range

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![Challenges](https://img.shields.io/badge/Challenges-54-orange.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

Dedicated XSS training range — 54 challenges across 11 tiers, from raw reflected injection through blind XSS, WAF and CSP bypass, GraphQL, WebSocket, and DOM prototype pollution. An automated admin bot visits stored and blind XSS pages every 30 seconds, so your payloads actually need to fire. **57,800 total points.**

> Do not expose this service on a public network.

---

## Challenges

### Tier 1 — Reflected XSS (Basic) · 6 challenges · 600 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `r1a` | Hello, Hacker | Reflected — raw param | 100 |
| `r1b` | Attribute Escape | Reflected — attribute context | 100 |
| `r1c` | Tag Soup | Reflected — inner HTML | 100 |
| `r1d` | Error Page | Reflected — URL path | 100 |
| `r1e` | Script Context | Reflected — JS string context | 100 |
| `r1f` | Header Echo | Reflected — HTTP header | 100 |

### Tier 2 — Reflected XSS (Filtered) · 6 challenges · 1,500 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `r2a` | Tag Stripper | Script-tag filter bypass | 250 |
| `r2b` | Quote Blocker | Quote filter bypass | 250 |
| `r2c` | Case Closed | Case-mixing bypass | 250 |
| `r2d` | Entity Encoder | Attribute, no-bracket bypass | 250 |
| `r2e` | Length Limit | Length-constrained (20 chars) | 250 |
| `r2f` | Keyword Doubler | Keyword-doubling bypass | 250 |

### Tier 3 — Stored XSS · 6 challenges · 3,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `s1a` | Guestbook | Stored — guestbook | 500 |
| `s1b` | Forum Post | Stored — forum post | 500 |
| `s1c` | Product Review | Stored — product review | 500 |
| `s1d` | Profile Bio | Stored — profile bio | 500 |
| `s1e` | Markdown Mayhem | Stored — Markdown HTML injection | 500 |
| `s1f` | JSON Feed | Stored — JSON to innerHTML | 500 |

### Tier 4 — DOM XSS · 6 challenges · 4,500 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `d1a` | Hash Hijack | DOM — location.hash to innerHTML | 750 |
| `d1b` | Search Widget | DOM — URLSearchParams to innerHTML | 750 |
| `d1c` | Document Write | DOM — document.write() sink | 750 |
| `d1d` | jQuery Sizzle | DOM — jQuery .html() sink | 750 |
| `d1e` | PostMessage Relay | DOM — postMessage to innerHTML | 750 |
| `d1f` | eval() Trap | DOM — eval() sink | 750 |

### Tier 5 — Blind XSS · 5 challenges · 5,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `b1a` | Support Ticket | Blind — support ticket | 1,000 |
| `b1b` | Feedback Form | Blind — feedback form | 1,000 |
| `b1c` | Log Viewer | Blind — User-Agent log | 1,000 |
| `b1d` | Contact Name | Blind — contact form name | 1,000 |
| `b1e` | Cookie Crumbles | Blind — cookie to admin panel | 1,000 |

### Tier 6 — WAF Bypass · 6 challenges · 7,200 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `w1a` | Space Invader | WAF — space stripping | 1,200 |
| `w1b` | Bracket Bust | WAF — angle bracket removal | 1,200 |
| `w1c` | Alert Ban | WAF — alert() blocked | 1,200 |
| `w1d` | Double Encode | WAF — double URL encoding | 1,200 |
| `w1e` | SVG Smuggler | WAF — SVG events | 1,200 |
| `w1f` | Protocol Swap | WAF — javascript: protocol | 1,200 |

### Tier 7 — CSP Bypass · 5 challenges · 10,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `c1a` | Unsafe Inline | CSP — unsafe-inline present | 2,000 |
| `c1b` | JSONP Junction | CSP — JSONP whitelisted domain | 2,000 |
| `c1c` | Nonce Leak | CSP — nonce reflected in body | 2,000 |
| `c1d` | Script Gadget | CSP — Angular script gadget | 2,000 |
| `c1e` | Data URI Dance | CSP — data: URI script | 2,000 |

### Tier 8 — Template Injection → XSS · 4 challenges · 12,000 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `t1a` | Jinja Sting | SSTI — Jinja2 → XSS | 3,000 |
| `t1b` | Twig Twist | SSTI — eval-based → XSS | 3,000 |
| `t1c` | Format String | SSTI — str.format() → XSS | 3,000 |
| `t1d` | Server Echo | SSTI — render_template_string → XSS | 3,000 |

### Tier 9 — GraphQL XSS · 3 challenges · 4,500 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `g1a` | also Scout | GraphQL — reflected string field → innerHTML | 1,500 |
| `g1b` | Mutation Station | GraphQL — stored mutation → admin bot | 1,500 |
| `g1c` | Error Echo | GraphQL — error message reflection → innerHTML | 1,500 |

### Tier 10 — WebSocket XSS · 3 challenges · 5,250 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `ws1a` | Echo Chamber | WebSocket — raw echo → innerHTML | 1,750 |
| `ws1b` | JSON Wire | WebSocket — JSON envelope → innerHTML | 1,750 |
| `ws1c` | Broadcast Booth | WebSocket — stored broadcast → admin bot | 1,750 |

### Tier 11 — DOM Advanced · 4 challenges · 4,250 pts

| ID | Title | Technique | Points |
|----|-------|-----------|--------|
| `d2a` | Prototype Pollution Gadget | DOM — prototype pollution → innerHTML | 1,250 |
| `d2b` | Redirect Jacking | DOM — open redirect → javascript: URI | 1,000 |
| `d2c` | Outer Replacement | DOM — outerHTML sink | 1,000 |
| `d2d` | Adjacent Injection | DOM — insertAdjacentHTML sink | 1,000 |

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start stingxss

# Stop (preserves scoreboard volume)
./octorig.sh stop stingxss

# Wipe scoreboard and restart clean
./octorig.sh reset stingxss
```

The app starts on **http://172.28.9.2**.

---

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML challenge index |
| `GET /scoreboard` | HTML scoreboard |
| `GET /api/challenges` | JSON list of all challenges (flags stripped) |
| `GET /api/scoreboard` | JSON scoreboard |
| `POST /api/submit-flag` | Submit a flag — `{"player", "challenge_id", "flag"}` |
| `POST /api/catch` | Blind XSS catch endpoint — payloads call this to earn points |
| `GET /health` | Health probe |

Challenge endpoints follow the pattern:

```bash
/challenges/{category}/{id}            # Challenge explanation page
/challenges/{category}/{id}/{resource} # Vulnerable endpoint
```

---

## Flag Format

All flags follow the pattern:

```text
STING{<challenge_id>_<short_description>}
```

Example: `STING{r1a_raw_reflected}`

---

## License

Licensed under the [AGPLv3](../../LICENSE).
