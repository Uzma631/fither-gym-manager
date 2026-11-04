"""
utils/styles.py — Shared dark gym-theme CSS for FitHer Gym Manager.

Import and call inject_styles() at the top of every Streamlit page.
"""

import streamlit as st


DARK_GYM_CSS = """
<style>
/* ═══════════════════════════════════════════════════════
   ROOT / BACKGROUND
═══════════════════════════════════════════════════════ */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: #0D0D0D !important;
    color: #F0F0F0 !important;
}

[data-testid="stHeader"] {
    background-color: #0D0D0D !important;
    border-bottom: 1px solid #2A2A2A;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D0D 0%, #1A0A2E 60%, #0D0D0D 100%) !important;
    border-right: 1px solid #2A1A4A;
}
section[data-testid="stSidebar"] * {
    color: #E0E0E0 !important;
}
section[data-testid="stSidebar"] a:hover {
    color: #E040FB !important;
}

/* Nav link highlight */
section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    background: rgba(224, 64, 251, 0.12) !important;
    border-radius: 8px;
}

/* ═══════════════════════════════════════════════════════
   KPI CARDS
═══════════════════════════════════════════════════════ */
.kpi-card {
    background: #161616;
    border-radius: 12px;
    padding: 20px 18px 14px 18px;
    border: 1px solid #2A2A2A;
    border-left: 4px solid #E040FB;
    margin-bottom: 10px;
    box-shadow: 0 4px 20px rgba(224, 64, 251, 0.08);
    transition: box-shadow 0.2s ease;
}
.kpi-card:hover {
    box-shadow: 0 4px 28px rgba(224, 64, 251, 0.18);
}
.kpi-card.warn   { border-left-color: #FFB300; box-shadow: 0 4px 20px rgba(255,179,0,0.08); }
.kpi-card.danger { border-left-color: #FF4444; box-shadow: 0 4px 20px rgba(255,68,68,0.08); }
.kpi-card.green  { border-left-color: #00E676; box-shadow: 0 4px 20px rgba(0,230,118,0.08); }
.kpi-card.pink   { border-left-color: #FF4081; box-shadow: 0 4px 20px rgba(255,64,129,0.08); }
.kpi-card.gold   { border-left-color: #FFD700; box-shadow: 0 4px 20px rgba(255,215,0,0.08); }

.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.10em;
    color: #888;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 2.0rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.72rem;
    color: #666;
    margin-top: 4px;
}

/* ═══════════════════════════════════════════════════════
   SECTION HEADERS
═══════════════════════════════════════════════════════ */
.section-header {
    font-size: 1.3rem;
    font-weight: 800;
    color: #E040FB;
    margin-bottom: 8px;
    padding-bottom: 6px;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    border-bottom: 2px solid #2A1A4A;
}

/* ═══════════════════════════════════════════════════════
   HERO BANNER (dashboard)
═══════════════════════════════════════════════════════ */
.gym-hero {
    background: linear-gradient(135deg, #1A0A2E 0%, #0D0D0D 50%, #1A0A18 100%);
    border: 1px solid #2A1A4A;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.gym-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(224,64,251,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.gym-hero-title {
    font-size: 2.0rem;
    font-weight: 900;
    background: linear-gradient(90deg, #E040FB, #FF4081, #FFB300);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
}
.gym-hero-sub {
    font-size: 0.88rem;
    color: #888;
    margin-top: 6px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════
   DEMO BANNER
═══════════════════════════════════════════════════════ */
.demo-banner {
    background: #1A1A1A;
    border: 1px solid #333;
    border-left: 4px solid #FFB300;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 0.82rem;
    color: #AAA;
    margin-bottom: 20px;
}
.demo-banner strong { color: #FFB300; }

/* ═══════════════════════════════════════════════════════
   CARDS / PANELS
═══════════════════════════════════════════════════════ */
.info-card, .pay-summary {
    background: #161616;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #2A2A2A;
    margin-bottom: 16px;
}
.pay-summary {
    border-left: 4px solid #E040FB;
}

/* ═══════════════════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
═══════════════════════════════════════════════════════ */

/* Input fields */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: #1A1A1A !important;
    color: #F0F0F0 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #E040FB !important;
    box-shadow: 0 0 0 2px rgba(224,64,251,0.2) !important;
}

/* Select boxes */
[data-testid="stSelectbox"] > div,
[data-testid="stSelectbox"] select {
    background-color: #1A1A1A !important;
    color: #F0F0F0 !important;
    border-color: #333 !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background-color: #161616 !important;
    border-bottom: 1px solid #2A2A2A;
    gap: 4px;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #888 !important;
    font-weight: 600;
    letter-spacing: 0.03em;
    border-radius: 6px 6px 0 0;
    padding: 10px 18px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background-color: #1A1A1A !important;
    color: #E040FB !important;
    border-bottom: 2px solid #E040FB !important;
}

/* Dataframes */
[data-testid="stDataFrame"],
[data-testid="stTable"] {
    background: #161616 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
}
iframe[title="st_dataframe"] {
    background: #161616 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-size: 0.82rem !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #E040FB, #AA00FF) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(224,64,251,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #FF4081, #E040FB) !important;
    box-shadow: 0 6px 20px rgba(224,64,251,0.5) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] {
    background: #1A1A1A !important;
    border: 1px solid #444 !important;
    color: #CCC !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #E040FB !important;
    color: #E040FB !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 10px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] { color: #E040FB !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #888 !important; font-weight: 600 !important; }

/* Expanders */
[data-testid="stExpander"] {
    background: #161616 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: #CCC !important;
    font-weight: 600 !important;
}

/* Alerts */
[data-testid="stAlert"][data-baseweb="notification"][data-kind="info"] {
    background-color: #0D1A2A !important;
    border-color: #1565C0 !important;
    color: #90CAF9 !important;
}
[data-testid="stAlert"][data-kind="success"] {
    background-color: #0D2A14 !important;
    border-color: #2E7D32 !important;
    color: #A5D6A7 !important;
}
[data-testid="stAlert"][data-kind="warning"] {
    background-color: #2A1A00 !important;
    border-color: #E65100 !important;
    color: #FFCC80 !important;
}
[data-testid="stAlert"][data-kind="error"] {
    background-color: #2A0D0D !important;
    border-color: #C62828 !important;
    color: #EF9A9A !important;
}

/* Forms */
[data-testid="stForm"] {
    background: #141414 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* Divider */
hr {
    border-color: #2A2A2A !important;
}

/* Caption */
.stCaption, caption { color: #666 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0D0D0D; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #E040FB; }

</style>
"""


SIDEBAR_HTML = """
<div style="text-align:center; padding: 10px 0 24px 0;">
    <div style="font-size:2.6rem; filter: drop-shadow(0 0 12px rgba(224,64,251,0.6));">💪</div>
    <div style="
        font-size: 1.15rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        background: linear-gradient(90deg, #E040FB, #FF4081);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-top: 6px;
    ">FitHer</div>
    <div style="font-size:0.65rem; color:#666; letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;">
        Gym Manager
    </div>
</div>
"""


def inject_styles():
    """Inject the dark gym CSS into the current Streamlit page."""
    st.markdown(DARK_GYM_CSS, unsafe_allow_html=True)


def render_sidebar():
    """Render the shared sidebar with branding and nav links."""
    with st.sidebar:
        st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
        st.page_link("app.py",                 label="🏠  Dashboard")
        st.page_link("pages/1_Members.py",     label="👥  Members")
        st.page_link("pages/2_Memberships.py", label="📋  Memberships")
        st.page_link("pages/3_Payments.py",    label="💳  Payments")
        st.page_link("pages/4_About.py",       label="ℹ️  About")
