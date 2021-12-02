from firebase_admin import db

def sync(user,body,id):
    ref = db.reference(f'Users/{user}/devices')
    state = ref.get()
    devices = []
    for i in state:
        devices.append({
            "id": i["id"],
            "type": "action.devices.types.LIGHT",
            "traits": [
                "action.devices.traits.OnOff",
                "action.devices.traits.ColorSetting"
            ],
            "name": {
                "defaultNames": [
                    "RGB Smart Lights"
                ],
                "name": "Smart light",
                "nicknames": [
                    i["nickname"]
                ]
            },
            "willReportState": True,
            "roomHint": i["room"],
            "attributes": {
                "colorModel": "rgb",
                "colorTemperatureRange": {
                    "temperatureMinK": 2000,
                    "temperatureMaxK": 9000
                },
                "commandOnlyColorSetting": False
            },
            "deviceInfo": {
                "manufacturer": "RectroPixel c.o",
                "model": "lstrp-01",
                "hwVersion": "1.0",
                "swVersion": "1.0"
            }
        })
    response = {
        "requestId": id,
        "payload": {
            "agentUserId": user,
            "devices": devices
        }
    }
    return response