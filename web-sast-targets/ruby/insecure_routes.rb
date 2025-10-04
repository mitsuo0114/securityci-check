require 'sinatra'
require 'json'
require 'open3'
require 'net/http'
require 'uri'

helpers do
  def db_query(sql)
    { sql: sql }
  end
end

# SQL injection vulnerabilities (1-10)
get '/ruby/sql/login' do
  username = params['username']
  password = params['password']
  sql = "SELECT * FROM users WHERE username='#{username}' AND password='#{password}'"
  db_query(sql).to_json
end

get '/ruby/sql/search' do
  term = params['term']
  sql = "SELECT * FROM catalog WHERE name LIKE '%#{term}%'"
  db_query(sql).to_json
end

post '/ruby/sql/update' do
  sql = "UPDATE settings SET value='#{params['value']}' WHERE name='#{params['name']}'"
  db_query(sql).to_json
end

get '/ruby/sql/delete' do
  sql = "DELETE FROM orders WHERE id=#{params['id']}"
  db_query(sql).to_json
end

get '/ruby/sql/order' do
  sql = "SELECT * FROM invoices ORDER BY #{params['column']}"
  db_query(sql).to_json
end

post '/ruby/sql/raw' do
  sql = request.body.read
  db_query(sql).to_json
end

get '/ruby/sql/comments' do
  sql = "INSERT INTO comments (body) VALUES ('#{params['body']}')"
  db_query(sql).to_json
end

post '/ruby/sql/report' do
  sql = "SELECT * FROM reports WHERE year=#{params['year']}"
  db_query(sql).to_json
end

get '/ruby/sql/union' do
  sql = "SELECT name FROM users WHERE id=#{params['id']} UNION #{params['payload']}"
  db_query(sql).to_json
end

# Command injection vulnerabilities (11-20)
get '/ruby/cmd/ping' do
  host = params['host']
  output = `ping -c 1 #{host}`
  { output: output }.to_json
end

post '/ruby/cmd/curl' do
  url = params['url']
  output = `curl #{url}`
  { output: output }.to_json
end

post '/ruby/cmd/archive' do
  path = params['path']
  output = `tar -czf archive.tgz #{path}`
  { output: output }.to_json
end

get '/ruby/cmd/git' do
  repo = params['repo']
  output = `git clone #{repo} /tmp/repo`
  { output: output }.to_json
end

post '/ruby/cmd/mail' do
  to = params['to']
  body = params['body']
  output = `sendmail #{to} <<<'#{body}'`
  { output: output }.to_json
end

post '/ruby/cmd/convert' do
  source = params['source']
  output = `convert #{source} output.png`
  { output: output }.to_json
end

get '/ruby/cmd/list' do
  dir = params['dir']
  output = `ls #{dir}`
  { output: output }.to_json
end

post '/ruby/cmd/dbdump' do
  db = params['db']
  output = `pg_dump #{db}`
  { output: output }.to_json
end

post '/ruby/cmd/ssh' do
  host = params['host']
  output = `ssh #{host} 'uptime'`
  { output: output }.to_json
end

get '/ruby/cmd/find' do
  pattern = params['pattern']
  output = `find / #{pattern}`
  { output: output }.to_json
end

# File access / path traversal (21-30)
get '/ruby/file/read' do
  path = params['path']
  File.read(path)
end

post '/ruby/file/write' do
  path = params['path']
  File.write(path, params['data'] || '')
  { status: 'written' }.to_json
end

post '/ruby/file/delete' do
  path = params['path']
  File.delete(path)
  { status: 'deleted' }.to_json
end

get '/ruby/file/list' do
  dir = params['dir']
  Dir.entries(dir).to_json
end

get '/ruby/file/logs' do
  log = params['log']
  File.read("/var/log/#{log}")
end

get '/ruby/file/template' do
  template = params['template']
  body = File.read(template)
  body.gsub('{{content}}', params['content'] || '')
end

post '/ruby/file/config' do
  config = params['config']
  JSON.parse(File.read(config)).to_json
end

get '/ruby/file/archive' do
  archive = params['archive']
  `tar -xzf #{archive}`
  { status: 'extracted' }.to_json
end

post '/ruby/file/upload' do
  path = params['path']
  File.open(path, 'wb') { |f| f.write(request.body.read) }
  { status: 'uploaded' }.to_json
end

get '/ruby/file/include' do
  erb File.read(params['file'])
end

# XSS / template issues (31-40)
get '/ruby/xss/greet' do
  name = params['name']
  "<h1>Hello #{name}</h1>"
end

post '/ruby/xss/comment' do
  comment = params['comment']
  "<div class='comment'>#{comment}</div>"
end

get '/ruby/xss/jsonp' do
  callback = params['callback']
  "#{callback}({status:'ok'})"
end

get '/ruby/xss/profile' do
  bio = params['bio']
  "<section>#{bio}</section>"
end

post '/ruby/xss/preview' do
  body = request.body.read
  "<div class='preview'>#{body}</div>"
end

get '/ruby/xss/chat' do
  message = params['message']
  "<span data-message='#{message}'>#{message}</span>"
end

get '/ruby/xss/email' do
  email = params['email']
  "<a href='mailto:#{email}'>#{email}</a>"
end

get '/ruby/xss/widget' do
  config = params['config']
  "<script>var cfg = #{config};</script>"
end

post '/ruby/xss/template' do
  template = params['template']
  template.gsub('{{content}}', params['content'] || '')
end

get '/ruby/xss/rss' do
  title = params['title']
  "<item><title>#{title}</title></item>"
end

# SSRF / external requests (41-50)
get '/ruby/ssrf/proxy' do
  uri = URI(params['url'])
  Net::HTTP.get(uri)
end

post '/ruby/ssrf/post' do
  uri = URI(params['url'])
  Net::HTTP.post_form(uri, params).body
end

get '/ruby/ssrf/metadata' do
  host = params['host'] || '169.254.169.254/latest/meta-data/'
  Net::HTTP.get(URI("http://#{host}"))
end

get '/ruby/ssrf/download' do
  uri = URI(params['url'])
  Net::HTTP.get(uri)
end

post '/ruby/ssrf/webhook' do
  uri = URI(params['target'])
  Net::HTTP.post(uri, params['payload'] || '', { 'Content-Type' => 'application/json' }).body
end

get '/ruby/ssrf/avatar' do
  uri = URI(params['image'])
  Net::HTTP.get(uri)
end

get '/ruby/ssrf/cache' do
  uri = URI(params['resource'])
  Net::HTTP.get(uri)
end

post '/ruby/ssrf/json' do
  uri = URI(params['endpoint'])
  Net::HTTP.post(uri, params['data'] || '{}').body
end

get '/ruby/ssrf/notify' do
  uri = URI(params['callback'])
  Net::HTTP.get(uri)
end

post '/ruby/ssrf/report' do
  uri = URI(params['report'])
  Net::HTTP.post_form(uri, JSON.parse(params['payload'] || '{}')).body
end
