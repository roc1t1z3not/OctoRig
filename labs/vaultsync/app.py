# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from flask import Flask, Response
from db import init_db, close_db
from helpers import current_user
import routes.auth, routes.dashboard, routes.vaults
import routes.sharing, routes.admin, routes.api

app = Flask(__name__)
app.secret_key = 'vaultsync-saas-2026-Lp9xWq'
app.teardown_appcontext(close_db)
app.jinja_env.globals.update(current_user=current_user)

routes.auth.init(app)
routes.dashboard.init(app)
routes.vaults.init(app)
routes.sharing.init(app)
routes.admin.init(app)
routes.api.init(app)


@app.route('/robots.txt')
def robots_txt():
    return Response(
        "User-agent: *\n"
        "Disallow: /admin\n"
        "Disallow: /admin/recovery-codes\n"
        "Disallow: /api/internal\n\n"
        "# VaultSync — CommonHuman-Lab\n"
        "# Deliberately vulnerable — do not store real credentials.\n",
        mimetype='text/plain'
    )


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=80, debug=False)
