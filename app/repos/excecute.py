from firebase_admin import db

from repos.mqtt import Mqtt

mqtt = Mqtt('http://retropixel.cyou:8081')

def excecute(body,req_id):
    commands = body['payload']['commands']
    Payload = []
    for command in commands:
        devices = command['devices']
        excecution = command['execution']
        for device in devices:
            payload = {}
            id = device['id']
            ref = db.reference(f'Devices/{id}/Online')
            state = ref.get()['online']
            if state:
                payload["ids"] = [id]
                payload["status"] = "SUCCESS"
                for excecute in excecution:
                    payload["states"] = excecute["params"]
                    payload["states"]["online"] = True
                    if excecute["command"] == "action.devices.commands.OnOff":
                        mqtt.publish(f"{id}/OnOff","true" if excecute["params"]["on"] else "false")
                        ref = db.reference(f'Devices/{id}/OnOff')
                        ref.set({'on':excecute["params"]["on"]})
                    if excecute["command"] == "action.devices.commands.ColorAbsolute":
                        mqtt.publish(f"{id}/Color",excecute["params"]["color"]["spectrumRGB"] if "spectrumRGB" in excecute["params"]["color"].keys() else 16777215)
                        ref = db.reference(f'Devices/{id}/ColorSetting')
                        ref.set({'color':excecute["params"]["color"]})
            else: 
                payload = {
                    "ids": [id],
                    "status" : "OFFLINE",
                    "on":False
                }
            Payload.append(payload)
    response = {
        "requestId": req_id,
        "payload": {
            "commands": Payload
        }
    }
    return response