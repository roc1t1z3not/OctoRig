# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Challenge registry and scoring store."""
from __future__ import annotations

CHALLENGES: list[dict] = [

    # ── Tier 1 — Reflected XSS (Basic) ───────────────────────────────────────
    dict(challenge_id="r1a", tier=1, title="Hello, Hacker",
         description="A search box that reflects your query back onto the page without any encoding.",
         hint="The q= parameter lands raw in the HTML. Inject a script tag.",
         technique="Reflected — raw param", points=100,
         flag="STING{r1a_raw_reflected}",
         endpoint="/challenges/reflected/r1a"),

    dict(challenge_id="r1b", tier=1, title="Attribute Escape",
         description="Your input lands inside an HTML attribute value. Break out of it.",
         hint="The value is wrapped in double quotes. Close the attribute and add an event handler.",
         technique="Reflected — attribute context", points=100,
         flag="STING{r1b_attribute_escape}",
         endpoint="/challenges/reflected/r1b"),

    dict(challenge_id="r1c", tier=1, title="Tag Soup",
         description="Input is injected directly between two tags without encoding.",
         hint="You are already inside the body — no need to break out of a tag first.",
         technique="Reflected — inner HTML", points=100,
         flag="STING{r1c_inner_html}",
         endpoint="/challenges/reflected/r1c"),

    dict(challenge_id="r1d", tier=1, title="Error Page",
         description="A 404-style error page that echoes the requested path back to the user.",
         hint="The path segment is reflected in the error message without encoding.",
         technique="Reflected — URL path", points=100,
         flag="STING{r1d_url_path_reflected}",
         endpoint="/challenges/reflected/r1d"),

    dict(challenge_id="r1e", tier=1, title="Script Context",
         description="Your input is interpolated directly into an inline script block.",
         hint="You are already inside a script block. No new tags needed — just break the string with a quote.",
         technique="Reflected — JS string context", points=100,
         flag="STING{r1e_js_string_context}",
         endpoint="/challenges/reflected/r1e"),

    dict(challenge_id="r1f", tier=1, title="Header Echo",
         description="The server reflects the value of a custom HTTP header back in the response body.",
         hint="Send an X-Custom-Name header. Its value appears verbatim in the page.",
         technique="Reflected — HTTP header", points=100,
         flag="STING{r1f_header_reflected}",
         endpoint="/challenges/reflected/r1f"),

    # ── Tier 2 — Reflected XSS (Filtered) ────────────────────────────────────
    dict(challenge_id="r2a", tier=2, title="Tag Stripper",
         description="The server strips script tags from input before reflecting it.",
         hint="Other tags execute JavaScript too. Try img, svg, or body event handlers.",
         technique="Reflected — script-tag filter bypass", points=250,
         flag="STING{r2a_script_tag_stripped}",
         endpoint="/challenges/reflected/r2a"),

    dict(challenge_id="r2b", tier=2, title="Quote Blocker",
         description="Single and double quotes are removed from the input before reflection.",
         hint="HTML entities and backtick-delimited JS strings can work without quotes.",
         technique="Reflected — quote filter bypass", points=250,
         flag="STING{r2b_quote_filter}",
         endpoint="/challenges/reflected/r2b"),

    dict(challenge_id="r2c", tier=2, title="Case Closed",
         description="A case-sensitive keyword filter blocks 'script' and 'onerror'.",
         hint="HTML parsers are case-insensitive. The filter is not. Try mixed case.",
         technique="Reflected — case-mixing bypass", points=250,
         flag="STING{r2c_case_mixing}",
         endpoint="/challenges/reflected/r2c"),

    dict(challenge_id="r2d", tier=2, title="Entity Encoder",
         description="The server HTML-encodes angle brackets but not quotes or slashes.",
         hint="You are reflected inside a tag attribute. Angle brackets are gone but you can still escape the attribute.",
         technique="Reflected — attribute no-bracket bypass", points=250,
         flag="STING{r2d_no_bracket_attr}",
         endpoint="/challenges/reflected/r2d"),

    dict(challenge_id="r2e", tier=2, title="Length Limit",
         description="The reflected parameter is truncated to 20 characters.",
         hint="20 characters is enough for a short event handler. Pick a compact tag and attribute combo.",
         technique="Reflected — length constrained", points=250,
         flag="STING{r2e_length_limited}",
         endpoint="/challenges/reflected/r2e"),

    dict(challenge_id="r2f", tier=2, title="Keyword Doubler",
         description="The server removes the first occurrence of 'script', 'onerror', and 'alert' from input.",
         hint="Only the first match is removed. Double up a keyword so one copy survives.",
         technique="Reflected — keyword doubling bypass", points=250,
         flag="STING{r2f_keyword_doubling}",
         endpoint="/challenges/reflected/r2f"),

    # ── Tier 3 — Stored XSS ──────────────────────────────────────────────────
    dict(challenge_id="s1a", tier=3, title="Guestbook",
         description="A public guestbook. Messages are stored and displayed to every visitor.",
         hint="Your payload persists. Every page load fires it — including the admin bot visits.",
         technique="Stored — guestbook", points=500,
         flag="STING{s1a_stored_guestbook}",
         endpoint="/challenges/stored/s1a"),

    dict(challenge_id="s1b", tier=3, title="Forum Post",
         description="A simple forum. Post a message and the admin bot reads the board.",
         hint="The post body is rendered without encoding. The admin will visit in about 30 seconds.",
         technique="Stored — forum post", points=500,
         flag="STING{s1b_stored_forum}",
         endpoint="/challenges/stored/s1b"),

    dict(challenge_id="s1c", tier=3, title="Product Review",
         description="An e-commerce product review section. Reviews appear on the product page.",
         hint="The review text is stored and rendered raw. Craft a payload and wait for the bot.",
         technique="Stored — product review", points=500,
         flag="STING{s1c_stored_review}",
         endpoint="/challenges/stored/s1c"),

    dict(challenge_id="s1d", tier=3, title="Profile Bio",
         description="A user profile with an editable bio field. The bio is displayed on the public profile page.",
         hint="Set your bio to a payload. The admin visits all profile pages.",
         technique="Stored — profile bio", points=500,
         flag="STING{s1d_stored_profile}",
         endpoint="/challenges/stored/s1d"),

    dict(challenge_id="s1e", tier=3, title="Markdown Mayhem",
         description="A note-taking app that renders Markdown. The renderer passes raw HTML through untouched.",
         hint="Markdown allows inline HTML. A tag with an event handler passes right through the renderer.",
         technique="Stored — Markdown HTML injection", points=500,
         flag="STING{s1e_stored_markdown}",
         endpoint="/challenges/stored/s1e"),

    dict(challenge_id="s1f", tier=3, title="JSON Feed",
         description="A news feed stored as JSON. The frontend reads the JSON and writes titles to innerHTML.",
         hint="The title field from the JSON lands in innerHTML. Server-side encoding does not help you here.",
         technique="Stored — JSON to innerHTML", points=500,
         flag="STING{s1f_stored_json_feed}",
         endpoint="/challenges/stored/s1f"),

    # ── Tier 4 — DOM XSS ─────────────────────────────────────────────────────
    dict(challenge_id="d1a", tier=4, title="Hash Hijack",
         description="A single-page app reads window.location.hash and writes it to innerHTML.",
         hint="The URL fragment is never sent to the server. Pure client-side source and sink.",
         technique="DOM — location.hash to innerHTML", points=750,
         flag="STING{d1a_hash_innerhtml}",
         endpoint="/challenges/dom/d1a"),

    dict(challenge_id="d1b", tier=4, title="Search Widget",
         description="A client-side search widget reads the q= param from the URL and renders results via innerHTML.",
         hint="The source is document.location.search. The sink is innerHTML.",
         technique="DOM — URLSearchParams to innerHTML", points=750,
         flag="STING{d1b_searchparam_innerhtml}",
         endpoint="/challenges/dom/d1b"),

    dict(challenge_id="d1c", tier=4, title="Document Write",
         description="A legacy widget uses document.write() with a URL parameter.",
         hint="document.write accepts raw HTML. The source is a query parameter.",
         technique="DOM — document.write sink", points=750,
         flag="STING{d1c_document_write}",
         endpoint="/challenges/dom/d1c"),

    dict(challenge_id="d1d", tier=4, title="jQuery Sizzle",
         description="A jQuery-powered page passes a URL parameter to .html().",
         hint="jQuery .html() with user input is a classic DOM XSS sink.",
         technique="DOM — jQuery .html() sink", points=750,
         flag="STING{d1d_jquery_html_sink}",
         endpoint="/challenges/dom/d1d"),

    dict(challenge_id="d1e", tier=4, title="PostMessage Relay",
         description="The page listens for postMessage events and writes the data directly to innerHTML.",
         hint="Open this page in an iframe or child window and send a postMessage payload to it.",
         technique="DOM — postMessage to innerHTML", points=750,
         flag="STING{d1e_postmessage_sink}",
         endpoint="/challenges/dom/d1e"),

    dict(challenge_id="d1f", tier=4, title="eval() Trap",
         description="A calculator widget passes a query parameter directly to eval().",
         hint="eval executes arbitrary JavaScript. The query parameter is the source.",
         technique="DOM — eval() sink", points=750,
         flag="STING{d1f_eval_sink}",
         endpoint="/challenges/dom/d1f"),

    # ── Tier 5 — Blind XSS ───────────────────────────────────────────────────
    dict(challenge_id="b1a", tier=5, title="Support Ticket",
         description="Submit a support ticket. The admin bot reads all open tickets every 30 seconds.",
         hint="Your payload must survive storage and fire when the admin renders the ticket list.",
         technique="Blind — support ticket", points=1000,
         flag="STING{b1a_blind_support_ticket}",
         endpoint="/challenges/blind/b1a"),

    dict(challenge_id="b1b", tier=5, title="Feedback Form",
         description="A feedback form. Submissions are reviewed by an admin in a separate panel.",
         hint="The admin panel renders the feedback body without encoding.",
         technique="Blind — feedback form", points=1000,
         flag="STING{b1b_blind_feedback}",
         endpoint="/challenges/blind/b1b"),

    dict(challenge_id="b1c", tier=5, title="Log Viewer",
         description="A web app that logs User-Agent strings and displays them in an admin log viewer.",
         hint="The injection surface is the User-Agent header. The admin bot renders the log.",
         technique="Blind — User-Agent log", points=1000,
         flag="STING{b1c_blind_useragent_log}",
         endpoint="/challenges/blind/b1c"),

    dict(challenge_id="b1d", tier=5, title="Contact Name",
         description="A contact form. The name field is echoed in the admin inbox view.",
         hint="The name field is rendered raw in the admin view. Craft a blind payload.",
         technique="Blind — contact form name", points=1000,
         flag="STING{b1d_blind_contact_name}",
         endpoint="/challenges/blind/b1d"),

    dict(challenge_id="b1e", tier=5, title="Cookie Crumbles",
         description="A page sets a cookie from a query parameter. The admin panel displays cookie values for debugging.",
         hint="Inject into the cookie value via the query param. The admin panel renders it raw.",
         technique="Blind — cookie to admin panel", points=1000,
         flag="STING{b1e_blind_cookie}",
         endpoint="/challenges/blind/b1e"),

    # ── Tier 6 — WAF Bypass ───────────────────────────────────────────────────
    dict(challenge_id="w1a", tier=6, title="Space Invader",
         description="A WAF strips all space characters from the input before reflection.",
         hint="JavaScript does not need spaces between tokens. Try slash-star comments or tab characters.",
         technique="WAF bypass — space stripping", points=1200,
         flag="STING{w1a_waf_space_strip}",
         endpoint="/challenges/waf/w1a"),

    dict(challenge_id="w1b", tier=6, title="Bracket Bust",
         description="The WAF removes all angle bracket characters from input.",
         hint="You are already inside a JS event handler attribute — no angle brackets needed to execute code.",
         technique="WAF bypass — angle bracket removal", points=1200,
         flag="STING{w1b_waf_no_brackets}",
         endpoint="/challenges/waf/w1b"),

    dict(challenge_id="w1c", tier=6, title="Alert Ban",
         description="The WAF blocks any payload containing the word 'alert'.",
         hint="alert is not the only way to run JavaScript. Try confirm, prompt, or call fetch directly.",
         technique="WAF bypass — alert() blocked", points=1200,
         flag="STING{w1c_waf_alert_banned}",
         endpoint="/challenges/waf/w1c"),

    dict(challenge_id="w1d", tier=6, title="Double Encode",
         description="Input is URL-decoded once server-side before reflection. The WAF runs before decoding.",
         hint="Double URL-encode your payload. The WAF sees the encoded form; the browser decodes to the real thing.",
         technique="WAF bypass — double URL encoding", points=1200,
         flag="STING{w1d_waf_double_encode}",
         endpoint="/challenges/waf/w1d"),

    dict(challenge_id="w1e", tier=6, title="SVG Smuggler",
         description="The WAF blocks common event handler keywords: onerror, onload, onclick.",
         hint="SVG elements have their own event handlers that are different from standard HTML ones.",
         technique="WAF bypass — SVG events", points=1200,
         flag="STING{w1e_waf_svg_events}",
         endpoint="/challenges/waf/w1e"),

    dict(challenge_id="w1f", tier=6, title="Protocol Swap",
         description="The WAF blocks the javascript: protocol in href attributes.",
         hint="There are other ways to make a link execute JS. Some browsers accept unusual casing or HTML entities.",
         technique="WAF bypass — javascript: protocol", points=1200,
         flag="STING{w1f_waf_js_protocol}",
         endpoint="/challenges/waf/w1f"),

    # ── Tier 7 — CSP Bypass ──────────────────────────────────────────────────
    dict(challenge_id="c1a", tier=7, title="Unsafe Inline",
         description="The page has a CSP but includes 'unsafe-inline', making inline scripts valid.",
         hint="If unsafe-inline is present, an inline script tag works without any bypass.",
         technique="CSP — unsafe-inline present", points=2000,
         flag="STING{c1a_csp_unsafe_inline}",
         endpoint="/challenges/csp/c1a"),

    dict(challenge_id="c1b", tier=7, title="JSONP Junction",
         description="The CSP whitelists a domain that serves a JSONP endpoint.",
         hint="A whitelisted JSONP endpoint lets you control script content via the callback parameter.",
         technique="CSP — JSONP whitelisted domain", points=2000,
         flag="STING{c1b_csp_jsonp}",
         endpoint="/challenges/csp/c1b"),

    dict(challenge_id="c1c", tier=7, title="Nonce Leak",
         description="The CSP uses a per-request nonce but the nonce value is also reflected in the page body.",
         hint="Find the nonce in the HTML source. A script tag carrying that nonce value will be allowed by CSP.",
         technique="CSP — nonce reflected in body", points=2000,
         flag="STING{c1c_csp_nonce_leak}",
         endpoint="/challenges/csp/c1c"),

    dict(challenge_id="c1d", tier=7, title="Script Gadget",
         description="CSP blocks inline scripts. Angular is loaded from a whitelisted CDN.",
         hint="Angular evaluates ng-init attributes and template expressions without needing a script tag.",
         technique="CSP — Angular script gadget", points=2000,
         flag="STING{c1d_csp_angular_gadget}",
         endpoint="/challenges/csp/c1d"),

    dict(challenge_id="c1e", tier=7, title="Data URI Dance",
         description="The CSP allows data: URIs in script-src.",
         hint="A script tag with a data: URI src is a valid script source when data: is whitelisted.",
         technique="CSP — data: URI script", points=2000,
         flag="STING{c1e_csp_data_uri}",
         endpoint="/challenges/csp/c1e"),

    # ── Tier 8 — Template Injection → XSS ───────────────────────────────────
    dict(challenge_id="t1a", tier=8, title="Jinja Sting",
         description="A Flask page renders a user-controlled template string with Jinja2.",
         hint="Try injecting 7 multiplied by 7 inside double curly braces as a probe. Then escalate to XSS output.",
         technique="SSTI — Jinja2 → XSS", points=3000,
         flag="STING{t1a_jinja2_ssti_xss}",
         endpoint="/challenges/template/t1a"),

    dict(challenge_id="t1b", tier=8, title="Twig Twist",
         description="A Python app evaluates expressions inside double curly brace blocks using eval().",
         hint="The expression evaluator runs eval on the content inside the braces. Inject Python that outputs a payload.",
         technique="SSTI — eval-based → XSS", points=3000,
         flag="STING{t1b_eval_template_xss}",
         endpoint="/challenges/template/t1b"),

    dict(challenge_id="t1c", tier=8, title="Format String",
         description="A Python str.format() call uses a user-controlled format string that outputs into an HTML page.",
         hint="Try accessing dunder attributes via format placeholders to leak Python internals and inject output.",
         technique="SSTI — str.format() → XSS", points=3000,
         flag="STING{t1c_format_string_xss}",
         endpoint="/challenges/template/t1c"),

    dict(challenge_id="t1d", tier=8, title="Server Echo",
         description="A server-side rendering endpoint evaluates a POST template body and returns raw HTML.",
         hint="The template body is passed to render_template_string. Escape the template context to inject HTML.",
         technique="SSTI — render_template_string → XSS", points=3000,
         flag="STING{t1d_render_template_string_xss}",
         endpoint="/challenges/template/t1d"),

    # ── Tier 9 — GraphQL XSS ─────────────────────────────────────────────────
    dict(challenge_id="g1a", tier=9, title="also Scout",
         description="A GraphQL search API with introspection enabled. Discover the schema, find the injectable string field, and exploit the reflected value rendered via innerHTML.",
         hint="Introspect the endpoint first. The query type has one string-typed field whose return value lands directly in innerHTML.",
         technique="GraphQL — reflected string field → innerHTML", points=1500,
         flag="STING{g1a_graphql_reflected}",
         endpoint="/challenges/graphql/g1a"),

    dict(challenge_id="g1b", tier=9, title="Mutation Station",
         description="A comment board backed by a GraphQL API. The mutation stores your input; the admin bot reads the board every 30 seconds.",
         hint="Use the createComment mutation to inject a stored payload. The board renders comment bodies without sanitisation.",
         technique="GraphQL — stored mutation → board → admin bot", points=1500,
         flag="STING{g1b_graphql_stored}",
         endpoint="/challenges/graphql/g1b"),

    dict(challenge_id="g1c", tier=9, title="Error Echo",
         description="A debug field that always fails validation and echoes your message verbatim inside the GraphQL errors array. The client renders errors[0].message via innerHTML.",
         hint="The debug field returns an error, not data. The error message contains your msg argument unchanged.",
         technique="GraphQL — error message reflection → innerHTML", points=1500,
         flag="STING{g1c_graphql_error_echo}",
         endpoint="/challenges/graphql/g1c"),

    # ── Tier 10 — WebSocket XSS ───────────────────────────────────────────────
    dict(challenge_id="ws1a", tier=10, title="Echo Chamber",
         description="A WebSocket chat server that echoes every message back verbatim. The client renders the echoed data via innerHTML with no sanitisation.",
         hint="Connect to the WebSocket endpoint visible in the page source. The server echoes your message; the client writes event.data to innerHTML.",
         technique="WebSocket — raw echo → innerHTML", points=1750,
         flag="STING{ws1a_websocket_echo}",
         endpoint="/challenges/ws/ws1a"),

    dict(challenge_id="ws1b", tier=10, title="JSON Wire",
         description="A WebSocket protocol that wraps messages in a JSON envelope. The server echoes the frame; the client parses it and renders msg.content via innerHTML.",
         hint="Send a raw string — the server wraps it as {type:'chat',content:'...'}. The client renders .content via innerHTML.",
         technique="WebSocket — JSON envelope → innerHTML", points=1750,
         flag="STING{ws1b_websocket_json}",
         endpoint="/challenges/ws/ws1b"),

    dict(challenge_id="ws1c", tier=10, title="Broadcast Booth",
         description="WebSocket messages are persisted and broadcast to every client on connect. The admin bot reads the board every 30 seconds.",
         hint="Send your payload via WebSocket — it is stored and rendered on the board without sanitisation. Wait for the admin to visit.",
         technique="WebSocket — stored broadcast → board → admin bot", points=1750,
         flag="STING{ws1c_websocket_stored}",
         endpoint="/challenges/ws/ws1c"),

    # ── Tier 11 — DOM Advanced ────────────────────────────────────────────────
    dict(challenge_id="d2a", tier=11, title="Prototype Pollution Gadget",
         description="A widget deep-merges URL hash JSON into a config object. A downstream gadget reads a property from a plain {} — with no own property — falling back to a polluted Object.prototype.",
         hint="Pollute Object.prototype.template via {\"__proto__\":{\"template\":\"PAYLOAD\"}} in the hash. The gadget reads ({}).template into innerHTML.",
         technique="DOM — prototype pollution gadget → innerHTML", points=1250,
         flag="STING{d2a_prototype_pollution}",
         endpoint="/challenges/dom/d2a"),

    dict(challenge_id="d2b", tier=11, title="Redirect Jacking",
         description="A post-login redirect reads the next= parameter and assigns it directly to window.location.href with no scheme validation.",
         hint="Any URI scheme is accepted. What happens when next= is a javascript: URI?",
         technique="DOM — open redirect → javascript: URI → XSS", points=1000,
         flag="STING{d2b_open_redirect_xss}",
         endpoint="/challenges/dom/d2b"),

    dict(challenge_id="d2c", tier=11, title="Outer Replacement",
         description="A widget builder reads the widget= parameter and assigns it to element.outerHTML, replacing the entire node with the parsed HTML.",
         hint="outerHTML replaces the element itself. All HTML — including event handlers — in the new markup is parsed and live.",
         technique="DOM — outerHTML sink", points=1000,
         flag="STING{d2c_outerhtml_sink}",
         endpoint="/challenges/dom/d2c"),

    dict(challenge_id="d2d", tier=11, title="Adjacent Injection",
         description="A notification widget appends the append= parameter directly via insertAdjacentHTML('beforeend', ...) with no sanitisation.",
         hint="insertAdjacentHTML is an innerHTML-equivalent sink that is often missed by WAF rules and linters. Treat it exactly like innerHTML.",
         technique="DOM — insertAdjacentHTML sink", points=1000,
         flag="STING{d2d_insertadjacenthtml}",
         endpoint="/challenges/dom/d2d"),
]


def all_challenges() -> list[dict]:
    return CHALLENGES


def challenge_by_id(cid: str) -> dict | None:
    return next((c for c in CHALLENGES if c["challenge_id"] == cid), None)
