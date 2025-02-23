

import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
import re

genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")  # Replace with your valid API key

def extract_video_id(url):
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([\w-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_list]
        preferred_languages = ["en", "hi"] + available_languages
        selected_language = next((lang for lang in preferred_languages if lang in available_languages), None)
        
        if selected_language:
            transcript = transcript_list.find_transcript([selected_language]).fetch()
            text = " ".join([t["text"] for t in transcript])
            return text, selected_language
        else:
            return "No transcript available.", None
    except (TranscriptsDisabled, NoTranscriptFound):
        return "Transcript not available for this video.", None
    except Exception as e:
        return f"Error fetching transcript: {str(e)}", None

def translate_text(text, target_lang="en"):
    words = text.split()
    translated_parts = []
    chunk_size = 100  # Translate in chunks of 100 words to prevent errors
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        translated_part = GoogleTranslator(source="auto", target=target_lang).translate(chunk)
        translated_parts.append(translated_part)
    
    return " ".join(translated_parts)

def generate_summary(text, lang="en"):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Summarize the following text in {lang}: {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_mcqs(text, lang="en"):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Generate 3 multiple-choice questions in {lang} from the following text. Provide four answer options for each question, and mark the correct answer with (*): {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, translate it, generate a summary, and create multiple-choice questions.")

video_url = st.text_input("Enter YouTube Video URL:")

if "mcqs" not in st.session_state:
    st.session_state["mcqs"] = []
if "score" not in st.session_state:
    st.session_state["score"] = 0

st.write(st.session_state.get("mcqs", "No MCQs generated"))

if st.button("Get Transcript"):
    if video_url.strip():
        video_id = extract_video_id(video_url)
        if video_id:
            transcript, detected_lang = get_youtube_transcript(video_id)
            st.session_state["transcript"] = transcript
            st.session_state["detected_lang"] = detected_lang if detected_lang else "Unknown"
            st.success("Transcript fetched successfully!")
        else:
            st.warning("Invalid YouTube URL. Please check the link.")
    else:
        st.warning("Please enter a valid YouTube URL.")

if "detected_lang" in st.session_state:
    st.subheader("Extracted Transcript")
    st.write(f"**Detected Language:** {st.session_state['detected_lang'].upper()}")
    st.write(st.session_state["transcript"])
else:
    st.warning("No transcript available or detected language.")

target_lang = st.selectbox("Select language to translate:", ["en", "hi", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko"], index=0)
if st.button("Translate Transcript"):
    translated_text = translate_text(st.session_state.get("transcript", ""), target_lang)
    st.session_state["translated_transcript"] = translated_text

if "translated_transcript" in st.session_state:
    st.subheader("Translated Transcript")
    st.write(st.session_state["translated_transcript"])

summary_lang = st.selectbox("Select language for Summary:", ["en", "hi", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko"], index=0)
if st.button("Generate Summary"):
    summary = generate_summary(st.session_state.get("transcript", ""), summary_lang)
    st.session_state["summary"] = summary

if "summary" in st.session_state:
    st.subheader("Summary")
    st.write(st.session_state["summary"])

quiz_lang = st.selectbox("Select language for Quiz:", ["en", "hi", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko"], index=0)
if st.button("Generate MCQs"):
    mcqs = generate_mcqs(st.session_state.get("transcript", ""), quiz_lang)
    st.session_state["mcqs"] = mcqs

if "mcqs" in st.session_state:
    st.subheader("Multiple-Choice Questions")
    st.write(st.session_state["mcqs"])






