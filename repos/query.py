from firebase_admin import db

def query(body,req_id):
    payload = {}
    for device in body["payload"]["devices"]:
        id = device['id']
        ref = db.reference(f"Devices/{device['id']}/OnOff")
        OnOff = ref.get()["on"]
        ref = db.reference(f"Devices/{device['id']}/Online")
        Online = ref.get()["online"]
        ref = db.reference(f"Devices/{device['id']}/ColorSetting")
        Color = ref.get()["color"]["spectrumRGB"] if ref.get()["color"].get('spectrumRGB') else 16777215
        if Online == "true":
            payload[id] = {
                "on":True if OnOff == "true" else False,
                "online":True,
                "color":{"spectrumRGB":Color},
                "status":"SUCCESS"
            }
        else: 
            payload[id] = {
                "status":"OFFLINE",
                "on":False
            }
    response = {
        "requestId": req_id,
        "payload": {
            "devices": payload
        }
    }
    return response