import requests

class Mqtt:
    def __init__(self,url):
        self.url = url
    def publish(self,topic,payload):
        response = requests.post(f"{self.url}/api/v4/mqtt/publish",
            auth=("admin","public"),
            json={
                "topic":topic,
                "payload":payload,
                "clientid":"admin"
            }
        )
        return response