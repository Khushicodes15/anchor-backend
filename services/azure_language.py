import os
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")
AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")


def get_language_client():
    """
    Create Azure AI Language client
    """
    if not AZURE_LANGUAGE_KEY or not AZURE_LANGUAGE_ENDPOINT:
        print("azure language env MISSING")
        return None

    return TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_LANGUAGE_KEY)
    )


def analyze_text(text: str) -> dict:
    print("analyze_text called")

    fallback = {
        "sentiment": "neutral",
        "sentiment_scores": {
            "positive": 0.33,
            "neutral": 0.34,
            "negative": 0.33
        },
        "key_phrases": []
    }

    client = get_language_client()
    if not client:
        print("Azure Language client missing")
        return fallback

    try:
        response = client.analyze_sentiment(
            documents=[text],
            show_opinion_mining=False
        )

        result = response[0]
        scores = result.confidence_scores  

        derived_sentiment = max(
            ["positive", "neutral", "negative"],
            key=lambda k: getattr(scores, k)
        )

        key_phrase_result = client.extract_key_phrases(
            documents=[text]
        )[0]

        return {
            "sentiment": derived_sentiment,
            "sentiment_scores": {
                "positive": scores.positive,
                "neutral": scores.neutral,
                "negative": scores.negative
            },
            "key_phrases": key_phrase_result.key_phrases
        }

    except Exception as e:
        print("Azure Language error:", e)
        return fallback