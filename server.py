from flask import Flask, request, jsonify
import hashlib
import os
from random import randrange
import joblib

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')

def generate_token():
    return randrange(100000, 999999)

def encode(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def authorize_login(token):
    for login in authorized_logins:
        if login['token'] == token:
            return True
    return False

def get_username(token):
    for login in authorized_logins:
        if login['token'] == token:
            return login['username']
    raise KeyError('No authorized user with that token')

def load_labels():
    label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
    return label_encoder.classes_.tolist()

labels = load_labels()
users = {
    'Sebastian': encode('Sebastian'),
    'Rafal': encode('Rafal'),
    'Michal': encode('Michal'),
    'Lukasz': encode('Lukasz')
}
ban_list = dict((k, []) for (k, v) in users.items())
authorized_logins = []


app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    if username in users and users[username] == password:
        for login in authorized_logins:
            if login['username'] == username:
                return login['token'], 200

        token = str(generate_token())
        authorized_logins.append({ 'token': token, 'username': username })
        return token, 200
    else:
        return '', 401

@app.route('/logout', methods=['GET'])
def logout():
    token = request.args.get('token')
    if not authorize_login(token): return '', 401

    for login in authorized_logins:
        if login['token'] == token:
            authorized_logins.remove(login)
    
    return '', 200

@app.route('/user_ban_list', methods=['GET'])
def get_user_ban_list():
    token = request.args.get('token')
    if not authorize_login(token): return '', 401
    username = get_username(token)

    return jsonify(ban_list[username]), 200

@app.route('/ban_list', methods=['PUT'])
def update_ban_list():
    data = request.get_json()
    token = str(data['token'])
    if not authorize_login(token): return '', 401
    user = data['user']
    bans = data['bans']

    if user not in users: return '', 404

    ban_list[user] = bans

    return jsonify(ban_list[user]), 200

@app.route('/ban_list', methods=['GET'])
def get_ban_list():
    token = request.args.get('token')
    if not authorize_login(token): return '', 401

    return jsonify(ban_list), 200

@app.route('/labels', methods=['GET'])
def get_labels():
    token = request.args.get('token')
    if not authorize_login(token): return '', 401

    return jsonify(labels), 200

if __name__ == '__main__':
    app.run(port=5000)
