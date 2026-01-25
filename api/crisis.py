from fastapi import APIRouter, Depends
from datetime import datetime
from services.firebase import get_db
from services.auth import verify_firebase_token


router = APIRouter(
    prefix="/crisis",
    tags=["Crisis Mode"]
)

# ------------------------------------
# System-defined grounding steps
# ------------------------------------
GROUNDING_STEPS = [
    "Pause and take 5 slow breaths.",
    "Name 3 things you can see around you.",
    "Place your feet on the ground and feel the floor beneath you."
]

# ------------------------------------
# START CRISIS MODE
# ------------------------------------
@router.post("/start")
def start_crisis(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    db.collection("crisis_logs").add({
        "uid": uid,
        "activated_at": datetime.utcnow()
    })

    return {
        "status": "crisis_started",
        "activated_at": datetime.utcnow().isoformat()
    }

# ------------------------------------
# CRISIS SUPPORT PAYLOAD
# ------------------------------------
@router.get("/support")
def crisis_support(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    plan_doc = db.collection("safety_plans").document(uid).get()

    if not plan_doc.exists:
        return {
            "status": "no_safety_plan",
            "grounding_steps": GROUNDING_STEPS,
            "message": "No safety plan found. Please create one when you feel able."
        }

    safety_plan = plan_doc.to_dict()

    return {
        "status": "crisis_mode_active",
        "grounding_steps": GROUNDING_STEPS,
        "coping_strategies": safety_plan.get("coping_strategies", []),
        "safe_contacts": safety_plan.get("safe_contacts", []),
        "reason_to_live": safety_plan.get("reason_to_live", "")
    }