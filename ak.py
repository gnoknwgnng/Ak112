import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to extract video transcript
def get_transcript(video_url):
    video_id = re.search(r"v=([\w-]+)", video_url)
    if video_id:
        video_id = video_id.group(1)
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            text = " ".join([entry['text'] for entry in transcript])
            return text
        except:
            return "Error: Unable to fetch transcript."
    return "Invalid YouTube URL."

# Function to generate summary and MCQs
def generate_summary_and_mcqs(transcript):
    prompt = f"""
    Generate a concise summary of the following transcript:
    {transcript}
    
    Then, create 5 multiple-choice questions (MCQs) with four options each. Indicate the correct answer.
    """
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# Extract MCQs from text
def extract_mcqs(text):
    mcqs = []
    pattern = re.findall(r"Q\d+: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: (.*?)\n", text)
    for match in pattern:
        question, *options, answer = match
        mcqs.append({
            "question": question,
            "options": options,
            "answer": answer.strip()
        })
    return mcqs

# Streamlit UI
st.title("YouTube AI Tutor")
video_url = st.text_input("Enter YouTube Video URL")

if st.button("Generate Summary & Quiz"):
    transcript = get_transcript(video_url)
    if "Error" in transcript:
        st.error(transcript)
    else:
        response_text = generate_summary_and_mcqs(transcript)
        summary, mcqs_text = response_text.split("\n\n", 1)
        
        st.write("**Summary:**")
        st.write(summary.strip())
        
        mcqs = extract_mcqs(mcqs_text)
        user_answers = {}
        
        st.write("**Quiz:**")
        for idx, mcq in enumerate(mcqs):
            user_answers[idx] = st.radio(mcq["question"], mcq["options"], key=idx)
        
        if st.button("Submit Test"):
            score = sum(1 for i in range(len(mcqs)) if user_answers[i] == mcqs[i]["answer"])
            st.write(f"Your Score: {score}/{len(mcqs)}")
















