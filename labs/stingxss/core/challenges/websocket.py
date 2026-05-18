# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""WebSocket XSS challenges — Tier 10 (ws1a–ws1c).

HTTP page routes live in the `bp` blueprint.
WebSocket handlers (ws1a_ws, ws1b_ws, ws1c_ws) are plain functions;
register them in app.py with:
    sock.route('/challenges/ws/ws1a/ws')(ws1a_ws)
"""
from __future__ import annotations
import json

from flask import Blueprint

from core.db.storedb import store_get, store_insert

bp = Blueprint("websocket_challenges", __name__)


def _page(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>StingXSS — {title}</title>
<style>
  body{{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;padding:32px;max-width:720px;margin:0 auto}}
  h1{{font-size:1.4rem;margin-bottom:8px;color:#f78166}}
  .desc{{color:#8b949e;font-size:.9rem;margin-bottom:24px}}
  input{{background:#21262d;border:1px solid #30363d;color:#e6edf3;padding:8px 12px;border-radius:4px;font-size:.9rem;width:100%}}
  button{{background:#f78166;color:#0d1117;border:none;padding:8px 20px;border-radius:4px;cursor:pointer;font-weight:700;margin-top:8px}}
  .card{{margin-top:12px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px}}
  .result{{margin-top:24px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px;min-height:48px}}
  a.back{{display:block;margin-top:24px;font-size:.82rem;color:#8b949e}}
  .flag-hint{{font-size:.75rem;color:#8b949e;margin-top:8px}}
  code{{background:#21262d;padding:2px 6px;border-radius:3px;font-size:.85rem}}
  .status{{font-size:.75rem;color:#8b949e;margin-top:4px}}
</style>
{extra_head}
</head>
<body>
{body}
<a class="back" href="/">&#8592; Back to challenges</a>
</body>
</html>"""


# ---------------------------------------------------------------------------
# WS1A — Echo Chamber: raw message echoed → innerHTML
# ---------------------------------------------------------------------------

@bp.get("/challenges/ws/ws1a")
def ws1a_page():
    body = """
<h1>Echo Chamber <small style="font-size:.7rem;color:#8b949e">[ws1a]</small></h1>
<p class="desc">A real-time chat backed by WebSocket. The server echoes every message back verbatim. The client renders the echoed message via <code>innerHTML</code> — no sanitisation.</p>
<input id="msg" placeholder="Type a message…" autocomplete="off" style="margin-bottom:8px">
<button onclick="send()">Send</button>
<div class="result" id="output"><em style="color:#8b949e">Messages appear here.</em></div>
<p class="status" id="status">Connecting…</p>
<p class="flag-hint">
  WebSocket: <code>ws://host/challenges/ws/ws1a/ws</code>. Source: raw <code>event.data</code>.
  Sink: <code>element.innerHTML</code>.<br>
  Payload: <code>fetch('/api/catch?cid=ws1a&amp;player=NAME&amp;flag=STING{ws1a_websocket_echo}')</code>
</p>
<script>
  const ws = new WebSocket('ws://' + location.host + '/challenges/ws/ws1a/ws');
  ws.onopen  = () => document.getElementById('status').textContent = 'Connected';
  ws.onclose = () => document.getElementById('status').textContent = 'Disconnected';
  ws.onmessage = (e) => { document.getElementById('output').innerHTML = e.data; };
  function send() {
    const msg = document.getElementById('msg').value;
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  }
  document.getElementById('msg').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
</script>
"""
    return _page("ws1a: Echo Chamber", body)


def ws1a_ws(ws) -> None:
    """Raw echo — every message reflected unchanged."""
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            ws.send(data)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# WS1B — JSON Wire: JSON envelope echoed → .content rendered via innerHTML
# ---------------------------------------------------------------------------

@bp.get("/challenges/ws/ws1b")
def ws1b_page():
    body = """
<h1>JSON Wire <small style="font-size:.7rem;color:#8b949e">[ws1b]</small></h1>
<p class="desc">The chat protocol wraps messages in a JSON envelope: <code>{"type":"chat","content":"…"}</code>. The server echoes the raw frame. The client parses the envelope and renders <code>msg.content</code> via <code>innerHTML</code>.</p>
<input id="msg" placeholder="Type a message…" autocomplete="off" style="margin-bottom:8px">
<button onclick="send()">Send</button>
<div class="result" id="output"><em style="color:#8b949e">Messages appear here.</em></div>
<p class="status" id="status">Connecting…</p>
<p class="flag-hint">
  WebSocket: <code>ws://host/challenges/ws/ws1b/ws</code>.<br>
  Send a raw string and the server wraps it: <code>{"type":"chat","content":"YOUR INPUT"}</code>.<br>
  Sink: <code>JSON.parse(event.data).content → innerHTML</code>.<br>
  Payload: <code>fetch('/api/catch?cid=ws1b&amp;player=NAME&amp;flag=STING{ws1b_websocket_json}')</code>
</p>
<script>
  const ws = new WebSocket('ws://' + location.host + '/challenges/ws/ws1b/ws');
  ws.onopen  = () => document.getElementById('status').textContent = 'Connected';
  ws.onclose = () => document.getElementById('status').textContent = 'Disconnected';
  ws.onmessage = (e) => {
    try {
      const msg = JSON.parse(e.data);
      if (msg.type === 'chat') {
        document.getElementById('output').innerHTML = msg.content;
      }
    } catch(_) {
      document.getElementById('output').textContent = e.data;
    }
  };
  function send() {
    const content = document.getElementById('msg').value;
    if (ws.readyState === WebSocket.OPEN) ws.send(content);
  }
  document.getElementById('msg').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
</script>
"""
    return _page("ws1b: JSON Wire", body)


def ws1b_ws(ws) -> None:
    """Accept raw strings or JSON; always echo back as a JSON chat envelope."""
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            # If already a JSON chat envelope pass it through; otherwise wrap it
            try:
                parsed = json.loads(data)
                content = parsed.get("content", data) if isinstance(parsed, dict) else data
            except (json.JSONDecodeError, TypeError):
                content = data
            ws.send(json.dumps({"type": "chat", "content": content}))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# WS1C — Broadcast Booth: stored messages → board server-rendered raw → admin bot
# ---------------------------------------------------------------------------

@bp.get("/challenges/ws/ws1c")
def ws1c_page():
    body = """
<h1>Broadcast Booth <small style="font-size:.7rem;color:#8b949e">[ws1c]</small></h1>
<p class="desc">Messages sent via WebSocket are persisted and broadcast to every new client on connect. The admin bot reads the board every 30 seconds.</p>
<input id="msg" placeholder="Broadcast a message…" autocomplete="off" style="margin-bottom:8px">
<button onclick="send()">Broadcast</button>
<div id="feed" style="margin-top:16px"></div>
<p class="status" id="status">Connecting…</p>
<p class="flag-hint">
  WebSocket: <code>ws://host/challenges/ws/ws1c/ws</code>. Payload must survive storage and fire when
  the admin visits the board.<br>
  Payload: <code>fetch('/api/catch?cid=ws1c&amp;player=NAME&amp;flag=STING{ws1c_websocket_stored}')</code>
</p>
<p><a href="/challenges/ws/ws1c/board" style="color:#58a6ff">View board &#8594;</a></p>
<script>
  const ws = new WebSocket('ws://' + location.host + '/challenges/ws/ws1c/ws');
  ws.onopen  = () => document.getElementById('status').textContent = 'Connected';
  ws.onclose = () => document.getElementById('status').textContent = 'Disconnected';
  ws.onmessage = (e) => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = e.data;
    document.getElementById('feed').appendChild(div);
  };
  function send() {
    const msg = document.getElementById('msg').value;
    if (ws.readyState === WebSocket.OPEN && msg.trim()) ws.send(msg);
  }
  document.getElementById('msg').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
  });
</script>
"""
    return _page("ws1c: Broadcast Booth", body)


@bp.get("/challenges/ws/ws1c/board")
def ws1c_board():
    messages = store_get("ws_messages")
    cards = "".join(
        f'<div class="card">{m["content"]}</div>'
        for m in messages
    ) or "<p style='color:#8b949e'>No broadcasts yet.</p>"
    body = f"""
<h1>Broadcast Board <small style="font-size:.7rem;color:#8b949e">[ws1c]</small></h1>
<p class="desc">All WebSocket broadcasts — persisted and rendered without sanitisation.</p>
{cards}
<p style="margin-top:16px"><a href="/challenges/ws/ws1c" style="color:#58a6ff">&#8592; Broadcast a message</a></p>
"""
    return _page("ws1c: Broadcast Board", body)


def ws1c_ws(ws) -> None:
    """Send stored history to new client, then persist and echo new messages."""
    # Replay last 10 stored messages to new client
    try:
        for row in store_get("ws_messages")[-10:]:
            ws.send(row["content"])
    except Exception:
        pass

    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            if data.strip():
                store_insert("ws_messages", content=data)
                ws.send(data)
    except Exception:
        pass
