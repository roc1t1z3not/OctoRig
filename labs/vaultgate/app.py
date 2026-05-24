# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""VaultGate IDOR Range — Flask entry point.

IDOR challenges, designed for benchmarking.

  Tokens        GET  /api/tokens            → all user credentials
  Login         POST /api/login             → {token, user_id, …}
  Challenges    GET  /api/challenges        → JSON list (flags stripped)
  Submit flag   POST /api/submit-flag       → {correct, message, …}
  Scoreboard    GET  /api/scoreboard        → JSON rankings
  Health        GET  /health                → {"status":"ok"}
  Index UI      GET  /                      → HTML challenge browser
  Scoreboard UI GET  /scoreboard            → HTML scoreboard

Challenge endpoints follow the pattern:
  /challenges/{category}/{id}              → HTML explanation page
  /challenges/{category}/{id}/{resource}   → Vulnerable API endpoint (JSON)

DO NOT expose this service on a public network.
"""
from __future__ import annotations

from flask import Flask

from core.db.scoredb import init_score_db
from core.api.routes import bp as api_bp
from core.challenges.horizontal import bp as horizontal_bp
from core.challenges.obfuscated import bp as obfuscated_bp
from core.challenges.body import bp as body_bp
from core.challenges.vertical import bp as vertical_bp
from core.challenges.method import bp as method_bp
from core.challenges.pollution import bp as pollution_bp
from core.challenges.massassign import bp as massassign_bp
from core.challenges.jwt_chals import bp as jwt_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.secret_key = "vaultgate-dev-secret"

    for bp in (api_bp, horizontal_bp, obfuscated_bp, body_bp,
               vertical_bp, method_bp, pollution_bp, massassign_bp, jwt_bp):
        app.register_blueprint(bp)

    with app.app_context():
        init_score_db()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=80, debug=False)
