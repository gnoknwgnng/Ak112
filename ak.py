import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to get transcript from YouTube video
def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Function to summarize text using Gemini
def summarize_text(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this: {text}")
        return response.text
    except Exception as e:
        return f"Error summarizing: {str(e)}"

# Function to generate MCQs using Gemini
def generate_mcqs(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Generate 5 multiple-choice questions from this: {text}")
        return response.text
    except Exception as e:
        return f"Error generating MCQs: {str(e)}"

# Streamlit UI
st.title("Generate Summary & Questions from Video")
video_url = st.text_input("Paste YouTube video URL")

if st.button("Generate Summary & Questions"):
    with st.spinner("Fetching transcript..."):
        transcript_text = get_youtube_transcript(video_url)

    if "Error" in transcript_text:
        st.error(transcript_text)
    else:
        st.subheader("Transcript")
        st.write(transcript_text[:1000] + "...")  # Show a preview of the transcript

        with st.spinner("Generating Summary..."):
            summary = summarize_text(transcript_text)
        st.subheader("Summary")
        st.write(summary)

        with st.spinner("Generating MCQs..."):
            mcqs = generate_mcqs(transcript_text)
        st.subheader("Multiple Choice Questions")
        st.write(mcqs)




























