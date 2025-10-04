"""Intentionally vulnerable Flask application for security scanners."""
from flask import Flask, request
import os
import sqlite3

app = Flask(__name__)

DATABASE = "users.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute(
        "INSERT INTO users (username, password) VALUES ('admin', 'admin')"
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return "Welcome to the vulnerable app!"


@app.route("/search")
def search():
    query = request.args.get("q", "")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    sql = f"SELECT username, password FROM users WHERE username = '{query}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return {"results": result, "query": query, "sql": sql}


@app.route("/run")
def run_command():
    command = request.args.get("cmd", "echo no command provided")
    return os.popen(command).read()


@app.route("/configure", methods=["POST"])
def configure():
    data = request.get_json() or {}
    secret = data.get("api_key", "")
    os.environ["EXTERNAL_SERVICE_KEY"] = secret
    exec(data.get("code", ""))
    return {"status": "configured", "secret": secret}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
