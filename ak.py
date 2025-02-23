


import streamlit as st
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator
import re

genai.configure(api_key="AIzaSyCFA8FGd9mF42_4ExVYTqOsvOeCbyHzBFU")  # Replace with your valid API key

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
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [t.language_code for t in transcript_list]
        preferred_languages = ["en", "hi"] + available_languages
        selected_language = next((lang for lang in preferred_languages if lang in available_languages), None)
        
        if selected_language:
            transcript = transcript_list.find_transcript([selected_language]).fetch()
            text = " ".join([t["text"] for t in transcript])
            return text, selected_language
        else:
            return "No transcript available.", None
    except (TranscriptsDisabled, NoTranscriptFound):
        return "Transcript not available for this video.", None
    except Exception as e:
        return f"Error fetching transcript: {str(e)}", None

def generate_mcqs(text, lang="en"):
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Generate 3 multiple-choice questions in {lang} from the following text. Provide four answer options labeled A, B, C, and D. Mark the correct answer with (*): {text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit UI
st.title("YouTube AI Tutor")
st.write("Enter a YouTube video URL to extract the transcript, translate it, generate a summary, and create multiple-choice questions.")

video_url = st.text_input("Enter YouTube Video URL:")

if "mcqs" not in st.session_state:
    st.session_state["mcqs"] = []
if "score" not in st.session_state:
    st.session_state["score"] = 0

if st.button("Get Transcript"):
    if video_url.strip():
        video_id = extract_video_id(video_url)
        if video_id:
            transcript, detected_lang = get_youtube_transcript(video_id)
            st.session_state["transcript"] = transcript
            st.session_state["detected_lang"] = detected_lang if detected_lang else "Unknown"
            st.success("Transcript fetched successfully!")
        else:
            st.warning("Invalid YouTube URL. Please check the link.")
    else:
        st.warning("Please enter a valid YouTube URL.")

quiz_lang = st.selectbox("Select language for Quiz:", ["en", "hi", "es", "fr", "de", "zh", "ar", "ru", "ja", "ko"], index=0)
if st.button("Generate MCQs"):
    mcqs_text = generate_mcqs(st.session_state.get("transcript", ""), quiz_lang)
    mcq_list = mcqs_text.split("\n")
    
    formatted_mcqs = []
    current_question = ""
    options = []
    correct_answer = ""
    
    for line in mcq_list:
        if line.startswith("Q"):
            if current_question:
                formatted_mcqs.append({"question": current_question, "options": options, "answer": correct_answer})
            current_question = line
            options = []
        elif line.startswith("A)" ) or line.startswith("B)" ) or line.startswith("C)" ) or line.startswith("D)" ):
            if "(*)" in line:
                correct_answer = line.replace("(*)", "").strip()
            options.append(line.replace("(*)", "").strip())
    if current_question:
        formatted_mcqs.append({"question": current_question, "options": options, "answer": correct_answer})
    
    st.session_state["mcqs"] = formatted_mcqs

if "mcqs" in st.session_state and st.session_state["mcqs"]:
    st.subheader("Multiple-Choice Questions")
    for index, mcq in enumerate(st.session_state["mcqs"]):
        st.write(mcq["question"])
        selected_option = st.radio("Select an option:", mcq["options"], key=index)
        if st.button(f"Submit Answer {index+1}", key=f"btn_{index}"):
            if selected_option == mcq["answer"]:
                st.session_state["score"] += 1
                st.success("Correct!")
            else:
                st.error(f"Wrong! Correct answer: {mcq['answer']}")

if st.button("Show Score"):
    st.subheader(f"Your Score: {st.session_state['score']} / {len(st.session_state['mcqs'])}")
