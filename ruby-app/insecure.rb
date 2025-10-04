# Intentionally vulnerable Ruby code
require 'sinatra'
require 'json'

set :bind, '0.0.0.0'
set :port, 4567

def users
  @users ||= [{ username: 'admin', password: 'admin' }]
end

get '/' do
  'Vulnerable Ruby app'
end

get '/exec' do
  cmd = params['cmd'] || 'ls'
  `#{cmd}`
end

post '/login' do
  data = JSON.parse(request.body.read)
  username = data['username']
  password = data['password']
  user = users.find { |u| u[:username] == username && u[:password] == password }
  if user
    session_token = "token-#{rand(1000)}"
    response.set_cookie('session', session_token, secure: false, http_only: false)
    "Welcome #{username}!"
  else
    halt 401, 'Invalid credentials'
  end
end

post '/load' do
  file = params['file']
  eval(File.read(file))
end
