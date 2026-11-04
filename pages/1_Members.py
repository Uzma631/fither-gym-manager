"""
pages/1_Members.py — Member Management page for FitHer Gym Manager.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

from services.member_service import (
    create_member, search_members, get_member_by_id,
    update_member, get_member_subscription_history,
)
from utils.money_utils import format_pkr
from utils.styles import inject_styles, render_sidebar

st.set_page_config(page_title="Members — FitHer", page_icon="👥", layout="wide")
inject_styles()
render_sidebar()

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="gym-hero">
    <div class="gym-hero-title">👥 Member Management</div>
    <div class="gym-hero-sub">Register · Search · Edit · View History</div>
</div>
""", unsafe_allow_html=True)

tab_list, tab_add, tab_edit, tab_detail = st.tabs([
    "📋  All Members", "➕  Register", "✏️  Edit", "🔍  Profile"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Member list
# ══════════════════════════════════════════════════════════════════════════════
with tab_list:
    col_s, col_f, col_exp = st.columns([3, 2, 1])
    with col_s:
        search_q = st.text_input("🔍 Search name or phone", placeholder="e.g. Ayesha or 0300...")
    with col_f:
        status_opts = {
            "All Members": "all",
            "Active Only": "active",
            "Expired Only": "expired",
            "Never Subscribed": "never_subscribed",
        }
        status_label = st.selectbox("Filter by status", list(status_opts.keys()))
    with col_exp:
        st.write("")
        export_btn = st.button("⬇️ Export", use_container_width=True)

    try:
        members = search_members(search_q, status_opts[status_label])
    except Exception as e:
        st.error(f"Could not load members: {e}")
        members = []

    if not members:
        st.info("No members found. Use the **Register** tab to add members." if not search_q else "No members match your search.")
    else:
        df = pd.DataFrame(members)
        display_cols = {
            "member_id":            "ID",
            "full_name":            "Full Name",
            "phone":                "Phone",
            "joining_date":         "Joined",
            "membership_status":    "Status",
            "current_plan":         "Current Plan",
            "subscription_end_date":"Expires On",
        }
        df_show = df[[c for c in display_cols if c in df.columns]].rename(columns=display_cols)
        st.dataframe(df_show, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(members)} member(s)")

        if export_btn:
            csv = df_show.to_csv(index=False, encoding="utf-8-sig")
            st.download_button("📥 Download CSV", data=csv,
                               file_name=f"fither_members_{date.today()}.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Register member
# ══════════════════════════════════════════════════════════════════════════════
with tab_add:
    st.markdown('<div class="section-header">Register a New Member</div>', unsafe_allow_html=True)

    with st.form("register_member_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            full_name    = st.text_input("Full Name *", placeholder="e.g. Ayesha Siddiqui")
            phone        = st.text_input("Phone Number *", placeholder="e.g. 03001234567")
        with col2:
            joining_date = st.date_input("Joining Date *", value=date.today(), max_value=date.today())
            gender       = st.selectbox("Gender", ["Female", "Male", "Other"], index=0)
        notes = st.text_area("Notes (optional)", placeholder="Any relevant notes...", max_chars=500)

        submitted = st.form_submit_button("✅ Register Member", use_container_width=True, type="primary")
        if submitted:
            ok, msg, new_id = create_member(full_name, phone, joining_date, gender, notes)
            if ok:
                st.success(f"🎉 {msg} — Member ID: **{new_id}**")
            else:
                st.error(f"❌ {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Edit member
# ══════════════════════════════════════════════════════════════════════════════
with tab_edit:
    st.markdown('<div class="section-header">Edit Member Details</div>', unsafe_allow_html=True)

    member_id_input = st.number_input("Member ID", min_value=1, step=1, format="%d")
    load_btn = st.button("Load Member", key="load_member_edit")

    if load_btn:
        member = get_member_by_id(int(member_id_input))
        if not member:
            st.error("Member not found. Please check the ID.")
            st.session_state["edit_member_loaded"] = False
        else:
            st.session_state["edit_member_loaded"] = True
            st.session_state["edit_member_data"] = member

    if st.session_state.get("edit_member_loaded") and st.session_state.get("edit_member_data"):
        m = st.session_state["edit_member_data"]
        st.success(f"Loaded: **{m['full_name']}** (ID {m['member_id']})")

        with st.form("edit_member_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name  = st.text_input("Full Name *", value=m["full_name"])
                new_phone = st.text_input("Phone Number *", value=m["phone"])
            with col2:
                st.text_input("Joining Date (read-only)", value=str(m["joining_date"]), disabled=True)
                st.text_input("Gender (read-only)", value=m["gender"], disabled=True)
            new_notes = st.text_area("Notes", value=m["notes"] or "", max_chars=500)

            if st.form_submit_button("💾 Save Changes", type="primary"):
                ok, msg = update_member(m["member_id"], new_name, new_phone, new_notes)
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state["edit_member_data"] = get_member_by_id(m["member_id"])
                else:
                    st.error(f"❌ {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Member details
# ══════════════════════════════════════════════════════════════════════════════
with tab_detail:
    st.markdown('<div class="section-header">Member Profile & History</div>', unsafe_allow_html=True)

    detail_id  = st.number_input("Member ID", min_value=1, step=1, format="%d", key="detail_id")
    detail_btn = st.button("Load Profile", key="load_profile_btn")

    if detail_btn:
        m = get_member_by_id(int(detail_id))
        if not m:
            st.error("Member not found.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Full Name", m["full_name"])
            c2.metric("Phone",     m["phone"])
            c3.metric("Joined",    str(m["joining_date"]))
            if m["notes"]:
                st.info(f"📝 {m['notes']}")

            st.markdown("---")
            st.markdown('<div class="section-header">Subscription History</div>', unsafe_allow_html=True)
            history = get_member_subscription_history(int(detail_id))
            if not history:
                st.info("No subscription history yet.")
            else:
                for sub in history:
                    with st.expander(
                        f"{sub['plan_name']}  |  {sub['start_date']} → {sub['end_date']}  |  {sub['derived_status']}"
                    ):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("Agreed Fee",  format_pkr(sub["agreed_fee"]))
                        c2.metric("Total Paid",  format_pkr(sub["total_paid"]))
                        c3.metric("Balance Due", format_pkr(sub["balance_due"]))
                        c4.metric("Status",      sub["derived_status"])
