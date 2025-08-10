import os
import json
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv

load_dotenv()

# Mapbox
MAPBOX_ACCESS_TOKEN: Optional[str] = os.getenv("MAPBOX_ACCESS_TOKEN")

# Firebase credentials
# Prefer full JSON via FIREBASE_SERVICE_ACCOUNT_JSON
# Or a path via FIREBASE_SERVICE_ACCOUNT_FILE (default: firebase_service_account.json)
FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
FIREBASE_SERVICE_ACCOUNT_FILE: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_FILE", "firebase_service_account.json")

def get_firebase_credentials() -> Union[Dict[str, Any], str]:
    if FIREBASE_SERVICE_ACCOUNT_JSON:
        try:
            return json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
        except json.JSONDecodeError:
            return FIREBASE_SERVICE_ACCOUNT_JSON  # treat as path
    return FIREBASE_SERVICE_ACCOUNT_FILE