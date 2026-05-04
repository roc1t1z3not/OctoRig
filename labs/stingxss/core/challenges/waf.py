# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""WAF bypass XSS challenges — Tier 6 (w1a–w1f)."""
from __future__ import annotations
import re
import urllib.parse

from flask import Blueprint, request

bp = Blueprint("waf", __name__)


def _page(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>StingXSS — {title}</title>
<style>
  body{{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;padding:32px;max-width:720px;margin:0 auto}}
  h1{{font-size:1.4rem;margin-bottom:8px;color:#f78166}}
  .desc{{color:#8b949e;font-size:.9rem;margin-bottom:24px}}
  input,textarea{{background:#21262d;border:1px solid #30363d;color:#e6edf3;padding:8px 12px;border-radius:4px;font-size:.9rem;width:100%}}
  button{{background:#f78166;color:#0d1117;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-weight:700;margin-top:8px}}
  .result{{margin-top:24px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px}}
  a.back{{display:block;margin-top:24px;font-size:.82rem;color:#8b949e}}
  .flag-hint{{font-size:.75rem;color:#8b949e;margin-top:8px}}
  .waf-badge{{display:inline-block;background:#da3633;color:#fff;font-size:.7rem;padding:2px 8px;border-radius:4px;margin-bottom:12px}}
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""


# ---------------------------------------------------------------------------
# W1A — Space stripping WAF
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1a")
def w1a():
    q = request.args.get("q", "")
    filtered = q.replace(" ", "")
    body = f"""
<h1>Space Invader <small style="font-size:.7rem;color:#8b949e">[w1a]</small></h1>
<span class="waf-badge">WAF: strips spaces</span>
<p class="desc">The WAF removes every space character from input before it reaches the page.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {filtered}</div>
<p class="flag-hint">No spaces allowed. Try <code>/**/</code>, <code>%09</code> (tab), or <code>%0a</code> (newline) to separate tokens.</p>
"""
    return _page("w1a: Space Invader", body)


# ---------------------------------------------------------------------------
# W1B — Angle bracket removal, input inside JS event handler attribute
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1b")
def w1b():
    q = request.args.get("q", "")
    filtered = q.replace("<", "").replace(">", "")
    # Value is placed into an onclick attribute — already in JS context
    body = f"""
<h1>Bracket Bust <small style="font-size:.7rem;color:#8b949e">[w1b]</small></h1>
<span class="waf-badge">WAF: strips &lt; and &gt;</span>
<p class="desc">All angle brackets are removed. But your input lands inside a JS event handler attribute.</p>
<form method="GET">
  <input name="q" value="" placeholder="Enter a label…" autocomplete="off">
  <button type="submit">Submit</button>
</form>
<div class="result">
  <button onclick="showMsg('{filtered}')">Click me</button>
</div>
<script>function showMsg(m){{document.querySelector('.result p')&&(document.querySelector('.result p').textContent=m)}}</script>
<p class="flag-hint">You're already inside an <code>onclick</code> attribute — no angle brackets needed to break out of HTML context.</p>
"""
    return _page("w1b: Bracket Bust", body)


# ---------------------------------------------------------------------------
# W1C — alert() blocked
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1c")
def w1c():
    q = request.args.get("q", "")
    if "alert" in q.lower():
        return _page("w1c: Alert Ban",
                     '<h1>Alert Ban [w1c]</h1><span class="waf-badge">WAF: BLOCKED</span>'
                     '<p class="desc">Your payload contained "alert". Blocked.</p>')
    body = f"""
<h1>Alert Ban <small style="font-size:.7rem;color:#8b949e">[w1c]</small></h1>
<span class="waf-badge">WAF: blocks "alert"</span>
<p class="desc">The WAF blocks any payload that contains the word <code>alert</code>.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">You don't need <code>alert()</code>. Try <code>confirm()</code>, <code>prompt()</code>, <code>console.log()</code>, or call <code>fetch</code> directly.</p>
"""
    return _page("w1c: Alert Ban", body)


# ---------------------------------------------------------------------------
# W1D — Double URL encoding bypass
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1d")
def w1d():
    raw = request.args.get("q", "")
    # WAF runs on raw input before decoding
    if re.search(r'<|>|script|onerror|onload', raw, re.IGNORECASE):
        return _page("w1d: Double Encode",
                     '<h1>Double Encode [w1d]</h1><span class="waf-badge">WAF: BLOCKED</span>'
                     '<p class="desc">WAF caught your payload in the raw encoded string.</p>')
    # Decode once server-side (simulates double-encoding bypass)
    decoded = urllib.parse.unquote(raw)
    body = f"""
<h1>Double Encode <small style="font-size:.7rem;color:#8b949e">[w1d]</small></h1>
<span class="waf-badge">WAF: inspects pre-decode</span>
<p class="desc">The WAF inspects the raw URL-encoded input before the server decodes it. But the server decodes once.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {decoded}</div>
<p class="flag-hint">Double URL-encode your payload: the WAF sees <code>%253c</code>, the app decodes to <code>%3c</code>, then the browser decodes to <code>&lt;</code>.</p>
"""
    return _page("w1d: Double Encode", body)


# ---------------------------------------------------------------------------
# W1E — SVG events bypass (onerror/onload/onclick blocked)
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1e")
def w1e():
    q = request.args.get("q", "")
    if re.search(r'onerror|onload|onclick|onmouse|onfocus', q, re.IGNORECASE):
        return _page("w1e: SVG Smuggler",
                     '<h1>SVG Smuggler [w1e]</h1><span class="waf-badge">WAF: BLOCKED</span>'
                     '<p class="desc">Common event handler keywords blocked.</p>')
    body = f"""
<h1>SVG Smuggler <small style="font-size:.7rem;color:#8b949e">[w1e]</small></h1>
<span class="waf-badge">WAF: blocks onload/onerror/onclick</span>
<p class="desc">The WAF blocks the most common HTML event handler keywords.</p>
<form method="GET">
  <input name="q" value="" placeholder="Inject here…" autocomplete="off">
  <button type="submit">Go</button>
</form>
<div class="result">{q}</div>
<p class="flag-hint">SVG elements have their own event space. Try <code>&lt;svg&gt;&lt;animate onbegin=…&gt;</code> or <code>&lt;svg&gt;&lt;set attributename=onmouseover …&gt;</code>.</p>
"""
    return _page("w1e: SVG Smuggler", body)


# ---------------------------------------------------------------------------
# W1F — javascript: protocol blocked in href, reflected in anchor tag
# ---------------------------------------------------------------------------

@bp.get("/challenges/waf/w1f")
def w1f():
    url = request.args.get("url", "#")
    if re.search(r'javascript\s*:', url, re.IGNORECASE):
        return _page("w1f: Protocol Swap",
                     '<h1>Protocol Swap [w1f]</h1><span class="waf-badge">WAF: BLOCKED</span>'
                     '<p class="desc">javascript: protocol detected and blocked.</p>')
    body = f"""
<h1>Protocol Swap <small style="font-size:.7rem;color:#8b949e">[w1f]</small></h1>
<span class="waf-badge">WAF: blocks javascript:</span>
<p class="desc">The WAF blocks <code>javascript:</code> in the URL parameter. Your value is placed inside an <code>&lt;a href&gt;</code>.</p>
<form method="GET">
  <input name="url" value="" placeholder="Enter a URL…" autocomplete="off">
  <button type="submit">Set link</button>
</form>
<div class="result"><a href="{url}" style="color:#58a6ff">Click this link</a></div>
<p class="flag-hint">The WAF pattern-matches <code>javascript:</code> literally. What about <code>&#106;avascript:</code> (HTML entity) or VBScript, or a data URI?</p>
"""
    return _page("w1f: Protocol Swap", body)
