import streamlit as st
import os
from frontend.utils.auth import init_session_state, is_authenticated, is_hr, logout, LOCATIONS
from frontend.utils.api import client
from frontend.utils.styles import inject_global_styles, page_header, sidebar_brand, sidebar_user_card

# Page configuration
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="📋",
    layout="wide"
)

# Inject styles
inject_global_styles()

# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    sidebar_brand()

    if is_authenticated():
        sidebar_user_card(st.session_state.name, st.session_state.location, st.session_state.role)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Documents", use_container_width=True):
                st.switch_page("pages/2_documents.py")

        with col2:
            if st.button("Logout", use_container_width=True):
                logout()

        if is_hr():
            if st.button("⚙️ Admin Panel", use_container_width=True):
                st.switch_page("pages/1_admin.py")
    else:
        st.info("Sign in to get started")


# Main content
if not is_authenticated():
    # Login screen
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div class="hb-hero">
            <div class="hb-hero-icon">🏃‍♂️</div>
            <h2>Your HR Companion</h2>
            <p>Get instant answers to all your HR policy questions — leave, benefits, compliance, and more.</p>
            <div class="hb-hero-pills">
                <span class="hb-hero-pill">Leave Policies</span>
                <span class="hb-hero-pill">Benefits</span>
                <span class="hb-hero-pill">Compliance</span>
                <span class="hb-hero-pill">Onboarding</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <h3>Sign In</h3>
        <p class="hb-login-subtitle">Use your Habuild email address to access HR resources</p>
        """, unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="your.email@habuild.in", label_visibility="collapsed")
        st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
        location = st.selectbox("Office Location", options=LOCATIONS)

        if st.button("Sign In →", type="primary", use_container_width=True):
            if not email or "@habuild.in" not in email:
                st.error("Please enter a valid Habuild email address")
            else:
                try:
                    # Verify employee
                    profile = client.verify_employee(email)

                    # Set session state
                    st.session_state.user_id = profile["id"]
                    st.session_state.email = profile["email"]
                    st.session_state.name = profile["name"]
                    st.session_state.location = location
                    st.session_state.role = profile["role"]

                    # If HR, redirect to admin
                    if profile["role"] == "hr":
                        st.switch_page("pages/1_admin.py")
                    else:
                        st.success("Signed in successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"Sign in failed: {str(e)}")

else:
    # Chat interface
    page_header("💬", "HR Policy Assistant", "Ask me anything about Habuild's HR policies")

    # Initialize conversation if needed
    if not st.session_state.conversation_id:
        try:
            conv_response = client.start_conversation(
                location=st.session_state.location,
                user_id=st.session_state.user_id
            )
            st.session_state.conversation_id = conv_response["conversation_id"]
        except Exception as e:
            st.error(f"Failed to start conversation: {str(e)}")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about HR policies..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Get streaming response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                for token in client.send_message(
                    question=prompt,
                    conversation_id=st.session_state.conversation_id,
                    location=st.session_state.location
                ):
                    full_response += token
                    message_placeholder.write(full_response)

                # Add assistant message to chat
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error getting response: {str(e)}")
