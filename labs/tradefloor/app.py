import random
import sqlite3 as _sqlite3
import threading
import time

from flask import Flask, Response, render_template_string
from db import init_db, close_db, DATABASE
from helpers import current_user
import routes.auth, routes.portfolio, routes.trading, routes.watchlist
import routes.filings, routes.alerts, routes.admin, routes.api


def _price_tick():
    from datetime import datetime, timezone
    while True:
        time.sleep(10)
        try:
            conn = _sqlite3.connect(DATABASE)
            rows = conn.execute("SELECT symbol, price FROM market_data").fetchall()
            now  = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
            for symbol, price in rows:
                if symbol == 'CMNH':
                    pct = random.uniform(0.005, 0.025)
                else:
                    pct = random.uniform(-0.03, 0.03)
                delta     = round(price * pct, 2)
                new_price = round(max(0.50, price + delta), 2)
                conn.execute(
                    "UPDATE market_data SET price = ?, change = ? WHERE symbol = ?",
                    (new_price, delta, symbol)
                )
                conn.execute(
                    "INSERT OR IGNORE INTO price_history (symbol, price, recorded_at) VALUES (?, ?, ?)",
                    (symbol, new_price, now)
                )
            # Keep at most 720 rows per symbol (~2 hours at 10 s intervals)
            conn.execute("""
                DELETE FROM price_history WHERE id IN (
                    SELECT id FROM price_history ph
                    WHERE (SELECT COUNT(*) FROM price_history
                           WHERE symbol = ph.symbol AND id >= ph.id) > 720
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass


threading.Thread(target=_price_tick, daemon=True).start()

app = Flask(__name__)
app.secret_key = 'tradefloor-y2k-xV6pNw2'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.portfolio.init(app)
routes.trading.init(app)
routes.watchlist.init(app)
routes.filings.init(app)
routes.alerts.init(app)
routes.admin.init(app)
routes.api.init(app)

@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /trading-engine\n"
        "Disallow: /settlement\n"
        "Disallow: /compliance-logs\n"
        "Disallow: /commonhuman\n\n"
        "# TradeFloor — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )

@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0b0f1a;color:#3b82f6;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem;border:1px solid #1f2d45;border-radius:12px;background:#111827}
  pre{font-family:monospace;color:#3b82f6;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#e2e8f0}
  p{color:#64748b;margin:.5rem 0}
  a{color:#3b82f6}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>TradeFloor &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#64748b;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to TradeFloor</a></p>
</div></body></html>''')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
