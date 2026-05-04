# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Blind XSS challenges — Tier 5 (b1a–b1e)."""
from __future__ import annotations

from flask import Blueprint, request, redirect, make_response

from core.db.storedb import store_get, store_insert

bp = Blueprint("blind", __name__)


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
  .card{{margin-top:16px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px}}
  .card .meta{{font-size:.75rem;color:#8b949e;margin-bottom:4px}}
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


def _admin_page(title: str, body: str) -> str:
    """Minimal admin panel page shell — no back link, different accent."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Admin — {title}</title>
<style>
  body{{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;padding:32px;max-width:900px;margin:0 auto}}
  h1{{font-size:1.2rem;color:#d29922}}
  .card{{margin-top:12px;padding:14px;background:#161b22;border:1px solid #30363d;border-radius:6px}}
  .meta{{font-size:.75rem;color:#8b949e;margin-bottom:4px}}
</style>
</head>
<body>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# B1A — Support ticket
# ---------------------------------------------------------------------------

@bp.get("/challenges/blind/b1a")
def b1a_form():
    body = """
<h1>Support Ticket <small style="font-size:.7rem;color:#8b949e">[b1a]</small></h1>
<p class="desc">Submit a support ticket. The admin bot reads all open tickets every 30 seconds.</p>
<form method="POST" action="/challenges/blind/b1a">
  <input name="author" placeholder="Your name" autocomplete="off" style="margin-bottom:8px">
  <input name="subject" placeholder="Subject" autocomplete="off" style="margin-bottom:8px">
  <textarea name="body" rows="4" placeholder="Describe your issue…"></textarea>
  <button type="submit">Submit ticket</button>
</form>
<p class="flag-hint">Your payload executes in the admin's browser when they review the tickets.
  Use: <code>fetch('/api/catch?cid=b1a&amp;player=NAME&amp;flag=STING{b1a_blind_support_ticket}')</code></p>
<p><a href="/challenges/blind/b1a/admin" style="color:#58a6ff;font-size:.8rem">Admin panel &#8594;</a></p>
"""
    return _page("b1a: Support Ticket", body)


@bp.post("/challenges/blind/b1a")
def b1a_post():
    author = request.form.get("author", "anon")
    subject = request.form.get("subject", "(no subject)")
    body = request.form.get("body", "")
    if body:
        store_insert("tickets", author=author, subject=subject, body=body)
    return _page("b1a: Submitted", """
<h1>Ticket Submitted</h1>
<p>Your ticket has been received. The admin will review it shortly.</p>
<p><a href="/challenges/blind/b1a" style="color:#58a6ff">&#8592; Submit another</a></p>
""")


@bp.get("/challenges/blind/b1a/admin")
def b1a_admin():
    tickets = store_get("tickets")
    cards = "".join(
        f'<div class="card"><div class="meta">#{t["id"]} — {t["author"]} — {t["subject"]}</div>{t["body"]}</div>'
        for t in tickets if t.get("open")
    ) or "<p style='color:#8b949e'>No open tickets.</p>"
    body = f"<h1>Admin: Open Tickets [b1a]</h1>{cards}"
    return _admin_page("Open Tickets", body)


# ---------------------------------------------------------------------------
# B1B — Feedback form
# ---------------------------------------------------------------------------

@bp.get("/challenges/blind/b1b")
def b1b_form():
    body = """
<h1>Feedback Form <small style="font-size:.7rem;color:#8b949e">[b1b]</small></h1>
<p class="desc">Submit feedback. An admin reviews submissions in a separate panel every 30 seconds.</p>
<form method="POST" action="/challenges/blind/b1b">
  <input name="name" placeholder="Your name" autocomplete="off" style="margin-bottom:8px">
  <textarea name="message" rows="4" placeholder="Your feedback…"></textarea>
  <button type="submit">Send feedback</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=b1b&amp;player=NAME&amp;flag=STING{b1b_blind_feedback}')</code></p>
<p><a href="/challenges/blind/b1b/admin" style="color:#58a6ff;font-size:.8rem">Admin panel &#8594;</a></p>
"""
    return _page("b1b: Feedback Form", body)


@bp.post("/challenges/blind/b1b")
def b1b_post():
    name = request.form.get("name", "anon")
    message = request.form.get("message", "")
    if message:
        store_insert("feedback", name=name, message=message)
    return _page("b1b: Thanks", """
<h1>Feedback received</h1>
<p>Thank you. An admin will review your feedback soon.</p>
<p><a href="/challenges/blind/b1b" style="color:#58a6ff">&#8592; Send more</a></p>
""")


@bp.get("/challenges/blind/b1b/admin")
def b1b_admin():
    rows = store_get("feedback")
    cards = "".join(
        f'<div class="card"><div class="meta">#{r["id"]} — {r["name"]}</div>{r["message"]}</div>'
        for r in rows
    ) or "<p style='color:#8b949e'>No feedback yet.</p>"
    body = f"<h1>Admin: Feedback [b1b]</h1>{cards}"
    return _admin_page("Feedback", body)


# ---------------------------------------------------------------------------
# B1C — User-Agent log viewer
# ---------------------------------------------------------------------------

@bp.get("/challenges/blind/b1c")
def b1c_form():
    # Primary injection via User-Agent header (blind); also accept ?ua= for tooling
    ua = request.args.get("ua") or request.headers.get("User-Agent", "")
    if ua:
        store_insert("ua_log", user_agent=ua)
    body = """
<h1>Log Viewer <small style="font-size:.7rem;color:#8b949e">[b1c]</small></h1>
<p class="desc">This page logs the visitor's <code>User-Agent</code> string (or the <code>ua=</code> query param). The admin reviews the log.</p>
<form method="GET">
  <input name="ua" placeholder="Custom user-agent string to log…" autocomplete="off">
  <button type="submit">Log it</button>
</form>
<p class="flag-hint">The admin panel renders User-Agent / ua= strings raw.
  Use: <code>fetch('/api/catch?cid=b1c&amp;player=NAME&amp;flag=STING{b1c_blind_useragent_log}')</code></p>
<p><a href="/challenges/blind/b1c/admin" style="color:#58a6ff">View log &#8594;</a></p>
"""
    return _page("b1c: Log Viewer", body)


@bp.get("/challenges/blind/b1c/admin")
def b1c_admin():
    rows = store_get("ua_log")
    cards = "".join(
        f'<div class="card"><div class="meta">#{r["id"]}</div>{r["user_agent"]}</div>'
        for r in rows
    ) or "<p style='color:#8b949e'>No log entries.</p>"
    body = f"<h1>Admin: UA Log [b1c]</h1>{cards}"
    return _admin_page("UA Log", body)


# ---------------------------------------------------------------------------
# B1D — Contact form (name field)
# ---------------------------------------------------------------------------

@bp.get("/challenges/blind/b1d")
def b1d_form():
    body = """
<h1>Contact Name <small style="font-size:.7rem;color:#8b949e">[b1d]</small></h1>
<p class="desc">A contact form. The <em>name</em> field is echoed in the admin's inbox without encoding.</p>
<form method="POST" action="/challenges/blind/b1d">
  <input name="name" placeholder="Your name" autocomplete="off" style="margin-bottom:8px">
  <input name="email" placeholder="Email" autocomplete="off" style="margin-bottom:8px">
  <textarea name="message" rows="3" placeholder="Your message…"></textarea>
  <button type="submit">Send</button>
</form>
<p class="flag-hint">The name field is the injection point. Admin panel renders it raw.
  Use: <code>fetch('/api/catch?cid=b1d&amp;player=NAME&amp;flag=STING{b1d_blind_contact_name}')</code></p>
<p><a href="/challenges/blind/b1d/admin" style="color:#58a6ff;font-size:.8rem">Admin panel &#8594;</a></p>
"""
    return _page("b1d: Contact Form", body)


@bp.post("/challenges/blind/b1d")
def b1d_post():
    name = request.form.get("name", "anon")
    email = request.form.get("email", "")
    message = request.form.get("message", "")
    store_insert("contacts", name=name, email=email, message=message)
    return _page("b1d: Sent", """
<h1>Message sent</h1>
<p>The admin will be in touch.</p>
<p><a href="/challenges/blind/b1d" style="color:#58a6ff">&#8592; Back</a></p>
""")


@bp.get("/challenges/blind/b1d/admin")
def b1d_admin():
    rows = store_get("contacts")
    cards = "".join(
        f'<div class="card"><div class="meta">#{r["id"]} — {r["name"]} &lt;{r["email"]}&gt;</div>{r["message"]}</div>'
        for r in rows
    ) or "<p style='color:#8b949e'>No contacts.</p>"
    body = f"<h1>Admin: Contact Inbox [b1d]</h1>{cards}"
    return _admin_page("Contact Inbox", body)


# ---------------------------------------------------------------------------
# B1E — Cookie to admin panel
# ---------------------------------------------------------------------------

@bp.get("/challenges/blind/b1e")
def b1e_form():
    cookie_val = request.args.get("theme", "")
    resp = make_response(_page("b1e: Cookie Crumbles", f"""
<h1>Cookie Crumbles <small style="font-size:.7rem;color:#8b949e">[b1e]</small></h1>
<p class="desc">A page sets a <code>theme</code> cookie from a query parameter. The admin panel displays cookie values for debugging.</p>
<form method="GET">
  <input name="theme" placeholder="Enter a theme value…" autocomplete="off" value="{cookie_val}">
  <button type="submit">Set theme</button>
</form>
<p>Current <code>theme</code> param: <code>{cookie_val or '(none)'}</code></p>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=b1e&amp;player=NAME&amp;flag=STING{{b1e_blind_cookie}}')</code><br>
  The cookie value is stored in the DB and rendered in the admin panel.</p>
<p><a href="/challenges/blind/b1e/admin" style="color:#58a6ff">Admin panel &#8594;</a></p>
"""))
    if cookie_val:
        resp.set_cookie("theme", cookie_val)
        store_insert("cookie_debug", cookie_val=cookie_val)
    return resp


@bp.get("/challenges/blind/b1e/admin")
def b1e_admin():
    rows = store_get("cookie_debug")
    cards = "".join(
        f'<div class="card"><div class="meta">#{r["id"]}</div>{r["cookie_val"]}</div>'
        for r in rows
    ) or "<p style='color:#8b949e'>No cookie entries.</p>"
    body = f"<h1>Admin: Cookie Debug [b1e]</h1>{cards}"
    return _admin_page("Cookie Debug", body)
