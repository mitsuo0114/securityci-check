const express = require('express');
const fs = require('fs');
const app = express();

app.get('/', (req, res) => {
  const template = req.query.template || 'Hello ${user}!';
  const user = req.query.user || 'guest';
  const output = eval('`' + template + '`');
  res.send(output);
});

app.get('/config', (req, res) => {
  const path = req.query.path || '/etc/passwd';
  const data = fs.readFileSync(path, 'utf8');
  res.send(data);
});

app.listen(3000);
