import streamlit as st
import random
import requests
import googleapiclient.discovery

# Set up Hugging Face API Key
HF_API_KEY = "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"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# YouTube API Key
YOUTUBE_API_KEY = "AIzaSyAZ_-5Iqe_fHM5fs6MqxEStrjWfBtSS4Kk"

def search_youtube(topic):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=topic, part="snippet", maxResults=3)
    response = request.execute()
    return [(item['snippet']['title'], "https://www.youtube.com/watch?v=" + item['id']['videoId']) for item in response['items'] if 'videoId' in item['id']]

def generate_summary(text):
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    response = requests.post(api_url, headers=headers, json={"inputs": text})
    return response.json()[0]['summary_text'] if response.status_code == 200 else "Error generating summary."

def generate_questions(text):
    api_url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    response = requests.post(api_url, headers=headers, json={"inputs": text})
    return response.json() if response.status_code == 200 else "Error generating questions."

# Streamlit UI
st.title("AI Study Planner")

# User Inputs
st.header("Enter Syllabus Details")
syllabus = st.text_area("Paste your syllabus here")
num_chapters = st.number_input("Number of chapters", min_value=1, step=1)
days_left = st.number_input("Days until exam", min_value=1, step=1)

chapter_details = {}
for i in range(num_chapters):
    chapter = st.text_input(f"Chapter {i+1} Name")
    pages = st.number_input(f"Pages in Chapter {i+1}", min_value=1, step=1)
    chapter_details[chapter] = pages

# YouTube Video Search
st.header("Find YouTube Videos for Study")
topic = st.text_input("Enter a topic to search for videos")
if st.button("Search Videos"):
    videos = search_youtube(topic)
    for title, link in videos:
        st.write(f"[{title}]({link})")

# Summary & Questions Generation
st.header("Generate Summary & Questions from Video")
video_text = st.text_area("Paste video transcript or key points")
if st.button("Generate Summary & Questions"):
    st.write("**Summary:**")
    st.write(generate_summary(video_text))
    st.write("**Questions:**")
    st.write(generate_questions(video_text))

st.write("---")
st.write("Developed by Akash")
