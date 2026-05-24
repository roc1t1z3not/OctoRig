# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""StingXSS Fire Range — Flask entry point."""
from __future__ import annotations
import threading
import time

from flask import Flask

from core.db.scoredb import init_score_db
from core.db.storedb import init_store_db
from core.api.routes import bp as api_bp
from core.challenges.reflected import bp as reflected_bp
from core.challenges.stored import bp as stored_bp
from core.challenges.dom import bp as dom_bp
from core.challenges.blind import bp as blind_bp
from core.challenges.waf import bp as waf_bp
from core.challenges.csp import bp as csp_bp
from core.challenges.template import bp as template_bp
from core.challenges.graphql import bp as graphql_bp
from core.challenges.websocket import bp as websocket_bp, ws1a_ws, ws1b_ws, ws1c_ws
from core.challenges.dom_advanced import bp as dom_advanced_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "stingxss-dev-secret"

    # Register blueprints
    for bp in (api_bp, reflected_bp, stored_bp, dom_bp,
               blind_bp, waf_bp, csp_bp, template_bp,
               graphql_bp, websocket_bp, dom_advanced_bp):
        app.register_blueprint(bp)

    # Register WebSocket routes (flask-sock)
    from flask_sock import Sock
    sock = Sock(app)
    sock.route("/challenges/ws/ws1a/ws")(ws1a_ws)
    sock.route("/challenges/ws/ws1b/ws")(ws1b_ws)
    sock.route("/challenges/ws/ws1c/ws")(ws1c_ws)

    # Init DBs
    with app.app_context():
        init_score_db()
        init_store_db()

    return app


# ---------------------------------------------------------------------------
# Background admin bot — visits stored/blind XSS pages every 30 s
# Uses a plain in-process HTTP request so the payload fires in the same process
# ---------------------------------------------------------------------------

def _admin_bot(app: Flask) -> None:
    """Simulate an admin visiting stored and blind XSS pages.

    Uses headless Chromium so injected JavaScript actually executes —
    payloads that call /api/catch will fire and award points.
    """
    import subprocess
    import shutil

    _chromium = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    _CHROME_FLAGS = [
        "--headless=new", "--no-sandbox", "--disable-gpu",
        "--disable-dev-shm-usage", "--dump-dom",
    ]

    def _visit(url: str) -> None:
        if _chromium:
            try:
                subprocess.run(
                    [_chromium, *_CHROME_FLAGS, url],
                    timeout=10, capture_output=True,
                )
            except Exception:
                pass

    BLIND_PAGES = [
        "http://127.0.0.1/challenges/blind/b1a/admin",
        "http://127.0.0.1/challenges/blind/b1b/admin",
        "http://127.0.0.1/challenges/blind/b1c/admin",
        "http://127.0.0.1/challenges/blind/b1d/admin",
        "http://127.0.0.1/challenges/blind/b1e/admin",
    ]
    STORED_PAGES = [
        "http://127.0.0.1/challenges/stored/s1a/board",
        "http://127.0.0.1/challenges/stored/s1b/board",
        "http://127.0.0.1/challenges/stored/s1c/reviews",
        "http://127.0.0.1/challenges/stored/s1d/profile/admin",
        "http://127.0.0.1/challenges/stored/s1e/board",
        "http://127.0.0.1/challenges/stored/s1f/board",
        # Tier 9 — GraphQL stored
        "http://127.0.0.1/challenges/graphql/g1b/board",
        # Tier 10 — WebSocket stored
        "http://127.0.0.1/challenges/ws/ws1c/board",
    ]

    # Wait for app to be ready
    time.sleep(5)

    while True:
        with app.app_context():
            for url in BLIND_PAGES + STORED_PAGES:
                _visit(url)
        time.sleep(30)


if __name__ == "__main__":
    application = create_app()

    bot_thread = threading.Thread(target=_admin_bot, args=(application,), daemon=True)
    bot_thread.start()

    application.run(host="0.0.0.0", port=80, debug=False, use_reloader=False)
