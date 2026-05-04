# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""API endpoints, health probe, and HTML UI."""
from __future__ import annotations
import collections
import time

from flask import Blueprint, jsonify, render_template, request

from core.db.mysqldb import _mysql_conn
from core.db.pgdb import _pg_conn
from core.db.sqdb import _sq_conn
from core.registry import (
    all_challenges, challenge_by_id,
    get_scoreboard, award_points, get_player_solved,
)

bp = Blueprint("api", __name__)

# In-memory rate-limit store: player -> deque of submission timestamps
_SUBMIT_HISTORY: dict[str, collections.deque] = collections.defaultdict(
    lambda: collections.deque()
)
_RATE_LIMIT = 10    # max submissions
_RATE_WINDOW = 60   # per N seconds

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@bp.get("/health")
def health():
    status = {}
    mysql_ok = False

    # MySQL — gates the startup readiness check in breachsql.sh
    try:
        cx = _mysql_conn(); cx.close()
        status["mysql"] = "ok"
        mysql_ok = True
    except Exception as exc:
        status["mysql"] = str(exc)

    # PostgreSQL — informational only; does not block startup
    try:
        cx = _pg_conn(); cx.close()
        status["postgres"] = "ok"
    except Exception as exc:
        status["postgres"] = str(exc)

    # SQLite — informational only; does not block startup
    try:
        cx = _sq_conn(); cx.close()
        status["sqlite"] = "ok"
    except Exception as exc:
        status["sqlite"] = str(exc)

    overall = "ok" if all(v == "ok" for v in status.values()) else "degraded"
    if mysql_ok:
        return jsonify({"status": overall, "backends": status})
    return jsonify({"status": "db_unavailable", "backends": status}), 503


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@bp.get("/api/challenges")
def api_challenges():
    chals = all_challenges()
    _strip = {"flag", "hint", "ui_endpoint"}
    public = [{k: v for k, v in c.items() if k not in _strip} for c in chals]
    return jsonify(public)


@bp.get("/api/scoreboard")
def api_scoreboard():
    return jsonify(get_scoreboard())


@bp.get("/api/player/<player>/solved")
def api_player_solved(player: str):
    solved_ids = get_player_solved(player)
    return jsonify({"player": player, "solved_ids": solved_ids})


@bp.post("/api/submit-flag")
def api_submit_flag():
    body = request.get_json(silent=True) or {}
    player       = str(body.get("player", "")).strip()
    challenge_id = str(body.get("challenge_id", "")).strip()
    flag         = str(body.get("flag", "")).strip()

    if not player or not challenge_id or not flag:
        return jsonify({"correct": False, "message": "player, challenge_id and flag are required"}), 400

    # Rate limit: max 10 submissions per player per 60 s
    now = time.time()
    hist = _SUBMIT_HISTORY[player]
    while hist and hist[0] < now - _RATE_WINDOW:
        hist.popleft()
    if len(hist) >= _RATE_LIMIT:
        return jsonify({"correct": False, "message": "Rate limit exceeded — slow down."}), 429
    hist.append(now)

    chal = challenge_by_id(challenge_id)
    if chal is None:
        return jsonify({"correct": False, "message": f"Unknown challenge: {challenge_id}"}), 400

    if flag != chal["flag"]:
        return jsonify({"correct": False, "message": "Incorrect flag."}), 200

    first_blood = award_points(player, challenge_id, chal["points"])
    return jsonify({
        "correct": True,
        "first_blood": first_blood,
        "points_awarded": chal["points"] if first_blood else 0,
        "message": "Correct! First blood!" if first_blood else "Correct — already solved.",
    }), 200


# ---------------------------------------------------------------------------
# HTML UI
# ---------------------------------------------------------------------------

_TIER_NAMES = {
    1: "Beginner", 2: "Intermediate", 3: "Advanced", 4: "Expert", 5: "Legend",
    6: "PostgreSQL — Entry", 7: "PostgreSQL — Intermediate", 8: "PostgreSQL — Expert",
    9: "PostgreSQL — Legend",
    10: "SQLite — Entry", 11: "SQLite — Intermediate", 12: "SQLite — Legend",
}
_TIER_COLORS = {
    1: "#4caf50", 2: "#2196f3", 3: "#ff9800", 4: "#f44336", 5: "#9c27b0",
    6: "#00bcd4", 7: "#0097a7", 8: "#006064", 9: "#004d40",
    10: "#795548", 11: "#5d4037", 12: "#3e2723",
}




def _badge(tier: int) -> str:
    c = _TIER_COLORS.get(tier, "#555")
    n = _TIER_NAMES.get(tier, f"Tier {tier}")
    return f'<span class="tier-badge" style="background:{c}">{n}</span>'


def _build_index_html(by_tier: dict, total: int, max_pts: int) -> str:
    # Group tiers into three backends
    _BACKENDS = [
        ("MySQL",      range(1, 6),   True),   # open by default
        ("PostgreSQL", range(6, 10),  False),
        ("SQLite",     range(10, 13), False),
    ]

    parts = [
        f'<h1>Challenge Index</h1>'
        f'<p class="subtitle">{total} challenges &mdash; {max_pts} total points available.</p>'
        f'<div class="index-toolbar">'
        f'<input id="search-box" class="search-input" type="search" placeholder="&#x1F50D; filter by title, technique, or ID…" oninput="filterCards(this.value)">'
        f'<div class="progress-bar-wrap" id="progress-wrap" style="display:none">'
        f'<div class="progress-bar-track"><div class="progress-bar-fill" id="progress-fill"></div></div>'
        f'<span class="progress-label" id="progress-label"></span>'
        f'</div>'
        f'</div>'
    ]

    for backend_name, tier_range, open_default in _BACKENDS:
        # collect tiers that have challenges
        backend_tiers = [t for t in tier_range if t in by_tier]
        if not backend_tiers:
            continue
        backend_total = sum(len(by_tier[t]) for t in backend_tiers)
        backend_pts   = sum(c["points"] for t in backend_tiers for c in by_tier[t])
        open_attr = " open" if open_default else ""

        parts.append(f'<details class="backend"{open_attr}>')
        parts.append(
            f'<summary>'
            f'<span class="backend-arrow">&#9654;</span>'
            f'<span class="backend-title">{backend_name}</span>'
            f'<span class="backend-meta">{backend_total} challenges &bull; {backend_pts} pts</span>'
            f'</summary>'
        )

        for tier_num in backend_tiers:
            chals = by_tier[tier_num]
            parts.append('<div class="tier-section">')
            parts.append(
                f'<div class="tier-heading">{_badge(tier_num)}'
                f'<span style="color:var(--muted);font-size:.85rem">'
                f'{len(chals)} challenge{"s" if len(chals) != 1 else ""}'
                f'</span></div>'
            )
            parts.append('<div class="cards">')
            for c in chals:
                hint_html = ""
                if c.get("hint"):
                    hint_html = (
                        f'<details class="hint">'
                        f'<summary>hint</summary>'
                        f'<div class="hint-body">{c["hint"]}</div>'
                        f'</details>'
                    )
                ui_btn = ""
                if c.get("ui_endpoint"):
                    ui_btn = f'<a class="card-ui-btn" href="{c["ui_endpoint"]}" title="Try in browser">&#x1F310;</a>'
                # Render the endpoint as a clickable link when it has a query
                # string (GET challenges) so the crawler can discover it.
                ep = c["endpoint"]
                if "?" in ep:
                    endpoint_html = f'<a class="card-endpoint-link" href="{ep}"><code>{ep}</code></a>'
                else:
                    endpoint_html = f'<code>{ep}</code>'
                parts.append(
                    f'<div class="card" data-cid="{c["challenge_id"]}">'
                    f'<div class="card-title-row">'
                    f'{ui_btn}'
                    f'<span class="card-title">{c["title"]}</span>'
                    f'<span class="card-solved-badge" style="display:none">&#x2713; solved</span>'
                    f'</div>'
                    f'<div class="card-desc">{c["description"]}</div>'
                    f'{hint_html}'
                    f'<div class="card-endpoint">{endpoint_html}</div>'
                    f'<div class="card-meta">'
                    f'<span class="card-technique">{c["technique"]}</span>'
                    f'<span class="card-points">{c["points"]} pts</span>'
                    f'</div>'
                    f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
                    f'ID: <code>{c["challenge_id"]}</code></div>'
                    f'</div>'
                )
            parts.append('</div></div>')

        parts.append('</details>')

    # my5b / pg4c / sq3b "Crawl & Conquer" — endpoints are intentionally hidden
    # from the challenge cards but still linked from this page for crawlers.
    parts.append(
        '<a href="/challenges/my5/dashboard?key=secret"'
        ' style="position:absolute;opacity:0;pointer-events:none"'
        ' aria-hidden="true" tabindex="-1"></a>'
        '<a href="/challenges/pg/hidden?token=secret"'
        ' style="position:absolute;opacity:0;pointer-events:none"'
        ' aria-hidden="true" tabindex="-1"></a>'
        '<a href="/challenges/sq/hidden?token=secret"'
        ' style="position:absolute;opacity:0;pointer-events:none"'
        ' aria-hidden="true" tabindex="-1"></a>'
    )
    return "\n".join(parts)


def _build_scoreboard_html(players: list) -> str:
    rows = ""
    if players:
        for i, p in players:
            cls = {1: "gold", 2: "silver", 3: "bronze"}.get(i, "")
            safe_name = p["player"].replace("'", "&#39;")
            detail_id = f"detail-{i}"
            rows += (
                f'<tr class="player-row" onclick="togglePlayerRow(\'{safe_name}\',\'{detail_id}\')" title="Click to see solved challenges">'
                f'<td class="rank {cls}">{i}</td>'
                f'<td>{p["player"]}</td>'
                f'<td>{p["solved"]}</td>'
                f'<td><strong>{p["total"]}</strong></td></tr>'
                f'<tr><td colspan="4" style="padding:0">'
                f'<div id="{detail_id}" class="solved-list">'
                f'<span style="font-size:.75rem;color:var(--muted)">Solved challenges:</span>'
                f'<div class="solved-chips"></div>'
                f'</div></td></tr>'
            )
    else:
        rows = ('<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">'
                'No scores yet — be the first!</td></tr>')
    return (
        '<h1>Scoreboard</h1>'
        '<p class="subtitle">Live rankings &mdash; click a player to see their solved challenges. Refreshes every 15 s.</p>'
        '<table><thead><tr><th>#</th><th>Player</th><th>Solved</th><th>Points</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )


@bp.get("/")
def index():
    chals = all_challenges()
    by_tier: dict[int, list] = {}
    for c in chals:
        by_tier.setdefault(c["tier"], []).append(c)
    total = len(chals)
    max_pts = sum(c["points"] for c in chals)
    return render_template(
        "layout.html",
        block_title=" — Challenges",
        block_content=_build_index_html(by_tier, total, max_pts),
    )


@bp.get("/scoreboard")
def scoreboard():
    board = get_scoreboard()
    players = list(enumerate(board, start=1))
    return render_template(
        "layout.html",
        block_title=" — Scoreboard",
        block_content=_build_scoreboard_html(players),
    )
