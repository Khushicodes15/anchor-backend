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

    doc_ref = db.collection("journals").document()
    session_id = journal.session_id or doc_ref.id

    # ✅ Use actual message content as title, not hardcoded string
    title = journal.title or ""
    if not title or title.strip().lower() == "journal reflection":
        title = (journal.content or "")[:40]

    journal_data = {
        "uid": uid,
        "session_id": session_id,
        "title": title,
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

    return {"id": doc_ref.id, "session_id": session_id, **journal_data}


@router.get("/sessions")
def get_sessions(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .stream()
    )

    seen: dict = {}
    for doc in docs:
        data = doc.to_dict()

        # Legacy docs with no session_id: use doc.id as session key
        sid = data.get("session_id") or doc.id
        created_at = data.get("created_at")

        if sid not in seen:
            # ✅ Treat "Journal reflection" as empty — fall back to content
            stored_title = data.get("title", "")
            if not stored_title or stored_title.strip().lower() in ("journal reflection", ""):
                stored_title = data.get("content", "")
            seen[sid] = {
                "session_id": sid,
                "title": stored_title[:40],
                "created_at": created_at,
            }
        else:
            # Keep earliest created_at as session anchor
            existing = seen[sid]["created_at"]
            if existing and created_at and created_at < existing:
                seen[sid]["created_at"] = created_at

    sessions = list(seen.values())
    sessions.sort(key=lambda s: s["created_at"] or datetime.min, reverse=True)
    return sessions


@router.get("/session/{session_id}")
def get_session_messages(
    session_id: str,
    uid: str = Depends(verify_firebase_token)
):
    db = get_db()

    # Modern: query by session_id field
    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .where("session_id", "==", session_id)
        .stream()
    )

    results = [{"id": doc.id, **doc.to_dict()} for doc in docs]

    # ✅ Legacy fallback: old docs had no session_id stored,
    # get_sessions used doc.id as the key — fetch that single doc directly
    if not results:
        doc = db.collection("journals").document(session_id).get()
        if doc.exists:
            data = doc.to_dict()
            if data.get("uid") == uid:
                results = [{"id": doc.id, **data}]

    results.sort(key=lambda x: x.get("created_at") or datetime.min)
    return results


@router.get("/")
def get_journals(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .stream()
    )

    results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
    results.sort(key=lambda x: x.get("created_at") or datetime.min)
    return results