# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""API endpoints, health, index, and scoreboard."""
from __future__ import annotations
import collections
import time

import os
from flask import Blueprint, jsonify, request, make_response

from core.registry import all_challenges, challenge_by_id
from core.db.scoredb import (
    get_scoreboard, get_player_solved, award_points, log_catch, init_score_db, _conn,
)

bp = Blueprint("api", __name__)

def _esc(s: str) -> str:
    """HTML-escape a string for safe embedding in page HTML."""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))

# ---------------------------------------------------------------------------
# Layout helper — bypasses Jinja2 to avoid {{ }} conflicts in challenge content
# ---------------------------------------------------------------------------

_LAYOUT_PATH = os.path.join(os.path.dirname(__file__), "../../templates/layout.html")

def _render_layout(title_suffix: str, content: str) -> str:
    with open(_LAYOUT_PATH, encoding="utf-8") as f:
        tpl = f.read()
    tpl = tpl.replace("BLOCK_TITLE", title_suffix, 1)
    tpl = tpl.replace("BLOCK_CONTENT", content, 1)
    return tpl

# Rate limiting: max 10 flag submissions per player per 60 s
_SUBMIT_HISTORY: dict[str, collections.deque] = collections.defaultdict(collections.deque)
_RATE_LIMIT  = 10
_RATE_WINDOW = 60

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@bp.get("/health")
def health():
    try:
        cx = _conn(); cx.close()
        return jsonify({"status": "ok"})
    except Exception as exc:
        return jsonify({"status": "db_unavailable", "detail": str(exc)}), 503


# ---------------------------------------------------------------------------
# /api/catch — XSS payload beacon endpoint
# Payloads call: fetch('/api/catch?cid=r1a&player=NAME&flag=STING{...}')
# ---------------------------------------------------------------------------

@bp.get("/api/catch")
def api_catch():
    cid    = request.args.get("cid", "").strip()
    player = request.args.get("player", "").strip()
    flag   = request.args.get("flag", "").strip()

    if not cid or not flag:
        return ("", 204)

    chal = challenge_by_id(cid)
    if chal and flag == chal["flag"]:
        log_catch(cid, player, flag)
        if player:
            award_points(player, cid, chal["points"])

    # Always return a 1x1 transparent GIF so img-beacon payloads work too
    gif = (b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
           b'\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00'
           b'\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
    return (gif, 200, {"Content-Type": "image/gif",
                       "Access-Control-Allow-Origin": "*"})


# ---------------------------------------------------------------------------
# /api/submit-flag — manual flag submission (same UX as BreachSQL)
# ---------------------------------------------------------------------------

@bp.post("/api/submit-flag")
def api_submit_flag():
    body = request.get_json(silent=True) or {}
    player       = str(body.get("player", "")).strip()
    challenge_id = str(body.get("challenge_id", "")).strip()
    flag         = str(body.get("flag", "")).strip()

    if not player or not challenge_id or not flag:
        return jsonify({"correct": False,
                        "message": "player, challenge_id and flag are required"}), 400

    now  = time.time()
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
# /api/challenges + /api/scoreboard + /api/player/<>/solved
# ---------------------------------------------------------------------------

@bp.get("/api/challenges")
def api_challenges():
    strip = {"flag", "hint"}
    return jsonify([{k: v for k, v in c.items() if k not in strip}
                    for c in all_challenges()])


@bp.get("/api/scoreboard")
def api_scoreboard():
    return jsonify(get_scoreboard())


@bp.get("/api/player/<player>/solved")
def api_player_solved(player: str):
    return jsonify({"player": player, "solved_ids": get_player_solved(player)})


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------

_TIER_NAMES = {
    1: "Reflected — Basic",
    2: "Reflected — Filtered",
    3: "Stored XSS",
    4: "DOM XSS",
    5: "Blind XSS",
    6: "WAF Bypass",
    7: "CSP Bypass",
    8: "Template Injection",
    9: "GraphQL XSS",
    10: "WebSocket XSS",
    11: "DOM Advanced",
}
_TIER_COLORS = {
    1: "#4caf50", 2: "#2196f3", 3: "#ff9800",  4: "#f44336",
    5: "#9c27b0", 6: "#00bcd4", 7: "#e91e63",  8: "#ff5722",
    9: "#009688", 10: "#3f51b5", 11: "#795548",
}


def _badge(tier: int) -> str:
    c = _TIER_COLORS.get(tier, "#555")
    n = _TIER_NAMES.get(tier, f"Tier {tier}")
    return f'<span class="tier-badge" style="background:{c}">{n}</span>'


def _build_index_html(by_tier: dict, total: int, max_pts: int) -> str:
    parts = [
        f'<h1>Challenge Index</h1>'
        f'<p class="subtitle">{total} challenges &mdash; {max_pts:,} total points available.</p>'
        f'<div class="index-toolbar">'
        f'<input id="search-box" class="search-input" type="search"'
        f' placeholder="&#x1F50D; filter by title, technique, or ID…"'
        f' oninput="filterCards(this.value)">'
        f'<div class="progress-bar-wrap" id="progress-wrap" style="display:none">'
        f'<div class="progress-bar-track"><div class="progress-bar-fill" id="progress-fill"></div></div>'
        f'<span class="progress-label" id="progress-label"></span>'
        f'</div></div>'
    ]

    _TIER_GROUPS = [
        ("Reflected XSS",     [1, 2],     True),
        ("Stored XSS",        [3],        False),
        ("DOM XSS",           [4],        False),
        ("Blind XSS",         [5],        False),
        ("WAF Bypass",        [6],        False),
        ("CSP Bypass",        [7],        False),
        ("Template Injection",[8],        False),
        ("GraphQL XSS",       [9],        False),
        ("WebSocket XSS",     [10],       False),
        ("DOM Advanced",      [11],       False),
    ]

    for group_name, tiers, open_default in _TIER_GROUPS:
        group_chals = [c for t in tiers for c in by_tier.get(t, [])]
        if not group_chals:
            continue
        open_attr = " open" if open_default else ""
        group_pts = sum(c["points"] for c in group_chals)

        parts.append(f'<details class="backend"{open_attr}>')
        parts.append(
            f'<summary>'
            f'<div class="backend-summary-inner">'
            f'<span class="backend-arrow">&#9654;</span>'
            f'<span class="backend-title">{group_name}</span>'
            f'<span class="backend-meta">{len(group_chals)} challenges &bull; {group_pts:,} pts</span>'
            f'</div>'
            f'</summary>'
        )

        for tier_num in tiers:
            chals = by_tier.get(tier_num, [])
            if not chals:
                continue
            parts.append('<div class="tier-section">')
            parts.append(
                f'<div class="tier-heading">{_badge(tier_num)}'
                f'<span style="color:var(--muted);font-size:.85rem">'
                f'{len(chals)} challenge{"s" if len(chals)!=1 else ""}</span></div>'
            )
            parts.append('<div class="cards">')
            for c in chals:
                hint_html = ""
                if c.get("hint"):
                    hint_html = (
                        f'<details class="hint"><summary>hint</summary>'
                        f'<div class="hint-body">{_esc(c["hint"])}</div></details>'
                    )
                parts.append(
                    f'<div class="card" data-cid="{c["challenge_id"]}">'
                    f'<div class="card-title-row">'
                    f'<a class="card-ui-btn" href="{c["endpoint"]}" title="Open challenge">&#x1F310;</a>'
                    f'<span class="card-title">{_esc(c["title"])}</span>'
                    f'<span class="card-solved-badge" style="display:none">&#x2713; solved</span>'
                    f'</div>'
                    f'<div class="card-desc">{_esc(c["description"])}</div>'
                    f'{hint_html}'
                    f'<div class="card-endpoint"><a class="card-endpoint-link" href="{c["endpoint"]}">'
                    f'<code>{c["endpoint"]}</code></a></div>'
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

    return "\n".join(parts)


def _build_scoreboard_html(players: list) -> str:
    rows = ""
    if players:
        for i, p in players:
            cls = {1: "gold", 2: "silver", 3: "bronze"}.get(i, "")
            safe = p["player"].replace("'", "&#39;")
            did  = f"detail-{i}"
            rows += (
                f'<tr class="player-row" onclick="togglePlayerRow(\'{safe}\',\'{did}\')"'
                f' title="Click to see solved challenges">'
                f'<td class="rank {cls}">{i}</td>'
                f'<td>{p["player"]}</td>'
                f'<td>{p["solved"]}</td>'
                f'<td><strong>{p["total"]}</strong></td></tr>'
                f'<tr><td colspan="4" style="padding:0">'
                f'<div id="{did}" class="solved-list">'
                f'<span style="font-size:.75rem;color:var(--muted)">Solved:</span>'
                f'<div class="solved-chips"></div></div></td></tr>'
            )
    else:
        rows = ('<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">'
                'No scores yet — be the first!</td></tr>')
    return (
        '<h1>Scoreboard</h1>'
        '<p class="subtitle">Live rankings &mdash; click a player to drill down. Refreshes every 15 s.</p>'
        '<table><thead><tr><th>#</th><th>Player</th><th>Solved</th><th>Points</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )


@bp.get("/")
def index():
    chals  = all_challenges()
    by_tier: dict[int, list] = {}
    for c in chals:
        by_tier.setdefault(c["tier"], []).append(c)
    html = _render_layout(
        " — Challenges",
        _build_index_html(by_tier, len(chals), sum(c["points"] for c in chals)),
    )
    return make_response(html, 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.get("/scoreboard")
def scoreboard():
    board   = get_scoreboard()
    players = list(enumerate(board, start=1))
    html = _render_layout(" — Scoreboard", _build_scoreboard_html(players))
    return make_response(html, 200, {"Content-Type": "text/html; charset=utf-8"})
