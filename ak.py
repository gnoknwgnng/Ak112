import streamlit as st
import requests

# Hugging Face API Key
API_KEY = "hf_your_api_key"  # Replace with your actual API key
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def generate_summary(text):
    """Generates a summary using Hugging Face API"""
    api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    response = requests.post(api_url, headers=HEADERS, json={"inputs": text})
    return response.json()[0]['summary_text'] if response.status_code == 200 else "Error generating summary."

def generate_questions(text):
    """Generates quiz questions using Hugging Face API"""
    api_url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
    response = requests.post(api_url, headers=HEADERS, json={"inputs": f"Generate 3 quiz questions from this text: {text}"})
    return response.json()[0]['generated_text'] if response.status_code == 200 else "Error generating questions."

# Streamlit UI
st.title("AI Study Planner")

st.header("Generate Summary & Questions from Video")
video_text = st.text_area("Paste video transcript or key points")
if st.button("Generate Summary & Questions"):
    st.write("**Summary:**")
    st.write(generate_summary(video_text))
    st.write("**Questions:**")
    st.write(generate_questions(video_text))

st.write("---")
st.write("Developed by Akash")
