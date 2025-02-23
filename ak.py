import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
import re

genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

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
    max_length = 5000
    words = text.split()
    translated_parts = []
    
    chunk = []
    chunk_length = 0
    
    for word in words:
        if chunk_length + len(word) + 1 <= max_length:
            chunk.append(word)
            chunk_length += len(word) + 1
        else:
            translated_part = GoogleTranslator(source="auto", target=target_lang).translate(" ".join(chunk))
            translated_parts.append(translated_part)
            chunk = [word]
            chunk_length = len(word) + 1
    
    if chunk:
        translated_part = GoogleTranslator(source="auto", target=target_lang).translate(" ".join(chunk))
        translated_parts.append(translated_part)
    
    return " ".join(translated_parts)

st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, translate it, generate a summary, and create multiple-choice questions.")

video_url = st.text_input("Enter YouTube Video URL:")

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
