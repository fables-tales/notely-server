import os
import json
import random
import psycopg2

from flask import Flask, request
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


def get_user_actions(user):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT actions FROM useractions WHERE user=%s", (user,))
    result = cursor.fetchone()
    if result == None:
        return None
    else:
        return result[0]


def create_user_actions(uuid):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO useractions VALUES (%s, '')", (uuid,))
    conn.commit()

def combine_user_actions(existing, new):
    for action in new["actions"]:
        if action not in existing["actions"]:
            existing["actions"].append(action)

def save_user_actions(uuid, actions):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE useractions SET actions=%s WHERE uuid=%s", (json.dumps(actions), uuid))
    conn.commit()

def encode_user_actions(uuid, actions):
    dict = {}
    dict["user-id"] = uuid
    dict["actions"] = actions
    new_messages = []
    sorted_actions = sorted(actions["actions"], lambda x,y:int(x["time"] - y["time"])) 

    for action in sorted_actions:
        if action.has_key("add"):
            new_messages.append({"message": action["add"], "id":len(new_messages)+1}) 
        if action.has_key("del"):
            for message in new_messages:
                if message["message"] == action["del"]:
                    new_messages.remove(message)
                    break
    dict["messages"] = new_messages
    return dict

            

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
        

@app.route("/sync", methods=["POST"])
def sync():
    data = request.form["actions"]
#    try:
    if True:
        obj = json.loads(data)
        uuid = request.form["uuid"] 
        actions = get_user_actions(uuid)
        if actions == None:
            create_user_actions(uuid)
            actions = json.dumps({"actions":[]})
        actions = json.loads(actions)
        combine_user_actions(actions, obj)
        save_user_actions(uuid, actions)
        return json.dumps(encode_user_actions(uuid, actions))
        
#    except:
#        return json.dumps({"err":"couldn't sync"})

@app.route("/")
def index():
    return "bees"

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
