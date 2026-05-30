from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.banking, routes.support, routes.admin, routes.docs, routes.api, routes.expanded

app = Flask(__name__)
app.secret_key = 'humanbank-2026-xQ8nRv4'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.banking.init(app)
routes.support.init(app)
routes.admin.init(app)
routes.docs.init(app)
routes.api.init(app)
routes.expanded.init(app)

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /vault\n"
        "Disallow: /wire-transfers\n"
        "Disallow: /audit-log\n"
        "Disallow: /api/v1/admin/users\n"
        "Disallow: /commonhuman\n\n"
        "# HumanBank — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )

@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0f1117;color:#d4a853;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem;border:1px solid #2a2a3a;border-radius:12px;background:#161b27}
  pre{font-family:monospace;color:#d4a853;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#e8c96d}
  p{color:#8b8b9b;margin:.5rem 0}
  a{color:#d4a853}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>HumanBank &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#9b8b6b;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to HumanBank</a></p>
</div></body></html>''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
