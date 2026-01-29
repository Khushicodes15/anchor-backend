import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os
import json


if not firebase_admin._apps:
    cred = None

    #ENV variable (used in deployment)
    raw_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if raw_env:
        try:
            service_account_info = json.loads(raw_env)
            cred = credentials.Certificate(service_account_info)
        except Exception as e:
            cred= None

    #Fallback to local file (used only locally)
    raw_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    if not raw_env:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON is not set. "
            "This is required in production."
        )
    try:
        service_account_info = json.loads(raw_env)
        cred = credentials.Certificate(service_account_info)
    except Exception as e:
        raise RuntimeError(
            "Failed to parse FIREBASE_SERVICE_ACCOUNT_JSON. "
            "Ensure it is valid single-line JSON."
        ) from e
    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
        }
    )
    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
        }
    )

# -------------------------------------------------
# Clients
# -------------------------------------------------
db = firestore.client()
firebase_auth = auth
bucket = storage.bucket()

def get_db():
    return db

def get_bucket():
    return bucket