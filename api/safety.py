from fastapi import APIRouter, Depends
from services.firebase import get_db
from services.auth import verify_firebase_token
from models.schemas import SafetyPlanCreate, SafetyPlanOut

router = APIRouter(
    prefix="/safety-plans",
    tags=["Safety"]
)

@router.post("/", response_model=SafetyPlanOut)
def create_or_update_safety_plan(
    plan: SafetyPlanCreate,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    doc_ref = db.collection("safety_plans").document(uid)

    safety_plan_data = {
        "uid": uid,
        **plan.dict()
    }

    doc_ref.set(safety_plan_data)

    return {
        "id": uid,
        **safety_plan_data
    }


@router.get("/", response_model=SafetyPlanOut)
def get_safety_plan(
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    doc_ref = db.collection("safety_plans").document(uid)
    doc = doc_ref.get()

    if not doc.exists:
        return {
            "id": uid,
            "uid": uid,
            "triggers": [],
            "coping_strategies": [],
            "safe_contacts": [],
            "reason_to_live": ""
        }

    return {
        "id": doc.id,
        **doc.to_dict()
    }