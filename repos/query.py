from firebase_admin import db

def query(body,req_id):
    payload = {}
    for device in body["payload"]["devices"]:
        id = device["id"]
        ref = db.reference(f"Devices/{id}")
        data = ref.get()
        OnOff = data["OnOff"]["on"]
        Online = data["Online"]["online"]
        Color = data["ColorSetting"]["color"]
        if Color.get('spectrumRGB'):
            Color = {"spectrumRGB": Color.get('spectrumRGB')}
        else:
            Color = {"temperature": Color.get('temperature')}
        # id = device['id']
        # ref = db.reference(f"Devices/{id}/OnOff")
        # OnOff = ref.get()["on"]
        # ref = db.reference(f"Devices/{id}/Online")
        # Online = ref.get()["online"]
        # ref = db.reference(f"Devices/{id}/ColorSetting")
        # Color = ref.get()["color"]["spectrumRGB"] if ref.get()["color"].get('spectrumRGB') else 16777215
        if Online:
            payload[id] = {
                "on":OnOff,
                "online":True,
                "color":Color,
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