const express = require('express');
const fs = require('fs');
const childProcess = require('child_process');
const axios = require('axios');

const app = express();
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

const db = {
  query(sql, params, cb) {
    if (typeof params === 'function') {
      cb = params;
    }
    setImmediate(() => cb(null, []));
  }
};

const User = {
  find(query) {
    return Promise.resolve([]);
  },
  aggregate(pipeline) {
    return Promise.resolve([]);
  }
};

function render(res, body) {
  res.send(body);
}

// Classic SQL injection samples (1-10)
app.get('/vulns/sql/basic', (req, res) => {
  const username = req.query.user || '';
  const sql = "SELECT * FROM accounts WHERE username = '" + username + "'";
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.post('/vulns/sql/login', (req, res) => {
  const { username, password } = req.body;
  const sql = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.get('/vulns/sql/search', (req, res) => {
  const term = req.query.q || '';
  const sql = "SELECT * FROM products WHERE name LIKE '%" + term + "%'";
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.get('/vulns/sql/report/:year', (req, res) => {
  const sql = `SELECT * FROM reports WHERE year = ${req.params.year}`;
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.post('/vulns/sql/profile/update', (req, res) => {
  const { bio, userId } = req.body;
  const sql = `UPDATE profiles SET bio='${bio}' WHERE id=${userId}`;
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.get('/vulns/sql/delete', (req, res) => {
  const id = req.query.id;
  const sql = 'DELETE FROM sessions WHERE id=' + id;
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.post('/vulns/sql/audit', (req, res) => {
  const { level } = req.body;
  const sql = "SELECT * FROM audit WHERE severity='" + level + "'";
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.get('/vulns/sql/comment', (req, res) => {
  const article = req.query.article;
  const sql = `INSERT INTO comments (article_id, body) VALUES (${article}, '${req.query.body}')`;
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.get('/vulns/sql/order', (req, res) => {
  const column = req.query.column;
  const sql = 'SELECT * FROM invoices ORDER BY ' + column + ' DESC';
  db.query(sql, (err, rows) => render(res, { sql, rows }));
});

app.post('/vulns/sql/raw', (req, res) => {
  const sql = req.body.sql;
  db.query('SELECT * FROM (' + sql + ') sub', (err, rows) => render(res, { sql, rows }));
});

// NoSQL injection samples (11-20)
app.post('/vulns/nosql/login', (req, res) => {
  const { username, password } = req.body;
  const query = { username: username, password: password };
  User.find(query).then(rows => render(res, { query, rows }));
});

app.post('/vulns/nosql/search', (req, res) => {
  const query = JSON.parse(req.body.filter || '{}');
  User.find(query).then(rows => render(res, { query, rows }));
});

app.get('/vulns/nosql/profile/:field', (req, res) => {
  const projection = '{ "' + req.params.field + '": 1 }';
  const pipeline = [{ $project: JSON.parse(projection) }];
  User.aggregate(pipeline).then(rows => render(res, { pipeline, rows }));
});

app.post('/vulns/nosql/regex', (req, res) => {
  const filter = { email: { $regex: req.body.regex } };
  User.find(filter).then(rows => render(res, { filter, rows }));
});

app.post('/vulns/nosql/admin-check', (req, res) => {
  const query = { role: req.body.role || { $ne: 'guest' } };
  User.find(query).then(rows => render(res, { query, rows }));
});

app.post('/vulns/nosql/match', (req, res) => {
  const pipeline = [{ $match: JSON.parse(req.body.match || '{}') }];
  User.aggregate(pipeline).then(rows => render(res, { pipeline, rows }));
});

app.get('/vulns/nosql/sort', (req, res) => {
  const pipeline = [{ $sort: JSON.parse(req.query.sort || '{"score": -1}') }];
  User.aggregate(pipeline).then(rows => render(res, { pipeline, rows }));
});

app.post('/vulns/nosql/update', (req, res) => {
  const query = JSON.parse(req.body.where || '{}');
  const update = JSON.parse(req.body.set || '{}');
  User.find({ query, update }).then(rows => render(res, { query, update, rows }));
});

app.post('/vulns/nosql/inject-or', (req, res) => {
  const query = { $or: [{ username: req.body.username }, JSON.parse(req.body.payload || '{}')] };
  User.find(query).then(rows => render(res, { query, rows }));
});

app.post('/vulns/nosql/mapreduce', (req, res) => {
  const map = req.body.map;
  const reduce = req.body.reduce;
  const pipeline = [{ $map: map }, { $reduce: reduce }];
  User.aggregate(pipeline).then(rows => render(res, { pipeline, rows }));
});

// Command injection samples (21-30)
app.get('/vulns/cmd/ping', (req, res) => {
  const host = req.query.host;
  childProcess.exec('ping -c 1 ' + host, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/curl', (req, res) => {
  const url = req.body.url;
  childProcess.exec(`curl ${url}`, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/backup', (req, res) => {
  const path = req.body.path;
  const cmd = 'tar -czf backup.tgz ' + path;
  childProcess.exec(cmd, (err, stdout) => render(res, stdout));
});

app.get('/vulns/cmd/list', (req, res) => {
  const dir = req.query.dir;
  childProcess.exec('ls ' + dir, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/git', (req, res) => {
  const repo = req.body.repo;
  childProcess.exec(`git clone ${repo} temp_repo`, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/dbdump', (req, res) => {
  const database = req.body.database;
  childProcess.exec('pg_dump ' + database, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/mail', (req, res) => {
  const to = req.body.to;
  const message = req.body.message;
  const cmd = `sendmail ${to} <<<'${message}'`;
  childProcess.exec(cmd, (err, stdout) => render(res, stdout));
});

app.get('/vulns/cmd/service', (req, res) => {
  const service = req.query.service;
  childProcess.exec('systemctl status ' + service, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/archive', (req, res) => {
  const files = req.body.files || '';
  childProcess.exec('zip archive.zip ' + files, (err, stdout) => render(res, stdout));
});

app.post('/vulns/cmd/convert', (req, res) => {
  const input = req.body.input;
  childProcess.exec('convert ' + input + ' output.png', (err, stdout) => render(res, stdout));
});

// File handling / path traversal samples (31-40)
app.get('/vulns/path/read', (req, res) => {
  const filePath = req.query.file;
  fs.readFile(filePath, 'utf8', (err, data) => render(res, data || err));
});

app.post('/vulns/path/write', (req, res) => {
  const filePath = req.body.path;
  fs.writeFile(filePath, req.body.contents, err => render(res, err || 'written'));
});

app.get('/vulns/path/append', (req, res) => {
  const file = req.query.file;
  fs.appendFile(file, req.query.data || '', err => render(res, err || 'appended'));
});

app.post('/vulns/path/delete', (req, res) => {
  const file = req.body.file;
  fs.unlink(file, err => render(res, err || 'deleted'));
});

app.post('/vulns/path/stream', (req, res) => {
  const file = req.body.file;
  const stream = fs.createReadStream(file);
  stream.pipe(res);
});

app.get('/vulns/path/template', (req, res) => {
  const template = fs.readFileSync(req.query.template || 'default.html', 'utf8');
  const html = template.replace('{{content}}', req.query.content || '');
  render(res, html);
});

app.post('/vulns/path/download', (req, res) => {
  const file = req.body.file;
  res.download(file);
});

app.get('/vulns/path/logs', (req, res) => {
  const name = req.query.name;
  const log = fs.readFileSync('/var/log/' + name, 'utf8');
  render(res, log);
});

app.post('/vulns/path/config', (req, res) => {
  const config = req.body.file;
  const json = JSON.parse(fs.readFileSync(config, 'utf8'));
  render(res, json);
});

app.get('/vulns/path/archive', (req, res) => {
  const archive = req.query.archive;
  childProcess.exec('tar -xzf ' + archive + ' -C /tmp', (err, stdout) => render(res, stdout));
});

// Dynamic code execution / template injection (41-45)
app.post('/vulns/eval/js', (req, res) => {
  const script = req.body.script;
  const result = eval(script);
  render(res, { result });
});

app.post('/vulns/eval/function', (req, res) => {
  const body = req.body.body;
  const fn = new Function('req', 'res', body);
  fn(req, res);
});

app.post('/vulns/eval/template', (req, res) => {
  const template = req.body.template || '';
  const compiled = new Function('data', `with(data){ return \`${template}\`; }`);
  render(res, compiled(req.body));
});

app.get('/vulns/eval/jsonp', (req, res) => {
  const callback = req.query.callback;
  render(res, `${callback}({"status":"ok"})`);
});

app.post('/vulns/eval/yaml', (req, res) => {
  const yaml = require('js-yaml');
  const data = yaml.load(req.body.yaml);
  render(res, data);
});

// SSRF samples (46-50)
app.get('/vulns/ssrf/fetch', async (req, res) => {
  const target = req.query.url;
  const response = await axios.get(target);
  render(res, response.data);
});

app.post('/vulns/ssrf/post', async (req, res) => {
  const target = req.body.url;
  const response = await axios.post(target, req.body.payload || {});
  render(res, response.data);
});

app.get('/vulns/ssrf/metadata', async (req, res) => {
  const host = req.query.host || '169.254.169.254/latest/meta-data/iam/security-credentials/';
  const response = await axios.get('http://' + host);
  render(res, response.data);
});

app.post('/vulns/ssrf/proxy', async (req, res) => {
  const target = req.body.target;
  const method = req.body.method || 'GET';
  const response = await axios({ url: target, method, data: req.body.body });
  render(res, response.data);
});

app.get('/vulns/ssrf/image', async (req, res) => {
  const imageUrl = req.query.image;
  const response = await axios.get(imageUrl, { responseType: 'arraybuffer' });
  res.set('Content-Type', 'image/png');
  res.send(response.data);
});

// Additional web flaws (51-60)
app.get('/vulns/xss/greeting', (req, res) => {
  const name = req.query.name || 'guest';
  res.send(`<h1>Welcome ${name}</h1>`);
});

app.get('/vulns/open-redirect', (req, res) => {
  const redirectTo = req.query.next || 'https://example.com';
  res.redirect(redirectTo);
});

app.post('/vulns/header/inject', (req, res) => {
  const headerName = req.body.name || 'X-Debug';
  const value = req.body.value || 'test';
  res.set(headerName, value);
  res.send('header set');
});

app.post('/vulns/jwt/decode', (req, res) => {
  const token = req.body.token || '';
  const segments = token.split('.');
  const payload = Buffer.from(segments[1] || '', 'base64').toString('utf8');
  res.send(payload);
});

app.post('/vulns/prototype/pollution', (req, res) => {
  const payload = req.body;
  const target = {};
  Object.assign(target, payload);
  res.send(target);
});

app.post('/vulns/deserialization', (req, res) => {
  const serialized = req.body.payload || '';
  const obj = eval('(' + serialized + ')');
  res.send(obj);
});

app.get('/vulns/cookie/unsafe', (req, res) => {
  const value = req.query.value || 'debug';
  res.cookie('session', value, { httpOnly: false, secure: false });
  res.send('cookie set');
});

app.post('/vulns/csrf/token', (req, res) => {
  const token = req.body.token;
  res.send(`CSRF token accepted: ${token}`);
});

app.post('/vulns/logging', (req, res) => {
  const message = req.body.message;
  console.log('User message:', message);
  res.send('logged');
});

app.get('/vulns/template/render', (req, res) => {
  const view = req.query.view || '';
  const renderFn = new Function(`return \`${view}\`;`);
  res.send(renderFn());
});

module.exports = app;
