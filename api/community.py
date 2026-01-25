from fastapi import APIRouter, HTTPException
from datetime import datetime
from services.firebase import get_db
from services.azure_safety import analyze_content
from google.cloud.firestore import Increment
from models.schemas import CommunityStoryCreate

router = APIRouter(
    prefix="/community",
    tags=["Community Hall"]
)

# ----------------------------
# GET COMMUNITY STORIES
# ----------------------------
@router.get("/fetch/stories")
def get_community_stories():
    db = get_db()

    stories = (
        db.collection("community_stories")
        .where("moderation_status", "==", "auto_approved")
        .order_by("created_at", direction="DESCENDING")
        .limit(50)
        .stream()
    )

    return {
        "stories": [
            {"id": doc.id, **doc.to_dict()}
            for doc in stories
        ]
    }


# ----------------------------
# SUBMIT STORY (HARD BLOCK)
# ----------------------------
@router.post("/post/story")
def submit_story(payload: CommunityStoryCreate):
    db = get_db()

    # ✅ Azure Content Safety analysis
    safety = analyze_content(payload.story)

    if safety["flagged"]:
        raise HTTPException(
            status_code=403,
            detail="This story cannot be posted due to safety concerns."
        )

    doc_ref = db.collection("community_stories").document()

    story_data = {
        "id": doc_ref.id,
        "story": payload.story,
        "tags": payload.tags,
        "created_at": datetime.utcnow(),
        "likes": 0,
        "saved": 0,
        "risk_score": safety["risk_score"],
        "categories": safety.get("categories", {}),
        "moderation_status": "auto_approved"
    }

    doc_ref.set(story_data)

    return {
        "message": "Story posted successfully",
        "story_id": doc_ref.id,
        "risk_score": safety["risk_score"]
    }


# ----------------------------
# LIKE STORY
# ----------------------------
@router.post("/story/like")
def like_story(story_id: str):
    db = get_db()

    db.collection("community_stories") \
      .document(story_id) \
      .update({"likes": Increment(1)})

    return {
        "message": "Story liked",
        "story_id": story_id
    }


# ----------------------------
# SAVE STORY
# ----------------------------
@router.post("/story/save")
def save_story(story_id: str):
    db = get_db()

    db.collection("community_stories") \
      .document(story_id) \
      .update({"saved": Increment(1)})

    return {
        "message": "Story saved",
        "story_id": story_id
    }