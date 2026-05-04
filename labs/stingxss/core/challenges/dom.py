# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""DOM XSS challenges — Tier 4 (d1a–d1f)."""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("dom", __name__)


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
# D1A — location.hash → innerHTML
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1a")
def d1a():
    body = """
<h1>Hash Hijack <small style="font-size:.7rem;color:#8b949e">[d1a]</small></h1>
<p class="desc">A single-page app reads <code>window.location.hash</code> and writes it to <code>innerHTML</code>.</p>
<div class="result" id="output"><em style="color:#8b949e">Add a #fragment to the URL…</em></div>
<p class="flag-hint">The server never sees the fragment. Pure client-side sink: <code>location.hash → innerHTML</code>.</p>
<script>
  window.addEventListener('hashchange', render);
  window.addEventListener('load', render);
  function render() {
    const h = decodeURIComponent(window.location.hash.slice(1));
    if (h) document.getElementById('output').innerHTML = h;
  }
</script>
"""
    return _page("d1a: Hash Hijack", body)


# ---------------------------------------------------------------------------
# D1B — URLSearchParams q= → innerHTML
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1b")
def d1b():
    body = """
<h1>Search Widget <small style="font-size:.7rem;color:#8b949e">[d1b]</small></h1>
<p class="desc">A client-side search widget reads the <code>q=</code> parameter and inserts a results message via <code>innerHTML</code>.</p>
<div class="result" id="output"><em style="color:#8b949e">Nothing searched yet.</em></div>
<p class="flag-hint">Source: <code>document.location.search</code>. Sink: <code>innerHTML</code>.</p>
<script>
  const params = new URLSearchParams(window.location.search);
  const q = params.get('q');
  if (q) {
    document.getElementById('output').innerHTML = 'Results for: ' + q;
  }
</script>
"""
    return _page("d1b: Search Widget", body)


# ---------------------------------------------------------------------------
# D1C — document.write() with query param
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1c")
def d1c():
    body = """
<h1>Document Write <small style="font-size:.7rem;color:#8b949e">[d1c]</small></h1>
<p class="desc">A legacy widget uses <code>document.write()</code> with a URL parameter.</p>
<p class="flag-hint">Source: <code>location.search</code>. Sink: <code>document.write()</code>.</p>
<script>
  const params = new URLSearchParams(window.location.search);
  const lang = params.get('lang') || 'en';
  document.write('<p>Selected language: ' + lang + '</p>');
</script>
"""
    return _page("d1c: Document Write", body)


# ---------------------------------------------------------------------------
# D1D — jQuery .html() sink
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1d")
def d1d():
    body = """
<h1>jQuery Sizzle <small style="font-size:.7rem;color:#8b949e">[d1d]</small></h1>
<p class="desc">A jQuery page passes a URL parameter to <code>.html()</code>.</p>
<div class="result" id="output"><em style="color:#8b949e">Awaiting input…</em></div>
<p class="flag-hint">Sink: <code>$('#output').html(userInput)</code>.</p>
<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
<script>
  const params = new URLSearchParams(window.location.search);
  const msg = params.get('msg');
  if (msg) {
    $('#output').html(msg);
  }
</script>
"""
    return _page("d1d: jQuery Sizzle", body)


# ---------------------------------------------------------------------------
# D1E — postMessage → innerHTML
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1e")
def d1e():
    body = """
<h1>PostMessage Relay <small style="font-size:.7rem;color:#8b949e">[d1e]</small></h1>
<p class="desc">The page listens for <code>postMessage</code> events and writes the data directly to <code>innerHTML</code>.</p>
<div class="result" id="output"><em style="color:#8b949e">Waiting for a message…</em></div>
<p class="flag-hint">Open this page in an iframe or child window and <code>postMessage</code> a payload to it.</p>
<script>
  window.addEventListener('message', function(e) {
    document.getElementById('output').innerHTML = e.data;
  });
</script>
"""
    return _page("d1e: PostMessage Relay", body)


# ---------------------------------------------------------------------------
# D1F — eval() sink
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d1f")
def d1f():
    body = """
<h1>eval() Trap <small style="font-size:.7rem;color:#8b949e">[d1f]</small></h1>
<p class="desc">A calculator widget passes the <code>expr=</code> query parameter directly to <code>eval()</code>.</p>
<div class="result" id="output"><em style="color:#8b949e">Enter an expression in the URL: ?expr=2+2</em></div>
<p class="flag-hint">Sink: <code>eval(expr)</code>. Craft an expression that also fires your XSS payload.</p>
<script>
  const params = new URLSearchParams(window.location.search);
  const expr = params.get('expr');
  if (expr) {
    try {
      const result = eval(expr);
      document.getElementById('output').innerHTML = 'Result: ' + result;
    } catch(e) {
      document.getElementById('output').innerHTML = 'Error: ' + e.message;
    }
  }
</script>
"""
    return _page("d1f: eval() Trap", body)
