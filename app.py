import os
import json
import random
import psycopg2

from flask import Flask
from flask_heroku import Heroku
import os
app = Flask(__name__)
app.debug = True
heroku = Heroku(app)
def create_conn():
    conn = None
    if os.environ.has_key("DATABASE_URL"):
        username = os.environ["DATABASE_URL"].split(":")[1].replace("//","")
        password = os.environ["DATABASE_URL"].split(":")[2].split("@")[0]
        host = os.environ["DATABASE_URL"].split(":")[2].split("@")[1].split("/")[0]
        dbname = os.environ["DATABASE_URL"].split(":")[2].split("@")[1].split("/")[1] 
        conn = psycopg2.connect(dbname=dbname, user=username, password=password, host=host) 
    else:
        import sqlite3
        conn = sqlite3.connect('/tmp/notely-test.db')
    return conn

def get_sync_code():
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    code = ""
    for i in xrange(0, 4):
        code += random.choice(alpha) 
    return code


def write_pair_request(uuid, code):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pairing VALUES (%s, %s)", (code, uuid));
    conn.commit()

def get_pair_request_uuid(code):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pairing WHERE code=%s", (code,))
    result = cursor.fetchone()
    if result == None:
        return None
    else:
        return result[1]


def delete_pair_request(code):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pairing WHERE code=%s", (code,))
    conn.commit()

@app.route('/startpair/<uuid>')
def startpair(uuid):
    global sync_ids
    u = str(uuid)
    unique_code = get_sync_code()
    write_pair_request(u, unique_code)
    return json.dumps({"code":unique_code}) 
    
@app.route('/endpair/<unique_code>')
def endpair(unique_code):
    global sync_ids
    code = str(unique_code)
    uuid = get_pair_request_uuid(code)
    if (uuid != None):
        delete_pair_request(code);
        return json.dumps({"uuid":uuid})
    else:
        return json.dumps({"err":"no pairing request matches that code"}) 
        

@app.route("/sync", methods="POST")
def sync():
    data = request.form["data"]

@app.route("/")
def index():
    return "bees"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
