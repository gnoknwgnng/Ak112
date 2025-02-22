import streamlit as st
import requests
import random
import googleapiclient.discovery

# API Keys
HUGGINGFACE_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyAZ_-5Iqe_fHM5fs6MqxEStrjWfBtSS4Kk"

# Function to summarize text using Hugging Face API
def summarize_text(text):
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text})
    return response.json()[0]['summary_text'] if response.ok else "Error in summarization"

# Function to generate questions using Hugging Face API
def generate_questions(text):
    url = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(url, headers=headers, json={"inputs": text})
    return response.json() if response.ok else "Error in question generation"

# Function to search YouTube videos
def search_youtube_videos(query):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=query, part="snippet", maxResults=5)
    response = request.execute()
    return response['items']

st.title("AI Study Planner")

# Step 1: Input syllabus details
st.header("Enter Your Syllabus Details")
syllabus = st.text_area("Paste the syllabus")
chapters = st.number_input("Number of chapters", min_value=1, step=1)
exam_days = st.number_input("Days until exam", min_value=1, step=1)

# Step 2: Remembrance Test
st.header("Remembrance Test")
paragraph = "Artificial Intelligence is the simulation of human intelligence in machines that are programmed to think and learn."
show_paragraph = st.checkbox("Show paragraph")
if show_paragraph:
    st.write(paragraph)

test_questions = [
    ("What does AI stand for?", "Artificial Intelligence"),
    ("What is AI programmed to do?", "Think and learn")
]

if st.button("Start Test"):
    st.write("Answer the following questions:")
    for q, ans in test_questions:
        user_ans = st.text_input(q)
        if user_ans:
            st.write("Correct!" if user_ans.lower() == ans.lower() else "Incorrect")

# Step 3: Generate Study Schedule
st.header("Study Schedule")
if st.button("Generate Schedule"):
    schedule = f"Study {chapters // exam_days} chapters per day."
    st.write(schedule)

# Step 4: Fetch Related YouTube Videos
st.header("Related YouTube Videos")
search_query = st.text_input("Enter topic to search on YouTube")
if st.button("Find Videos"):
    if search_query:
        videos = search_youtube_videos(search_query)
        for video in videos:
            st.write(f"[{video['snippet']['title']}](https://www.youtube.com/watch?v={video['id']['videoId']})")
    else:
        st.write("Please enter a topic to search.")

# Step 5: Summarize and Generate Questions from Video Content
st.header("Summarize & Generate Questions from Video Content")
video_text = st.text_area("Paste video transcript")
if st.button("Summarize"):
    summary = summarize_text(video_text)
    st.write("Summary:", summary)

if st.button("Generate Questions"):
    questions = generate_questions(video_text)
    st.write("Generated Questions:", questions)

st.write("Deploy this app on Streamlit!")






