import random
from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for
from db import get_db

RED_NUMS   = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}


def _color(n):
    if n == 0:    return 'green'
    if n in RED_NUMS: return 'red'
    return 'black'


def _payout(bet_type, bet_value, landed, amount):
    """Return payout amount (0 = lose). amount is the original bet."""
    n = landed
    if bet_type == 'straight':
        return amount * 36 if str(n) == str(bet_value) else 0
    if bet_type == 'color':
        hit = (bet_value == 'red' and n in RED_NUMS) or \
              (bet_value == 'black' and n in BLACK_NUMS)
        return amount * 2 if hit else 0
    if bet_type == 'parity':
        if n == 0: return 0
        hit = (bet_value == 'odd' and n % 2 == 1) or \
              (bet_value == 'even' and n % 2 == 0)
        return amount * 2 if hit else 0
    if bet_type == 'half':
        hit = (bet_value == 'low' and 1 <= n <= 18) or \
              (bet_value == 'high' and 19 <= n <= 36)
        return amount * 2 if hit else 0
    if bet_type == 'dozen':
        ranges = {'1': range(1,13), '2': range(13,25), '3': range(25,37)}
        return amount * 3 if n in ranges.get(str(bet_value), []) else 0
    if bet_type == 'column':
        cols = {'1': [c for c in range(1,37) if c % 3 == 1],
                '2': [c for c in range(1,37) if c % 3 == 2],
                '3': [c for c in range(1,37) if c % 3 == 0]}
        return amount * 3 if n in cols.get(str(bet_value), []) else 0
    return 0


def init(app):

    @app.route('/roulette')
    def roulette():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = get_db().execute("SELECT * FROM users WHERE id = ?",
                                (session['user_id'],)).fetchone()
        return render_template('roulette.html', user=user, result=None)

    # VULN: no CSRF token; bet amount not validated (negative allowed)
    @app.route('/roulette/spin', methods=['POST'])
    def roulette_spin():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid      = session['user_id']
        db       = get_db()
        user     = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        bet_type = request.form.get('bet_type', 'color')
        bet_val  = request.form.get('bet_value', 'red')
        amount   = float(request.form.get('amount', 10))
        memo     = request.form.get('memo', '')
        landed   = random.randint(0, 36)
        pay      = _payout(bet_type, bet_val, landed, amount)
        net      = pay - amount
        result   = 'win' if pay > amount else ('push' if pay == amount else 'loss')
        now      = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        new_bal  = user['balance'] + net

        db.execute("UPDATE users SET balance = ? WHERE id = ?", (new_bal, uid))
        db.execute(
            "INSERT INTO game_history (user_id,game_type,bet,result,payout,memo,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (uid, 'roulette', amount, result, pay, memo, now)
        )
        db.execute(
            "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
            " VALUES (?,?,?,?,?,?)",
            (uid, result, net, f'Roulette {result}', 'roulette', now)
        )
        db.commit()

        return render_template('roulette.html', user=user, result={
            'landed':      landed,
            'color':       _color(landed),
            'bet_type':    bet_type,
            'bet_value':   bet_val,
            'amount':      amount,
            'payout':      pay,
            'net':         net,
            'outcome':     result,
            'new_balance': new_bal,
            'memo':        memo,
        })
