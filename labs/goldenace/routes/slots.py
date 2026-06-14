import random
from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for, jsonify
from db import get_db

SYMBOLS  = ['CHERRY', 'BELL', 'STAR', 'SEVEN', 'DIAMOND', 'JOKER']
# Weights: higher = more common, lower = rarer
WEIGHTS  = [30, 25, 20, 15, 8, 2]
# 3-match payout multiplier
PAYOUTS3 = {'CHERRY': 2, 'BELL': 3, 'STAR': 5, 'SEVEN': 10, 'DIAMOND': 20, 'JOKER': 50}
# Symbol display (emoji-like text)
DISPLAY  = {'CHERRY': '🍒', 'BELL': '🔔', 'STAR': '⭐', 'SEVEN': '7️⃣', 'DIAMOND': '💎', 'JOKER': '🃏'}


def _spin():
    return random.choices(SYMBOLS, weights=WEIGHTS, k=3)


def init(app):

    @app.route('/slots')
    def slots():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user = get_db().execute("SELECT * FROM users WHERE id = ?",
                                (session['user_id'],)).fetchone()
        return render_template('slots.html', user=user, result=None)

    # VULN: bet amount taken directly from POST — no negative/zero validation (price tampering)
    @app.route('/slots/spin', methods=['POST'])
    def slots_spin():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        uid  = session['user_id']
        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

        # VULN: client-supplied bet, no validation — negative bet = free money
        bet  = float(request.form.get('bet', 10))
        negative_bet_flag = 'FLAG{ga_negative_bet_exploit}' if bet < 0 else None
        memo = request.form.get('memo', '')

        reels  = _spin()
        now    = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        result = 'loss'
        payout = 0.0

        if reels[0] == reels[1] == reels[2]:
            # 3 of a kind
            payout = bet * PAYOUTS3[reels[0]]
            result = 'win'
        elif reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]:
            # 2 of a kind — return 50% of bet
            payout = bet * 0.5
            result = 'win' if payout > bet else 'loss'

        net = payout - bet
        new_balance = user['balance'] + net

        db.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, uid))
        db.execute(
            "INSERT INTO game_history (user_id,game_type,bet,result,payout,memo,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (uid, 'slots', bet, result, payout, memo, now)
        )
        db.execute(
            "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
            " VALUES (?,?,?,?,?,?)",
            (uid, result, net, f'Slots {result}', 'slots', now)
        )
        db.commit()

        display_reels = [DISPLAY[s] for s in reels]
        return render_template('slots.html', user=user, result={
            'reels':              display_reels,
            'reels_raw':          reels,
            'bet':                bet,
            'payout':             payout,
            'net':                net,
            'outcome':            result,
            'new_balance':        new_balance,
            'memo':               memo,
            'negative_bet_flag':  negative_bet_flag,
        })
