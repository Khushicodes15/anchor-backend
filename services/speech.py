import os
from dotenv import load_dotenv

load_dotenv()

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")

def speech_to_text(audio_bytes: bytes) -> str:
    """
    Converts speech audio to text using Azure Speech.
    """
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        return ""

    try:
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )

        audio_config = speechsdk.AudioConfig(stream=speechsdk.AudioInputStream(audio_bytes))
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        result = recognizer.recognize_once()

        return result.text if result.text else ""

    except Exception as e:
        print("Speech to text failed:", e)
        return ""


def text_to_speech(text: str) -> bytes:
    """
    Converts text to calming speech audio.
    """
    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        return b""

    try:
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=None
        )

        result = synthesizer.speak_text_async(text).get()
        return result.audio_data

    except Exception as e:
        print("Text to speech failed:", e)
        return b""