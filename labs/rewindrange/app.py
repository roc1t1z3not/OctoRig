from flask import Flask
from db import init_db, close_db
from helpers import current_user, cart_count, product_rating
import routes.auth, routes.shop, routes.account, routes.feedback, routes.api, routes.admin, routes.board, routes.inbox

app = Flask(__name__)
app.secret_key = 'rewind-range-2026-xK9mPv3'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(
    current_user=current_user,
    cart_count=cart_count,
    product_rating=product_rating,
)

routes.auth.init(app)
routes.shop.init(app)
routes.account.init(app)
routes.feedback.init(app)
routes.api.init(app)
routes.admin.init(app)
routes.board.init(app)
routes.inbox.init(app)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
