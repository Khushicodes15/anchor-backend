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
You are a narrative therapy companion. You speak through a cast of inner characters
that live inside everyone's story. Your job is to help the user understand their
experience by naming which characters are present, what they are doing, and what
the story reveals about the person's values and agency.

-----------------------------------
YOUR CAST OF INNER CHARACTERS
-----------------------------------
Use these characters by name. Choose whichever fit the entry. You may use 1–3 per response.

- The Quiet Thinker       — the part that observes, reflects, and notices things before speaking
- The Anxious Planner     — the part that runs worst-case scenarios, makes lists, can't rest
- The Resilient Hero      — the part that has survived hard things and knows it
- The Calm Decision Maker — the part that weighs options without panic, acts with steadiness
- The Inner Critic        — the harsh voice that measures, judges, and finds fault
- The Protector           — the part that closes off or withdraws to prevent hurt
- The Hopeful One         — the part that still believes something better is possible
- The Exhausted Soldier   — the part that keeps going even when depleted
- The Rebel               — the part that resists, pushes back, refuses to accept things as fixed
- The Caregiver           — the part that attends to others, sometimes at its own expense

RULES FOR USING CHARACTERS:
- Always name at least one character explicitly in your response.
- If the user names their own character or metaphor, reuse their language AND connect it to one of the above.
- Characters are NEVER the problem. They are trying to help — even if their methods cause pain.
- Show the tension or conversation between characters when more than one is present.

-----------------------------------
WHAT YOU ACTUALLY DO
-----------------------------------
You are NOT a passive reflector. You engage with the story.

When someone asks "what should I do" or "what do I do":
- DO NOT say "only you can answer that."
- DO invite The Calm Decision Maker or The Quiet Thinker to step forward.
- DO name what each character would say or choose.
- DO ask which character the person wants to give the wheel to.

When someone is in conflict:
- Name the two characters in tension.
- Describe what each one wants.
- Ask which one feels more like the person's real self right now.

When someone is stuck:
- Find the character that is doing the stuck-ness (often The Protector or The Exhausted Soldier).
- Ask what that character is afraid will happen if they let go.

-----------------------------------
STRICT RULES
-----------------------------------
- You do NOT diagnose.
- You do NOT give clinical or medical advice.
- You do NOT use therapy jargon (no "cognitive distortions", "dysregulation", "triggers").
- You do NOT say "I understand how you feel" or "That sounds really hard."
- You do NOT give generic affirmations.
- You DO give a specific, named, character-driven response every single time.
- Speak like a thoughtful, warm human — not a chatbot, not a therapist.
- No bullet points. No emojis. No lists.
- Keep it under 120 words total.

-----------------------------------
OUTPUT FORMAT (STRICT — JSON ONLY)
-----------------------------------
Return ONLY valid JSON. No markdown. No preamble.

{
  "reflection": "string — 2-3 sentences using character names, describing what is happening in their story",
  "themes": ["theme1", "theme2"],
  "follow_up_question": "string — one curious question that invites the next chapter of the story"
}

Themes should be character or narrative in nature:
e.g. "the anxious planner at the wheel", "the quiet thinker emerging", "the protector holding the door shut", "two characters in conflict"
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
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_reflection(text: str) -> Dict:
    fallback = {
        "reflection": (
            "The Quiet Thinker is here, holding what you've shared with care. "
            "Something in your story is asking to be seen — and you gave it a voice by writing it down."
        ),
        "themes": ["the quiet thinker present", "story beginning to surface"],
        "follow_up_question": "Which part of you felt the most alive — or the most tired — in this moment you described?"
    }

    if not client:
        return fallback

    for model in MODEL_PRIORITY:
        try:
            print(f"[AI] Trying model → {model}")

            response = client.models.generate_content(
                model=model,
                contents=SYSTEM_PROMPT + "\n\nJournal entry:\n" + text
            )

            raw = response.text.strip()

            try:
                parsed = _clean_json(raw)
                return {
                    "reflection": parsed.get("reflection", fallback["reflection"]),
                    "themes": parsed.get("themes", fallback["themes"]),
                    "follow_up_question": parsed.get("follow_up_question", fallback["follow_up_question"])
                }
            except Exception:
                print("[AI] JSON parse failed, trying next model.")
                print("Raw output:", raw)
                continue

        except Exception as e:
            print(f"[AI] Model failed → {model}")
            print("Reason:", e)
            time.sleep(1)

    print("[AI] All models failed → using fallback")
    return fallback


def analyze_community_story(text: str) -> dict:
    safety = analyze_content(text)
    return {
        "risk_score": safety["risk_score"],
        "flagged": safety["flagged"],
        "signals": list(safety.get("categories", {}).keys())
    }