import streamlit as st


def inject_global_styles():
    """Inject global CSS styles for Habuild HR Policy Assistant."""
    st.markdown("""
    <style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }

    /* BASE */
    .stApp { background-color: #F0F9F8; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }

    /* SIDEBAR NAV */
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNavLink"] span {
        text-transform: capitalize !important;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003E50 0%, #005068 100%);
        border-right: none;
    }
    [data-testid="stSidebar"] * { color: #C8E6E0 !important; }
    [data-testid="stSidebar"] h1 { color: #3FA68E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] strong { color: #FFFFFF !important; font-weight: 600; }
    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(63,166,142,0.12) !important;
        color: #3FA68E !important;
        border: 1px solid rgba(63,166,142,0.3) !important;
        border-radius: 8px !important;
        font-size: 0.8rem !important; font-weight: 500;
        width: 100%; transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(63,166,142,0.25) !important;
        border-color: #3FA68E !important;
    }

    /* TYPOGRAPHY */
    h1 { color: #003E50 !important; font-weight: 800 !important; letter-spacing: -0.5px; }
    h2 { color: #003E50 !important; font-weight: 700 !important; }
    h3 { color: #003E50 !important; font-weight: 600 !important; }

    /* PRIMARY BUTTONS */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3FA68E 0%, #2D8A74 100%) !important;
        color: #FFFFFF !important; border: none !important;
        border-radius: 8px !important; font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(63,166,142,0.35);
        transition: all 0.2s ease;
    }
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2D8A74 0%, #1F6B58 100%) !important;
        box-shadow: 0 4px 16px rgba(63,166,142,0.45);
        transform: translateY(-1px);
    }

    /* SECONDARY BUTTONS */
    .stButton button[kind="secondary"] {
        background-color: #FFFFFF !important; color: #003E50 !important;
        border: 1.5px solid #D6E8E6 !important; border-radius: 8px !important;
        font-weight: 500 !important; transition: all 0.2s ease;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #3FA68E !important; color: #3FA68E !important;
        background-color: #F0F9F8 !important;
    }

    /* FORM INPUTS */
    .stTextInput input, .stTextArea textarea,
    .stSelectbox > div > div, .stMultiSelect > div > div {
        border: 1.5px solid #D6E8E6 !important; border-radius: 8px !important;
        background-color: #FFFFFF !important; color: #003E50 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3FA68E !important;
        box-shadow: 0 0 0 3px rgba(63,166,142,0.12) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label,
    .stMultiSelect label, .stFileUploader label {
        font-weight: 600 !important; color: #003E50 !important; font-size: 0.875rem !important;
    }

    /* EXPANDERS */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important; border: 1.5px solid #D6E8E6 !important;
        border-radius: 10px !important; font-weight: 600 !important;
        color: #003E50 !important; padding: 0.75rem 1rem !important;
    }
    .streamlit-expanderHeader:hover {
        background-color: #F0F9F8 !important; border-color: #3FA68E !important;
    }
    [data-testid="stExpander"] {
        border: none !important; border-radius: 10px !important;
        box-shadow: 0 1px 4px rgba(0,62,80,0.06); margin-bottom: 0.75rem !important;
    }
    [data-testid="stExpander"] > div:last-child {
        background-color: #FFFFFF; border: 1.5px solid #D6E8E6;
        border-top: none; border-radius: 0 0 10px 10px; padding: 1rem;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #E0F2EF !important; border-radius: 12px !important;
        padding: 4px !important; gap: 4px; border-bottom: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important; color: #5A7A7A !important;
        border-radius: 8px !important; font-weight: 600 !important;
        font-size: 0.875rem !important; border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important; color: #003E50 !important;
        box-shadow: 0 1px 4px rgba(0,62,80,0.12);
    }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

    /* FILE UPLOADER */
    [data-testid="stFileUploader"] {
        border: 2px dashed #D6E8E6 !important; border-radius: 10px !important;
        background-color: #F8FDFC !important; transition: border-color 0.2s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #3FA68E !important; background-color: #F0F9F8 !important;
    }

    /* ALERTS */
    div[data-testid="stNotification"][kind="success"] {
        background-color: #F0FDF4 !important; border-left: 4px solid #22C55E !important; border-radius: 8px !important;
    }
    div[data-testid="stNotification"][kind="error"] {
        background-color: #FEF2F2 !important; border-left: 4px solid #EF4444 !important; border-radius: 8px !important;
    }
    div[data-testid="stNotification"][kind="info"] {
        background-color: #F0F9F8 !important; border-left: 4px solid #3FA68E !important; border-radius: 8px !important;
    }

    /* CHAT */
    [data-testid="stChatMessage"] { border-radius: 12px !important; margin-bottom: 0.5rem; }
    [data-testid="stChatMessage"][data-author="user"] { background-color: #F0F9F8; }
    [data-testid="stChatMessage"][data-author="assistant"] { background-color: #FFFFFF; border: 1px solid #D6E8E6; }
    .stChatInput textarea {
        border-radius: 12px !important; border: 1.5px solid #D6E8E6 !important; background-color: #FFFFFF !important;
    }
    .stChatInput textarea:focus {
        border-color: #3FA68E !important; box-shadow: 0 0 0 3px rgba(63,166,142,0.12) !important;
    }

    /* UTILITY CLASSES */
    .hb-card {
        background: #FFFFFF; border: 1.5px solid #D6E8E6; border-radius: 12px;
        padding: 1.25rem 1.5rem; margin-bottom: 1rem;
        box-shadow: 0 1px 4px rgba(0,62,80,0.06); transition: box-shadow 0.2s ease;
    }
    .hb-card:hover { box-shadow: 0 4px 16px rgba(0,62,80,0.1); }

    .hb-hero {
        background: linear-gradient(135deg, #003E50 0%, #005068 50%, #3FA68E 100%);
        border-radius: 16px; padding: 3rem 2rem; color: #FFFFFF; text-align: center;
        min-height: 380px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
    }
    .hb-hero h2 { color: #FFFFFF !important; font-size: 1.75rem; font-weight: 800; margin-bottom: 0.75rem; }
    .hb-hero p { color: rgba(255,255,255,0.8) !important; font-size: 1rem; line-height: 1.6; max-width: 320px; }
    .hb-hero-icon { font-size: 3.5rem; margin-bottom: 1.25rem; }
    .hb-hero-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: center; margin-top: 1.5rem; }
    .hb-hero-pill {
        background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
        border-radius: 20px; padding: 0.25rem 0.75rem; font-size: 0.8rem; color: rgba(255,255,255,0.9);
    }

    .hb-login-form {
        background: #FFFFFF; border: 1.5px solid #D6E8E6; border-radius: 16px;
        padding: 2rem 2.25rem; box-shadow: 0 4px 24px rgba(0,62,80,0.08);
    }
    .hb-login-form h3 { color: #003E50 !important; font-size: 1.4rem !important; font-weight: 800 !important; }
    .hb-login-subtitle { color: #5A7A7A; font-size: 0.875rem; margin-bottom: 1.5rem; }

    .hb-page-header {
        background: linear-gradient(135deg, #003E50 0%, #005068 100%);
        border-radius: 14px; padding: 1.25rem 1.75rem; margin-bottom: 1.75rem;
        display: flex; align-items: center; gap: 1rem;
    }
    .hb-page-header h1 { color: #FFFFFF !important; font-size: 1.4rem !important; font-weight: 800 !important; margin: 0; }
    .hb-page-header p { color: rgba(255,255,255,0.65) !important; font-size: 0.85rem !important; margin: 0; }
    .hb-page-header-icon { font-size: 2rem; flex-shrink: 0; }

    .hb-section-header {
        display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;
        padding-bottom: 0.75rem; border-bottom: 2px solid #D6E8E6;
    }
    .hb-section-header-bar { width: 4px; height: 1.5rem; background: #3FA68E; border-radius: 2px; flex-shrink: 0; }
    .hb-section-header h3 { margin: 0; color: #003E50 !important; font-size: 1.1rem !important; font-weight: 700 !important; }

    .hb-badge {
        display: inline-block; background: #F0F9F8; border: 1px solid rgba(63,166,142,0.3);
        color: #2D8A74; font-size: 0.775rem; font-weight: 700;
        padding: 0.2rem 0.6rem; border-radius: 20px;
    }

    .hb-sidebar-brand {
        display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.5rem;
        padding-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .hb-sidebar-brand-name { font-size: 1.1rem; font-weight: 800; color: #3FA68E !important; letter-spacing: 0.5px; }
    .hb-sidebar-brand-sub { font-size: 0.7rem; color: rgba(255,255,255,0.5) !important; letter-spacing: 1px; text-transform: uppercase; }

    .hb-sidebar-user {
        background: rgba(63,166,142,0.1); border: 1px solid rgba(63,166,142,0.2);
        border-radius: 10px; padding: 0.75rem; margin-bottom: 1rem;
    }
    .hb-sidebar-user .user-name { font-weight: 700; color: #FFFFFF !important; font-size: 0.9rem; }
    .hb-sidebar-user .user-meta { color: rgba(255,255,255,0.55) !important; font-size: 0.775rem; line-height: 1.6; }

    .hb-doc-card {
        background: #FFFFFF; border: 1.5px solid #E0F2EF; border-radius: 10px;
        padding: 1rem 1.1rem; margin-bottom: 0.75rem; transition: all 0.2s ease;
    }
    .hb-doc-card:hover { border-color: #3FA68E; box-shadow: 0 2px 12px rgba(63,166,142,0.12); transform: translateY(-1px); }
    .hb-doc-card .doc-title { font-weight: 700; color: #003E50; font-size: 0.9rem; margin-bottom: 0.2rem; }
    .hb-doc-card .doc-meta { color: #5A7A7A; font-size: 0.775rem; margin-bottom: 0.5rem; }
    .hb-doc-card a { color: #3FA68E; font-size: 0.825rem; font-weight: 600; text-decoration: none; }
    .hb-doc-card a:hover { text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    """Render a styled dark-gradient page header strip."""
    sub_html = f'<p>{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div class="hb-page-header">
        <div class="hb-page-header-icon">{icon}</div>
        <div>
            <h1>{title}</h1>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str) -> None:
    """Render a section header with a teal accent bar."""
    st.markdown(f"""
    <div class="hb-section-header">
        <div class="hb-section-header-bar"></div>
        <h3>{title}</h3>
    </div>
    """, unsafe_allow_html=True)


def sidebar_brand() -> None:
    """Render the Habuild brand block at the top of the sidebar."""
    st.markdown("""
    <div class="hb-sidebar-brand">
        <div style="font-size: 1.3rem; font-weight: 800; color: #3FA68E;">🏃</div>
        <div>
            <div class="hb-sidebar-brand-name">Habuild</div>
            <div class="hb-sidebar-brand-sub">HR Portal</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_user_card(name: str, location: str, role: str) -> None:
    """Render a user info card in the sidebar."""
    st.markdown(f"""
    <div class="hb-sidebar-user">
        <div class="user-name">{name}</div>
        <div class="user-meta">
            📍 {location}<br>
            🎭 {role.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)
