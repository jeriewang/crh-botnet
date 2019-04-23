from flask import Flask, request, render_template, current_app, g
import os, sqlite3

app = Flask(__name__)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('robots.sqlite3')
        g.db.row_factory = sqlite3.Row
    
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.commit()
        db.close()


@app.route('/api/connect', methods=['PUT'])
def connect():
    return '', 204

