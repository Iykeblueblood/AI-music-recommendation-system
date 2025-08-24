# generative_ai_client.py

import streamlit as st
import google.generativeai as genai

# Configure the generative AI model from secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

def get_search_terms_with_ai(user_input):
    """Uses Generative AI to translate a mood into a YouTube search query."""
    prompt = f"""
    Analyze the user's mood and generate a concise YouTube music search query. 
    The query should include relevant genres, moods, or keywords.
    For example, if the user feels 'sad but hopeful', a good query might be 'ambient post-rock uplifting music'.
    If the user feels 'ready to party on a Friday night', a good query might be 'upbeat dance pop energetic official music video'.
    
    User Mood: "{user_input}"
    
    YouTube Search Query:
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error interpreting mood with AI: {e}")
        return user_input

def create_playlist_title_with_ai(mood):
    """Uses Generative AI to create a creative playlist title."""
    prompt = f"Generate a short, creative, and catchy title for a YouTube playlist based on this mood: '{mood}'"
    try:
        response = model.generate_content(prompt)
        return response.text.strip().replace('"', '')
    except Exception as e:
        print(f"Error creating playlist title: {e}")
        return f"{mood} Mix"