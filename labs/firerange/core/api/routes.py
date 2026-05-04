# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""API endpoints, health probe, and HTML UI."""
from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from core.db.mysqldb import _mysql_conn
from core.registry import (
    all_challenges, challenge_by_id,
    get_scoreboard, award_points,
)

bp = Blueprint("api", __name__)

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@bp.get("/health")
def health():
    try:
        cx = _mysql_conn()
        cx.close()
        return jsonify({"status": "ok"})
    except Exception as exc:
        return jsonify({"status": "db_unavailable", "detail": str(exc)}), 503


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


@bp.post("/api/submit-flag")
def api_submit_flag():
    body = request.get_json(silent=True) or {}
    player       = str(body.get("player", "")).strip()
    challenge_id = str(body.get("challenge_id", "")).strip()
    flag         = str(body.get("flag", "")).strip()

    if not player or not challenge_id or not flag:
        return jsonify({"correct": False, "message": "player, challenge_id and flag are required"}), 400

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
                ui_html = ""
                if c.get("ui_endpoint"):
                    ui_html = f'<a class="card-ui-link" href="{c["ui_endpoint"]}">Try it in browser &rsaquo;</a>'
                parts.append(
                    f'<div class="card">'
                    f'<div class="card-title">{c["title"]}</div>'
                    f'<div class="card-desc">{c["description"]}</div>'
                    f'{hint_html}'
                    f'<div class="card-endpoint"><code>{c["endpoint"]}</code></div>'
                    f'<div class="card-meta">'
                    f'<span class="card-technique">{c["technique"]}</span>'
                    f'<span class="card-points">{c["points"]} pts</span>'
                    f'</div>'
                    f'<div style="font-size:.72rem;color:var(--muted);margin-top:4px">'
                    f'ID: <code>{c["challenge_id"]}</code></div>'
                    f'{ui_html}'
                    f'</div>'
                )
            parts.append('</div></div>')

        parts.append('</details>')

    return "\n".join(parts)


def _build_scoreboard_html(players: list) -> str:
    rows = ""
    if players:
        for i, p in players:
            cls = {1: "gold", 2: "silver", 3: "bronze"}.get(i, "")
            rows += (
                f'<tr><td class="rank {cls}">{i}</td>'
                f'<td>{p["player"]}</td>'
                f'<td>{p["solved"]}</td>'
                f'<td><strong>{p["total"]}</strong></td></tr>'
            )
    else:
        rows = ('<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">'
                'No scores yet — be the first!</td></tr>')
    return (
        '<h1>Scoreboard</h1>'
        '<p class="subtitle">Live rankings — refreshes every 15 s.</p>'
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
