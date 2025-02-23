import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to get transcript from YouTube video
def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

# Function to summarize text using Gemini
def summarize_text(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this: {text}")
        return response.text
    except Exception as e:
        return f"Error summarizing: {str(e)}"

# Function to generate MCQs using Gemini
def generate_mcqs(text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Generate 5 multiple-choice questions from this text. Format it as:\n\nQ1: ...?\nA) ...\nB) ...\nC) ...\nD) ...\nAnswer: ...")
        return response.text
    except Exception as e:
        return f"Error generating MCQs: {str(e)}"

# Function to parse MCQs into a test format
def parse_mcqs(mcqs_text):
    questions = []
    lines = mcqs_text.split("\n")
    question = None
    options = []
    correct_answer = None

    for line in lines:
        line = line.strip()
        if line.startswith("Q"):
            if question:
                questions.append((question, options, correct_answer))
            question = line
            options = []
            correct_answer = None
        elif line.startswith(("A)", "B)", "C)", "D)")):
            options.append(line)
        elif line.startswith("Answer:"):
            correct_answer = line.split("Answer:")[-1].strip()
    
    if question:
        questions.append((question, options, correct_answer))

    return questions

# Streamlit UI
st.title("Generate Summary & Questions from Video")
video_url = st.text_input("Paste YouTube video URL")

if st.button("Generate Summary & Questions"):
    with st.spinner("Fetching transcript..."):
        transcript_text = get_youtube_transcript(video_url)

    if "Error" in transcript_text:
        st.error(transcript_text)
    else:
        st.subheader("Transcript")
        st.write(transcript_text[:1000] + "...")  # Show a preview of the transcript 

        with st.spinner("Generating Summary..."):
            summary = summarize_text(transcript_text)
        st.subheader("Summary")
        st.write(summary)

        with st.spinner("Generating MCQs..."):
            mcqs_text = generate_mcqs(transcript_text)
        st.subheader("Multiple Choice Questions")

        # Convert text to structured questions
        questions = parse_mcqs(mcqs_text)

        user_answers = {}
        for idx, (question, options, correct_answer) in enumerate(questions):
            st.write(question)
            user_answers[idx] = st.radio(f"Select your answer for {question}", options)

        if st.button("Submit Test"):
            score = sum(1 for idx, (q, opts, ans) in enumerate(questions) if user_answers.get(idx) == ans)
            st.success(f"You scored {score} out of {len(questions)}")
