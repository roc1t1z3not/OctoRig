from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: SQLi + reflected XSS — q and sector injected into query; q rendered | safe
    @app.route('/filings')
    def filings():
        redir = _require_login()
        if redir:
            return redir
        q      = request.args.get('q', '')
        sector = request.args.get('sector', '')
        db     = get_db()

        where = '1=1'
        if q:
            where += f" AND (f.title LIKE '%{q}%' OR f.body LIKE '%{q}%')"
        if sector:
            where += f" AND f.sector = '{sector}'"

        rows = db.execute(
            f"SELECT f.*, m.name, m.price FROM filings f "
            f"LEFT JOIN market_data m ON f.symbol = m.symbol "
            f"WHERE {where} ORDER BY f.filed_date DESC"
        ).fetchall()
        sectors = db.execute("SELECT DISTINCT sector FROM filings ORDER BY sector").fetchall()
        return render_template('filings.html', filings=rows, q=q, sector=sector, sectors=sectors)

    @app.route('/filings/<int:filing_id>')
    def filing_detail(filing_id):
        redir = _require_login()
        if redir:
            return redir
        filing = get_db().execute("SELECT * FROM filings WHERE id = ?", (filing_id,)).fetchone()
        if not filing:
            return render_template('404.html'), 404
        mkt = get_db().execute(
            "SELECT * FROM market_data WHERE symbol = ?", (filing['symbol'],)
        ).fetchone()
        return render_template('filing_detail.html', filing=filing, mkt=mkt)
