from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.portal, routes.messaging, routes.docs, routes.admin, routes.api, routes.expanded

app = Flask(__name__)
app.secret_key = 'medihuman-2026-xQ8nRv4'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.portal.init(app)
routes.messaging.init(app)
routes.docs.init(app)
routes.admin.init(app)
routes.api.init(app)
routes.expanded.init(app)

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /patient-records\n"
        "Disallow: /staff-only\n"
        "Disallow: /mri-archive\n"
        "Disallow: /mri-viewer\n"
        "Disallow: /billing-portal\n"
        "Disallow: /api/v1/admin/export\n"
        "Disallow: /commonhuman\n\n"
        "# MediHuman — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )

@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#f8fafc;color:#1e293b;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem;border:1px solid #e2e8f0;border-radius:12px;background:#fff;box-shadow:0 4px 24px rgba(0,0,0,.07)}
  pre{font-family:monospace;color:#e11d48;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#1e293b}
  p{color:#64748b;margin:.5rem 0}
  a{color:#e11d48}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>MediHuman &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#94a3b8;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to MediHuman</a></p>
</div></body></html>''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
