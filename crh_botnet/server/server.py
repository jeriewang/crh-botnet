from flask import Flask, request, render_template, make_response, g, jsonify
from werkzeug.serving import WSGIRequestHandler
from datetime import datetime, timedelta
import os, sqlite3, secrets, re
from crh_botnet.message import Message

app = Flask(__name__)


def initialize():
    conn = sqlite3.connect('robots.sqlite3', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS robots (
            id INTEGER PRIMARY KEY,
            token CHAR(16) UNIQUE,
            last_seen TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender INTEGER NOT NULL,
            recipient INTEGER NOT NULL,
            content TEXT,
            time_created TIMESTAMP  NOT NULL,
            retrieved BOOL DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('robots.sqlite3', detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    
    return g.db


def get_robot_id(request, cursor):
    auth = request.headers.get('Authorization', '')
    match = re.match(r'Token ([a-f0-9]{16})', auth)
    if match:
        token = match.group(1)
        cursor.execute("SELECT id FROM robots WHERE token=?", (token,))
        res = cursor.fetchone()
        return res['id'] if res else None
    return None


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.commit()
        db.close()


@app.route('/api/connect', methods=['POST'])
def connect():
    try:
        # print(request.get_json())
        robot_id = int(request.json['id'])
        db = get_db()
        c = db.cursor()
        c.execute('DELETE FROM robots WHERE id=? AND last_seen<?', (robot_id, datetime.now() - timedelta(seconds=30)))
        c.execute('SELECT * FROM robots WHERE id=?', (robot_id,))
        if c.fetchone():
            return 'A robot with the same id is connected', 403
        token = secrets.token_hex(8)
        c.execute('INSERT INTO robots (id, token, last_seen) VALUES (?,?,?)', (robot_id, token, datetime.now()))
        return jsonify({'token': token})
    except:
        return 'Bad request', 400


@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    db = get_db()
    c = db.cursor()
    id = get_robot_id(request, c)
    if id is not None:
        c.execute('DELETE FROM robots WHERE id=?', (id,))
        return '', 204
    return 'Unauthorized', 401


@app.route('/api/poll', methods=['GET'])
def poll():
    # print(request.get_data())
    # print(request.headers)
    db = get_db()
    c = db.cursor()
    id = get_robot_id(request, c)
    res = {'messages': [], 'robots': []}
    if id is not None:
        c.execute("SELECT id,sender,content, time_created,recipient FROM messages WHERE recipient=? AND retrieved=0", (id,))
        for row in c.fetchall():
            res['messages'].append(Message.from_db_record(row).to_dict())
            # c.execute('UPDATE messages SET retrieved=1 WHERE id=?',(row['id'],))
            c.execute('DELETE FROM messages WHERE id=?', (row['id'],))
        # c.execute('UPDATE messages SET retrieved=1 WHERE recipient=?',(id,))
        # if there's a race condition we may drop a message or few
        c.execute('SELECT id FROM robots')
        for row in c.fetchall():
            res['robots'].append(row['id'])
        c.execute('UPDATE robots SET last_seen=? WHERE id=?', (datetime.now(), id))
        db.commit()
        return jsonify(res)
    return 'Unauthorized', 401


@app.route('/api/send', methods=['PUT'])
def send():
    db = get_db()
    c = db.cursor()
    id = get_robot_id(request, c)
    try:
        # print(request)
        # print(request.headers)
        # print(request.get_data())
        msg = Message.from_dict(request.get_json())
    except KeyError:
        return 'Bad Request', 400
    
    if id is not None:
        if msg.sender != id:
            return 'Unauthorized', 401
        
        if msg.recipient == -1:
            c.execute('SELECT id FROM robots')
            for row in c.fetchall():
                if row['id'] != id:
                    c.execute('INSERT INTO messages (sender, recipient, content, time_created) VALUES'
                              '(?,?,?,?)', (id, row['id'], msg.content, msg.time_created))
        else:
            c.execute('INSERT INTO messages (sender, recipient, content, time_created) VALUES'
                      '(?,?,?,?)', (id, msg.recipient, msg.content, msg.time_created))
        db.commit()
        return make_response('', 201)
    return 'Unauthorized', 401


if __name__ == '__main__':
    initialize()
    WSGIRequestHandler.protocol_version = "HTTP/1.1"  # for keep-alive
    app.run(port=5003)
