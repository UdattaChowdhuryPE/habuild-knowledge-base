import os
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
LOCATIONS = ["Bangalore", "Gurgaon", "Nagpur"]


def init_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "email" not in st.session_state:
        st.session_state.email = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "location" not in st.session_state:
        st.session_state.location = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []


def get_google_oauth_url() -> str:
    """Get Google OAuth URL from Supabase."""
    # This would be constructed using Supabase auth config
    # For now, return a placeholder that would be handled by Supabase Auth
    return f"{SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=http://localhost:8501"


def logout():
    """Log out the current user."""
    st.session_state.user_id = None
    st.session_state.email = None
    st.session_state.name = None
    st.session_state.location = None
    st.session_state.role = None
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.rerun()


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.user_id is not None


def is_hr() -> bool:
    """Check if user has HR role."""
    return st.session_state.role == "hr"
