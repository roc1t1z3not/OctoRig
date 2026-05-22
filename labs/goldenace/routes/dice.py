import random
from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for
from db import get_db


def init(app):

    @app.route('/dice')
    def dice():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = get_db().execute("SELECT * FROM users WHERE id = ?",
                                (session['user_id'],)).fetchone()
        return render_template('dice.html', user=user, result=None)

    # VULN: bet not validated — negative bets allowed
    @app.route('/dice/roll', methods=['POST'])
    def dice_roll():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid    = session['user_id']
        db     = get_db()
        user   = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        choice = request.form.get('choice', 'high')   # 'high' or 'low'
        bet    = float(request.form.get('bet', 10))
        memo   = request.form.get('memo', '')
        d1     = random.randint(1, 6)
        d2     = random.randint(1, 6)
        total  = d1 + d2
        now    = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # 7 = house wins; >7 = high; <7 = low
        if total == 7:
            result = 'loss'
            payout = 0.0
        elif (choice == 'high' and total > 7) or (choice == 'low' and total < 7):
            result = 'win'
            payout = bet * 2
        else:
            result = 'loss'
            payout = 0.0

        net     = payout - bet
        new_bal = user['balance'] + net

        db.execute("UPDATE users SET balance = ? WHERE id = ?", (new_bal, uid))
        db.execute(
            "INSERT INTO game_history (user_id,game_type,bet,result,payout,memo,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (uid, 'dice', bet, result, payout, memo, now)
        )
        db.execute(
            "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
            " VALUES (?,?,?,?,?,?)",
            (uid, result, net, f'Dice {result}', 'dice', now)
        )
        db.commit()

        return render_template('dice.html', user=user, result={
            'd1':          d1,
            'd2':          d2,
            'total':       total,
            'choice':      choice,
            'bet':         bet,
            'payout':      payout,
            'net':         net,
            'outcome':     result,
            'new_balance': new_bal,
            'memo':        memo,
        })
