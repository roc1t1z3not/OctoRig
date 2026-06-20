# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.dashboard, routes.shipments, routes.depots
import routes.billing, routes.admin, routes.api

app = Flask(__name__)
app.secret_key = 'fleetwave-logistics-2026-Pq9rTz'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.dashboard.init(app)
routes.shipments.init(app)
routes.depots.init(app)
routes.billing.init(app)
routes.admin.init(app)
routes.api.init(app)


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /admin/driver-roster\n"
        "Disallow: /api/internal\n"
        "Disallow: /commonhuman\n\n"
        "# FleetWave WMS — CommonHuman-Lab\n"
        "# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not\n"
        "# Deliberately vulnerable — do not route real freight.\n",
        mimetype='text/plain'
    )


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0b2027;color:#19b3a6;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem}
  pre{color:#19b3a6;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#f59f00}
  p{color:#6b8f8a;margin:.5rem 0}
  a{color:#19b3a6}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>FleetWave &mdash; Lab</p>
<p>Author of this lab: <a href="https://github.com/roc1t1z3not" target="_blank">roc1t1z3not</a></p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#6b8f8a;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project.</p>
<p style="margin-top:1rem;"><a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a></p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to FleetWave</a></p>
</div></body></html>''')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
