
import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi

# API Keys
HUGGINGFACE_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyAZ_-5Iqe_fHM5fs6MqxEStrjWfBtSS4Kk"

# Function to get video details (Title) from YouTube API
def get_video_details(video_url):
    try:
        video_id = video_url.split("v=")[-1]
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "items" in data and len(data["items"]) > 0:
            return data["items"][0]["snippet"]["title"]
        return "Error fetching video title"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to get transcript from YouTube video
def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1]  # Extract video ID
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry["text"] for entry in transcript])
        return full_text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Function to summarize text using Hugging Face API
def summarize_text(text):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text})
    
    if response.ok:
        return response.json()[0]['summary_text']
    return "Error in summarization"

# Function to generate questions using Hugging Face API
def generate_questions(text):
    url = "https://api-inference.huggingface.co/models/valhalla/t5-base-qa-qg-hl"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text})

    if response.ok:
        return response.json()["generated_text"]
    return "Error generating questions"

# Streamlit UI
st.title("Plan: AI Study Assistant")

# Input: YouTube video URL
video_url = st.text_input("Paste YouTube Video URL")

if video_url:
    video_title = get_video_details(video_url)
    st.write("**Video Title:**", video_title)

    if st.button("Get Transcript"):
        transcript = get_youtube_transcript(video_url)
        st.text_area("Video Transcript", transcript, height=200)

    if st.button("Summarize"):
        if transcript:
            summary = summarize_text(transcript)
            st.write("**Summary:**", summary)
        else:
            st.write("Error: Please get the transcript first.")

    if st.button("Generate Questions"):
        if transcript:
            questions = generate_questions(transcript)
            st.write("**Generated Questions:**", questions)
        else:
            st.write("Error: Please get the transcript first.")

    st.button("Take a Remembrance Test")
    st.button("Show Related Videos")










