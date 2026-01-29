import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import os
import json


if not firebase_admin._apps:
    cred = None

    # 1️⃣ Render Secret File (production)
    render_secret_path = "/etc/secrets/firebase-service-account.json"
    if os.path.exists(render_secret_path):
        cred = credentials.Certificate(render_secret_path)

    # 2️⃣ ENV variable (deployment / fallback)
    if cred is None:
        raw_env = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if raw_env:
            try:
                service_account_info = json.loads(raw_env)
                cred = credentials.Certificate(service_account_info)
            except Exception:
                cred = None

    # 3️⃣ Local file (local development only)
    if cred is None:
        try:
            cred = credentials.Certificate("firebase-service-account.json")
        except Exception as e:
            raise RuntimeError(
                "Firebase credentials not found.\n"
                "Provide one of:\n"
                "- Render secret file\n"
                "- FIREBASE_SERVICE_ACCOUNT_JSON env var\n"
                "- firebase-service-account.json locally"
            ) from e

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
