import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import re
from deep_translator import GoogleTranslator

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to extract video ID from any YouTube URL format
def extract_video_id(url):
    patterns = [
        r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]{11})",
        r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([\w-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# Function to extract YouTube transcript with language support
def get_youtube_transcript(video_id, lang_code="en"):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang_code])
        text = " ".join([t["text"] for t in transcript])  # Merge transcript text
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Function to translate text
def translate_text(text, target_lang="en"):
    max_length = 5000  # Limit for translation API
    translated_parts = []
    
    # Split text into chunks of max_length characters
    for i in range(0, len(text), max_length):
        part = text[i:i+max_length]
        translated_part = GoogleTranslator(source="auto", target=target_lang).translate(part)
        translated_parts.append(translated_part)

    # Combine translated parts
    return " ".join(translated_parts)

# Function to summarize text
def summarize_text(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize the following text in simple points:\n\n{text}")
        return response.text
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# Function to generate MCQs
def generate_mcqs(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"""
        Generate 5 multiple-choice questions from this text in the following format:
        
        Q1: What is the main topic discussed?
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: B
        
        Ensure the format is strictly followed. Only return questions, options, and correct answers.
        Text: {text}
        """)
        return response.text
    except Exception as e:
        return f"Error generating MCQs: {str(e)}"

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, generate a summary, and create multiple-choice questions.")

# User inputs YouTube URL
video_url = st.text_input("Enter YouTube Video URL:")
lang_code = st.selectbox("Select language for transcript:", ["en", "hi", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko"], index=0)

if st.button("Get Transcript"):
    if video_url.strip():
        video_id = extract_video_id(video_url)
        
        if video_id:
            transcript = get_youtube_transcript(video_id, lang_code)
            st.session_state["transcript"] = transcript  # Store transcript in session state
        else:
            st.warning("Invalid YouTube URL. Please check the link.")
    else:
        st.warning("Please enter a valid YouTube URL.")

# Display transcript
if "transcript" in st.session_state:
    st.subheader("Extracted Transcript")
    st.write(st.session_state["transcript"])

    # Generate Summary
    if st.button("Summarize Transcript"):
        transcript = st.session_state.get("transcript", "")
        if transcript:
            translated_text = translate_text(transcript, "en")
            summary = summarize_text(translated_text)
            st.session_state["summary"] = summary  # Store summary in session state
        else:
            st.warning("No transcript available.")

# Display Summary
if "summary" in st.session_state:
    st.subheader("Summary of the Video")
    st.write(st.session_state["summary"])

    # Generate MCQs
    if st.button("Generate MCQs"):
        mcq_text = generate_mcqs(st.session_state["summary"])  # Use summary for MCQs
        st.session_state["mcqs"] = mcq_text  # Store MCQs in session state

# Display MCQs
if "mcqs" in st.session_state:
    st.subheader("Multiple Choice Questions")
    
    mcqs = st.session_state["mcqs"].strip().split("\n\n")  # Split each question
    answers = {}  # Store user-selected answers
    
    for i, mcq in enumerate(mcqs):
        lines = mcq.split("\n")
        if len(lines) >= 5:  # Ensure it's a valid MCQ format
            question = lines[0]
            options = lines[1:5]
            correct_answer = lines[5].split(":")[-1].strip()
            
            st.write(question)
            user_answer = st.radio(f"Select answer for {question}", options, key=f"q{i}")
            answers[f"q{i}"] = (user_answer, correct_answer)  # Store answer

    # Submit button to calculate score
    if st.button("Submit Test"):
        score = sum(1 for key, (user_ans, correct_ans) in answers.items() if user_ans.startswith(correct_ans))
        st.success(f"Test completed! Your score: {score}/{len(answers)}")
