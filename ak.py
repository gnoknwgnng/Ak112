import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi

HUGGINGFACE_API_KEY = "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"

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def generate_summary(text):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    response = requests.post(url, headers=headers, json={"inputs": text}, timeout=60)
    
    if response.ok:
        return response.json()["summary_text"]
    return f"Error generating summary: {response.json()}"

def generate_questions(text):
    url = "https://api-inference.huggingface.co/models/iarfmoose/t5-base-question-generator"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    response = requests.post(url, headers=headers, json={"inputs": text}, timeout=60)
    
    if response.ok:
        return response.json()[0]['generated_text']  # Adjust based on model response
    return f"Error generating questions: {response.json()}"  # Print exact error

st.title("YouTube Video Transcript Summarizer & Question Generator")

video_url = st.text_input("Enter YouTube Video URL:")

if video_url:
    video_id = video_url.split("v=")[-1]
    transcript = get_transcript(video_id)
    
    if "Error" not in transcript:
        st.write("### Video Transcript:")
        st.write(transcript)
        
        if st.button("Summarize"):
            summary = generate_summary(transcript)
            st.write("### Summary:")
            st.write(summary)
        
        if st.button("Generate Questions"):
            questions = generate_questions(transcript)
            st.write("### Questions:")
            st.write(questions)
    else:
        st.error(transcript)






























































































