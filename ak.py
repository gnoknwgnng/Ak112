








import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

# Configure Gemini API Key
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")

# Function to extract YouTube transcript
def get_youtube_transcript(video_url):
    try:
        video_id = video_url.split('v=')[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error fetching transcript: {e}"

# Function to generate summary and MCQs using Gemini
def generate_summary_and_mcqs(text):
    prompt = f"""
    Summarize the following text in a few sentences:
    {text}
    
    Then generate 5 multiple-choice questions (MCQs) based on the summary. Each question should have 4 options, and the correct answer should be marked.
    """
    response = genai.generate_text(model="gemini-pro", prompt=prompt)
    return response.text

# Function to parse MCQs from response
def parse_mcqs(response_text):
    mcqs = []
    lines = response_text.split('\n')
    current_question = {}
    
    for line in lines:
        if line.startswith("Q:"):
            if current_question:
                mcqs.append(current_question)
            current_question = {"question": line[2:].strip(), "options": [], "answer": ""}
        elif line.startswith("A:"):
            current_question["answer"] = line[2:].strip()
        elif line.strip():
            current_question["options"].append(line.strip())
    
    if current_question:
        mcqs.append(current_question)
    return mcqs

# Streamlit UI
st.title("YouTube Video to Summary & Quiz")
video_url = st.text_input("Enter YouTube Video URL")

if st.button("Generate Summary & Quiz"):
    transcript = get_youtube_transcript(video_url)
    if "Error" in transcript:
        st.error(transcript)
    else:
        response_text = generate_summary_and_mcqs(transcript)
        st.session_state.mcqs = parse_mcqs(response_text)
        st.session_state.quiz_started = False
        st.success("Summary and MCQs generated!")

# Quiz Section
if "mcqs" in st.session_state and not st.session_state.get("quiz_started", False):
    st.write("## Take the Quiz")
    user_answers = []
    
    for idx, mcq in enumerate(st.session_state.mcqs):
        st.write(f"**{mcq['question']}**")
        answer = st.radio(f"Select an answer for Question {idx+1}", mcq["options"], key=f"q{idx}")
        user_answers.append((mcq["question"], answer, mcq["answer"]))
    
    if st.button("Submit Quiz"):
        score = sum(1 for q, user_ans, correct_ans in user_answers if user_ans == correct_ans)
        total = len(user_answers)
        st.session_state.quiz_started = True
        st.session_state.quiz_score = (score, total)

# Show Results
if st.session_state.get("quiz_started", False):
    score, total = st.session_state.quiz_score
    st.write(f"## Your Score: {score} / {total}")
    
    for q, user_ans, correct_ans in user_answers:
        st.write(f"**{q}**")
        st.write(f"Your Answer: {user_ans}")
        st.write(f"Correct Answer: {correct_ans}")
        st.write("---")



















