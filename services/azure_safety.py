import os
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.contentsafety.models import AnalyzeTextOptions

AZURE_CONTENT_SAFETY_KEY = os.getenv("AZURE_CONTENT_SAFETY_KEY")
AZURE_CONTENT_SAFETY_ENDPOINT = os.getenv("AZURE_CONTENT_SAFETY_ENDPOINT")

client = None
if AZURE_CONTENT_SAFETY_KEY and AZURE_CONTENT_SAFETY_ENDPOINT:
    client = ContentSafetyClient(
        endpoint=AZURE_CONTENT_SAFETY_ENDPOINT,
        credential=AzureKeyCredential(AZURE_CONTENT_SAFETY_KEY)
    )


def analyze_content(text: str) -> dict:
    fallback = {
        "risk_score": 0.1,
        "categories": {},
        "flagged": False
    }

    if not client:
        print("Content Safety client missing")
        return fallback

    try:
        options = AnalyzeTextOptions(text=text)
        response = client.analyze_text(options)

        max_severity = 0
        categories = {}

        for item in response.categories_analysis:
            category = item.category
            severity = item.severity or 0

            categories[category] = severity
            max_severity = max(max_severity, severity)

        # Normalize severity (Azure scale is 0–4)
        risk_score = min(max_severity / 4, 1.0)

        return {
            "risk_score": risk_score,
            "categories": categories,
            "flagged": risk_score >= 0.5
        }

    except Exception as e:
        print("Content Safety error:", e)
        return fallback