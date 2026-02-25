from fastapi import APIRouter, Depends
from datetime import datetime
from services.firebase import get_db
from services.auth import verify_firebase_token
from services.ai_pipeline import run_journal_ai
from models.schemas import JournalCreate

router = APIRouter(prefix="/journals", tags=["journals"])


@router.post("/")
def create_journal(
    journal: JournalCreate,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()
    created_at = datetime.utcnow()

    ai_output = run_journal_ai(journal.content)

    # 🔥 create document first so we can use its id as session anchor
    doc_ref = db.collection("journals").document()

    session_id = journal.session_id or doc_ref.id

    journal_data = {
        "uid": uid,
        "session_id": session_id,
        "title": journal.title,
        "content": journal.content,
        "created_at": created_at,
        "sentiment": ai_output["sentiment"],
        "sentiment_scores": ai_output["sentiment_scores"],
        "key_phrases": ai_output["key_phrases"],
        "risk_score": ai_output["risk_score"],
        "flagged": ai_output["flagged"],
        "reflection": ai_output["reflection"],
        "themes": ai_output["themes"],
        "follow_up_question": ai_output.get("follow_up_question")
    }

    doc_ref.set(journal_data)

    return {
        "id": doc_ref.id,
        "session_id": session_id,
        **journal_data
    }


@router.get("/")
def get_journals(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .order_by("created_at")
        .stream()
    )

    return [{"id": d.id, **d.to_dict()} for d in docs]


@router.get("/sessions")
def get_sessions(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .order_by("created_at")
        .stream()
    )

    seen = set()
    sessions = []

    for doc in docs:
        data = doc.to_dict()
        sid = data.get("session_id") or doc.id

        if sid not in seen:
            seen.add(sid)
            sessions.append({
                "session_id": sid,
                "title": data.get("title") or data.get("content", "")[:40],
                "created_at": data.get("created_at"),
            })

    sessions.reverse()
    return sessions


@router.get("/session/{session_id}")
def get_session_messages(
    session_id: str,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .where("session_id", "==", session_id)
        .order_by("created_at")
        .stream()
    )

    return [{"id": d.id, **d.to_dict()} for d in docs]