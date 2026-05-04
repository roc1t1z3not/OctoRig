# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Template injection → XSS challenges — Tier 8 (t1a–t1d)."""
from __future__ import annotations
import re

from flask import Blueprint, request, render_template_string

bp = Blueprint("template", __name__)


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
  .result{{margin-top:24px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px;font-family:monospace}}
  a.back{{display:block;margin-top:24px;font-size:.82rem;color:#8b949e}}
  .flag-hint{{font-size:.75rem;color:#8b949e;margin-top:8px}}
  .tier-badge{{display:inline-block;background:#6e40c9;color:#fff;font-size:.7rem;padding:2px 8px;border-radius:4px;margin-bottom:12px}}
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""


# ---------------------------------------------------------------------------
# T1A — Jinja2 SSTI → XSS
# ---------------------------------------------------------------------------

@bp.get("/challenges/template/t1a")
def t1a():
    tmpl = request.args.get("tmpl", "Hello, World!")
    try:
        rendered = render_template_string(tmpl)
    except Exception as e:
        rendered = f"Template error: {e}"
    body = f"""
<h1>Jinja Sting <small style="font-size:.7rem;color:#8b949e">[t1a]</small></h1>
<span class="tier-badge">SSTI — Jinja2</span>
<p class="desc">The server renders the <code>tmpl=</code> parameter directly with <code>render_template_string()</code>.</p>
<form method="GET">
  <input name="tmpl" value="" placeholder="Enter a template…" autocomplete="off">
  <button type="submit">Render</button>
</form>
<div class="result">{rendered}</div>
<p class="flag-hint">Probe with <code>{{{{7*7}}}}</code>. If you get 49, you have SSTI. Escalate to XSS output.</p>
"""
    return _page("t1a: Jinja Sting", body)


# ---------------------------------------------------------------------------
# T1B — eval-based template evaluator → XSS
# ---------------------------------------------------------------------------

def _eval_template(text: str) -> str:
    """Replace {{expr}} with eval(expr) result — intentionally unsafe."""
    def replace_expr(m: re.Match) -> str:
        expr = m.group(1).strip()
        try:
            result = eval(expr)  # noqa: S307 — intentional for challenge
            return str(result)
        except Exception as e:
            return f"[error: {e}]"
    return re.sub(r'\{\{(.+?)\}\}', replace_expr, text)


@bp.get("/challenges/template/t1b")
def t1b():
    text = request.args.get("text", "Hello, {{1+1}}!")
    rendered = _eval_template(text)
    body = f"""
<h1>Twig Twist <small style="font-size:.7rem;color:#8b949e">[t1b]</small></h1>
<span class="tier-badge">SSTI — eval-based</span>
<p class="desc">A Python app mimicking Twig-style <code>{{'{{expr}}'}}</code> syntax. It evaluates expressions with <code>eval()</code>.</p>
<form method="GET">
  <input name="text" value="" placeholder="Enter text with {{{{expr}}}} blocks…" autocomplete="off">
  <button type="submit">Render</button>
</form>
<div class="result">{rendered}</div>
<p class="flag-hint">Expressions inside <code>{{'{{…}}'}}</code> are passed to <code>eval()</code>. Inject Python that outputs an XSS payload.</p>
"""
    return _page("t1b: Twig Twist", body)


# ---------------------------------------------------------------------------
# T1C — str.format() injection → XSS
# ---------------------------------------------------------------------------

@bp.get("/challenges/template/t1c")
def t1c():
    fmt = request.args.get("fmt", "Welcome, {name}!")
    try:
        rendered = fmt.format(name="guest", version="1.0")
    except Exception as e:
        rendered = f"Format error: {e}"
    body = f"""
<h1>Format String <small style="font-size:.7rem;color:#8b949e">[t1c]</small></h1>
<span class="tier-badge">SSTI — str.format()</span>
<p class="desc">A Python <code>str.format()</code> call with a user-controlled format string rendered into an HTML page.</p>
<form method="GET">
  <input name="fmt" value="" placeholder="e.g. Welcome, {{name}}!" autocomplete="off">
  <button type="submit">Render</button>
</form>
<div class="result">{rendered}</div>
<p class="flag-hint"><code>{{0.__class__}}</code> leaks Python internals through <code>str.format()</code>. Chain attribute traversal to output a <code>&lt;script&gt;</code> tag.</p>
"""
    return _page("t1c: Format String", body)


# ---------------------------------------------------------------------------
# T1D — render_template_string with POST body
# ---------------------------------------------------------------------------

@bp.route("/challenges/template/t1d", methods=["GET", "POST"])
def t1d():
    rendered = ""
    tmpl_val = ""
    if request.method == "POST":
        tmpl_val = request.form.get("template", "")
        try:
            rendered = render_template_string(tmpl_val)
        except Exception as e:
            rendered = f"Error: {e}"

    result_block = f'<div class="result">{rendered}</div>' if rendered else ""
    body = f"""
<h1>Server Echo <small style="font-size:.7rem;color:#8b949e">[t1d]</small></h1>
<span class="tier-badge">SSTI — render_template_string</span>
<p class="desc">A server-side rendering endpoint evaluates a POST <code>template</code> body and returns raw HTML.</p>
<form method="POST">
  <textarea name="template" rows="4" placeholder="Enter a Jinja2 template…">{tmpl_val}</textarea>
  <button type="submit">Render</button>
</form>
{result_block}
<p class="flag-hint">The template body is passed verbatim to <code>render_template_string()</code>. Escape the template context to inject arbitrary HTML.</p>
"""
    return _page("t1d: Server Echo", body)
