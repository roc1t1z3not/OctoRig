import random
import sqlite3 as _sqlite3
import threading
import time

from flask import Flask, Response, render_template_string
from db import init_db, close_db, DATABASE
from helpers import current_user
import routes.auth, routes.lobby, routes.slots, routes.blackjack
import routes.roulette, routes.dice, routes.account, routes.chat
import routes.promo, routes.admin, routes.api

_NPC_USERS = [
    (2, 'lucky_larry'), (3, 'high_roller'), (4, 'jane.doe'),
    (5, 'mike.b'), (6, 'poker_queen'), (7, 'chips_ahoy'), (8, 'novak.m'),
]
_GAMES     = ['slots', 'blackjack', 'roulette', 'dice']
_WIN_MSGS  = [
    '{user} won ${amount} on {game}!',
    '{user} hit a hot streak on {game} — ${amount}!',
    '{user} just walked away with ${amount} from {game}!',
    '{user} cleaned up at {game}: +${amount}!',
]


def _npc_tick():
    from datetime import datetime, timezone
    while True:
        time.sleep(8)
        try:
            uid, uname = random.choice(_NPC_USERS)
            game = random.choice(_GAMES)
            bet  = round(random.uniform(5, 500), 2)
            win  = random.random() < 0.45   # slight house edge
            if win:
                payout = round(bet * random.uniform(1.5, 4.0), 2)
                net    = round(payout - bet, 2)
                result = 'win'
            else:
                payout = 0.0
                net    = -bet
                result = 'loss'
            now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            conn = _sqlite3.connect(DATABASE)
            conn.execute(
                "INSERT INTO game_history (user_id,game_type,bet,result,payout,memo,created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                (uid, game, bet, result, payout, '', now)
            )
            conn.execute(
                "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
                " VALUES (?,?,?,?,?,?)",
                (uid, result, net, f'{game.capitalize()} {result}', game, now)
            )
            conn.execute(
                "UPDATE users SET balance = balance + ? WHERE id = ?", (net, uid)
            )
            if win:
                msg = random.choice(_WIN_MSGS).format(
                    user=uname, amount=f'{payout:,.2f}', game=game
                )
                conn.execute(
                    "INSERT INTO live_feed (message, created_at) VALUES (?, ?)", (msg, now)
                )
                conn.execute(
                    "DELETE FROM live_feed WHERE id NOT IN "
                    "(SELECT id FROM live_feed ORDER BY id DESC LIMIT 50)"
                )
            conn.commit()
            conn.close()
        except Exception:
            pass


threading.Thread(target=_npc_tick, daemon=True).start()

app = Flask(__name__)
app.secret_key = 'goldenace-xK9mPq3'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.lobby.init(app)
routes.slots.init(app)
routes.blackjack.init(app)
routes.roulette.init(app)
routes.dice.init(app)
routes.account.init(app)
routes.chat.init(app)
routes.promo.init(app)
routes.admin.init(app)
routes.api.init(app)


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /suite\n"
        "Disallow: /api\n"
        "Disallow: /commonhuman\n\n"
        "# GoldenAce — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not use real credentials.\n",
        mimetype='text/plain'
    )


@app.route('/commonhuman')
def commonhuman_easter_egg():
    return render_template_string('''<!DOCTYPE html><html lang="en">
<head><meta charset="UTF-8"><title>CommonHuman-Lab</title>
<style>
  body{background:#0a0a0f;color:#f59e0b;font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
  .egg{text-align:center;max-width:520px;padding:2rem;border:1px solid #2a2a40;border-radius:12px;background:#12121a}
  pre{font-family:monospace;color:#f59e0b;line-height:1.5;margin:1.5rem 0}
  h2{font-size:1.4rem;margin-bottom:1rem;color:#e2e8f0}
  p{color:#64748b;margin:.5rem 0}
  a{color:#f59e0b}
</style></head>
<body><div class="egg">
<pre>     ___
    /   \\
   | o_o |
    \\___/
   /|   |\\
  (_)   (_)</pre>
<h2>&#x1F419; You found it.</h2>
<p>GoldenAce &mdash; Lab</p>
<p>Part of the <strong>CommonHuman-Lab</strong> community.</p>
<p style="margin-top:1.5rem;color:#64748b;">Thank you for using these tools. If they have been useful for your training or teaching, a follow and a star on GitHub help more people find the project &mdash; and they mean a lot.</p>
<p style="margin-top:1rem;">
  <a href="https://github.com/CommonHuman-Lab" target="_blank">&#11088; Star &amp; Follow on GitHub</a>
</p>
<p style="margin-top:1.5rem"><a href="/">&#8592; Back to GoldenAce</a></p>
</div></body></html>''')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
