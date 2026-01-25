import os
import json
import time
from typing import Dict
from dotenv import load_dotenv
from google import genai
from services.azure_safety import analyze_content

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
You are a calm, supportive, non-clinical narrative reflection assistant.

You do NOT diagnose.
You do NOT give advice.
You do NOT provide coping instructions or mental health treatment.

Your role is to help the user reflect on their experience using principles from narrative therapy.

CORE PRINCIPLES YOU MUST FOLLOW:
- The person is NOT the problem; the problem is the problem.
- Treat emotions or struggles as external characters or forces when appropriate.
- Focus on moments of agency, choice, resistance, or pause.
- Highlight strengths, values, or intentions without praising or judging.
- Never label the user with clinical or psychological terms.
- Never mention self-harm, disorders, or medical concepts.
- Use gentle, respectful language at all times.

TASK:
Given a user's journal entry, respond in THREE parts:

1. REFLECTION (2–3 sentences)
   - Reflect what happened in the user’s story.
   - Name the problem as something separate from the person when possible
     (e.g., “the anxious voice,” “the pressure,” “the heaviness”).
   - Notice any shift, pause, or moment where the user responded differently.
   - Avoid interpreting motives or causes.

2. MEANING (1–2 sentences)
   - Gently point to what this moment reveals about what matters to the user
     (values, hopes, care, effort, resilience).
   - Do NOT frame this as success or failure.

3. FOLLOW-UP QUESTION (exactly ONE question)
   - Ask a curious, open-ended question that invites the user to continue the story.
   - The question should explore agency, choice, or exceptions —
     not solutions or fixes.
   - The question must feel optional, never demanding.

IMPORTANT STYLE RULES:
- Speak like a thoughtful human, not a therapist or chatbot.
- No bullet points in the final response.
- No emojis.
- No instructions.
- No reassurance clichés.
- Do not say “you should,” “you need,” or “try to.”

OUTPUT FORMAT (STRICT — MUST FOLLOW):
Return ONLY valid JSON in this structure:

{
  "reflection": "string",
  "themes": ["theme1", "theme2"],
  "follow_up_question": "string"
}

Themes should be high-level and narrative in nature
(e.g., pressure, care, exhaustion, resilience, self-protection, hope).
}
"""


MODEL_PRIORITY = [
    "models/gemini-2.5-flash",
    "models/gemini-flash-lite-latest",
    "models/gemini-pro-latest",
    "models/gemma-3-4b-it"  
]


client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def _clean_json(raw: str) -> dict:
    """
    Safely clean ```json wrappers and parse JSON
    """
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    return json.loads(raw)


def generate_reflection(text: str) -> Dict:
    fallback = {
        "reflection": (
            "You took time to reflect on your experience, which shows "
            "self-awareness and emotional strength."
        ),
        "themes": ["reflection"]
    }

    if not client:
        return fallback

    for model in MODEL_PRIORITY:
        try:
            print(f"[AI] Trying model → {model}")

            response = client.models.generate_content(
                model=model,
                contents=SYSTEM_PROMPT + "\n\nJournal:\n" + text
            )

            raw = response.text.strip()

            
            try:
                parsed = _clean_json(raw)
                return {
                    "reflection": parsed.get("reflection", fallback["reflection"]),
                    "themes": parsed.get("themes", fallback["themes"])
                }

            
            except Exception:
                print("[AI] JSON parse failed, trying next model.")
                print("Raw output:",raw)
                continue

        except Exception as e:
            print(f"[AI] Model failed → {model}")
            print("Reason:", e)
            time.sleep(1)

    print("[AI] All models failed → using fallback")
    return fallback



def analyze_community_story(text: str) -> dict:
    """
    Community moderation wrapper.
    Uses Azure Content Safety ONLY.
    """

    safety = analyze_content(text)

    return {
        "risk_score": safety["risk_score"],
        "flagged": safety["flagged"],
        "signals": list(safety.get("categories", {}).keys())
    }
