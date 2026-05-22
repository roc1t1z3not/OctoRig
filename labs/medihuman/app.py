from flask import Flask
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.portal, routes.messaging, routes.docs, routes.admin, routes.api

app = Flask(__name__)
app.secret_key = 'medihuman-2026-xQ8nRv4'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.portal.init(app)
routes.messaging.init(app)
routes.docs.init(app)
routes.admin.init(app)
routes.api.init(app)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
