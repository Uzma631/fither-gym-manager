"""
app.py — Entry point for FitHer Gym Manager.
Run with:  streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from config import APP_TITLE, APP_ICON, APP_VERSION, DEMO_MODE
from database.connection import test_connection
from utils.styles import inject_styles, SIDEBAR_HTML

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.page_link("app.py",                 label="🏠  Dashboard")
    st.page_link("pages/1_Members.py",     label="👥  Members")
    st.page_link("pages/2_Memberships.py", label="📋  Memberships")
    st.page_link("pages/3_Payments.py",    label="💳  Payments")
    st.page_link("pages/4_About.py",       label="ℹ️  About")
    st.divider()

    connected, db_info = test_connection()
    if connected:
        st.markdown(
            f"<div style='font-size:0.75rem; color:#00E676;'>🟢 {db_info}</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div style='font-size:0.75rem; color:#FF4444;'>🔴 Database offline</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.68rem; color:#FF8888; word-break:break-word;'>{db_info[:120]}</div>", unsafe_allow_html=True)

# ── Demo banner ───────────────────────────────────────────────────────────────
if DEMO_MODE:
    st.markdown("""
    <div class="demo-banner">
    ⚡ <strong>Demo Mode</strong> — Fictional data only. No login implemented in Phase 1.
    </div>
    """, unsafe_allow_html=True)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="gym-hero">
    <div class="gym-hero-title">💪 FitHer Gym Manager</div>
    <div class="gym-hero-sub">Phase 1 Prototype &nbsp;·&nbsp; Live Dashboard</div>
</div>
""", unsafe_allow_html=True)

# ── Imports ───────────────────────────────────────────────────────────────────
from services.dashboard_service import get_dashboard_kpis, get_expiring_soon_list, get_recent_payments
import pandas as pd
from utils.money_utils import format_pkr

kpis = get_dashboard_kpis()

if kpis["error"]:
    st.error(f"⚠️ Could not load dashboard data: {kpis['error']}")
    st.info("Make sure MySQL is running and your `.env` file is configured. See README for help.")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Overview</div>', unsafe_allow_html=True)

cols = st.columns(6)

def kpi_card(col, label, value, sub="", css_class=""):
    col.markdown(f"""
    <div class="kpi-card {css_class}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(cols[0], "Total Members",    kpis["total_members"],        "Registered",       "")
kpi_card(cols[1], "Active",           kpis["active_members"],       "With valid plan",  "green")
kpi_card(cols[2], "Expiring Soon",    kpis["expiring_soon"],        "Next 7 days",      "warn")
kpi_card(cols[3], "Expired",          kpis["expired_memberships"],  "Need renewal",     "danger")
kpi_card(cols[4], "This Month",       format_pkr(kpis["monthly_collections"]), "Collected", "pink")
kpi_card(cols[5], "Outstanding",      format_pkr(kpis["total_outstanding"]),   "Balance due","gold")

st.write("")

# ── Two-column tables ─────────────────────────────────────────────────────────
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown('<div class="section-header">⏰ Expiring Soon</div>', unsafe_allow_html=True)
    expiring = get_expiring_soon_list(7)
    if not expiring:
        st.info("✅ No memberships expiring in the next 7 days.")
    else:
        df_exp = pd.DataFrame(expiring).rename(columns={
            "full_name": "Member", "phone": "Phone",
            "plan_name": "Plan",   "end_date": "Expires On", "days_left": "Days Left",
        })
        st.dataframe(df_exp, use_container_width=True, hide_index=True)

with col_right:
    st.markdown('<div class="section-header">💳 Recent Payments</div>', unsafe_allow_html=True)
    recent = get_recent_payments(8)
    if not recent:
        st.info("No payments recorded yet.")
    else:
        df_pay = pd.DataFrame(recent)
        df_pay["amount"] = df_pay["amount"].apply(format_pkr)
        df_pay = df_pay.rename(columns={
            "payment_date": "Date", "amount": "Amount",
            "payment_method": "Method", "full_name": "Member",
        })
        st.dataframe(df_pay[["Date", "Member", "Amount", "Method"]], use_container_width=True, hide_index=True)
