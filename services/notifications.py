from services.firebase import firebase_auth
import os
from dotenv import load_dotenv

load_dotenv()
TOPIC = os.getenv("FCM_TOPIC", "anchor_notifications")

def send_notification(title: str, body: str, topic: str = TOPIC):
    """
    Send a notification to all users subscribed to the topic.
    """
    from firebase_admin import messaging

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        topic=topic
    )

    try:
        response = messaging.send(message)
        return {"success": True, "response": response}
    except Exception as e:
        return {"success": False, "error": str(e)}
