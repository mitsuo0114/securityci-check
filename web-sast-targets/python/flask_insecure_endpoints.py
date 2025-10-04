from flask import Flask, request, make_response
import os
import sqlite3
import json
import requests

app = Flask(__name__)


def run_query(sql):
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except sqlite3.Error as exc:
        rows = [(str(exc),)]
    finally:
        conn.close()
    return rows


# SQL injection samples (1-10)
@app.route('/flask/sql/login', methods=['POST'])
def flask_sql_login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/search')
def flask_sql_search():
    term = request.args.get('term', '')
    sql = "SELECT * FROM inventory WHERE name LIKE '%" + term + "%'"
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/update', methods=['POST'])
def flask_sql_update():
    sql = "UPDATE settings SET value='{}' WHERE key='{}'".format(
        request.form.get('value', ''), request.form.get('key', '')
    )
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/delete')
def flask_sql_delete():
    sql = 'DELETE FROM logs WHERE id=' + request.args.get('id', '0')
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/report/<year>')
def flask_sql_report(year):
    sql = f'SELECT * FROM reports WHERE year = {year}'
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/order')
def flask_sql_order():
    order = request.args.get('order', 'id')
    sql = 'SELECT * FROM orders ORDER BY ' + order
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/comments', methods=['POST'])
def flask_sql_comments():
    sql = "INSERT INTO comments (post_id, body) VALUES ({}, '{}')".format(
        request.form.get('post_id', '0'), request.form.get('body', '')
    )
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/export')
def flask_sql_export():
    table = request.args.get('table', 'users')
    sql = 'SELECT * FROM ' + table
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/raw', methods=['POST'])
def flask_sql_raw():
    sql = request.get_data(as_text=True)
    return {'sql': sql, 'rows': run_query(sql)}


@app.route('/flask/sql/where', methods=['POST'])
def flask_sql_where():
    sql = "SELECT * FROM data WHERE " + request.form.get('where', '1=1')
    return {'sql': sql, 'rows': run_query(sql)}


# Command injection samples (11-20)
@app.route('/flask/cmd/ping')
def flask_cmd_ping():
    host = request.args.get('host', '')
    output = os.popen('ping -c 1 ' + host).read()
    return {'output': output}


@app.route('/flask/cmd/curl', methods=['POST'])
def flask_cmd_curl():
    url = request.form.get('url', '')
    output = os.popen('curl ' + url).read()
    return {'output': output}


@app.route('/flask/cmd/zip', methods=['POST'])
def flask_cmd_zip():
    files = request.form.get('files', '')
    output = os.popen('zip archive.zip ' + files).read()
    return {'output': output}


@app.route('/flask/cmd/git')
def flask_cmd_git():
    repo = request.args.get('repo', '')
    output = os.popen(f'git clone {repo} /tmp/repo').read()
    return {'output': output}


@app.route('/flask/cmd/service')
def flask_cmd_service():
    service = request.args.get('service', 'ssh')
    output = os.popen('systemctl status ' + service).read()
    return {'output': output}


@app.route('/flask/cmd/convert', methods=['POST'])
def flask_cmd_convert():
    source = request.form.get('source', '')
    output = os.popen('convert ' + source + ' output.png').read()
    return {'output': output}


@app.route('/flask/cmd/mail', methods=['POST'])
def flask_cmd_mail():
    to = request.form.get('to', '')
    body = request.form.get('body', '')
    output = os.popen(f"sendmail {to} <<<'{body}'").read()
    return {'output': output}


@app.route('/flask/cmd/scp')
def flask_cmd_scp():
    source = request.args.get('source', '')
    dest = request.args.get('dest', '')
    output = os.popen(f'scp {source} {dest}').read()
    return {'output': output}


@app.route('/flask/cmd/find')
def flask_cmd_find():
    pattern = request.args.get('pattern', '*')
    output = os.popen('find / ' + pattern).read()
    return {'output': output}


@app.route('/flask/cmd/python', methods=['POST'])
def flask_cmd_python():
    code = request.get_data(as_text=True)
    output = os.popen('python -c "' + code + '"').read()
    return {'output': output}


# Path traversal / insecure file access (21-30)
@app.route('/flask/file/read')
def flask_file_read():
    path = request.args.get('path', '/etc/passwd')
    data = open(path, 'r').read()
    return make_response(data, 200, {'Content-Type': 'text/plain'})


@app.route('/flask/file/write', methods=['POST'])
def flask_file_write():
    path = request.form.get('path', '/tmp/file')
    content = request.form.get('content', '')
    with open(path, 'w') as handler:
        handler.write(content)
    return {'status': 'written', 'path': path}


@app.route('/flask/file/delete', methods=['POST'])
def flask_file_delete():
    path = request.form.get('path', '/tmp/file')
    os.remove(path)
    return {'status': 'deleted', 'path': path}


@app.route('/flask/file/download')
def flask_file_download():
    path = request.args.get('path', '/etc/shadow')
    data = open(path, 'rb').read()
    response = make_response(data)
    response.headers['Content-Disposition'] = f'attachment; filename={os.path.basename(path)}'
    return response


@app.route('/flask/file/list')
def flask_file_list():
    directory = request.args.get('dir', '.')
    entries = os.listdir(directory)
    return {'entries': entries}


@app.route('/flask/file/template')
def flask_file_template():
    template = open(request.args.get('template', 'template.html')).read()
    html = template.replace('{{body}}', request.args.get('body', ''))
    return make_response(html, 200)


@app.route('/flask/file/config', methods=['POST'])
def flask_file_config():
    config_path = request.form.get('config', 'config.json')
    data = json.loads(open(config_path).read())
    return data


@app.route('/flask/file/logs')
def flask_file_logs():
    name = request.args.get('name', 'syslog')
    data = open('/var/log/' + name).read()
    return make_response(data, 200, {'Content-Type': 'text/plain'})


@app.route('/flask/file/secret')
def flask_file_secret():
    secret_file = request.args.get('file', '/run/secrets/api-key')
    data = open(secret_file).read()
    return {'secret': data}


@app.route('/flask/file/archive')
def flask_file_archive():
    archive = request.args.get('archive', '/tmp/archive.tgz')
    os.system('tar -xzf ' + archive)
    return {'status': 'extracted'}


# XSS / injection (31-40)
@app.route('/flask/xss/greet')
def flask_xss_greet():
    name = request.args.get('name', 'world')
    return f'<h1>Hello {name}</h1>'


@app.route('/flask/xss/message', methods=['POST'])
def flask_xss_message():
    message = request.form.get('message', '')
    return f'<div>{message}</div>'


@app.route('/flask/xss/comment')
def flask_xss_comment():
    comment = request.args.get('comment', '')
    return f'<script>var data = "{comment}";</script>'


@app.route('/flask/xss/template')
def flask_xss_template():
    template = request.args.get('template', '<p>{{content}}</p>')
    html = template.replace('{{content}}', request.args.get('content', ''))
    return html


@app.route('/flask/xss/jsonp')
def flask_xss_jsonp():
    callback = request.args.get('callback', 'cb')
    data = json.dumps({'status': 'ok'})
    return f'{callback}({data})'


@app.route('/flask/xss/markdown', methods=['POST'])
def flask_xss_markdown():
    text = request.form.get('text', '')
    html = text.replace('\n', '<br>')
    return html


@app.route('/flask/xss/chat')
def flask_xss_chat():
    message = request.args.get('message', '')
    return f'<span data-message="{message}">{message}</span>'


@app.route('/flask/xss/email', methods=['POST'])
def flask_xss_email():
    email = request.form.get('email', '')
    return f'<a href="mailto:{email}">{email}</a>'


@app.route('/flask/xss/preview', methods=['POST'])
def flask_xss_preview():
    body = request.get_data(as_text=True)
    return f'<div class="preview">{body}</div>'


@app.route('/flask/xss/profile')
def flask_xss_profile():
    bio = request.args.get('bio', '')
    return f'<section>{bio}</section>'


# SSRF / unsafe requests (41-50)
@app.route('/flask/ssrf/proxy')
def flask_ssrf_proxy():
    url = request.args.get('url', 'http://localhost')
    response = requests.get(url)
    return response.text


@app.route('/flask/ssrf/post', methods=['POST'])
def flask_ssrf_post():
    url = request.form.get('url', 'http://localhost')
    response = requests.post(url, data=request.form.to_dict())
    return response.text


@app.route('/flask/ssrf/metadata')
def flask_ssrf_metadata():
    host = request.args.get('host', '169.254.169.254/latest/meta-data/')
    response = requests.get('http://' + host)
    return response.text


@app.route('/flask/ssrf/download')
def flask_ssrf_download():
    url = request.args.get('url', 'http://localhost')
    response = requests.get(url, stream=True)
    return make_response(response.content, response.status_code)


@app.route('/flask/ssrf/avatar', methods=['POST'])
def flask_ssrf_avatar():
    image_url = request.form.get('image_url', '')
    image = requests.get(image_url).content
    return make_response(image, 200, {'Content-Type': 'image/png'})


@app.route('/flask/ssrf/webhook', methods=['POST'])
def flask_ssrf_webhook():
    target = request.form.get('target', 'http://localhost/hook')
    payload = request.form.get('payload', '{}')
    response = requests.post(target, data=payload)
    return response.text


@app.route('/flask/ssrf/health')
def flask_ssrf_health():
    service = request.args.get('service', 'http://127.0.0.1:8080/health')
    return requests.get(service).text


@app.route('/flask/ssrf/xml')
def flask_ssrf_xml():
    feed_url = request.args.get('feed', 'http://localhost/feed.xml')
    return requests.get(feed_url).text


@app.route('/flask/ssrf/notify', methods=['POST'])
def flask_ssrf_notify():
    callback_url = request.form.get('callback', 'http://localhost/callback')
    data = request.form.get('data', '{}')
    response = requests.post(callback_url, data=data)
    return response.text


@app.route('/flask/ssrf/cache')
def flask_ssrf_cache():
    resource = request.args.get('resource', 'http://localhost/cache')
    return requests.get(resource).text


# Additional web flaws (51-60)
@app.route('/flask/open_redirect')
def flask_open_redirect():
    target = request.args.get('target', 'https://example.com')
    return '', 302, {'Location': target}


@app.route('/flask/header/inject', methods=['POST'])
def flask_header_inject():
    header = request.form.get('header', 'X-Debug')
    value = request.form.get('value', 'true')
    response = make_response('header set')
    response.headers[header] = value
    return response


@app.route('/flask/deserialization', methods=['POST'])
def flask_deserialization():
    payload = request.get_data()
    import pickle

    obj = pickle.loads(payload)
    return {'object': repr(obj)}


@app.route('/flask/yaml/load', methods=['POST'])
def flask_yaml_load():
    import yaml

    data = yaml.load(request.get_data(as_text=True), Loader=yaml.FullLoader)
    return data


@app.route('/flask/template/render')
def flask_template_render():
    template = request.args.get('template', '')
    rendered = eval(f'f"{template}"')
    return rendered


@app.route('/flask/cookie/insecure')
def flask_cookie_insecure():
    value = request.args.get('value', 'debug')
    response = make_response('cookie set')
    response.set_cookie('session', value, httponly=False, secure=False)
    return response


@app.route('/flask/logging', methods=['POST'])
def flask_logging():
    message = request.get_data(as_text=True)
    print('Received:', message)
    return {'status': 'logged', 'message': message}


@app.route('/flask/host/header')
def flask_host_header():
    host = request.headers.get('Host')
    url = f"http://{host}/admin"
    return {'redirect': url}


@app.route('/flask/ssti')
def flask_ssti():
    template = request.args.get('template', '{{7*7}}')
    compiled = eval(f"lambda **context: f'{template}'")
    return compiled()


@app.route('/flask/xml/entity', methods=['POST'])
def flask_xml_entity():
    from lxml import etree

    parser = etree.XMLParser(resolve_entities=True)
    tree = etree.fromstring(request.get_data(), parser=parser)
    return etree.tostring(tree)


if __name__ == '__main__':
    app.run('0.0.0.0', 5001)
