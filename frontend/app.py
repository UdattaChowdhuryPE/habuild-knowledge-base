import streamlit as st
import os
from frontend.utils.auth import init_session_state, is_authenticated, is_hr, logout, LOCATIONS
from frontend.utils.api import client

# Page configuration
st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="📋",
    layout="wide"
)

# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    st.title("HR Policy Assistant")

    if is_authenticated():
        st.write(f"**{st.session_state.name}**")
        st.write(f"Location: {st.session_state.location}")
        st.write(f"Role: {st.session_state.role}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Documents"):
                st.switch_page("pages/2_documents.py")

        with col2:
            if st.button("Logout"):
                logout()

        if is_hr():
            if st.button("⚙️ Admin Panel"):
                st.switch_page("pages/1_admin.py")
    else:
        st.info("Sign in to get started")


# Main content
if not is_authenticated():
    # Login screen
    st.title("Welcome to HR Policy Assistant")
    st.write("Sign in with your Habuild email to access HR policies and documents.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image("https://via.placeholder.com/300x200?text=HR+Policies", use_column_width=True)

    with col2:
        st.write("### Sign In")

        email = st.text_input("Email", placeholder="your.email@habuild.in")
        location = st.selectbox("Office Location", options=LOCATIONS)

        if st.button("Sign In", type="primary", use_container_width=True):
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
    st.title("HR Policy Assistant")

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
