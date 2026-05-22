from flask import request, render_template, session, redirect, url_for
from db import get_db

try:
    from lxml import etree as _etree
    _LXML_AVAILABLE = True
except ImportError:
    _LXML_AVAILABLE = False


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    @app.route('/watchlist')
    def watchlist():
        redir = _require_login()
        if redir:
            return redir
        uid  = session['user_id']
        rows = get_db().execute(
            "SELECT w.*, m.name, m.price, m.change FROM watchlist w "
            "LEFT JOIN market_data m ON w.symbol = m.symbol WHERE w.user_id = ?",
            (uid,)
        ).fetchall()
        return render_template('watchlist.html', items=rows)

    # VULN: XXE — XML parsed with lxml, external entities enabled
    @app.route('/watchlist/import', methods=['POST'])
    def watchlist_import():
        redir = _require_login()
        if redir:
            return redir
        uid   = session['user_id']
        error = None
        added = []
        f     = request.files.get('xmlfile')
        if not f:
            error = 'No file uploaded.'
            return render_template('watchlist_import.html', error=error, added=added)
        data = f.read()
        if not _LXML_AVAILABLE:
            error = 'lxml not available.'
            return render_template('watchlist_import.html', error=error, added=added)
        try:
            # VULN: XXE — load_dtd=True, no_network=False, resolve_entities=True
            parser = _etree.XMLParser(load_dtd=True, no_network=False, resolve_entities=True)
            root   = _etree.fromstring(data, parser=parser)
            db     = get_db()
            for sym_el in root.findall('symbol'):
                symbol = (sym_el.text or '').strip().upper()
                if symbol:
                    existing = db.execute(
                        "SELECT id FROM watchlist WHERE user_id = ? AND symbol = ?",
                        (uid, symbol)
                    ).fetchone()
                    if not existing:
                        db.execute(
                            "INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)",
                            (uid, symbol)
                        )
                        added.append(symbol)
            db.commit()
        except Exception as e:
            error = str(e)
        return render_template('watchlist_import.html', error=error, added=added)

    @app.route('/watchlist/add', methods=['POST'])
    def watchlist_add():
        redir = _require_login()
        if redir:
            return redir
        uid    = session['user_id']
        symbol = request.form.get('symbol', '').upper().strip()
        if symbol:
            db = get_db()
            exists = db.execute(
                "SELECT id FROM watchlist WHERE user_id = ? AND symbol = ?", (uid, symbol)
            ).fetchone()
            if not exists:
                db.execute("INSERT INTO watchlist (user_id, symbol) VALUES (?, ?)", (uid, symbol))
                db.commit()
        return redirect(url_for('watchlist'))

    @app.route('/watchlist/remove', methods=['POST'])
    def watchlist_remove():
        redir = _require_login()
        if redir:
            return redir
        uid    = session['user_id']
        wid    = request.form.get('watchlist_id', '')
        if wid:
            db = get_db()
            db.execute("DELETE FROM watchlist WHERE id = ? AND user_id = ?", (wid, uid))
            db.commit()
        return redirect(url_for('watchlist'))
