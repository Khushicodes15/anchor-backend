from pydantic import BaseModel
from typing import List, Optional, Dict 
from datetime import datetime

# --------------------
# Journal Schemas
# --------------------
class JournalCreate(BaseModel):
    title: Optional[str] = None
    content: str

class JournalOut(BaseModel):
    id: str
    title: Optional[str]
    content: str
    created_at: datetime

    # Azure Language
    sentiment: Optional[str]
    sentiment_scores: Optional[Dict[str, float]]
    key_phrases: Optional[List[str]]

    # Azure Content Safety
    risk_score: Optional[float]
    flagged: Optional[bool]

    # GenAI
    reflection: Optional[str]
    themes: Optional[List[str]]
    follow_up_question: Optional[str]  
    
# --------------------
# Safety Plan Schemas
# --------------------
class SafetyPlanCreate(BaseModel):
    plan_name: Optional[str] = None  # from auth-firebase
    steps: Optional[List[str]] = [] # from auth-firebase

class SafetyPlanOut(SafetyPlanCreate):
    id: Optional[str] = None

class SafeContact(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class ReasonToLive(BaseModel):
    text: Optional[str] = None
    media_url: Optional[str] = None
    
class SafetyPlan(BaseModel):
    triggers: Optional[List[str]] = []
    coping_strategies: Optional[List[str]] = []
    safe_contacts: Optional[List[SafeContact]] = []
    reason_to_live: Optional[ReasonToLive] = None
class CommunityStoryCreate(BaseModel):
    story: str
    tags: List[str] = []
