import streamlit as st
from frontend.utils.auth import init_session_state, is_authenticated, logout, LOCATIONS, get_initials
from frontend.utils.api import client
from frontend.utils.styles import inject_global_styles, page_header, sidebar_brand, sidebar_user_card

st.set_page_config(page_title="Documents", layout="wide")

inject_global_styles()
init_session_state()

if not is_authenticated():
    st.error("Please sign in first")
    st.stop()

with st.sidebar:
    sidebar_brand()
    sidebar_user_card(st.session_state.name, st.session_state.location, st.session_state.role, get_initials(st.session_state.name))
    if st.button("← Back to Chat", use_container_width=True):
        st.switch_page("app.py")
    if st.button("Logout", use_container_width=True):
        logout()

page_header("📄", "HR Documents", "Browse and download company HR documents")

col1, col2 = st.columns([1, 0.15], gap="small")
with col1:
    search_term = st.text_input("", placeholder="Search documents...", label_visibility="collapsed")
with col2:
    st.markdown('<div style="height:2.5rem"></div>', unsafe_allow_html=True)

try:
    docs_data = client.get_documents(location=st.session_state.location)
    documents = docs_data.get("documents", [])

    if not documents:
        st.info("No documents available for your location")
    else:
        if search_term:
            documents = [
                doc for doc in documents
                if search_term.lower() in doc["title"].lower()
                or search_term.lower() in doc["category"].lower()
            ]

        if not documents:
            st.info("No documents match your search")
        else:
            cols = st.columns(2)
            icon_map = {".pdf": "📕", ".docx": "📗", ".doc": "📗", ".txt": "📄", ".xlsx": "📙", ".xls": "📙"}

            for idx, doc in enumerate(documents):
                file_name = doc.get("file_name", "document")
                ext = next((k for k in icon_map if file_name.lower().endswith(k)), None)
                icon = icon_map.get(ext, "📄")

                date_str = doc.get("created_at", "").split("T")[0] if doc.get("created_at") else "Unknown date"
                file_size = doc.get("file_size", "Unknown size")

                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="hb-doc-card-v2">
                        <div class="hb-doc-card-v2-badge">{doc['category']}</div>
                        <div class="hb-doc-card-v2-icon">{icon}</div>
                        <div class="hb-doc-card-v2-title">{doc['title']}</div>
                        <div class="hb-doc-card-v2-meta">{date_str}  •  {file_size}</div>
                        <a href="{doc['file_url']}" target="_blank" class="hb-doc-card-v2-btn">⬇ Download</a>
                    </div>
                    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading documents: {str(e)}")
