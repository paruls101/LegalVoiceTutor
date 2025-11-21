import streamlit as st
import os
import json
import time
from dotenv import load_dotenv
from quiz_engine import QuizEngine
import voice_handler

# Load environment variables
load_dotenv()

# Constants
PROCESSED_DATA_FILE = "data/processed/knowledge_base.json"

# Page Config
st.set_page_config(
    page_title="LegalMind Voice Tutor",
    page_icon="⚖️",
    layout="wide"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []  # List of {role, content, audio_bytes}
if "current_item" not in st.session_state:
    st.session_state.current_item = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "waiting_for_answer" not in st.session_state:
    st.session_state.waiting_for_answer = False
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = []
if "quiz_engine" not in st.session_state:
    st.session_state.quiz_engine = QuizEngine()

def load_data():
    """Loads the knowledge base JSON."""
    if os.path.exists(PROCESSED_DATA_FILE):
        with open(PROCESSED_DATA_FILE, "r", encoding="utf-8") as f:
            st.session_state.knowledge_base = json.load(f)
            st.sidebar.success(f"Loaded {len(st.session_state.knowledge_base)} cases/principles.")
    else:
        st.sidebar.warning("No knowledge base found. Please upload notes and parse them.")

def play_audio(audio_bytes):
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)

def next_question():
    """Generates a new question and updates state."""
    if not st.session_state.knowledge_base:
        st.error("No knowledge base loaded.")
        return

    q_text, item = st.session_state.quiz_engine.generate_question(st.session_state.knowledge_base)
    
    if q_text and item:
        st.session_state.current_question = q_text
        st.session_state.current_item = item
        st.session_state.waiting_for_answer = True
        
        # Generate Audio for Question
        audio_bytes = voice_handler.synthesize_speech(q_text)
        
        # Add to history
        st.session_state.history.append({
            "role": "assistant",
            "content": q_text,
            "audio": audio_bytes
        })
        return True
    return False

def handle_answer(user_text=None, audio_file=None):
    """Processes user answer (text or audio)."""
    if not st.session_state.waiting_for_answer:
        return

    user_input = user_text
    
    if audio_file:
        with st.spinner("Transcribing..."):
            user_input = voice_handler.transcribe_audio(audio_file)
            
    if not user_input:
        return

    # Add User Answer to History
    st.session_state.history.append({
        "role": "user",
        "content": user_input,
        "audio": None
    })

    # Evaluate
    if st.session_state.current_question and st.session_state.current_item:
        with st.spinner("Evaluating..."):
            feedback = st.session_state.quiz_engine.evaluate_answer(
                st.session_state.current_question,
                user_input,
                st.session_state.current_item
            )
            
            # Generate Audio for Feedback
            audio_bytes = voice_handler.synthesize_speech(feedback)
            
            st.session_state.history.append({
                "role": "assistant",
                "content": feedback,
                "audio": audio_bytes
            })
            
    st.session_state.waiting_for_answer = False

def sidebar_ui():
    with st.sidebar:
        st.title("LegalMind ⚖️")
        st.markdown("### Settings")
        
        # API Key Status
        openai_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
        eleven_key = os.getenv("ELEVENLABS_API_KEY") or st.secrets.get("ELEVENLABS_API_KEY")
        
        if openai_key:
            st.success("OpenAI Key Detected")
        else:
            st.error("OpenAI Key Missing")
            
        if eleven_key:
            st.success("ElevenLabs Key Detected")
        else:
            st.warning("ElevenLabs Key Missing (Voice Output Disabled)")

        st.markdown("---")
        
        # Data Management
        st.subheader("Knowledge Base")
        if st.button("Reload Data"):
            load_data()
            
        if st.button("Process Raw Notes"):
            with st.spinner("Parsing notes... this may take a while"):
                try:
                    import parser
                    parser.parse_notes()
                    load_data()
                    st.success("Parsing Complete!")
                except Exception as e:
                    st.error(f"Parsing failed: {e}")

def main_ui():
    st.title("LegalMind Voice Tutor")
    st.markdown("Practice your oral argumentation and recall.")

    # 1. Quiz Display Area
    st.markdown("### 🗣️ Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        for msg in st.session_state.history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("audio"):
                    st.audio(msg["audio"], format="audio/mp3")

    # 2. Interaction Area
    st.markdown("---")
    
    # Controls based on state
    if not st.session_state.current_question:
        # Initial Start
        if st.button("Start Quiz"):
            if next_question():
                st.rerun()
    elif st.session_state.waiting_for_answer:
        # Waiting for user input
        st.write("🎙️ **Your Turn**")
        
        # Audio Input
        audio_val = st.audio_input("Record your answer")
        if audio_val:
            handle_answer(audio_file=audio_val)
            st.rerun()
            
        # Text Input Fallback
        user_text = st.chat_input("Or type your answer here...")
        if user_text:
            handle_answer(user_text=user_text)
            st.rerun()
            
        if st.button("Skip / Show Answer"):
             handle_answer(user_text="I don't know, please explain.")
             st.rerun()
             
    else:
        # Feedback given, waiting for Next
        if st.button("Next Question", type="primary"):
            next_question()
            st.rerun()

if __name__ == "__main__":
    # Load data on start
    if not st.session_state.knowledge_base:
        load_data()
        
    sidebar_ui()
    main_ui()

