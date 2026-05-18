# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""GraphQL XSS challenges — Tier 9 (g1a–g1c)."""
from __future__ import annotations
import re

from flask import Blueprint, request, redirect

from core.db.storedb import store_get, store_insert

bp = Blueprint("graphql_challenges", __name__)


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
  .result{{margin-top:24px;padding:16px;background:#161b22;border:1px solid #30363d;border-radius:6px}}
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
# Shared helpers
# ---------------------------------------------------------------------------

def _gql_ok(data: dict) -> dict:
    return {"data": data}


def _gql_err(message: str) -> dict:
    return {"errors": [{"message": message}]}


def _extract_string_arg(query: str, field: str, arg: str) -> str | None:
    """Pull a string argument from a simple GraphQL query.

    Matches: {field(arg: "VALUE")} — handles basic JSON string escapes.
    Returns None when the field/arg is not found.
    """
    pattern = (
        rf'{re.escape(field)}\s*\(\s*{re.escape(arg)}\s*:\s*'
        rf'"((?:[^"\\]|\\.)*)"\s*\)'
    )
    m = re.search(pattern, query, re.DOTALL)
    if m:
        return m.group(1).replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
    return None


def _introspection(query_type: str, types: list[dict]) -> dict:
    return _gql_ok({
        "__schema": {
            "queryType": {"name": query_type},
            "types": types,
        }
    })


# ---------------------------------------------------------------------------
# G1A — Schema Scout: search(q: String!) reflected → innerHTML
# ---------------------------------------------------------------------------

_G1A_TYPES = [
    {
        "name": "Query", "kind": "OBJECT",
        "fields": [{
            "name": "search",
            "args": [{"name": "q", "type": {"kind": "SCALAR", "name": "String", "ofType": None}}],
            "type": {"kind": "SCALAR", "name": "String", "ofType": None},
        }],
    }
]


@bp.get("/challenges/graphql/g1a")
def g1a_page():
    body = """
<h1>Schema Scout <small style="font-size:.7rem;color:#8b949e">[g1a]</small></h1>
<p class="desc">A search API powered by GraphQL. Introspection is enabled — discover the schema and find the injectable string field.</p>
<input id="q" placeholder="Search term…" autocomplete="off" style="margin-bottom:8px">
<button onclick="doSearch()">Search</button>
<div class="result" id="output"><em style="color:#8b949e">Results appear here.</em></div>
<p class="flag-hint">
  Endpoint: <code>POST /challenges/graphql/g1a/graphql</code>. Try introspection first,
  then find the string-typed field and inject.<br>
  Payload: <code>fetch('/api/catch?cid=g1a&amp;player=NAME&amp;flag=STING{g1a_graphql_reflected}')</code>
</p>
<script>
  async function doSearch() {
    const q = document.getElementById('q').value;
    const resp = await fetch('/challenges/graphql/g1a/graphql', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: '{search(q: "' + q + '")}'})
    });
    const data = await resp.json();
    const result = data?.data?.search ?? data?.errors?.[0]?.message ?? '(no result)';
    document.getElementById('output').innerHTML = result;
  }
  const q = new URLSearchParams(location.search).get('q');
  if (q) { document.getElementById('q').value = q; doSearch(); }
</script>
"""
    return _page("g1a: Schema Scout", body)


@bp.post("/challenges/graphql/g1a/graphql")
def g1a_graphql():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")

    if "__schema" in query or "__type" in query:
        return _introspection("Query", _G1A_TYPES)

    val = _extract_string_arg(query, "search", "q")
    if val is not None:
        return _gql_ok({"search": val})

    return _gql_err("Unknown field or invalid query syntax")


# ---------------------------------------------------------------------------
# G1B — Mutation Station: createComment(body) stored → board raw → admin bot
# ---------------------------------------------------------------------------

_G1B_TYPES = [
    {
        "name": "Query", "kind": "OBJECT",
        "fields": [{
            "name": "comments",
            "args": [],
            "type": {"kind": "LIST", "name": None,
                     "ofType": {"kind": "OBJECT", "name": "Comment", "ofType": None}},
        }],
    },
    {
        "name": "Mutation", "kind": "OBJECT",
        "fields": [{
            "name": "createComment",
            "args": [{"name": "body", "type": {"kind": "SCALAR", "name": "String", "ofType": None}}],
            "type": {"kind": "OBJECT", "name": "Comment", "ofType": None},
        }],
    },
    {
        "name": "Comment", "kind": "OBJECT",
        "fields": [
            {"name": "id",   "args": [], "type": {"kind": "SCALAR", "name": "ID",     "ofType": None}},
            {"name": "body", "args": [], "type": {"kind": "SCALAR", "name": "String", "ofType": None}},
        ],
    },
]


@bp.get("/challenges/graphql/g1b")
def g1b_page():
    body = """
<h1>Mutation Station <small style="font-size:.7rem;color:#8b949e">[g1b]</small></h1>
<p class="desc">A comment board backed by a GraphQL API. Post a payload — the admin bot reads the board every 30 seconds.</p>
<form method="POST" action="/challenges/graphql/g1b/comment">
  <textarea name="body" rows="3" placeholder="Write a comment…"></textarea>
  <button type="submit">Post via form</button>
</form>
<p class="flag-hint">
  Or send a GraphQL mutation directly: <code>POST /challenges/graphql/g1b/graphql</code> (introspection enabled).<br>
  Payload: <code>fetch('/api/catch?cid=g1b&amp;player=NAME&amp;flag=STING{g1b_graphql_stored}')</code>
</p>
<p><a href="/challenges/graphql/g1b/board" style="color:#58a6ff">View board &#8594;</a></p>
"""
    return _page("g1b: Mutation Station", body)


@bp.post("/challenges/graphql/g1b/comment")
def g1b_comment_post():
    body = request.form.get("body", "")
    if body:
        store_insert("gql_comments", body=body)
    return redirect("/challenges/graphql/g1b/board")


@bp.post("/challenges/graphql/g1b/graphql")
def g1b_graphql():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")

    if "__schema" in query or "__type" in query:
        return _introspection("Query", _G1B_TYPES)

    # Mutation: createComment(body: "...")
    val = _extract_string_arg(query, "createComment", "body")
    if val is not None:
        rid = store_insert("gql_comments", body=val)
        return _gql_ok({"createComment": {"id": str(rid), "body": val}})

    # Query: {comments{body}}
    if "comments" in query:
        rows = store_get("gql_comments")
        return _gql_ok({"comments": [{"id": str(r["id"]), "body": r["body"]} for r in rows]})

    return _gql_err("Unknown operation")


@bp.get("/challenges/graphql/g1b/board")
def g1b_board():
    rows = store_get("gql_comments")
    cards = "".join(
        f'<div class="card">{r["body"]}</div>'
        for r in rows
    ) or "<p style='color:#8b949e'>No comments yet.</p>"
    body = f"""
<h1>Comment Board <small style="font-size:.7rem;color:#8b949e">[g1b]</small></h1>
<p class="desc">Comments posted via GraphQL mutation — rendered without sanitisation.</p>
{cards}
<p style="margin-top:16px"><a href="/challenges/graphql/g1b" style="color:#58a6ff">&#8592; Post a comment</a></p>
"""
    return _page("g1b: Comment Board", body)


# ---------------------------------------------------------------------------
# G1C — Error Echo: debug(msg: String!) reflected in errors[0].message → innerHTML
# ---------------------------------------------------------------------------

_G1C_TYPES = [
    {
        "name": "Query", "kind": "OBJECT",
        "fields": [{
            "name": "debug",
            "args": [{"name": "msg", "type": {"kind": "SCALAR", "name": "String", "ofType": None}}],
            "type": {"kind": "SCALAR", "name": "String", "ofType": None},
        }],
    }
]


@bp.get("/challenges/graphql/g1c")
def g1c_page():
    body = """
<h1>Error Echo <small style="font-size:.7rem;color:#8b949e">[g1c]</small></h1>
<p class="desc">A debug field that always fails validation — and echoes your message verbatim inside the GraphQL error response. The client renders <code>errors[0].message</code> via <code>innerHTML</code>.</p>
<input id="msg" placeholder="Debug message…" autocomplete="off" style="margin-bottom:8px">
<button onclick="doDebug()">Send</button>
<div class="result" id="output"><em style="color:#8b949e">Error output appears here.</em></div>
<p class="flag-hint">
  Endpoint: <code>POST /challenges/graphql/g1c/graphql</code>. The <code>debug</code> field always
  returns a validation error containing your message. Sink: <code>errors[0].message → innerHTML</code>.<br>
  Payload: <code>fetch('/api/catch?cid=g1c&amp;player=NAME&amp;flag=STING{g1c_graphql_error_echo}')</code>
</p>
<script>
  async function doDebug() {
    const msg = document.getElementById('msg').value;
    const resp = await fetch('/challenges/graphql/g1c/graphql', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({query: '{debug(msg: "' + msg + '")}'})
    });
    const data = await resp.json();
    const errMsg = data?.errors?.[0]?.message ?? data?.data?.debug ?? '(no response)';
    document.getElementById('output').innerHTML = errMsg;
  }
  const msg = new URLSearchParams(location.search).get('msg');
  if (msg) { document.getElementById('msg').value = msg; doDebug(); }
</script>
"""
    return _page("g1c: Error Echo", body)


@bp.post("/challenges/graphql/g1c/graphql")
def g1c_graphql():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")

    if "__schema" in query or "__type" in query:
        return _introspection("Query", _G1C_TYPES)

    val = _extract_string_arg(query, "debug", "msg")
    if val is not None:
        return _gql_err(f"Debug validation failed: {val}")

    return _gql_err("Parse error: malformed query")
