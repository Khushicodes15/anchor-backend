import os
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from services.firebase import firebase_auth

security = HTTPBearer(auto_error=False)


DEV_MODE = os.getenv("DEV_MODE") == "true"
print("DEV_MODE=",DEV_MODE)

def verify_firebase_token(token=Depends(security)):
    """
    Verify Firebase ID token.
    In DEV_MODE, bypass auth and return a dummy uid.
    """

    if DEV_MODE:
        return "dev_user_123"

   
    if token is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        decoded_token = firebase_auth.verify_id_token(token.credentials)
        return decoded_token.get("uid")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")