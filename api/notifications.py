from fastapi import APIRouter, Depends
from datetime import datetime
from services.firebase import get_db
from services.auth import verify_firebase_token

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/")
def get_notifications(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("notifications")
        .where("uid", "==", uid)
        .order_by("created_at", direction="DESCENDING")
        .stream()
    )

    return {
        "notifications": [
            {"id": doc.id, **doc.to_dict()}
            for doc in docs
        ]
    }


@router.post("/acknowledge")
def acknowledge_notification(
    notification_id: str,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    doc_ref = db.collection("notifications").document(notification_id)
    doc = doc_ref.get()

    if not doc.exists or doc.to_dict().get("uid") != uid:
        return {"message": "Notification not found"}

    doc_ref.update({"acknowledged": True})

    return {"message": "Notification acknowledged"}


def create_notification(uid: str, message: str, n_type: str = "check_in"):
    db = get_db()

    notification_data = {
        "uid": uid,
        "type": n_type,
        "message": message,
        "created_at": datetime.utcnow(),
        "acknowledged": False
    }

    db.collection("notifications").add(notification_data)