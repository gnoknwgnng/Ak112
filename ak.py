import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
import re

# Configure API
genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")  # Replace with a valid API key

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

def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except (TranscriptsDisabled, NoTranscriptFound):
        return "Transcript not available."
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def translate_text(text, target_lang="en"):
    words = text.split()
    translated_parts = []
    chunk_size = 100  # To avoid errors in translation
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        translated_part = GoogleTranslator(source="auto", target=target_lang).translate(chunk)
        translated_parts.append(translated_part)
    
    return " ".join(translated_parts)

def generate_mcqs(text, lang="en"):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Generate 3 multiple-choice questions in {lang} from the following text. Provide four answer options for each question, and mark the correct answer with (*): {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, translate it, generate MCQs, and take a quiz!")

# Session states
if "mcqs" not in st.session_state:
    st.session_state["mcqs"] = []
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "answers" not in st.session_state:
    st.session_state["answers"] = {}

video_url = st.text_input("Enter YouTube Video URL:")

def parse_mcqs(mcq_text):
    questions = []
    mcq_blocks = mcq_text.split("Q")
    for block in mcq_blocks[1:]:
        lines = block.strip().split("\n")
        question = lines[0].strip()
        options = {chr(65+i): line.strip().replace("(*)", "").strip() for i, line in enumerate(lines[1:])}
        correct_option = [k for k, v in options.items() if "(*)" in lines[i+1]]
        if correct_option:
            correct_option = correct_option[0]
        questions.append({"question": question, "options": options, "correct": correct_option})
    return questions

if st.button("Generate MCQs"):
    if video_url.strip():
        video_id = extract_video_id(video_url)
        if video_id:
            transcript = get_youtube_transcript(video_id)
            mcq_text = generate_mcqs(transcript)
            st.session_state["mcqs"] = parse_mcqs(mcq_text)
        else:
            st.warning("Invalid YouTube URL.")
    else:
        st.warning("Please enter a valid YouTube URL.")

if st.session_state["mcqs"]:
    st.subheader("Quiz")
    for idx, mcq in enumerate(st.session_state["mcqs"], 1):
        st.write(f"Q{idx}: {mcq['question']}")
        selected_option = st.radio(f"Select an answer for Q{idx}:", list(mcq["options"].keys()), key=f"q{idx}")
        st.session_state["answers"][f"q{idx}"] = selected_option

if st.button("Submit Quiz"):
    score = 0
    for idx, mcq in enumerate(st.session_state["mcqs"], 1):
        if st.session_state["answers"].get(f"q{idx}") == mcq["correct"]:
            score += 1
    st.session_state["score"] = score
    st.success(f"Quiz completed! Your score: {score}/{len(st.session_state['mcqs'])}")





















