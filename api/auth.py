from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.firebase import firebase_auth


router = APIRouter(prefix="/auth", tags=["auth"])

# --- Request models ---
class SignUpRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class VerifyTokenRequest(BaseModel):
    id_token: str


# --- Endpoints ---
@router.post("/signup")
def signup(request: SignUpRequest):
    """
    Create a new user in Firebase Auth
    """
    try:
        user = firebase_auth.create_user(
            email=request.email,
            password=request.password
        )
        return {"uid": user.uid, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(request: LoginRequest):
    """
    Backend cannot issue tokens; frontend should use Firebase SDK
    """
    try:
        user = firebase_auth.get_user_by_email(request.email)
        return {
            "uid": user.uid,
            "email": user.email,
            "message": "Frontend should use Firebase client SDK to get idToken"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-token")
def verify_token(request: VerifyTokenRequest):
    """
    Verify ID token sent from frontend
    """
    try:
        decoded_token = firebase_auth.verify_id_token(request.id_token)
        return {"uid": decoded_token["uid"], "email": decoded_token.get("email")}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
