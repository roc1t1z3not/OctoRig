# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
BreachSQL Fire Range — deliberately vulnerable Flask application.

Part of OctoRig (https://github.com/CommonHuman-Lab/OctoRig).

57 SQL injection challenges across three backends.

  MySQL  (/challenges/my1–my5/…)  28 challenges  — my1a–my5c
  PG     (/challenges/pg/…)       16 challenges  — pg1a–pg4b
  SQLite (/challenges/sq/…)       13 challenges  — sq1a–sq3a

Scoring / player UI
───────────────────
  GET  /                       → HTML challenge index
  GET  /scoreboard             → HTML scoreboard
  GET  /api/challenges         → JSON list of challenges (flags stripped)
  GET  /api/scoreboard         → JSON scoreboard
  POST /api/submit-flag        → JSON  {"player", "challenge_id", "flag"}
  GET  /health                 → JSON  {"status":"ok"} (probes all DBs)

DO NOT expose this service on a public network.
"""

from __future__ import annotations

from flask import Flask

from core.db.sqdb import init_sq_db
from core.registry import init_score_db
from core.api.routes import bp as api_bp
from core.api.ui import bp as ui_bp
from core.challenges.mysql import bp as mysql_bp
from core.challenges.postgres import bp as pg_bp
from core.challenges.sqlite import bp as sq_bp

app = Flask(__name__)

# Initialise persistent stores
init_sq_db()
init_score_db()

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(ui_bp)
app.register_blueprint(mysql_bp)
app.register_blueprint(pg_bp)
app.register_blueprint(sq_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
