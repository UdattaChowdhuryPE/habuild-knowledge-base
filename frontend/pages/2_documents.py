import streamlit as st
from frontend.utils.auth import init_session_state, is_authenticated, logout, LOCATIONS
from frontend.utils.api import client

st.set_page_config(page_title="Documents", layout="wide")

init_session_state()

# Check authentication
if not is_authenticated():
    st.error("Please sign in first")
    st.stop()

# Sidebar
with st.sidebar:
    st.title("Documents")
    st.write(f"**{st.session_state.name}**")

    if st.button("← Back to Chat"):
        st.switch_page("pages/app.py")

    if st.button("Logout"):
        logout()

st.title("Document Library")
st.write(f"Documents for your location: **{st.session_state.location}**")

# Search and filter
search_term = st.text_input("Search documents...")

try:
    # Fetch documents for user's location
    docs_data = client.get_documents(location=st.session_state.location)
    documents = docs_data.get("documents", [])

    if not documents:
        st.info("No documents available for your location")
    else:
        # Filter by search term
        if search_term:
            documents = [
                doc for doc in documents
                if search_term.lower() in doc["title"].lower()
                or search_term.lower() in doc["category"].lower()
            ]

        if not documents:
            st.info("No documents match your search")
        else:
            # Group by category
            categories = {}
            for doc in documents:
                cat = doc["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(doc)

            for category, docs in categories.items():
                with st.expander(f"📂 {category} ({len(docs)} documents)", expanded=True):
                    cols = st.columns(2)

                    for idx, doc in enumerate(docs):
                        with cols[idx % 2]:
                            st.write(f"**{doc['title']}**")
                            st.caption(f"Added: {doc['created_at'][:10]}")

                            # File type icon and link
                            file_name = doc["file_name"]
                            if file_name.endswith(".pdf"):
                                icon = "📕"
                            elif file_name.endswith(".docx") or file_name.endswith(".doc"):
                                icon = "📗"
                            elif file_name.endswith(".xlsx") or file_name.endswith(".xls"):
                                icon = "📙"
                            else:
                                icon = "📄"

                            st.markdown(f"[{icon} Open {file_name}]({doc['file_url']})")

except Exception as e:
    st.error(f"Error loading documents: {str(e)}")
