import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import random

HUGGINGFACE_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyAZ_-5Iqe_fHM5fs6MqxEStrjWfBtSS4Kk"

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
    response = requests.post(url, headers=headers, json={"inputs": text[:1024]})
    return response.json()[0]['summary_text'] if response.ok else "Error in summarization"

# Function to generate questions using Hugging Face API
def generate_questions(text):
    url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text[:1024]})
    return response.json()[0]['question'] if response.ok else "Error generating questions"

# Function to fetch related YouTube videos
def get_related_videos(video_url):
    video_id = video_url.split("v=")[-1]
    url = f"https://www.googleapis.com/youtube/v3/search?relatedToVideoId={video_id}&type=video&key={YOUTUBE_API_KEY}&part=snippet"
    response = requests.get(url)
    if response.ok:
        videos = response.json().get("items", [])
        return [(video["snippet"]["title"], "https://www.youtube.com/watch?v=" + video["id"]["videoId"]) for video in videos]
    return [("No related videos found", "#")]

st.title("AI Study Tutor: Summarize, Quiz & Plan")
video_url = st.text_input("Paste YouTube Video URL")

if st.button("Get Transcript"):
    transcript = get_youtube_transcript(video_url)
    st.session_state.transcript = transcript
    st.text_area("Video Transcript", transcript, height=200)

if "transcript" in st.session_state:
    transcript = st.session_state.transcript
    
    if st.button("Summarize"):
        summary = summarize_text(transcript)
        st.session_state.summary = summary
        st.write("Summary:", summary)
    
    if "summary" in st.session_state:
        if st.button("Generate Questions"):
            questions = generate_questions(st.session_state.summary)
            st.write("Generated Questions:", questions)
    
    if st.button("Take a Remembrance Test"):
        st.write("Answer the following questions:")
        sample_questions = ["What is the main topic of the video?", "What are key points mentioned?", "Summarize in your own words."]
        random.shuffle(sample_questions)
        for i, q in enumerate(sample_questions[:3]):
            st.text_input(f"Q{i+1}: {q}")

    if st.button("Show Related Videos"):
        related_videos = get_related_videos(video_url)
        for title, link in related_videos:
            st.markdown(f"[{title}]({link})")










