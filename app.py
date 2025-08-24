# app.py

import streamlit as st
from youtube_client import YouTubeHandler
from generative_ai_client import get_search_terms_with_ai, create_playlist_title_with_ai

# --- Page Configuration ---
st.set_page_config(page_title="AI Mood DJ (YouTube Edition)", page_icon="🎵", layout="wide")

def main():
    st.title("🎵 AI Mood DJ (for YouTube)")
    st.markdown("Describe how you feel, and we'll build the perfect YouTube playlist for you.")

    # --- Authentication Flow ---
    # Load secrets and initialize handler
    client_secrets = {"web": st.secrets["web"]}
    yt_handler = YouTubeHandler(client_secrets)

    # Check if we are in the middle of an OAuth redirect
    query_params = st.query_params
    if query_params.get("code"):
        if 'credentials' not in st.session_state:
            auth_code = query_params.get("code")
            yt_handler.fetch_token(auth_code)
            st.query_params.clear() # Clear query params
            st.rerun()

    if not yt_handler.credentials:
        st.subheader("Step 1: Connect to YouTube")
        auth_url = yt_handler.get_auth_url()
        st.markdown(f'<a href="{auth_url}" target="_self">Click here to authorize with your YouTube Account</a>', unsafe_allow_html=True)
        return # Stop the app until authorized

    # --- Main App Logic (if authenticated) ---
    st.success(f"Successfully connected to YouTube!")
    st.subheader("Step 2: Create Your Playlist")

    user_input_mood = st.text_input(
        "How are you feeling right now? (e.g., 'A chill, rainy Sunday afternoon')", ""
    )
    
    if st.button("✨ Generate Playlist"):
        if not user_input_mood:
            st.warning("Please describe your mood.")
            return

        with st.spinner("🧠 AI is interpreting your mood..."):
            search_query = get_search_terms_with_ai(user_input_mood)
            playlist_title = create_playlist_title_with_ai(user_input_mood)
        
        st.write(f"🔍 Searching YouTube for: **'{search_query}'**")

        with st.spinner("🎶 Finding the perfect tracks..."):
            videos = yt_handler.search_videos(search_query)

        if not videos:
            st.warning("No tracks found for your mood. Try a different description.")
            return

        st.success(f"Found {len(videos)} tracks! Creating playlist titled: **'{playlist_title}'**")

        with st.spinner("📝 Creating your playlist on YouTube..."):
            try:
                playlist_id = yt_handler.create_playlist(playlist_title)
                for video in videos:
                    video_id = video["id"]["videoId"]
                    yt_handler.add_video_to_playlist(playlist_id, video_id)
                
                playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
                st.balloons()
                st.success(f"Playlist created! [Click here to listen on YouTube]({playlist_url})")

            except Exception as e:
                st.error(f"An error occurred while creating the playlist: {e}")


if __name__ == "__main__":
    main()