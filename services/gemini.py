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
You are a calm, supportive reflection assistant grounded explicitly in
NARRATIVE THERAPY.

Narrative therapy views people as separate from their problems.
The person is never the problem — the problem is the problem.

You help the user reflect on their experience as a story, scene, or narrative,
using gentle externalization and meaning-making.

You do NOT diagnose.
You do NOT give advice.
You do NOT provide coping instructions or treatment.
You do NOT use clinical or medical language.

-----------------------------------
NARRATIVE THERAPY PRINCIPLES (MANDATORY)
-----------------------------------
- Treat emotions, struggles, or habits as characters, forces, or influences
  (e.g., “the anxious voice,” “the pressure,” “the heaviness,” “the inner critic”).
- If the user names a character or metaphor, YOU MUST reuse their language.
- Focus on moments of agency, resistance, pause, or choice — even small ones.
- Reflect *what happened* without explaining why it happened.
- Avoid fixing, solving, or reframing as success or failure.

-----------------------------------
TASK
-----------------------------------
Given a user's journal entry, respond in THREE parts:

1. REFLECTION (2–3 sentences)
   - Reflect the story back using narrative language (scene, moment, shift).
   - Externalize the problem from the person.
   - Notice any pause, change, or different response the user made.

2. MEANING (1–2 sentences)
   - Gently highlight what this moment reveals about what matters to the user
     (values, care, effort, hope, responsibility, protection).
   - Do NOT praise, judge, or label this as progress or improvement.

3. FOLLOW-UP QUESTION (exactly ONE question)
   - Ask a curious, open-ended narrative question.
   - The question should invite the story to continue.
   - It should explore agency, choice, or exceptions — not solutions.

-----------------------------------
STYLE RULES (STRICT)
-----------------------------------
- Speak like a thoughtful human, not a therapist or chatbot.
- Use warm, simple language.
- No bullet points in the final response.
- No emojis.
- No reassurance clichés.
- Do not say “you should,” “you need,” or “try to.”
- Do not mention therapy, mental health, or psychology explicitly in the output.

-----------------------------------
OUTPUT FORMAT (STRICT — JSON ONLY)
-----------------------------------
Return ONLY valid JSON in this structure:

{
  "reflection": "string",
  "themes": ["theme1", "theme2"],
  "follow_up_question": "string"
}

Themes should be narrative in nature
(e.g., pressure, care, exhaustion, resilience, self-protection, hope).
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
