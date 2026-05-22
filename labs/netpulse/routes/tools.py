import subprocess
import requests as _requests
from flask import request, render_template, session, redirect, url_for


def _require_login():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return None


def init(app):

    # VULN: SSRF — user-supplied URL fetched by the server, response reflected back
    @app.route('/tools/linkcheck', methods=['GET', 'POST'])
    def tools_linkcheck():
        redir = _require_login()
        if redir:
            return redir
        result = None
        url    = ''
        error  = None
        if request.method == 'POST':
            url = request.form.get('url', '').strip()
            if url:
                try:
                    resp   = _requests.get(url, timeout=5, allow_redirects=True)
                    result = {
                        'status':  resp.status_code,
                        'size':    len(resp.content),
                        'preview': resp.text[:2048],
                    }
                except Exception as e:
                    error = str(e)
        return render_template('linkcheck.html', url=url, result=result, error=error)

    # VULN: command injection — hostname interpolated into shell command
    @app.route('/tools/dnslookup', methods=['GET', 'POST'])
    def tools_dnslookup():
        redir = _require_login()
        if redir:
            return redir
        output   = None
        hostname = ''
        error    = None
        if request.method == 'POST':
            hostname = request.form.get('hostname', '').strip()
            if hostname:
                try:
                    output = subprocess.check_output(
                        f"nslookup {hostname}",
                        shell=True,
                        stderr=subprocess.STDOUT,
                        timeout=5,
                    ).decode(errors='replace')
                except subprocess.TimeoutExpired:
                    error = 'Lookup timed out.'
                except subprocess.CalledProcessError as e:
                    output = e.output.decode(errors='replace')
        return render_template('dnslookup.html', hostname=hostname, output=output, error=error)
