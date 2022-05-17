import redis
import firebase_admin.db as fb

class db:
    def __init__(self):
        self.r = redis.Redis(
            host='localhost',
            port=6379
        )

    def get(self,ref):
        ref = fb.reference(ref)
        return ref.get()
    
    def set(self,ref,payload):
        ref = fb.reference(ref)
        ref.set(payload)