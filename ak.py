import streamlit as st
import google.generativeai as genai

# Set up Gemini API Key
GEMINI_API_KEY = "AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU"
genai.configure(api_key=GEMINI_API_KEY)

def generate_summary(text):
    """Generate a summary using Gemini API."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Summarize the following text:\n{text}")
    
    if response and response.text:
        return response.text
    return "Error generating summary."

def generate_questions(text):
    """Generate questions using Gemini API."""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Generate 3 quiz questions from the following text:\n{text}")
    
    if response and response.text:
        return response.text
    return "Error generating questions."

# Streamlit UI
st.title("Generate Summary & Questions from Video")

video_text = st.text_area("Paste video transcript or key points")
if st.button("Generate Summary & Questions"):
    st.write("**Summary:**")
    summary = generate_summary(video_text)
    st.write(summary)

    st.write("**Questions:**")
    questions = generate_questions(video_text)
    st.write(questions)

st.write("---")
st.write("Developed by Akash")



















































































