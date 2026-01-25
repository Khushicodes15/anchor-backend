from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from statistics import mean

from services.firebase import get_db
from services.auth import verify_firebase_token
from services.gemini import generate_reflection  # AI summary

router = APIRouter(
    prefix="/wrapped",
    tags=["Wrapped"]
)


@router.get("/")
def get_wrapped(uid: str = Depends(verify_firebase_token)):
    db = get_db()

    now = datetime.utcnow()
    start_date = now - timedelta(days=30)

    # -----------------------------
    # Fetch last 30 days journals
    # -----------------------------
    docs = (
        db.collection("journals")
        .where("uid", "==", uid)
        .where("created_at", ">=", start_date)
        .stream()
    )

    journals = [doc.to_dict() for doc in docs]

    if len(journals) < 3:
        return {
            "message": "Not enough check-ins yet for your Anchor Wrapped.",
            "required": 3,
            "current": len(journals)
        }

    # -----------------------------
    # Basic stats
    # -----------------------------
    total_journals = len(journals)
    active_days = len(
        set(j["created_at"].date() for j in journals if j.get("created_at"))
    )

    # -----------------------------
    # Mood scoring
    # -----------------------------
    daily_scores = defaultdict(list)

    for j in journals:
        scores = j.get("sentiment_scores", {})
        pos = scores.get("positive", 0.0)
        neg = scores.get("negative", 0.0)

        raw_score = pos - neg                 # -1 → +1
        normalized = int((raw_score + 1) * 50)  # 0 → 100

        date_key = j["created_at"].date().isoformat()
        daily_scores[date_key].append(normalized)

    mood_trend = [
        {
            "date": day,
            "score": int(mean(scores))
        }
        for day, scores in sorted(daily_scores.items())
    ]

    average_mood_score = int(
        mean(item["score"] for item in mood_trend)
    )

    if average_mood_score <= 30:
        mood_label = "Struggling"
    elif average_mood_score <= 50:
        mood_label = "Heavy"
    elif average_mood_score <= 70:
        mood_label = "Steady"
    elif average_mood_score <= 85:
        mood_label = "Positive"
    else:
        mood_label = "Thriving"

    # -----------------------------
    # Emotional themes
    # -----------------------------
    themes = []
    for j in journals:
        themes.extend(j.get("themes", []))

    top_themes = [
        theme for theme, _ in Counter(themes).most_common(3)
    ]

    # -----------------------------
    # Safety snapshot
    # -----------------------------
    risk_scores = [j.get("risk_score", 0.0) for j in journals]
    high_risk_entries = len([r for r in risk_scores if r >= 0.5])
    max_risk_score = round(max(risk_scores), 2)

    # -----------------------------
    # Highlights
    # -----------------------------
    day_counts = Counter(
        j["created_at"].strftime("%A") for j in journals
    )
    most_active_day = day_counts.most_common(1)[0][0]

    # longest streak
    dates = sorted(
        set(j["created_at"].date() for j in journals)
    )

    longest_streak = current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
            longest_streak = max(longest_streak, current)
        else:
            current = 1

    # -----------------------------
    # AI Summary (Gemini)
    # -----------------------------
    summary_prompt = f"""
Create a warm, encouraging monthly reflection.

Context:
- Journals written: {total_journals}
- Active days: {active_days}
- Average mood score: {average_mood_score} ({mood_label})
- Top emotional themes: {', '.join(top_themes)}
- High intensity moments: {high_risk_entries}

Rules:
- No diagnosis
- No clinical language
- Gentle, human tone
- 3–4 sentences max
"""

    ai_summary = generate_reflection(summary_prompt)

    # -----------------------------
    # Final response
    # -----------------------------
    return {
        "period": "Last 30 Days",

        "stats": {
            "total_journals": total_journals,
            "active_days": active_days
        },

        "mood": {
            "average_score": average_mood_score,
            "label": mood_label,
            "trend": mood_trend
        },

        "emotions": {
            "top_themes": top_themes
        },

        "safety": {
            "high_risk_entries": high_risk_entries,
            "max_risk_score": max_risk_score
        },

        "highlights": {
            "most_active_day": most_active_day,
            "longest_streak": longest_streak
        },

        "ai_summary": {
            "title": ai_summary.get("themes", ["Your month"])[0],
            "narrative": ai_summary.get("reflection")
        }
    }

@router.get("/demo")
def wrapped_demo():
    """
    Demo endpoint for video/screenshots.
    Does NOT use real user data.
    """

    return {
        "demo": True,
        "period": "Last 30 Days",

        "stats": {
            "total_journals": 18,
            "active_days": 11
        },

        "mood": {
            "average_score": 68,
            "label": "Steady",
            "trend": [
                {"date": "2025-12-01", "score": 42},
                {"date": "2025-12-04", "score": 48},
                {"date": "2025-12-07", "score": 55},
                {"date": "2025-12-10", "score": 60},
                {"date": "2025-12-14", "score": 64},
                {"date": "2025-12-18", "score": 70},
                {"date": "2025-12-22", "score": 74},
                {"date": "2025-12-26", "score": 80}
            ]
        },

        "emotions": {
            "top_themes": ["resilience", "stress", "hope"]
        },

        "safety": {
            "high_risk_entries": 2,
            "max_risk_score": 0.62
        },

        "highlights": {
            "most_active_day": "Wednesday",
            "longest_streak": 4
        },

        "ai_summary": {
            "title": "A Month of Quiet Strength",
            "narrative": (
                "This month shows moments of emotional weight, but also steady progress. "
                "You returned to journaling even on difficult days, which reflects resilience. "
                "Over time, your reflections became calmer and more hopeful — a sign of growth, "
                "even when things weren’t easy."
            )
        }
    }