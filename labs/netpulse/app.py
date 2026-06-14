from flask import Flask, Response, render_template_string
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.account, routes.tools, routes.billing
import routes.tickets, routes.board, routes.admin, routes.api, routes.expanded

app = Flask(__name__)
app.secret_key = 'netpulse-1998-xT7kLm9'
app.config['SSTI_FLAG'] = 'FLAG{np_ssti_template_exec}'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.account.init(app)
routes.tools.init(app)
routes.billing.init(app)
routes.tickets.init(app)
routes.board.init(app)
routes.admin.init(app)
routes.api.init(app)
routes.expanded.init(app)

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /dialup-pool\n"
        "Disallow: /billing-db\n"
        "Disallow: /syslog\n"
        "Disallow: /api/v1/admin/config\n"
        "Disallow: /commonhuman\n\n"
        "# NetPulse Internet Services — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )

@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0c1419;color:#00bcd4;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem}
  pre{color:#00bcd4;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#f59e0b}
  p{color:#607d8b;margin:.5rem 0}
  a{color:#00bcd4}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>NetPulse &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#607d8b;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to NetPulse</a></p>
</div></body></html>''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
