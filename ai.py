import os
import csv
import datetime
import streamlit as st
import pyttsx3
import speech_recognition as sr
from openai import OpenAI

#  CONFIG 
OPENAI_API_KEY = "your api key" #https://platform.openai.com/api-keys
CSV_LOG_FILE = "voice_ai_log.csv" #file name
client = OpenAI(api_key=OPENAI_API_KEY)


def listen_to_microphone():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("🎤 Listening..."):
            audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        return text
    except:
        return None

def gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ GPT Error: {e}"

def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def log_to_csv(user_text, ai_text):
    file_exists = os.path.isfile(CSV_LOG_FILE)
    with open(CSV_LOG_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "User", "AI"])
        writer.writerow([datetime.datetime.now().isoformat(), user_text, ai_text])

#  CUSTOM UI
st.markdown("""
    <style>
        body {
            background-color: #F1F5F8;
        }
        .main {
            background-color: #F7FAFC;
            padding: 2rem;
            border-radius: 12px;
        }
        .block-container {
            padding-top: 2rem;
        }
        .chat-bubble {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        }
        .user {
            color: #3b82f6;
            font-weight: bold;
        }
        .ai {
            color: #10b981;
            font-weight: bold;
        }
        button[kind="primary"] {
            background-color: #3b82f6;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("🎙️ Voice AI Chat")
st.caption("Talk to an AI, hear it reply, and keep a log!")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("🎤 Start Voice Input"):
    user_input = listen_to_microphone()

    if user_input:
        st.success(f"🧑 You said: {user_input}")
        ai_reply = gpt_response(user_input)
        st.info(f"🤖 GPT: {ai_reply}")

        
        speak_text(ai_reply) # Speak out loud

        
        log_to_csv(user_input, ai_reply) # Save to CSV

        
        st.session_state.history.append((user_input, ai_reply)) # Save to history
    else:
        st.warning("Could not understand audio. Please try again.")

#  CHAT HISTORY 
st.markdown("## 🧾 Chat History")
for i, (user, ai) in enumerate(reversed(st.session_state.history), 1):
    st.markdown(f"""
        <div class='chat-bubble'>
            <div class='user'>🧑 You:</div>
            <div>{user}</div>
            <div class='ai'>🤖 GPT:</div>
            <div>{ai}</div>
        </div>
    """, unsafe_allow_html=True)
