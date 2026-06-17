# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from datetime import datetime
from flask import request, render_template, session, redirect, url_for
from db import get_db


def _require_login():
    if not session.get('operator_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: MQTT/IoT command injection — the operator is only supposed to publish
    # to their own zone's command topic (grid/zone/<their_zone>/cmd), but the full
    # topic is taken from the request. Publishing to another zone's topic (or a
    # wildcard) lets you issue grid commands to devices you don't control.
    @app.route('/mqtt', methods=['GET', 'POST'])
    def mqtt_console():
        redir = _require_login()
        if redir:
            return redir
        db   = get_db()
        uid  = session['operator_id']
        op   = db.execute("SELECT * FROM operators WHERE id = ?", (uid,)).fetchone()
        own_topic = f"grid/zone/{op['zone_id']}/cmd"
        result = None
        flag   = None

        if request.method == 'POST':
            topic   = request.form.get('topic', own_topic).strip()
            payload = request.form.get('payload', '').strip()
            now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            db.execute(
                "INSERT INTO mqtt_log (topic, payload, published_by, created_at) VALUES (?, ?, ?, ?)",
                (topic, payload, uid, now),
            )
            db.commit()
            result = {'topic': topic, 'payload': payload}

            # Publishing outside your own zone topic (cross-zone / wildcard) trips
            # the broker ACL audit and leaks the flag.
            crosses_zone = (topic != own_topic) and topic.startswith('grid/zone/')
            wildcard     = ('#' in topic) or ('+' in topic)
            if crosses_zone or wildcard:
                row = db.execute("SELECT value FROM _flags WHERE name = 'mqtt-inject'").fetchone()
                flag = row['value'] if row else None

        log = db.execute(
            "SELECT * FROM mqtt_log ORDER BY id DESC LIMIT 15"
        ).fetchall()
        return render_template(
            'mqtt.html',
            own_topic=own_topic, result=result, flag=flag, log=log,
        )
