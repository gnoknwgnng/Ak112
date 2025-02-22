import streamlit as st
import random
import openai
import googleapiclient.discovery

# Set up Hugging Face API Key
openai.api_key = "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"

# YouTube API Key (Replace with your API key)
YOUTUBE_API_KEY = "AIzaSyAZ_-5Iqe_fHM5fs6MqxEStrjWfBtSS4Kk"

def search_youtube(topic):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(q=topic, part="snippet", maxResults=3)
    response = request.execute()
    return [(item['snippet']['title'], "https://www.youtube.com/watch?v=" + item['id']['videoId']) for item in response['items'] if 'videoId' in item['id']]

def generate_summary(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "system", "content": "Summarize the following content."},
                  {"role": "user", "content": text}]
    )
    return response["choices"][0]["message"]["content"]

def generate_questions(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "system", "content": "Generate 3 quiz questions from the following content."},
                  {"role": "user", "content": text}]
    )
    return response["choices"][0]["message"]["content"]

# Streamlit UI
st.title("AI Study Planner")

# User Inputs
st.header("Enter Syllabus Details")
syllabus = st.text_area("Paste your syllabus here")
num_chapters = st.number_input("Number of chapters", min_value=1, step=1)
days_left = st.number_input("Days until exam", min_value=1, step=1)

chapter_details = {}
for i in range(num_chapters):
    chapter = st.text_input(f"Chapter {i+1} Name", key=f"chapter_{i}")
    pages = st.number_input(f"Pages in Chapter {i+1}", min_value=1, step=1, key=f"pages_{i}")
    chapter_details[chapter] = pages

# Remembrance Test
st.header("Remembrance Test")
test_paragraph = "This is a sample paragraph for testing memory. Try to remember it!"
if st.button("Start Test"):
    st.session_state.show_questions = True
    st.session_state.test_paragraph_shown = True

if st.session_state.get("test_paragraph_shown", False):
    st.write(test_paragraph)

if st.session_state.get("show_questions", False):
    st.write("\nAnswer the following questions:")
    st.write("1. What was the topic about?")
    st.text_input("Your Answer:", key="question_1")
    st.write("2. Mention a key point.")
    st.text_input("Your Answer:", key="question_2")
    score = random.randint(0, 10)  # Simulated score
    st.write(f"Your Score: {score}/10")

    # Study Plan Logic
    st.header("Your Study Plan")
    plan = ""
    if score > 7:
        plan = "Revise each chapter lightly, focus on weak areas."
    elif score > 4:
        plan = "Balanced study approach with moderate revision."
    else:
        plan = "Intensive study required. Allocate more time to difficult topics."
    st.write(plan)

# YouTube Video Search and Summary
st.header("Find YouTube Videos for Study")
topic = st.text_input("Enter a topic to search for videos", key="video_topic")
if st.button("Search Videos"):
    videos = search_youtube(topic)
    for title, link in videos:
        st.write(f"[{title}]({link})")

st.header("Generate Summary & Questions from Video")
video_text = st.text_area("Paste video transcript or key points", key="video_text")
if st.button("Generate Summary & Questions"):
    st.write("**Summary:**")
    st.write(generate_summary(video_text))
    st.write("**Questions:**")
    st.write(generate_questions(video_text))

st.write("---")
st.write("Developed by Akash")
