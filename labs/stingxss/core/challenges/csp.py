# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""CSP bypass XSS challenges — Tier 7 (c1a–c1e)."""
from __future__ import annotations
import os
import secrets

from flask import Blueprint, request, make_response

bp = Blueprint("csp", __name__)


def _page(title: str, body: str, csp: str = "", extra_head: str = "") -> str:
    html = f"""<!DOCTYPE html>
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
  .csp-badge{{display:inline-block;background:#1f6feb;color:#fff;font-size:.7rem;padding:2px 8px;border-radius:4px;margin-bottom:12px;word-break:break-all}}
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""
    resp = make_response(html)
    if csp:
        resp.headers["Content-Security-Policy"] = csp
    return resp


# ---------------------------------------------------------------------------
# C1A — CSP with unsafe-inline
# ---------------------------------------------------------------------------

@bp.get("/challenges/csp/c1a")
def c1a():
    q = request.args.get("q", "")
    csp = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    body = f"""
<h1>Unsafe Inline <small style="font-size:.7rem;color:#8b949e">[c1a]</small></h1>
<span class="csp-badge">CSP: script-src 'self' 'unsafe-inline'</span>
<p class="desc">The page has a CSP but includes <code>'unsafe-inline'</code> — inline scripts are still allowed.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">If <code>'unsafe-inline'</code> is present, a plain <code>&lt;script&gt;</code> tag works fine.</p>
"""
    return _page("c1a: Unsafe Inline", body, csp=csp)


# ---------------------------------------------------------------------------
# C1B — JSONP endpoint whitelisted in CSP
# ---------------------------------------------------------------------------

@bp.get("/challenges/csp/c1b")
def c1b():
    q = request.args.get("q", "")
    # Whitelist self (which hosts our JSONP endpoint)
    csp = "default-src 'self'; script-src 'self'"
    body = f"""
<h1>JSONP Junction <small style="font-size:.7rem;color:#8b949e">[c1b]</small></h1>
<span class="csp-badge">CSP: script-src 'self'  (JSONP at /challenges/csp/c1b/jsonp)</span>
<p class="desc">The CSP allows scripts from <code>'self'</code>. A JSONP endpoint exists at
  <code>/challenges/csp/c1b/jsonp?callback=…</code>.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">A same-origin JSONP endpoint lets you control the script content:
  <code>&lt;script src="/challenges/csp/c1b/jsonp?callback=YOUR_PAYLOAD"&gt;&lt;/script&gt;</code></p>
"""
    return _page("c1b: JSONP Junction", body, csp=csp)


@bp.get("/challenges/csp/c1b/jsonp")
def c1b_jsonp():
    cb = request.args.get("callback", "console.log")
    from flask import Response
    # Reflect callback name directly — intentional JSONP vulnerability
    return Response(f'{cb}({{"status":"ok"}})', mimetype="application/javascript")


# ---------------------------------------------------------------------------
# C1C — Nonce reflected in body
# ---------------------------------------------------------------------------

# Use a process-level nonce that resets on restart (for simplicity)
_C1C_NONCE = secrets.token_hex(16)


@bp.get("/challenges/csp/c1c")
def c1c():
    q = request.args.get("q", "")
    nonce = _C1C_NONCE
    csp = f"default-src 'self'; script-src 'nonce-{nonce}'"
    body = f"""
<h1>Nonce Leak <small style="font-size:.7rem;color:#8b949e">[c1c]</small></h1>
<span class="csp-badge">CSP: script-src 'nonce-…'</span>
<p class="desc">The CSP uses a nonce for scripts — but the nonce is also reflected in the page body.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<!-- debug: nonce={nonce} -->
<p class="flag-hint">Find the nonce in the HTML source. A <code>&lt;script nonce="…"&gt;</code> with that value will be allowed.</p>
"""
    return _page("c1c: Nonce Leak", body, csp=csp)


# ---------------------------------------------------------------------------
# C1D — Angular script gadget
# ---------------------------------------------------------------------------

@bp.get("/challenges/csp/c1d")
def c1d():
    q = request.args.get("q", "")
    # Whitelist angular CDN
    csp = "default-src 'self'; script-src 'self' https://ajax.googleapis.com"
    body = f"""
<h1>Script Gadget <small style="font-size:.7rem;color:#8b949e">[c1d]</small></h1>
<span class="csp-badge">CSP: script-src 'self' https://ajax.googleapis.com</span>
<p class="desc">CSP blocks inline scripts. Angular is loaded from the whitelisted Google CDN.</p>
<div ng-app>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
</div>
<script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.8.3/angular.min.js"></script>
<p class="flag-hint">Angular evaluates <code>ng-init</code> and template expressions <code>{{'{{'}}'1+1'{{'}}'}}</code> without a <code>&lt;script&gt;</code> tag.</p>
"""
    return _page("c1d: Script Gadget", body, csp=csp)


# ---------------------------------------------------------------------------
# C1E — data: URI in script-src
# ---------------------------------------------------------------------------

@bp.get("/challenges/csp/c1e")
def c1e():
    q = request.args.get("q", "")
    csp = "default-src 'self'; script-src 'self' data:"
    body = f"""
<h1>Data URI Dance <small style="font-size:.7rem;color:#8b949e">[c1e]</small></h1>
<span class="csp-badge">CSP: script-src 'self' data:</span>
<p class="desc">The CSP allows <code>data:</code> URIs as script sources.</p>
<form method="GET">
  <input name="q" value="" placeholder="Search…" autocomplete="off">
  <button type="submit">Search</button>
</form>
<div class="result">Results for: {q}</div>
<p class="flag-hint">A <code>&lt;script src="data:text/javascript,YOUR_CODE"&gt;</code> is a valid script if <code>data:</code> is whitelisted.</p>
"""
    return _page("c1e: Data URI Dance", body, csp=csp)
