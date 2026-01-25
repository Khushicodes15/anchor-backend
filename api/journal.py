from fastapi import APIRouter, Depends
from datetime import datetime
from services.firebase import get_db
from services.auth import verify_firebase_token
from services.ai_pipeline import run_journal_ai
from models.schemas import JournalCreate, JournalOut


router = APIRouter(
    prefix="/journals",
    tags=["journals"]
)


@router.post("/")
def create_journal(
    journal: JournalCreate,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    created_at = datetime.utcnow()

    # -------------------------
    # AI Reflection (Azure / fallback)
    # -------------------------
    ai_output = run_journal_ai(journal.content)

    journal_data = {
    "uid": uid,
    "title": journal.title,
    "content": journal.content,
    "created_at": created_at,

    # Azure AI Language
    "sentiment": ai_output["sentiment"],
    "sentiment_scores": ai_output["sentiment_scores"],
    "key_phrases": ai_output["key_phrases"],

    # Azure Content Safety
    "risk_score": ai_output["risk_score"],
    "flagged": ai_output["flagged"],

    # GenAI 
    "reflection": ai_output["reflection"],
    "themes": ai_output["themes"],
    "follow_up_question": ai_output.get("follow_up_question")
    }

    doc_ref = db.collection("journals").document()
    doc_ref.set(journal_data)

    return {
        "id": doc_ref.id,
        **journal_data
    }



@router.get("/")
def get_journals(
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .stream()
    )

    return [
        {
            "id": doc.id,
            **doc.to_dict()
        }
        for doc in docs
    ]
