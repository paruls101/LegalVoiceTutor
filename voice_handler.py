import os
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
import streamlit as st

# Initialize clients
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

def get_elevenlabs_client():
    api_key = os.getenv("ELEVENLABS_API_KEY") or st.secrets.get("ELEVENLABS_API_KEY")
    if not api_key:
        return None
    return ElevenLabs(api_key=api_key)

def transcribe_audio(audio_file):
    """
    Transcribes audio file object using OpenAI Whisper.
    """
    client = get_openai_client()
    if not client:
        return "Error: OpenAI API Key missing."
        
    try:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        return f"Transcription Error: {e}"

def synthesize_speech(text):
    """
    Converts text to speech using ElevenLabs.
    Returns bytes of audio data.
    """
    client = get_elevenlabs_client()
    if not client:
        return None

    try:
        # Using a standard pre-made voice (e.g., 'Adam' or 'Rachel')
        # You might want to make this configurable
        audio_generator = client.generate(
            text=text,
            voice="Rachel", 
            model="eleven_monolingual_v1"
        )
        
        # Gather the generator into bytes
        audio_bytes = b"".join(list(audio_generator))
        return audio_bytes
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return None

