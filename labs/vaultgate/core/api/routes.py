# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""API, health, token listing, flag submission, index, and scoreboard."""
from __future__ import annotations

import collections
import os
import time

from flask import Blueprint, jsonify, make_response, request

from core.db.appdb import TOKENS, login
from core.db.scoredb import get_scoreboard, get_player_solved, award_points
from core.registry import all_challenges, challenge_by_id

bp = Blueprint("api", __name__)

_LAYOUT_PATH = os.path.join(os.path.dirname(__file__), "../../templates/layout.html")


def _render_layout(title_suffix: str, content: str) -> str:
    with open(_LAYOUT_PATH, encoding="utf-8") as f:
        tpl = f.read()
    tpl = tpl.replace("BLOCK_TITLE", title_suffix, 1)
    tpl = tpl.replace("BLOCK_CONTENT", content, 1)
    return tpl


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
                  .replace(">", "&gt;").replace('"', "&quot;"))


# ── Health ────────────────────────────────────────────────────────────────────

@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


# ── Token listing (lab convenience — exposes all credentials) ─────────────────

@bp.get("/api/tokens")
def api_tokens():
    users = []
    seen = set()
    for token, info in TOKENS.items():
        uid = info["user_id"]
        if uid in seen:
            continue
        seen.add(uid)
        users.append({"user_id": uid, "username": info["username"],
                      "role": info["role"], "token": token,
                      "password": info["username"]})  # password == username
    users.sort(key=lambda u: u["user_id"])
    return jsonify({"users": users,
                    "note": "Lab credentials — use these tokens as Bearer auth or cookies."})


# ── Login endpoint ────────────────────────────────────────────────────────────

@bp.post("/api/login")
def api_login():
    body = request.get_json(silent=True) or {}
    username = str(body.get("username", "")).strip()
    password = str(body.get("password", "")).strip()
    result = login(username, password)
    if not result:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify(result)


# ── Flag submission ───────────────────────────────────────────────────────────

_SUBMIT_HISTORY: dict[str, collections.deque] = collections.defaultdict(collections.deque)
_RATE_LIMIT  = 10
_RATE_WINDOW = 60


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
        return jsonify({"correct": False, "message": "Rate limit exceeded."}), 429
    hist.append(now)

    chal = challenge_by_id(challenge_id)
    if chal is None:
        return jsonify({"correct": False,
                        "message": f"Unknown challenge: {challenge_id}"}), 400
    if flag != chal["flag"]:
        return jsonify({"correct": False, "message": "Incorrect flag."}), 200

    first_blood = award_points(player, challenge_id, chal["points"])
    return jsonify({
        "correct": True,
        "first_blood": first_blood,
        "points_awarded": chal["points"] if first_blood else 0,
        "message": "Correct! First blood!" if first_blood else "Correct — already solved.",
    }), 200


# ── Challenge / scoreboard JSON ───────────────────────────────────────────────

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


# ── HTML index ────────────────────────────────────────────────────────────────

_TIER_NAMES = {
    1: "Horizontal IDOR",  2: "Obfuscated IDs",    3: "Body / Param IDOR",
    4: "Vertical IDOR",    5: "Method Bypass",      6: "Param Pollution",
    7: "Mass Assignment",  8: "JWT Tampering",
}
_TIER_COLORS = {
    1: "#26c6da", 2: "#42a5f5", 3: "#66bb6a",
    4: "#ef5350", 5: "#ff7043", 6: "#ab47bc",
    7: "#ffa726", 8: "#ec407a",
}
_TIER_GROUPS = [
    ("Horizontal IDOR",   [1], True),
    ("Obfuscated IDs",    [2], False),
    ("Body / Param IDOR", [3], False),
    ("Vertical IDOR",     [4], False),
    ("Method Bypass",     [5], False),
    ("Param Pollution",   [6], False),
    ("Mass Assignment",   [7], False),
    ("JWT Tampering",     [8], False),
]


def _badge(tier: int) -> str:
    c = _TIER_COLORS.get(tier, "#555")
    n = _TIER_NAMES.get(tier, f"Tier {tier}")
    return f'<span class="tier-badge" style="background:{c}">{n}</span>'


def _build_index_html(by_tier: dict, total: int, max_pts: int) -> str:
    parts = [
        f'<h1>Challenge Index</h1>'
        f'<p class="subtitle">{total} IDOR challenges &mdash; {max_pts:,} total points.</p>'
        f'<div class="index-toolbar">'
        f'<input id="search-box" class="search-input" type="search"'
        f' placeholder="&#x1F50D; filter by title, technique, or ID&hellip;"'
        f' oninput="filterCards(this.value)">'
        f'<div class="progress-bar-wrap" id="progress-wrap" style="display:none">'
        f'<div class="progress-bar-track"><div class="progress-bar-fill" id="progress-fill"></div></div>'
        f'<span class="progress-label" id="progress-label"></span>'
        f'</div></div>'
    ]

    for group_name, tiers, open_default in _TIER_GROUPS:
        group_chals = [c for t in tiers for c in by_tier.get(t, [])]
        if not group_chals:
            continue
        open_attr = " open" if open_default else ""
        group_pts = sum(c["points"] for c in group_chals)
        parts.append(f'<details class="backend"{open_attr}>')
        parts.append(
            f'<summary><div class="backend-summary-inner">'
            f'<span class="backend-arrow">&#9654;</span>'
            f'<span class="backend-title">{group_name}</span>'
            f'<span class="backend-meta">{len(group_chals)} challenges &bull; {group_pts:,} pts</span>'
            f'</div></summary>'
        )
        for tier_num in tiers:
            chals = by_tier.get(tier_num, [])
            if not chals:
                continue
            parts.append('<div class="tier-section">')
            parts.append(
                f'<div class="tier-heading">{_badge(tier_num)}'
                f'<span style="color:var(--muted);font-size:.85rem">'
                f'{len(chals)} challenge{"s" if len(chals) != 1 else ""}</span></div>'
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
                    f'<span class="card-technique">{_esc(c["technique"])}</span>'
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
                f'<tr class="player-row" onclick="togglePlayerRow(\'{safe}\',\'{did}\')">'
                f'<td class="rank {cls}">{i}</td>'
                f'<td>{_esc(p["player"])}</td>'
                f'<td>{p["solved"]}</td>'
                f'<td><strong>{p["total"]}</strong></td></tr>'
                f'<tr><td colspan="4" style="padding:0">'
                f'<div id="{did}" class="solved-list">'
                f'<span style="font-size:.75rem;color:var(--muted)">Solved:</span>'
                f'<div class="solved-chips"></div></div></td></tr>'
            )
    else:
        rows = ('<tr><td colspan="4" style="color:var(--muted);text-align:center;padding:32px">'
                'No scores yet — submit a flag to get started.</td></tr>')
    return (
        '<h1>Scoreboard</h1>'
        '<p class="subtitle">Live rankings. Refreshes every 15 s.</p>'
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
