import requests

endpoint = "a324s852z2w8jk-ats.iot.us-east-1.amazonaws.com"
cert = "./73533a8c1caac1e5b0ea5b4a5a32bae6a35ba8b120c1feb43952024ad33bef11-certificate.pem.crt"
key = "./73533a8c1caac1e5b0ea5b4a5a32bae6a35ba8b120c1feb43952024ad33bef11-private.pem.key"

class Mqtt:
    def __init__(self,url):
        self.url = url
    def publish(self,topic,payload):
        publish_url = 'https://' + self.url + ':8443/topics/' + topic + '?qos=1'
        publish_msg = payload.encode('utf-8')
        response = requests.post(
            publish_url,
            data=publish_msg,
            cert=[cert, key])
        return response