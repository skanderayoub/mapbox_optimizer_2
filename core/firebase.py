import firebase_admin
from firebase_admin import credentials, firestore
import core.config as config

# Initialize Firebase app and expose Firestore client `db`
_creds = config.get_firebase_credentials()
cred = credentials.Certificate(_creds) if isinstance(_creds, dict) else credentials.Certificate(_creds)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
