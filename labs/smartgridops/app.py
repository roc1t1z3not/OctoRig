# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.dashboard, routes.devices, routes.zones
import routes.meters, routes.credits, routes.mqtt, routes.api

app = Flask(__name__)
app.secret_key = 'smartgridops-scada-2023-Qk7vNz'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.dashboard.init(app)
routes.devices.init(app)
routes.zones.init(app)
routes.meters.init(app)
routes.credits.init(app)
routes.mqtt.init(app)
routes.api.init(app)


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /api/device\n"
        "Disallow: /devices/poll\n"
        "Disallow: /admin\n"
        "Disallow: /historian\n"
        "Disallow: /commonhuman\n\n"
        "# SmartGridOps SCADA — CommonHuman-Lab\n"
        "# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not\n"
        "# Deliberately vulnerable — do not connect real grid hardware.\n",
        mimetype='text/plain'
    )


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0a0f0d;color:#39ff7a;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem}
  pre{color:#39ff7a;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#ffd166}
  p{color:#6b8f7f;margin:.5rem 0}
  a{color:#39ff7a}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>SmartGridOps &mdash; Lab</p>
<p>Author of this lab: <a href="https://github.com/roc1t1z3not" target="_blank">roc1t1z3not</a></p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#6b8f7f;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to SmartGridOps</a></p>
</div></body></html>''')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
