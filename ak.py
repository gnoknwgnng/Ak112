import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

def extract_video_id(url):
    """Extracts the YouTube video ID from various URL formats."""
    pattern = r"(?:v=|be/|embed/|youtu.be/|/v/|/e/|watch\?v=|&v=|/v=)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_available_languages(video_id):
    """Fetches available subtitle languages for a given YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return {t.language: t.language_code for t in transcript_list}
    except TranscriptsDisabled:
        return "Transcripts are disabled for this video."
    except Exception as e:
        return f"Error: {str(e)}"

def get_youtube_transcript(video_id, lang_code="en"):
    """Fetches transcript in the selected language."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
        text = " ".join([t["text"] for t in transcript])
        return text
    except NoTranscriptFound:
        return "No transcript available in the selected language."
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def summarize_text(text):
    """Generates a summary using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this in simple points:\n\n{text}")
        return response.text
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def generate_mcqs(text):
    """Generates MCQs from the text using Gemini AI."""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"""
        Generate 5 multiple-choice questions from this text in the following format:
        
        Q1: What is the main topic discussed?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: B
        
        Ensure the format is strictly followed. Only return questions, options, and correct answers.
        Text: {text}
        """)
        return response.text
    except Exception as e:
        return f"Error generating MCQs: {str(e)}"

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, generate a summary, and create multiple-choice questions.")

video_url = st.text_input("Enter YouTube Video URL:")

if st.button("Fetch Available Languages"):
    video_id = extract_video_id(video_url)
    if video_id:
        available_languages = get_available_languages(video_id)
        if isinstance(available_languages, dict):
            st.session_state["languages"] = available_languages
            st.success("Languages fetched successfully!")
        else:
            st.error(available_languages)
    else:
        st.error("Invalid YouTube URL.")

if "languages" in st.session_state:
    selected_language = st.selectbox("Select language for transcript:", list(st.session_state["languages"].keys()))
    lang_code = st.session_state["languages"][selected_language]
    
    if st.button("Get Transcript"):
        transcript = get_youtube_transcript(video_id, lang_code)
        st.session_state["transcript"] = transcript
        
if "transcript" in st.session_state:
    st.subheader("Extracted Transcript")
    st.write(st.session_state["transcript"])
    
    if st.button("Summarize Transcript"):
        summary = summarize_text(st.session_state["transcript"])
        st.session_state["summary"] = summary

if "summary" in st.session_state:
    st.subheader("Summary of the Video")
    st.write(st.session_state["summary"])
    
    if st.button("Generate MCQs"):
        mcq_text = generate_mcqs(st.session_state["summary"])
        st.session_state["mcqs"] = mcq_text

if "mcqs" in st.session_state:
    st.subheader("Multiple Choice Questions")
    
    mcqs = st.session_state["mcqs"].strip().split("\n\n")
    answers = {}
    
    for i, mcq in enumerate(mcqs):
        lines = mcq.split("\n")
        if len(lines) >= 5:
            question = lines[0]
            options = lines[1:5]
            correct_answer = lines[5].split(":")[-1].strip()
            
            st.write(question)
            user_answer = st.radio(f"Select answer for {question}", options, key=f"q{i}")
            answers[f"q{i}"] = (user_answer, correct_answer)
    
    if st.button("Submit Test"):
        score = sum(1 for key, (user_ans, correct_ans) in answers.items() if user_ans.startswith(correct_ans))
        st.success(f"Test completed! Your score: {score}/{len(answers)}")
