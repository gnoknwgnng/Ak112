


import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to extract video ID from various YouTube URL formats
def extract_video_id(video_url):
    if "youtu.be" in video_url:
        return video_url.split("/")[-1].split("?")[0]
    elif "v=" in video_url:
        return video_url.split("v=")[-1].split("&")[0]
    return None

# Function to get YouTube transcript with language support
def get_youtube_transcript(video_id, lang_code="en"):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Check if transcript is available in the requested language
        if lang_code in [t.language_code for t in transcript_list]:
            transcript = transcript_list.find_transcript([lang_code]).fetch()
            text = " ".join([t["text"] for t in transcript])
            return text, lang_code
        
        # If Hindi is available but not English, return Hindi with a translation option
        elif "hi" in [t.language_code for t in transcript_list]:
            transcript = transcript_list.find_transcript(["hi"]).fetch()
            text = " ".join([t["text"] for t in transcript])
            return text, "hi"
        
        return "Transcript not available in the requested language.", None
    except Exception as e:
        return f"Error fetching transcript: {str(e)}", None

# Function to summarize text
def summarize_text(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize the following text in simple points:\n\n{text}")
        return response.text
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

# Function to translate text
def translate_to_english(text):
    try:
        return GoogleTranslator(source="hi", target="en").translate(text)
    except Exception as e:
        return f"Error translating text: {str(e)}"

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
        
        Ensure the format is *strictly followed*. Only return questions, options, and correct answers.
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
lang_code = st.selectbox("Select language for transcript:", ["en", "hi"], index=0)

if st.button("Get Transcript"):
    if video_url:  # Ensure URL is entered
        video_id = extract_video_id(video_url)
        
        if video_id:  # Check if video ID is extracted
            transcript, detected_lang = get_youtube_transcript(video_id, lang_code)
            st.session_state["transcript"] = transcript  # Store transcript in session state
            st.session_state["transcript_lang"] = detected_lang  # Store detected language
        else:
            st.warning("Invalid YouTube URL. Please check the link.")
    else:
        st.warning("Please enter a YouTube URL.")

# Display transcript
if "transcript" in st.session_state:
    st.subheader("Extracted Transcript")
    st.write(st.session_state["transcript"])
    
    # If transcript is in Hindi, provide an option to translate
    if st.session_state["transcript_lang"] == "hi":
        if st.button("Translate to English"):
            translated_text = translate_to_english(st.session_state["transcript"])
            st.session_state["translated_transcript"] = translated_text
    
# Display translated transcript
if "translated_transcript" in st.session_state:
    st.subheader("Translated Transcript (English)")
    st.write(st.session_state["translated_transcript"])
    
    # Generate Summary
    if st.button("Summarize Transcript"):
        summary = summarize_text(st.session_state["translated_transcript"])
        st.session_state["summary"] = summary

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

