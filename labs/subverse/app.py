# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.posts, routes.communities, routes.comments
import routes.messages, routes.profile, routes.admin, routes.api

app = Flask(__name__)
app.secret_key = 'subverse-2026-xK9mQp7'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.posts.init(app)
routes.communities.init(app)
routes.comments.init(app)
routes.messages.init(app)
routes.profile.init(app)
routes.admin.init(app)
routes.api.init(app)


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /admin/users\n"
        "Disallow: /api/internal\n"
        "Disallow: /community/hidden\n"
        "Disallow: /commonhuman\n\n"
        "# SubVerse — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0d1117;color:#e6edf3;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem;border:1px solid #30363d;border-radius:12px;background:#161b22;box-shadow:0 4px 24px rgba(0,0,0,.4)}
  pre{font-family:monospace;color:#ff4500;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#e6edf3}
  p{color:#8b949e;margin:.5rem 0}
  a{color:#ff4500}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>SubVerse &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#6e7681;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to SubVerse</a></p>
</div></body></html>''')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=True)
