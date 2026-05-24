# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Reflected XSS challenges — Tiers 1 and 2."""
from __future__ import annotations
import re
import urllib.parse

from flask import Blueprint, request, make_response
from markupsafe import escape

bp = Blueprint("reflected", __name__)

FLAG_BASE = "http://127.0.0.1"

# ---------------------------------------------------------------------------
# Shared page shell — intentionally minimal, no CSP
# ---------------------------------------------------------------------------

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
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""


# ---------------------------------------------------------------------------
# R1A — Raw reflected query param
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1a")
def r1a():
    q = request.args.get("q", "")
    result = f'<div class="result">Search results for: {q}</div>' if q else ""
    body = f"""
<h1>Hello, Hacker <small style="font-size:.7rem;color:#8b949e">[r1a]</small></h1>
<p class="desc">A search box that reflects your query directly back onto the page.</p>
<form method="GET">
  <input name="q" value="{q}" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
{result}
<p class="flag-hint">Fire your XSS by calling <code>fetch('/api/catch?cid=r1a&amp;player=NAME&amp;flag=STING{{r1a_raw_reflected}}')</code></p>
"""
    return _page("r1a: Hello Hacker", body)


# ---------------------------------------------------------------------------
# R1B — Input inside an HTML attribute
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1b")
def r1b():
    name = request.args.get("name", "")
    body = f"""
<h1>Attribute Escape <small style="font-size:.7rem;color:#8b949e">[r1b]</small></h1>
<p class="desc">Your name is placed inside an HTML attribute. Break out of the attribute context.</p>
<form method="GET">
  <input name="name" value="" placeholder="Your name" autocomplete="off">
  <button type="submit">Greet me</button>
</form>
<div class="result">
  <input type="text" value="{name}" readonly>
</div>
<p class="flag-hint">Escape the attribute, inject an event handler, exfil the flag.</p>
"""
    return _page("r1b: Attribute Escape", body)


# ---------------------------------------------------------------------------
# R1C — Input between tags (inner HTML)
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1c")
def r1c():
    msg = request.args.get("msg", "")
    body = f"""
<h1>Tag Soup <small style="font-size:.7rem;color:#8b949e">[r1c]</small></h1>
<p class="desc">Your message is injected between two HTML tags without encoding.</p>
<form method="GET">
  <input name="msg" value="" placeholder="Leave a message" autocomplete="off">
  <button type="submit">Post</button>
</form>
<div class="result"><p>{msg}</p></div>
<p class="flag-hint">You're already in the body context — inject a tag with an event handler.</p>
"""
    return _page("r1c: Tag Soup", body)


# ---------------------------------------------------------------------------
# R1D — URL path reflected in error page
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1d")
@bp.get("/challenges/reflected/r1d/<path:subpath>")
def r1d(subpath: str = ""):
    body = f"""
<h1>Error Page <small style="font-size:.7rem;color:#8b949e">[r1d]</small></h1>
<p class="desc">This page reflects the URL path in the error message — without encoding.</p>
<div class="result">
  <strong>404 Not Found:</strong> The path <code>/challenges/reflected/r1d/{subpath}</code> does not exist.
</div>
<p class="flag-hint">Inject your payload into the URL path segment after <code>/r1d/</code>.</p>
"""
    return _page("r1d: Error Page", body)


# ---------------------------------------------------------------------------
# R1E — Input interpolated into a JS string inside a <script> block
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1e")
def r1e():
    val = request.args.get("color", "blue")
    body = f"""
<h1>Script Context <small style="font-size:.7rem;color:#8b949e">[r1e]</small></h1>
<p class="desc">Your input is placed directly into a JavaScript string variable inside a &lt;script&gt; block.</p>
<form method="GET">
  <input name="color" value="" placeholder="Favourite colour" autocomplete="off">
  <button type="submit">Set colour</button>
</form>
<script>
  var userColor = '{val}';
  document.write('<p style="color:'+userColor+'">Your colour: '+userColor+'</p>');
</script>
<p class="flag-hint">You're inside a JS string — break out with a quote and add your payload.</p>
"""
    return _page("r1e: Script Context", body)


# ---------------------------------------------------------------------------
# R1F — Custom HTTP header reflected in the page body
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r1f")
def r1f():
    custom = request.headers.get("X-Custom-Name", "")
    display = custom or "<em>(no X-Custom-Name header sent)</em>"
    body = f"""
<h1>Header Echo <small style="font-size:.7rem;color:#8b949e">[r1f]</small></h1>
<p class="desc">The server reflects the <code>X-Custom-Name</code> HTTP header back in the page body.</p>
<div class="result">Welcome, {display}</div>
<p class="flag-hint">Send an <code>X-Custom-Name</code> header containing your XSS payload.</p>
"""
    return _page("r1f: Header Echo", body)


# ===========================================================================
# Tier 2 — Reflected XSS (Filtered)
# ===========================================================================

# ---------------------------------------------------------------------------
# R2A — script tag stripped
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2a")
def r2a():
    q = request.args.get("q", "")
    filtered = re.sub(r'(?i)<script[\s\S]*?</script>', '', q)
    body = f"""
<h1>Tag Stripper <small style="font-size:.7rem;color:#8b949e">[r2a]</small></h1>
<p class="desc">The server removes &lt;script&gt;…&lt;/script&gt; blocks from your input.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {filtered}</div>
<p class="flag-hint">&lt;script&gt; is gone — find another tag that executes JavaScript.</p>
"""
    return _page("r2a: Tag Stripper", body)


# ---------------------------------------------------------------------------
# R2B — quotes stripped
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2b")
def r2b():
    q = request.args.get("q", "")
    filtered = q.replace("'", "").replace('"', "")
    body = f"""
<h1>Quote Blocker <small style="font-size:.7rem;color:#8b949e">[r2b]</small></h1>
<p class="desc">Single and double quotes are stripped from your input before reflection.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {filtered}</div>
<p class="flag-hint">No quotes allowed — use HTML entities or backtick JS strings.</p>
"""
    return _page("r2b: Quote Blocker", body)


# ---------------------------------------------------------------------------
# R2C — case-sensitive keyword filter
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2c")
def r2c():
    q = request.args.get("q", "")
    # Only blocks exact lowercase versions
    for kw in ["script", "onerror", "onload", "onclick", "alert"]:
        if kw in q:
            return _page("r2c: Case Closed",
                         '<h1>Case Closed [r2c]</h1><p class="desc">Blocked.</p>')
    body = f"""
<h1>Case Closed <small style="font-size:.7rem;color:#8b949e">[r2c]</small></h1>
<p class="desc">A case-sensitive filter blocks lowercase XSS keywords.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">The filter only checks lowercase. MiXeD cAsE might slip through.</p>
"""
    return _page("r2c: Case Closed", body)


# ---------------------------------------------------------------------------
# R2D — angle brackets encoded, reflected inside attribute
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2d")
def r2d():
    q = request.args.get("q", "")
    # Encode < and > but not quotes
    filtered = q.replace("<", "&lt;").replace(">", "&gt;")
    body = f"""
<h1>Entity Encoder <small style="font-size:.7rem;color:#8b949e">[r2d]</small></h1>
<p class="desc">Angle brackets are HTML-encoded, but you're reflected inside an attribute.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">
  <input type="text" value="{filtered}" readonly>
</div>
<p class="flag-hint">No &lt; or &gt; — but you're already inside an attribute. Can you escape it?</p>
"""
    return _page("r2d: Entity Encoder", body)


# ---------------------------------------------------------------------------
# R2E — input truncated to 20 chars
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2e")
def r2e():
    q = request.args.get("q", "")[:20]
    body = f"""
<h1>Length Limit <small style="font-size:.7rem;color:#8b949e">[r2e]</small></h1>
<p class="desc">Your input is truncated to 20 characters before reflection.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" maxlength="20" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">20 chars is tight. Pick a short tag + event combo — <code>&lt;svg onload=…&gt;</code> perhaps.</p>
"""
    return _page("r2e: Length Limit", body)


# ---------------------------------------------------------------------------
# R2F — first occurrence of keywords removed
# ---------------------------------------------------------------------------

@bp.get("/challenges/reflected/r2f")
def r2f():
    q = request.args.get("q", "")
    for kw in ["script", "onerror", "alert", "onload"]:
        q = re.sub(kw, "", q, count=1, flags=re.IGNORECASE)
    body = f"""
<h1>Keyword Doubler <small style="font-size:.7rem;color:#8b949e">[r2f]</small></h1>
<p class="desc">The server removes the first occurrence of common XSS keywords.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">Only the first match is stripped. Double up your keywords so one survives.</p>
"""
    return _page("r2f: Keyword Doubler", body)
