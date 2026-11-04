"""
pages/4_About.py — About and Demo Information page.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from config import APP_VERSION
from utils.styles import inject_styles, render_sidebar

st.set_page_config(page_title="About — FitHer", page_icon="ℹ️", layout="wide")
inject_styles()
render_sidebar()

st.markdown("""
<div class="gym-hero">
    <div class="gym-hero-title">ℹ️ About FitHer</div>
    <div class="gym-hero-sub">Phase 1 Prototype &nbsp;·&nbsp; Demo Information</div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    <div class="info-card">
    <h3 style="color:#E040FB; text-transform:uppercase; letter-spacing:0.06em;">💪 FitHer Gym Manager</h3>
    <p style="color:#CCC;">
    A simple, professional gym management system designed specifically for
    small, locally operated female gyms in Pakistan.
    This Phase 1 prototype replaces paper registers and manual calculations.
    </p>

    <h4 style="color:#FF4081; margin-top:20px;">✅ What this prototype can do</h4>
    <ul style="color:#AAA;">
        <li>Register and manage gym members</li>
        <li>Assign membership plans and track subscription dates</li>
        <li>Automatically calculate membership expiry dates</li>
        <li>Record full and partial fee payments</li>
        <li>Track outstanding balances per subscription</li>
        <li>Show memberships due for renewal in 7 days</li>
        <li>Live dashboard KPIs from the MySQL database</li>
        <li>Export member and payment data as CSV</li>
    </ul>

    <h4 style="color:#FFB300; margin-top:20px;">🚫 Not in Phase 1</h4>
    <ul style="color:#666;">
        <li>Attendance tracking</li>
        <li>Trainer or workout management</li>
        <li>Online payment integration</li>
        <li>WhatsApp / SMS notifications</li>
        <li>User login / access control</li>
        <li>Multi-branch management</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
    <h4 style="color:#FFB300;">⚠️ Demo Notice</h4>
    <p style="color:#AAA;">
    This is a <strong style="color:#E040FB;">local demonstration prototype</strong>.<br>
    All data shown is <strong>fictional</strong> — created for testing only.<br>
    No real customer information is stored.
    </p>
    <p style="color:#666; font-size:0.85rem;">
    This app has <strong>no login screen</strong> in Phase 1.
    Do not expose it on a shared or public network.
    </p>
    </div>

    <div class="info-card">
    <h4 style="color:#E040FB;">🛠️ Technical Stack</h4>
    <table style="width:100%; font-size:0.88rem; color:#CCC;">
        <tr><td style="color:#888; padding:4px 0;">Language</td><td><strong>Python 3.12</strong></td></tr>
        <tr><td style="color:#888; padding:4px 0;">UI</td><td><strong>Streamlit</strong></td></tr>
        <tr><td style="color:#888; padding:4px 0;">Database</td><td><strong>MySQL 8.0</strong></td></tr>
        <tr><td style="color:#888; padding:4px 0;">Connector</td><td><strong>mysql-connector-python</strong></td></tr>
        <tr><td style="color:#888; padding:4px 0;">Tests</td><td><strong>81 / 81 passing</strong></td></tr>
        <tr><td style="color:#888; padding:4px 0;">Version</td><td><strong>Phase 1 Prototype</strong></td></tr>
    </table>
    </div>

    <div class="info-card">
    <h4 style="color:#00E676;">📞 Common Fixes</h4>
    <ul style="color:#888; font-size:0.84rem;">
        <li><strong style="color:#CCC;">MySQL offline</strong> → Start MySQL80 service</li>
        <li><strong style="color:#CCC;">Missing .env</strong> → Copy .env.example to .env</li>
        <li><strong style="color:#CCC;">Wrong password</strong> → Update DB_PASSWORD in .env</li>
        <li><strong style="color:#CCC;">No tables</strong> → Run database/schema.sql in Workbench</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption(f"FitHer Gym Manager — {APP_VERSION} | Built with ❤️ for local female gyms in Pakistan")
