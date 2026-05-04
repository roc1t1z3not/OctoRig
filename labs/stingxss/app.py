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


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "stingxss-dev-secret"

    # Register blueprints
    for bp in (api_bp, reflected_bp, stored_bp, dom_bp,
               blind_bp, waf_bp, csp_bp, template_bp):
        app.register_blueprint(bp)

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
    """Simulate an admin visiting stored and blind XSS pages."""
    import requests

    BLIND_PAGES = [
        "http://127.0.0.1:5000/challenges/blind/b1a/admin",
        "http://127.0.0.1:5000/challenges/blind/b1b/admin",
        "http://127.0.0.1:5000/challenges/blind/b1c/admin",
        "http://127.0.0.1:5000/challenges/blind/b1d/admin",
        "http://127.0.0.1:5000/challenges/blind/b1e/admin",
    ]
    STORED_PAGES = [
        "http://127.0.0.1:5000/challenges/stored/s1a/board",
        "http://127.0.0.1:5000/challenges/stored/s1b/board",
        "http://127.0.0.1:5000/challenges/stored/s1c/reviews",
        "http://127.0.0.1:5000/challenges/stored/s1d/profile/admin",
        "http://127.0.0.1:5000/challenges/stored/s1e/board",
        "http://127.0.0.1:5000/challenges/stored/s1f/board",
    ]

    # Wait for app to be ready
    time.sleep(5)

    while True:
        with app.app_context():
            for url in BLIND_PAGES + STORED_PAGES:
                try:
                    requests.get(url, timeout=5,
                                 headers={"X-Admin-Bot": "1",
                                          "User-Agent": "StingXSS-AdminBot/1.0"})
                except Exception:
                    pass
        time.sleep(30)


if __name__ == "__main__":
    application = create_app()

    bot_thread = threading.Thread(target=_admin_bot, args=(application,), daemon=True)
    bot_thread.start()

    application.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
