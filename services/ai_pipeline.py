from services.azure_language import analyze_text
from services.azure_safety import analyze_content
from services.gemini import generate_reflection


def run_journal_ai(content: str) -> dict:
    """
    Central AI pipeline for journal entries.
    Uses:
    - Azure AI Language (sentiment + key phrases)
    - Azure Content Safety (risk scoring)
    - Gemini (reflection + themes with model failover)
    """

    print("run_journal_ai() called")

    # -------------------------
    # Azure AI Language
    # -------------------------
    language_result = analyze_text(content)

    # -------------------------
    # Azure Content Safety
    # -------------------------
    safety_result = analyze_content(content)

    # -------------------------
    # Gemini (reflection + themes)
    # -------------------------
    reflection_result = generate_reflection(content)

    return {
        # Azure Language
        "sentiment": language_result.get("sentiment", "neutral"),
        "sentiment_scores": language_result.get("sentiment_scores", {}),
        "key_phrases": language_result.get("key_phrases", []),

        # Azure Content Safety
        "risk_score": safety_result.get("risk_score", 0.0),
        "flagged": safety_result.get("flagged", False),

        # Gemini GenAI
        "reflection": reflection_result.get("reflection"),
        "themes": reflection_result.get("themes", []),
        "follow_up_question": reflection_result.get("follow_up_question")
    }
