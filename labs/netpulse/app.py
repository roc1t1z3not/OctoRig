from flask import Flask
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.account, routes.tools, routes.billing
import routes.tickets, routes.board, routes.admin, routes.api

app = Flask(__name__)
app.secret_key = 'netpulse-1998-xT7kLm9'
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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
