import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Configure Gemini API
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")  # Replace with your actual API key

# Function to extract transcript from YouTube video
def get_video_transcript(video_url):
    video_id = re.search(r"v=([A-Za-z0-9_-]+)", video_url)
    if not video_id:
        return "Invalid YouTube URL"
    video_id = video_id.group(1)

    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Function to generate summary and MCQs using Gemini
def generate_summary_and_mcqs(transcript):
    prompt = f"""
    Given the following video transcript, generate:
    1. A short summary.
    2. Five multiple-choice questions (MCQs) with four options each, and indicate the correct answer.

    Transcript:
    {transcript}
    """
    
    response = genai.generate_text(model="gemini-pro", prompt=prompt)
    return response.text

# Function to extract MCQs from Gemini's response
def extract_mcqs(response_text):
    mcqs = []
    pattern = re.findall(r"(\d+\..*?)\n(A\..*?)\n(B\..*?)\n(C\..*?)\n(D\..*?)\nAnswer: (.)", response_text, re.DOTALL)
    
    for q in pattern:
        question, option_a, option_b, option_c, option_d, answer = q
        mcqs.append({
            "question": question.strip(),
            "options": [option_a.strip(), option_b.strip(), option_c.strip(), option_d.strip()],
            "answer": answer.strip()
        })
    
    return mcqs

# Streamlit UI
st.title("Generate Summary & Quiz from Video")

video_url = st.text_input("Enter YouTube Video URL", "")

if st.button("Generate Summary & Quiz"):
    if video_url:
        transcript = get_video_transcript(video_url)
        
        if "Error" in transcript or "Invalid" in transcript:
            st.error(transcript)
        else:
            st.write("**Summary:**")
            response_text = generate_summary_and_mcqs(transcript)
            summary, mcqs_text = response_text.split("2.", 1)
            st.write(summary.strip())

            # Extract and display MCQs
            mcqs = extract_mcqs(mcqs_text)
            st.write("**Quiz:**")

            score = 0
            user_answers = {}
            
            for idx, mcq in enumerate(mcqs):
                st.write(f"**{idx+1}. {mcq['question']}**")
                user_answers[idx] = st.radio(
                    f"Select an answer for question {idx+1}:", mcq["options"], index=None
                )

            if st.button("Submit Answers"):
                for idx, mcq in enumerate(mcqs):
                    if user_answers[idx] and user_answers[idx][0] == mcq["answer"]:
                        score += 1

                st.write(f"**Your Score: {score}/{len(mcqs)}**")

    else:
        st.warning("Please enter a valid YouTube video URL.")



















