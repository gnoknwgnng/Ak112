import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Gemini API key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

def extract_video_id(youtube_url):
    """Extracts the video ID from a YouTube URL"""
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_url)
    return match.group(1) if match else None

def get_transcript(video_url):
    """Fetches transcript for a YouTube video"""
    video_id = extract_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL"
    
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {e}"

def generate_summary_and_mcqs(transcript):
    """Generates summary and MCQs using Gemini AI"""
    prompt = f"Summarize this transcript:\n{transcript}\n\nThen generate 5 multiple-choice questions with 4 options each, marking the correct answer."
    
    try:
        response = genai.generate_text(model="gemini-pro", prompt=prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("### Enter YouTube Video URL")

youtube_url = st.text_input("Enter YouTube Video URL", "")

if st.button("Generate Summary & Quiz"):
    transcript = get_transcript(youtube_url)
    
    if "Error" in transcript or "Invalid" in transcript:
        st.error(transcript)
    else:
        st.write("**Summary & Quiz:**")
        response_text = generate_summary_and_mcqs(transcript)
        st.write(response_text)
