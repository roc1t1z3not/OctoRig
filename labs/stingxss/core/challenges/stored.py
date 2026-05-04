# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Stored XSS challenges — Tier 3 (s1a–s1f)."""
from __future__ import annotations
import json

from flask import Blueprint, request, redirect

from core.db.storedb import store_get, store_insert, store_update, store_get_where

bp = Blueprint("stored", __name__)


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
  .card .author{{font-size:.75rem;color:#8b949e;margin-bottom:4px}}
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
# S1A — Guestbook (raw stored message → board)
# ---------------------------------------------------------------------------

@bp.get("/challenges/stored/s1a")
def s1a_form():
    body = """
<h1>Guestbook <small style="font-size:.7rem;color:#8b949e">[s1a]</small></h1>
<p class="desc">Sign the public guestbook. Messages are stored and shown to every visitor (including the admin bot).</p>
<form method="POST" action="/challenges/stored/s1a">
  <input name="name" placeholder="Your name" autocomplete="off" style="margin-bottom:8px">
  <textarea name="message" rows="3" placeholder="Leave a message…"></textarea>
  <button type="submit">Sign</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1a&amp;player=NAME&amp;flag=STING{s1a_stored_guestbook}')</code></p>
<p><a href="/challenges/stored/s1a/board" style="color:#58a6ff">View guestbook board &#8594;</a></p>
"""
    return _page("s1a: Guestbook", body)


@bp.post("/challenges/stored/s1a")
def s1a_post():
    name = request.form.get("name", "Anonymous")
    message = request.form.get("message", "")
    if message:
        store_insert("guestbook", name=name, message=message)
    return redirect("/challenges/stored/s1a/board")


@bp.get("/challenges/stored/s1a/board")
def s1a_board():
    entries = store_get("guestbook")
    cards = "".join(
        f'<div class="card"><div class="author">{e["name"]}</div>{e["message"]}</div>'
        for e in entries
    ) or "<p style='color:#8b949e'>No entries yet.</p>"
    body = f"""
<h1>Guestbook Board <small style="font-size:.7rem;color:#8b949e">[s1a]</small></h1>
{cards}
<p style="margin-top:16px"><a href="/challenges/stored/s1a" style="color:#58a6ff">&#8592; Sign the guestbook</a></p>
"""
    return _page("s1a: Guestbook Board", body)


# ---------------------------------------------------------------------------
# S1B — Forum post
# ---------------------------------------------------------------------------

@bp.get("/challenges/stored/s1b")
def s1b_form():
    body = """
<h1>Forum <small style="font-size:.7rem;color:#8b949e">[s1b]</small></h1>
<p class="desc">Post a message to the forum. The admin bot reads the board every 30 seconds.</p>
<form method="POST" action="/challenges/stored/s1b">
  <input name="author" placeholder="Username" autocomplete="off" style="margin-bottom:8px">
  <textarea name="body" rows="4" placeholder="Write your post…"></textarea>
  <button type="submit">Post</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1b&amp;player=NAME&amp;flag=STING{s1b_stored_forum}')</code></p>
<p><a href="/challenges/stored/s1b/board" style="color:#58a6ff">View forum board &#8594;</a></p>
"""
    return _page("s1b: Forum", body)


@bp.post("/challenges/stored/s1b")
def s1b_post():
    author = request.form.get("author", "anon")
    body = request.form.get("body", "")
    if body:
        store_insert("forum_posts", author=author, body=body)
    return redirect("/challenges/stored/s1b/board")


@bp.get("/challenges/stored/s1b/board")
def s1b_board():
    posts = store_get("forum_posts")
    cards = "".join(
        f'<div class="card"><div class="author">{p["author"]}</div>{p["body"]}</div>'
        for p in posts
    ) or "<p style='color:#8b949e'>No posts yet.</p>"
    body = f"""
<h1>Forum Board <small style="font-size:.7rem;color:#8b949e">[s1b]</small></h1>
{cards}
<p style="margin-top:16px"><a href="/challenges/stored/s1b" style="color:#58a6ff">&#8592; Write a post</a></p>
"""
    return _page("s1b: Forum Board", body)


# ---------------------------------------------------------------------------
# S1C — Product review
# ---------------------------------------------------------------------------

@bp.get("/challenges/stored/s1c")
def s1c_form():
    body = """
<h1>Product Review <small style="font-size:.7rem;color:#8b949e">[s1c]</small></h1>
<p class="desc">Write a review for Widget Pro. Reviews appear on the product page visited by the admin bot.</p>
<form method="POST" action="/challenges/stored/s1c">
  <input name="author" placeholder="Your name" autocomplete="off" style="margin-bottom:8px">
  <textarea name="body" rows="3" placeholder="Your review…"></textarea>
  <button type="submit">Submit review</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1c&amp;player=NAME&amp;flag=STING{s1c_stored_review}')</code></p>
<p><a href="/challenges/stored/s1c/reviews" style="color:#58a6ff">View all reviews &#8594;</a></p>
"""
    return _page("s1c: Product Review", body)


@bp.post("/challenges/stored/s1c")
def s1c_post():
    author = request.form.get("author", "anon")
    body = request.form.get("body", "")
    if body:
        store_insert("reviews", author=author, body=body)
    return redirect("/challenges/stored/s1c/reviews")


@bp.get("/challenges/stored/s1c/reviews")
def s1c_reviews():
    reviews = store_get("reviews")
    cards = "".join(
        f'<div class="card"><div class="author">{r["author"]}</div>{r["body"]}</div>'
        for r in reviews
    ) or "<p style='color:#8b949e'>No reviews yet.</p>"
    body = f"""
<h1>Widget Pro — Reviews <small style="font-size:.7rem;color:#8b949e">[s1c]</small></h1>
{cards}
<p style="margin-top:16px"><a href="/challenges/stored/s1c" style="color:#58a6ff">&#8592; Write a review</a></p>
"""
    return _page("s1c: Reviews", body)


# ---------------------------------------------------------------------------
# S1D — Profile bio
# ---------------------------------------------------------------------------

@bp.get("/challenges/stored/s1d")
def s1d_form():
    body = """
<h1>Profile Bio <small style="font-size:.7rem;color:#8b949e">[s1d]</small></h1>
<p class="desc">Create or update a public profile. The admin bot visits all profile pages.</p>
<form method="POST" action="/challenges/stored/s1d">
  <input name="username" placeholder="Username" autocomplete="off" style="margin-bottom:8px">
  <textarea name="bio" rows="3" placeholder="Write your bio…"></textarea>
  <button type="submit">Save profile</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1d&amp;player=NAME&amp;flag=STING{s1d_stored_profile}')</code></p>
"""
    return _page("s1d: Profile Bio", body)


@bp.post("/challenges/stored/s1d")
def s1d_post():
    username = request.form.get("username", "")
    bio = request.form.get("bio", "")
    if not username:
        return redirect("/challenges/stored/s1d")
    existing = store_get_where("profiles", "username=?", (username,))
    if existing:
        from core.db.storedb import store_update
        store_update("profiles", "bio=?", "username=?", (bio, username))
    else:
        store_insert("profiles", username=username, bio=bio)
    return redirect(f"/challenges/stored/s1d/profile/{username}")


@bp.get("/challenges/stored/s1d/profile/<username>")
def s1d_profile(username: str):
    rows = store_get_where("profiles", "username=?", (username,))
    if not rows:
        return _page("s1d: Profile", "<h1>Profile not found</h1>"), 404
    row = rows[0]
    body = f"""
<h1>Profile: {row["username"]} <small style="font-size:.7rem;color:#8b949e">[s1d]</small></h1>
<div class="card">{row["bio"]}</div>
<p style="margin-top:16px"><a href="/challenges/stored/s1d" style="color:#58a6ff">&#8592; Edit profile</a></p>
"""
    return _page(f"s1d: {username}", body)


# ---------------------------------------------------------------------------
# S1E — Markdown notes (HTML injection via raw HTML pass-through)
# ---------------------------------------------------------------------------

def _render_markdown(text: str) -> str:
    """Extremely minimal Markdown: convert **bold**, *italic*, newlines.
    Raw HTML is passed through untouched — that's the vulnerability."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = text.replace("\n", "<br>")
    return text  # raw HTML allowed — intentional


@bp.get("/challenges/stored/s1e")
def s1e_form():
    body = """
<h1>Markdown Notes <small style="font-size:.7rem;color:#8b949e">[s1e]</small></h1>
<p class="desc">A note-taking app that renders Markdown. The renderer passes raw HTML through untouched.</p>
<form method="POST" action="/challenges/stored/s1e">
  <input name="author" placeholder="Author" autocomplete="off" style="margin-bottom:8px">
  <textarea name="body" rows="5" placeholder="Write in Markdown… or raw HTML"></textarea>
  <button type="submit">Save note</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1e&amp;player=NAME&amp;flag=STING{s1e_stored_markdown}')</code></p>
<p><a href="/challenges/stored/s1e/board" style="color:#58a6ff">View notes &#8594;</a></p>
"""
    return _page("s1e: Markdown Notes", body)


@bp.post("/challenges/stored/s1e")
def s1e_post():
    author = request.form.get("author", "anon")
    body = request.form.get("body", "")
    if body:
        store_insert("notes", author=author, body=body)
    return redirect("/challenges/stored/s1e/board")


@bp.get("/challenges/stored/s1e/board")
def s1e_board():
    notes = store_get("notes")
    cards = "".join(
        f'<div class="card"><div class="author">{n["author"]}</div>{_render_markdown(n["body"])}</div>'
        for n in notes
    ) or "<p style='color:#8b949e'>No notes yet.</p>"
    body = f"""
<h1>Notes Board <small style="font-size:.7rem;color:#8b949e">[s1e]</small></h1>
{cards}
<p style="margin-top:16px"><a href="/challenges/stored/s1e" style="color:#58a6ff">&#8592; Write a note</a></p>
"""
    return _page("s1e: Notes Board", body)


# ---------------------------------------------------------------------------
# S1F — JSON feed (title field → innerHTML client-side)
# ---------------------------------------------------------------------------

@bp.get("/challenges/stored/s1f")
def s1f_form():
    body = """
<h1>JSON Feed <small style="font-size:.7rem;color:#8b949e">[s1f]</small></h1>
<p class="desc">Submit a news item. The frontend fetches the JSON feed and renders titles via <code>innerHTML</code>.</p>
<form method="POST" action="/challenges/stored/s1f">
  <input name="title" placeholder="Headline" autocomplete="off" style="margin-bottom:8px">
  <textarea name="content" rows="3" placeholder="Article body…"></textarea>
  <button type="submit">Publish</button>
</form>
<p class="flag-hint">Payload: <code>fetch('/api/catch?cid=s1f&amp;player=NAME&amp;flag=STING{s1f_stored_json_feed}')</code></p>
<p><a href="/challenges/stored/s1f/board" style="color:#58a6ff">View feed &#8594;</a></p>
"""
    return _page("s1f: JSON Feed", body)


@bp.post("/challenges/stored/s1f")
def s1f_post():
    title = request.form.get("title", "")
    content = request.form.get("content", "")
    if title:
        store_insert("feed_items", title=title, content=content)
    return redirect("/challenges/stored/s1f/board")


@bp.get("/challenges/stored/s1f/feed.json")
def s1f_feed():
    items = store_get("feed_items")
    from flask import Response
    return Response(json.dumps(items), mimetype="application/json")


@bp.get("/challenges/stored/s1f/board")
def s1f_board():
    items = store_get("feed_items")
    # Render server-side too so HTTP-layer scanners can detect stored XSS.
    # The client-side JS re-renders via fetch+innerHTML — that's the actual vuln.
    ssr_cards = "".join(
        f'<div class="card ssr-item" style="display:none"><strong>{it["title"]}</strong><p>{it["content"]}</p></div>'
        for it in items
    ) if items else ""
    body = f"""
<h1>News Feed <small style="font-size:.7rem;color:#8b949e">[s1f]</small></h1>
<div id="feed"><em style="color:#8b949e">Loading…</em></div>
{ssr_cards}
<p style="margin-top:16px"><a href="/challenges/stored/s1f" style="color:#58a6ff">&#8592; Publish</a></p>
<script>
fetch('/challenges/stored/s1f/feed.json')
  .then(r=>r.json())
  .then(items=>{{
    const feed=document.getElementById('feed');
    feed.innerHTML='';
    items.forEach(item=>{{
      const div=document.createElement('div');
      div.className='card';
      div.innerHTML='<strong>'+item.title+'</strong><p>'+item.content+'</p>';
      feed.appendChild(div);
    }});
  }});
</script>
"""
    return _page("s1f: News Feed", body)
