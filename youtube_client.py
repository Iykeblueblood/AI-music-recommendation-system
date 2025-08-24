# youtube_client.py

import streamlit as st
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

class YouTubeHandler:
    def __init__(self, client_secrets):
        self.client_secrets = client_secrets
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        # --- THIS IS THE CRITICAL FIX ---
        # The app needs to know if it's running online or on your computer.
        # This code checks if it's on Streamlit's server.
        # If yes, it uses your public URL. If no, it uses localhost.
        # This was the cause of the crash.
        if "HOSTNAME" in os.environ and os.environ["HOSTNAME"] == "streamlit":
             # We are on Streamlit Cloud
             self.redirect_uri = self.client_secrets["web"]["redirect_uris"][1]
        else:
             # We are on a local computer
             self.redirect_uri = self.client_secrets["web"]["redirect_uris"][0]

        self.credentials = self.get_credentials_from_session()
        if self.credentials:
            self.youtube_api = build('youtube', 'v3', credentials=self.credentials)

    def get_credentials_from_session(self):
        """Loads credentials from Streamlit's session state."""
        if 'credentials' in st.session_state:
            return google.oauth2.credentials.Credentials(**st.session_state['credentials'])
        return None

    def get_auth_url(self):
        """Generates the Google Authentication URL."""
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_secrets, scopes=self.scopes
        )
        # Use the correct redirect_uri
        flow.redirect_uri = self.redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true'
        )
        st.session_state['state'] = state
        return authorization_url

    def fetch_token(self, code):
        """Fetches the OAuth token using the authorization code."""
        state = st.session_state.get('state')
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.client_secrets, scopes=self.scopes, state=state
        )
        # Use the correct redirect_uri
        flow.redirect_uri = self.redirect_uri
        flow.fetch_token(code=code)
        
        creds_data = {
            'token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_uri': flow.credentials.token_uri,
            'client_id': flow.credentials.client_id,
            'client_secret': flow.credentials.client_secret,
            'scopes': flow.credentials.scopes
        }
        st.session_state['credentials'] = creds_data
        return True

    def search_videos(self, query, max_results=20):
        """Searches for music videos on YouTube."""
        request = self.youtube_api.search().list(
            part="snippet",
            q=query,
            type="video",
            videoCategoryId="10",
            maxResults=max_results
        )
        response = request.execute()
        return response.get("items", [])

    def create_playlist(self, title, description="Created by AI Mood DJ"):
        """Creates a new private YouTube playlist."""
        request = self.youtube_api.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": "private"}
            }
        )
        response = request.execute()
        return response["id"]

    def add_video_to_playlist(self, playlist_id, video_id):
        """Adds a single video to the specified playlist."""
        request = self.youtube_api.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id}
                }
            }
        )
        request.execute()