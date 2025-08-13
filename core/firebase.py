import os
import core.config as config

# Allow disabling Firebase initialization (e.g., in CI/tests)
if os.getenv("FIREBASE_DISABLE_INIT") == "1":
    db = None  # Will be monkeypatched in tests
else:
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Initialize Firebase app and expose Firestore client `db`
    _creds = config.get_firebase_credentials()
    cred = credentials.Certificate(_creds) if isinstance(_creds, dict) else credentials.Certificate(_creds)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
