from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import Counter

from services.firebase import get_db
from services.auth import verify_firebase_token

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/overview")
def dashboard_overview(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .order_by("created_at")
        .stream()
    )

    journals = [doc.to_dict() for doc in docs]

    if not journals:
        return {
            "total_journals": 0,
            "last_journal_at": None,
            "average_sentiment": None,
            "mood_trend": [],
            "risk_alert": False,
            "top_keywords": [],
            "top_themes": []
        }

    # -------------------------
    # Basic stats
    # -------------------------
    total_journals = len(journals)
    last_journal_at = journals[-1]["created_at"].isoformat()

    # -------------------------
    # Mood trend (0–100 scale)
    # -------------------------
    mood_trend = []
    sentiment_values = []

    for j in journals:
        scores = j.get("sentiment_scores", {})
        positive = scores.get("positive", 0)
        negative = scores.get("negative", 0)

        # Normalize: -1 → 0, 0 → 50, +1 → 100
        score = round((positive - negative + 1) * 50, 2)

        sentiment_values.append(score)

        mood_trend.append({
            "date": j["created_at"].isoformat(),
            "score": score
        })

    avg_sentiment = round(sum(sentiment_values) / len(sentiment_values), 2)

    # -------------------------
    # Risk alert
    # -------------------------
    risk_alert = any(j.get("flagged", False) for j in journals)

    # -------------------------
    # Keywords & themes
    # -------------------------
    all_keywords = []
    all_themes = []

    for j in journals:
        all_keywords.extend(j.get("key_phrases", []))
        all_themes.extend(j.get("themes", []))

    top_keywords = [k for k, _ in Counter(all_keywords).most_common(5)]
    top_themes = [t for t, _ in Counter(all_themes).most_common(5)]

    return {
        "total_journals": total_journals,
        "last_journal_at": last_journal_at,
        "average_sentiment": avg_sentiment,
        "mood_trend": mood_trend,
        "risk_alert": risk_alert,
        "top_keywords": top_keywords,
        "top_themes": top_themes
    }