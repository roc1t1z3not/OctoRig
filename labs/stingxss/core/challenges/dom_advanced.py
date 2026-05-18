# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""DOM Advanced XSS challenges — Tier 11 (d2a–d2d).

Each challenge targets a sink or pattern that StingXSS's DOM scanner and
browser engine can now detect:

  d2a — Prototype pollution gadget  (location.hash JSON → __proto__ → innerHTML)
  d2b — Open redirect → XSS        (location.href = params.get('next'))
  d2c — outerHTML sink              (element.outerHTML = params.get('widget'))
  d2d — insertAdjacentHTML sink     (element.insertAdjacentHTML('beforeend', …))
"""
from __future__ import annotations

from flask import Blueprint

bp = Blueprint("dom_advanced", __name__)


def _page(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>StingXSS — {title}</title>
<style>
  body{{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;padding:32px;max-width:720px;margin:0 auto}}
  h1{{font-size:1.4rem;margin-bottom:8px;color:#f78166}}
  .desc{{color:#8b949e;font-size:.9rem;margin-bottom:24px}}
  .result{{margin-top:24px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px;min-height:48px}}
  a.back{{display:block;margin-top:24px;font-size:.82rem;color:#8b949e}}
  .flag-hint{{font-size:.75rem;color:#8b949e;margin-top:8px}}
  code{{background:#21262d;padding:2px 6px;border-radius:3px;font-size:.85rem}}
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""


# ---------------------------------------------------------------------------
# D2A — Prototype Pollution Gadget
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d2a")
def d2a():
    body = """
<h1>Prototype Pollution Gadget <small style="font-size:.7rem;color:#8b949e">[d2a]</small></h1>
<p class="desc">
  A widget reads configuration from the URL hash as JSON and deep-merges it into a defaults object.
  A downstream gadget reads <code>template</code> from a plain <code>{}</code> — an object
  with <em>no own property</em> — so it falls back to <code>Object.prototype</code> if that
  has been polluted.
</p>
<div class="result" id="widget"><em style="color:#8b949e">Widget content appears here.</em></div>
<p class="flag-hint">
  Source: <code>location.hash</code> (URL-decoded JSON). Gadget: <code>{}.template → innerHTML</code>.<br>
  Hint: pollute <code>Object.prototype.template</code> via <code>__proto__</code> in the JSON payload.<br>
  Payload: <code>fetch('/api/catch?cid=d2a&amp;player=NAME&amp;flag=STING{d2a_prototype_pollution}')</code>
</p>
<script>
  // Recursive merge — deliberately vulnerable to __proto__ pollution
  function merge(dst, src) {
    for (const k in src) {
      if (src[k] !== null && typeof src[k] === 'object') {
        dst[k] = (dst[k] !== null && typeof dst[k] === 'object') ? dst[k] : {};
        merge(dst[k], src[k]);
      } else {
        dst[k] = src[k];
      }
    }
    return dst;
  }

  const defaults = { theme: 'dark' };
  const frag = location.hash.slice(1);
  if (frag) {
    try { merge(defaults, JSON.parse(decodeURIComponent(frag))); } catch (_) {}
  }

  // content has no own 'template' — reads from prototype if polluted
  const content = {};
  document.getElementById('widget').innerHTML =
    content.template || '<em style="color:#8b949e">No template configured.</em>';
</script>
"""
    return _page("d2a: Prototype Pollution Gadget", body)


# ---------------------------------------------------------------------------
# D2B — Open Redirect → XSS
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d2b")
def d2b():
    body = """
<h1>Redirect Jacking <small style="font-size:.7rem;color:#8b949e">[d2b]</small></h1>
<p class="desc">
  After login, the app redirects the user to the URL stored in the <code>next=</code> parameter.
  No scheme validation is applied — any URI is accepted, including <code>javascript:</code>.
</p>
<div class="result" id="output"><em style="color:#8b949e">Redirect destination will appear here.</em></div>
<p class="flag-hint">
  Source: <code>URLSearchParams.get('next')</code>. Sink: <code>window.location.href</code>.<br>
  What happens when <code>next=javascript:alert(1)</code>?<br>
  Payload: <code>fetch('/api/catch?cid=d2b&amp;player=NAME&amp;flag=STING{d2b_open_redirect_xss}')</code>
</p>
<script>
  const next = new URLSearchParams(location.search).get('next');
  if (next) {
    document.getElementById('output').textContent = 'Redirecting to: ' + next;
    // Post-login redirect — no origin or scheme check
    window.location.href = next;
  }
</script>
"""
    return _page("d2b: Redirect Jacking", body)


# ---------------------------------------------------------------------------
# D2C — outerHTML sink
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d2c")
def d2c():
    body = """
<h1>Outer Replacement <small style="font-size:.7rem;color:#8b949e">[d2c]</small></h1>
<p class="desc">
  A widget builder reads the <code>widget=</code> parameter and assigns it to
  <code>element.outerHTML</code>, replacing the entire placeholder node.
  Unlike <code>innerHTML</code>, <code>outerHTML</code> replaces the element itself —
  including any attached event listeners — with the parsed HTML.
</p>
<div id="placeholder" class="result">
  <em style="color:#8b949e">Placeholder — replaced via outerHTML assignment.</em>
</div>
<p class="flag-hint">
  Source: <code>URLSearchParams.get('widget')</code>. Sink: <code>element.outerHTML = …</code>.<br>
  Payload: <code>fetch('/api/catch?cid=d2c&amp;player=NAME&amp;flag=STING{d2c_outerhtml_sink}')</code>
</p>
<script>
  const widget = new URLSearchParams(location.search).get('widget');
  if (widget) {
    document.getElementById('placeholder').outerHTML = widget;
  }
</script>
"""
    return _page("d2c: Outer Replacement", body)


# ---------------------------------------------------------------------------
# D2D — insertAdjacentHTML sink
# ---------------------------------------------------------------------------

@bp.get("/challenges/dom/d2d")
def d2d():
    body = """
<h1>Adjacent Injection <small style="font-size:.7rem;color:#8b949e">[d2d]</small></h1>
<p class="desc">
  A notification widget appends user-controlled HTML to a container using
  <code>insertAdjacentHTML('beforeend', …)</code>. No sanitisation is applied.
  This sink is often missed by rules targeting only <code>innerHTML</code>.
</p>
<div class="result" id="notifications">
  <em style="color:#8b949e">Notifications appear here.</em>
</div>
<p class="flag-hint">
  Source: <code>URLSearchParams.get('append')</code>.
  Sink: <code>element.insertAdjacentHTML('beforeend', …)</code>.<br>
  Payload: <code>fetch('/api/catch?cid=d2d&amp;player=NAME&amp;flag=STING{d2d_insertadjacenthtml}')</code>
</p>
<script>
  const data = new URLSearchParams(location.search).get('append');
  if (data) {
    document.getElementById('notifications').insertAdjacentHTML('beforeend', data);
  }
</script>
"""
    return _page("d2d: Adjacent Injection", body)
