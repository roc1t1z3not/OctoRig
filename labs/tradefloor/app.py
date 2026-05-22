from flask import Flask
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.portfolio, routes.trading, routes.watchlist
import routes.filings, routes.alerts, routes.admin, routes.api

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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
