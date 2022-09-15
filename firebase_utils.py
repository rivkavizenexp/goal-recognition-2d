import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class firebase_handler:
    def __init__(self,cred_path = 'firebase-adminsdk.json') -> None:
        if not firebase_admin._apps:
            # Fetch the service account key JSON file contents
            cred = credentials.Certificate(cred_path)
            # Initialize the app with a service account, granting admin privileges
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://goal-recognition.firebaseio.com'
            })

    def read(self,path='/'):
        ref = db.reference(path)
        return ref.get()

    def write(self,key,data,path='/'):
        ref = db.reference(path)
        ref.child(key).set(data)

    def delete(self,key,path='/'):
        ref = db.reference(path)
        ref.child(key).delete()
