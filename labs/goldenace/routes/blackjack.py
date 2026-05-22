import json
import random
from datetime import datetime, timezone
from flask import request, render_template, session, redirect, url_for
from db import get_db

SUITS  = ['♠', '♥', '♦', '♣']
RANKS  = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']


def _new_deck():
    deck = [r + s for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def _card_val(card):
    r = card[:-1]
    if r in ('J', 'Q', 'K'):
        return 10
    if r == 'A':
        return 11
    return int(r)


def _hand_val(hand):
    total = sum(_card_val(c) for c in hand)
    aces  = sum(1 for c in hand if c[:-1] == 'A')
    while total > 21 and aces:
        total -= 10
        aces  -= 1
    return total


def _resolve(player, dealer, bet):
    pv, dv = _hand_val(player), _hand_val(dealer)
    if pv > 21:
        return 'player_bust', 0.0
    if dv > 21:
        return 'dealer_bust', bet * 2
    if pv > dv:
        return 'player_win', bet * 2
    if pv < dv:
        return 'dealer_win', 0.0
    return 'push', bet


def init(app):

    @app.route('/blackjack')
    def blackjack():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        user  = get_db().execute("SELECT * FROM users WHERE id = ?",
                                 (session['user_id'],)).fetchone()
        state = session.get('bj')
        return render_template('blackjack.html', user=user, state=state)

    # VULN: bet taken from POST — no negative validation
    @app.route('/blackjack/deal', methods=['POST'])
    def blackjack_deal():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        bet  = float(request.form.get('bet', 25))
        deck = _new_deck()
        player = [deck.pop(), deck.pop()]
        dealer = [deck.pop(), deck.pop()]
        session['bj'] = {
            'deck':   deck,
            'player': player,
            'dealer': dealer,
            'bet':    bet,
            'status': 'playing',
            'doubled': False,
        }
        # Check natural blackjack
        if _hand_val(player) == 21:
            state = session['bj']
            state['status'] = 'blackjack'
            payout = round(bet * 2.5, 2)
            _finish_hand(state, 'blackjack', payout)
        return redirect(url_for('blackjack'))

    @app.route('/blackjack/action', methods=['POST'])
    def blackjack_action():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        state = session.get('bj')
        if not state or state['status'] != 'playing':
            return redirect(url_for('blackjack'))

        action = request.form.get('action', '')
        deck, player, dealer, bet = (
            state['deck'], state['player'], state['dealer'], state['bet']
        )

        if action == 'hit':
            player.append(deck.pop())
            if _hand_val(player) > 21:
                state['player'] = player
                state['deck']   = deck
                state['status'] = 'player_bust'
                _finish_hand(state, 'player_bust', 0.0)
            else:
                state['player'] = player
                state['deck']   = deck

        elif action == 'stand':
            # Dealer draws to 17
            while _hand_val(dealer) < 17:
                dealer.append(deck.pop())
            state['dealer'] = dealer
            state['deck']   = deck
            outcome, payout = _resolve(player, dealer, bet)
            state['status'] = outcome
            _finish_hand(state, outcome, payout)

        elif action == 'double':
            # VULN: doubled bet not validated against balance
            player.append(deck.pop())
            state['bet']    = bet * 2
            state['doubled'] = True
            if _hand_val(player) > 21:
                state['player'] = player
                state['status'] = 'player_bust'
                _finish_hand(state, 'player_bust', 0.0)
            else:
                while _hand_val(dealer) < 17:
                    dealer.append(deck.pop())
                state['dealer'] = dealer
                state['deck']   = deck
                outcome, payout = _resolve(player, dealer, state['bet'])
                state['status'] = outcome
                _finish_hand(state, outcome, payout)

        elif action == 'split' and len(player) == 2 and _card_val(player[0]) == _card_val(player[1]):
            # Simple split: give each hand one new card, play first hand only
            hand1 = [player[0], deck.pop()]
            hand2 = [player[1], deck.pop()]
            state['player'] = hand1
            state['split_hand'] = hand2
            state['deck']   = deck

        session.modified = True
        return redirect(url_for('blackjack'))


def _finish_hand(state, outcome, payout):
    uid = session.get('user_id')
    if not uid:
        return
    db  = get_db()
    bet = state['bet']
    net = payout - bet
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    res = 'win' if payout > bet else ('push' if payout == bet else 'loss')
    db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (net, uid))
    db.execute(
        "INSERT INTO game_history (user_id,game_type,bet,result,payout,memo,created_at)"
        " VALUES (?,?,?,?,?,?,?)",
        (uid, 'blackjack', bet, res, payout, '', now)
    )
    db.execute(
        "INSERT INTO transactions (user_id,type,amount,description,game_type,created_at)"
        " VALUES (?,?,?,?,?,?)",
        (uid, res, net, f'Blackjack {outcome.replace("_"," ")}', 'blackjack', now)
    )
    db.commit()
    state['payout'] = payout
    session.modified = True
