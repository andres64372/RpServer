from flask import Flask, request, jsonify, render_template, redirect
# from flask_mqtt import Mqtt
from flask_cors import CORS
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import bcrypt
import jwt
import urllib.parse
import datetime
import os
import threading

from conf import settings
from repos.sync import sync
from repos.query import query
from repos.excecute import excecute
from repos.mqtt import Mqtt

app = Flask(__name__)

# app.config['MQTT_CLIENT_ID'] = 'localhost'
# app.config['MQTT_BROKER_URL'] = 'retropixel.cyou'
# app.config['MQTT_BROKER_PORT'] = 1883
# app.config['MQTT_USERNAME'] = 'admin'
# app.config['MQTT_PASSWORD'] = 'public'
# app.config['MQTT_KEEPALIVE'] = 30
# app.config['MQTT_TLS_ENABLED'] = False

SECRET = 'R1BhE53$yt76$RR1hB5YJM'

CORS(app)
mqtt = Mqtt('http://localhost:8081')
socketio = SocketIO(app, cors_allowed_origins='*')

cred = credentials.Certificate(os.path.join(settings.BASE_DIR,"service-account.json"))
firebase_admin.initialize_app(cred,{
    'databaseURL': 'https://retropixel-8f415-default-rtdb.firebaseio.com/'
})

@app.route('/login',methods=['POST'])
def index():
    user = request.get_json()['userid']
    password = request.get_json()['password']
    ref = db.reference(f'Users/{user}')
    verify = ref.get()
    if not verify: return jsonify({"status":False}),401
    verify = verify["password"]
    if bcrypt.checkpw(password.encode('utf8'), verify.encode('utf8')):
        code = jwt.encode({"user": user,"exp":datetime.datetime.now() + datetime.timedelta(hours=24)}, SECRET, algorithm="HS256")
        refresh = jwt.encode({"username": user}, SECRET, algorithm="HS256")
        return jsonify({"status":True,"token":code,"refresh":refresh}),200
    else:
        return jsonify({"status":False}),401

@app.route('/refresh',methods=['POST'])
def refresh():
    refresh = request.args.get('token')
    user = jwt.decode(refresh, SECRET, algorithms=["HS256"])["username"]
    code = jwt.encode({"user": user,"exp":datetime.datetime.now() + datetime.timedelta(hours=24)}, SECRET, algorithm="HS256")
    return jsonify({"status":True,"token":code,"refresh":refresh}),200

@socketio.on('connect')
def connect():
    pass

@app.route('/deploy',methods=['POST'])
def deploy():
    def update_backend():
        os.chdir('/home/admin/RpServer/app')
        os.system("sudo bash -i restart.sh")
    def update_frontend():
        os.chdir('/home/admin/RpApp')
        os.system("sudo bash -i restart.sh")
    data = request.get_json()
    try:
        if data["repository"]["default_branch"] == "main":
            thread = threading.Thread(target=update_backend)
            thread.start()
        return ' ',200
    except:
        return ' ',404

@app.route('/')
@app.route('/auth',methods=['GET', 'POST'])
def auth():
    if request.method == 'GET':
        return render_template('login.html',invalid='hidden')
    elif request.method == 'POST':
        user = request.form.get('userid')
        password = request.form.get('password')
        url = request.args.get('redirect_uri')
        state = request.args.get('state')
        ref = db.reference(f'Users/{user}')
        verify = ref.get()
        if not verify: return render_template('login.html',state=state,url=url)
        verify = verify["password"]
        if bcrypt.checkpw(password.encode('utf8'), verify.encode('utf8')):
            code = jwt.encode({"user": user}, SECRET, algorithm="HS256")
            return redirect(f'{url}?code={code}&state={state}')
        else:
            return render_template('login.html',state=state,url=url)
    else: return 'Bad request',400

@app.route('/token',methods=['POST'])
def token():
    data = urllib.parse.parse_qs(request.get_data().decode('utf-8'))
    grant_type = data['grant_type'][0]
    if grant_type == 'authorization_code':
        code = data['code'][0]
        try:
            user = jwt.decode(code, SECRET, algorithms=["HS256"])
        except:
            return 'Invalid token',401
        access = jwt.encode({"user": user["user"],"exp":datetime.datetime.now() + datetime.timedelta(hours=24)}, SECRET, algorithm="HS256")
        refresh = jwt.encode({"user": user["user"]}, SECRET, algorithm="HS256")
        payload = {
            "token_type": "Bearer",
            "access_token": access,
            "refresh_token": refresh,
            "expires_in": 24*3600
        }
        return jsonify(payload)
    elif grant_type == 'refresh_token':
        code = data['refresh_token'][0]
        try:
            user = jwt.decode(code, SECRET, algorithms=["HS256"])
        except:
            return 'Invalid token',401
        access = jwt.encode({"user": user["user"],"exp":datetime.datetime.now() + datetime.timedelta(hours=24)}, SECRET, algorithm="HS256")
        payload = {
            "token_type": "Bearer",
            "access_token": access,
            "expires_in": 24*3600
        }
        return jsonify(payload)
    else: return 'Bad request',400

@app.route('/smarthome',methods=['GET', 'POST'])
def smarthome():
    token = request.headers.get('Authorization')[7:]
    try:
        user = jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        return 'Invalid token',401
    user = user["user"]
    body = request.get_json()
    inputs = body['inputs']
    id = body['requestId']
    for i in inputs:
        if i["intent"] == "action.devices.SYNC":
            data = sync(user,i,id)
            return jsonify(data)
        if i["intent"] == "action.devices.QUERY":
            data = query(i,id)
            return jsonify(data)
        if i["intent"] == "action.devices.EXECUTE":
            data = excecute(i,id)
            return jsonify(data)

@app.route('/connected',methods=['POST'])
def connected():
    payload = request.get_json()
    if payload["action"] == "client_disconnected":
        ref = db.reference(f"Devices/{payload['clientid']}/Online")
        ref.set({'online':False})
        socketio.emit(payload['clientid'],{"branch":"Online","id":payload['clientid'],"state":False})
    if payload["action"] == "client_connected":
        ref = db.reference(f"Devices/{payload['clientid']}/Online")
        ref.set({'online':True})
        socketio.emit(payload['clientid'],{"branch":"Online","id":payload['clientid'],"state":True})
    if payload["action"] == "message_publish":
        # if payload["topic"].split('/')[1] == "Ping":
        #     id = payload['topic'].split('/')[0]
        #     ref = db.reference(f"Devices/{id}/Online")
        #     ref.set({'online':True})
        if payload["topic"].split('/')[1] == "Online":
            id = payload['topic'].split('/')[0]
            ref = db.reference(f"Devices/{id}/OnOff")
            OnOff = "true" if ref.get()["on"] else "false"
            ref = db.reference(f"Devices/{id}/ColorSetting")
            Color = ref.get()["color"]["spectrumRGB"] if ref.get()["color"]["spectrumRGB"] else 16777215
            mqtt.publish(f"{id}/OnOff",OnOff)
            mqtt.publish(f"{id}/Color",Color)
        if payload["topic"].split('/')[1] == "OnOff":
            id = payload['topic'].split('/')[0]
            socketio.emit(id,{"branch":"OnOff","id":id,"state":True if payload["payload"] == "true" else False})
        if payload["topic"].split('/')[1] == "Color":
            id = payload['topic'].split('/')[0]
            socketio.emit(id,{"branch":"Color","id":id,"state":int(payload["payload"])})
    return 'OK',200

@app.route('/devices')
def devices():
    token = request.headers.get('Authorization')[7:]
    user = jwt.decode(token, SECRET, algorithms=["HS256"])
    user = user["user"]
    ref = db.reference(f'Users/{user}/devices')
    devices = ref.get()
    if not devices: return jsonify({'list':[],'states':{}})
    device_list = []
    device_states = {}
    for device in devices:
        device_list.append(device["id"])
        ref = db.reference(f"Devices/{device['id']}/OnOff")
        OnOff = ref.get()["on"]
        ref = db.reference(f"Devices/{device['id']}/Online")
        Online = ref.get()["online"]
        ref = db.reference(f"Devices/{device['id']}/ColorSetting")
        Color = ref.get()["color"]["spectrumRGB"] if ref.get()["color"].get('spectrumRGB') else 16777215
        device_states.update({device["id"]:{
            "name": device["nickname"],
            "OnOff":OnOff,
            "Online":Online,
            "Color":int(Color)
        }})
    return jsonify({'list':device_list,'states':device_states})

@app.route('/set')
def set():
    token = request.headers.get('Authorization')[7:]
    user = jwt.decode(token, SECRET, algorithms=["HS256"])
    topic = request.args.get('topic')
    payload = request.args.get('payload')
    id = topic.split('/')[0]
    ref = db.reference(f'Devices/{id}')
    Online = ref.get()
    #Online = r.get(f"{id}/Online").decode('utf-8') if r.get(f"{id}/Online") else "true"
    if Online:
        if topic.split('/')[1] == "OnOff":
            socketio.emit(id,{"branch":"OnOff","id":id,"state":True if payload == "true" else False})
            ref = db.reference(f'Devices/{id}/OnOff')
            ref.set({'on':True if payload == "true" else False})
        if topic.split('/')[1] == "Color":
            socketio.emit(id,{"branch":"Color","id":id,"state":int(payload)})
            ref = db.reference(f'Devices/{id}/ColorSetting')
            ref.set({'color':{"spectrumRGB":int(payload)}})
        mqtt.publish(topic,payload)
    else: 
        socketio.emit(id,{"branch":"Online","id":id,"state":False})
        socketio.emit(id,{"branch":"OnOff","id":id,"state":False})
        
    return jsonify({topic:payload}),200

# @mqtt.on_connect()
# def handle_connect(client, userdata, flags, rc):
#     print('connected to brooker')

if __name__ == '__main__':
    socketio.run(app,debug=True,port=8000,host='0.0.0.0')
    #app.run(debug=True,port=80,host='0.0.0.0')