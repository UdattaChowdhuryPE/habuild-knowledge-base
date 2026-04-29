import streamlit as st
from frontend.utils.auth import init_session_state, is_authenticated, logout, LOCATIONS
from frontend.utils.api import client
from frontend.utils.styles import inject_global_styles, page_header, sidebar_brand, sidebar_user_card

st.set_page_config(page_title="Documents", layout="wide")

inject_global_styles()
init_session_state()

# Check authentication
if not is_authenticated():
    st.error("Please sign in first")
    st.stop()

# Sidebar
with st.sidebar:
    sidebar_brand()
    sidebar_user_card(st.session_state.name, st.session_state.location, st.session_state.role)

    if st.button("← Back to Chat", use_container_width=True):
        st.switch_page("app.py")

    if st.button("Logout", use_container_width=True):
        logout()

page_header("📚", "Document Library", f"Documents for {st.session_state.location}")

# Search and filter
st.markdown('<div style="max-width:520px">', unsafe_allow_html=True)
search_term = st.text_input("", placeholder="🔍  Search by title or category...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

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
                            file_name = doc["file_name"]
                            icon_map = {".pdf": "📕", ".docx": "📗", ".doc": "📗", ".xlsx": "📙", ".xls": "📙"}
                            ext = next((k for k in icon_map if file_name.endswith(k)), None)
                            icon = icon_map.get(ext, "📄")

                            st.markdown(f"""
                            <div class="hb-doc-card">
                                <div class="doc-title">{doc['title']}</div>
                                <div class="doc-meta">Added {doc['created_at'][:10]}</div>
                                <a href="{doc['file_url']}" target="_blank">{icon} Open {file_name}</a>
                            </div>
                            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading documents: {str(e)}")
