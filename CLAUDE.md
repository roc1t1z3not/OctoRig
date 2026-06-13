# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What OctoRig Is

OctoRig is a Docker-based vulnerable security lab platform. It spins up realistic intentionally-vulnerable environments for penetration testing practice, DAST tool validation (primarily for the CommonHuman-Lab scanner tools), and offensive security training. Labs run in fully isolated Docker networks and are never intended to be exposed publicly.

## Commands

```bash
# Interactive menu (most common entry point)
./octorig.sh

# Non-interactive
./octorig.sh start <id|name>   # e.g. start 8, start breachsql, start rewind
./octorig.sh stop <id|name>
./octorig.sh restart <id|name>
./octorig.sh start all         # all labs sequentially
./octorig.sh start world       # real-world scenario labs 1–7 in parallel
./octorig.sh stop all
./octorig.sh status            # show running octorig-* containers
./octorig.sh list

# Some lab scripts expose a reset action (e.g. to wipe the BreachSQL scoreboard)
bash labs/breachsql.sh reset
```

Labs can also be invoked directly via their individual scripts:
```bash
bash labs/rewindrange.sh start
bash labs/breachsql.sh stop
```

## Architecture

### Lab registry

All labs are declared in the `LABS` array in `octorig.sh` in the format `"ID|NAME|SCRIPT|DESCRIPTION"`. `octorig.sh` dispatches to the individual lab scripts in `labs/`. Labs 1–7 are the "world" set (realistic apps); labs 8–11 are dedicated scanner fire-ranges; labs 12–17 are third-party images.

### Lab script pattern

Every lab script (e.g. `labs/rewindrange.sh`) follows the same shape:

1. Declares constants: `LAB_NAME`, `CONTAINER_NAME` / `APP_CONTAINER`, `LAB_NET`, `LAB_SUBNET`, `LAB_IP`
2. Sources `labs/_common.sh` for shared helpers
3. Calls `require_action "$1"` to enforce `start|stop|status`
4. `start`: calls `ensure_container_gone`, `ensure_network`, `docker build`, `docker run`, `wait_for_port` or health-check loop, then `access_card` to print connection info
5. `stop`: `docker rm -f` containers, `remove_network`
6. `status`: `container_status` for each container

### Shared helpers — `labs/_common.sh`

Source this at the top of any new lab script. Key functions:

| Function | Purpose |
|---|---|
| `good` / `bad` / `info` / `warn` / `header` | Coloured output |
| `access_card <nameref-array>` | Print the post-start connection info box. Array entries are `"KEY\|VALUE"` strings. |
| `docker_pull <image> [timeout]` | Pull with spinner; skips if image cached locally |
| `wait_for_port <host> <port> [timeout]` | Polls `nc` until open |
| `ensure_network <name> <subnet>` | Idempotent bridge network creation |
| `remove_network <name>` | Silent remove (ignores if in use) |
| `ensure_container_gone <name>` | Force-remove container if it exists (stopped or running) |
| `container_status <name>` | Print running/stopped/not-found status |
| `require_action <arg>` | Exit with usage if arg is not `start|stop|status` |

### Networking convention

Each lab lives on its own Docker bridge network with a `/24` subnet. App containers are assigned fixed IPs within that subnet (always `.2`). Subnets follow the pattern `172.28.<N>.0/24` where `N` increments per lab. Container names are prefixed `octorig-<labname>`.

### Custom-built labs (1–11)

Labs 1–7 and 8–11 are built from source on `start`. Sources live in `labs/<labname>/` and contain:
- `Dockerfile` — build instructions; Flask + Python, sometimes with `openssh-server`, `vsftpd`, `supervisor`
- `app.py` — Flask application (intentionally vulnerable)
- `db.py` / `helpers.py` — database init and shared utilities
- `supervisord.conf` / `vsftpd.conf` — multi-service config for labs that expose SSH and FTP
- `requirements.txt` — minimal pip deps

Multi-service labs (1–7) use `supervisord` to run Flask + sshd + vsftpd inside a single container. SSH and FTP credentials are intentionally weak and seeded with harvestable secrets (`.env`, `.netrc`, `.bash_history`) for VaultRip testing.

### Scanner fire-ranges (labs 8–10)

- **Lab 8 — BreachSQL** (`labs/firerange/`): 57 SQLi challenges across MySQL, PostgreSQL, and SQLite. Uses three containers (MySQL, PostgreSQL, Flask app). Scoreboard is persisted in a Docker volume (`octorig-breachsql-scores`) — survives `stop`/`start`. Use `reset` to wipe it.
- **Lab 9 — StingXSS** (`labs/stingxss/`): Tiered XSS challenges (T1–T8).
- **Lab 10 — VaultGate** (`labs/vaultgate/`): IDOR benchmarking challenges.

### Third-party labs (12–17)

These pull official images (`docker_pull` is called with a spinner). No source code to maintain; update by bumping the image tag in the lab script.

## Adding a new lab

1. Create `labs/<labname>/` with `Dockerfile`, `app.py`, `requirements.txt`.
2. Create `labs/<labname>.sh` following the existing lab script pattern (copy `rewindrange.sh` as a template).
3. Pick the next available subnet (`172.28.<N>.0/24`) and register it in the `LABS` array in `octorig.sh`.
4. If the lab needs SSH/FTP, copy the `supervisord.conf` / `vsftpd.conf` pattern from an existing multi-service lab.
