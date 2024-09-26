import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import re
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt="""You are Youtube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 500 words. Please provide the summary of the text given here:  """

def extract_video_id(youtube_url):
    video_id_match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11}).*', youtube_url)
    if video_id_match:
        return video_id_match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")

def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    if transcript_text is None:
        return "No transcript available to generate content."
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    try:
        video_id = extract_video_id(youtube_link)
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except ValueError:
        st.error("Invalid YouTube URL")

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        prompt = "Provide a detailed summary: "  # Define your prompt here
        summary = generate_gemini_content(transcript_text, prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)
    else:
        st.warning("No transcript available for this video.")
