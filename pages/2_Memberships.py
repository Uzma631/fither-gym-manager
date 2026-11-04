"""
pages/2_Memberships.py — Membership assignment and management page.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal

from services.membership_service import (
    get_active_plans, assign_membership,
    get_active_subscription_for_member,
    search_subscriptions, cancel_subscription,
)
from services.member_service import get_all_members_simple
from utils.date_utils import calculate_end_date
from utils.money_utils import format_pkr, to_decimal
from utils.styles import inject_styles, render_sidebar

st.set_page_config(page_title="Memberships — FitHer", page_icon="📋", layout="wide")
inject_styles()
render_sidebar()

st.markdown("""
<div class="gym-hero">
    <div class="gym-hero-title">📋 Memberships</div>
    <div class="gym-hero-sub">Assign · View · Renew · Cancel</div>
</div>
""", unsafe_allow_html=True)

tab_assign, tab_list, tab_expiring = st.tabs([
    "➕  Assign Plan", "📋  All Subscriptions", "⏰  Expiring Soon"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Assign membership
# ══════════════════════════════════════════════════════════════════════════════
with tab_assign:
    st.markdown('<div class="section-header">Assign a Membership Plan</div>', unsafe_allow_html=True)

    try:
        plans   = get_active_plans()
        members = get_all_members_simple()
    except Exception as e:
        st.error(f"Could not load data: {e}")
        plans, members = [], []

    if not plans:
        st.warning("No active membership plans found in the database.")
        st.stop()
    if not members:
        st.info("No members yet. Register members first.")
        st.stop()

    member_opts = {
        f"{m['full_name']} — {m['phone']} (ID {m['member_id']})": m['member_id']
        for m in members
    }
    selected_label = st.selectbox("Select Member *", list(member_opts.keys()))
    selected_member_id = member_opts[selected_label]

    existing = get_active_subscription_for_member(selected_member_id)
    if existing:
        st.warning(
            f"⚠️ **{selected_label.split(' — ')[0]}** already has an active plan: "
            f"**{existing['plan_name']}** (expires {existing['end_date']}). "
            "A new subscription will overlap."
        )
        allow_overlap = st.checkbox("I understand — assign anyway (early renewal)", value=False)
        if not allow_overlap:
            st.info("Tick the checkbox above to continue.")
            st.stop()

    plan_opts = {p["plan_name"]: p for p in plans}
    selected_plan_name = st.selectbox("Select Plan *", list(plan_opts.keys()))
    selected_plan = plan_opts[selected_plan_name]

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date *", value=date.today(), max_value=date(2030, 12, 31))
    preview_end = calculate_end_date(start_date, selected_plan["duration_months"])
    with col2:
        st.text_input("End Date (auto-calculated)", value=str(preview_end), disabled=True)

    col3, col4 = st.columns(2)
    with col3:
        standard = float(selected_plan["price"])
        agreed   = st.number_input("Agreed Fee (Rs) *", min_value=0.0, max_value=999999.0,
                                   value=standard, step=100.0,
                                   help=f"Standard: Rs {standard:,.2f}. Adjust for discounts.")
    with col4:
        if agreed < standard:
            st.info(f"💸 Discount applied: Rs {standard - agreed:,.2f} off")
        else:
            st.success(f"✅ Standard price: Rs {standard:,.2f}")

    st.caption(f"📌 {selected_plan.get('description', '')}  |  Duration: {selected_plan['duration_months']} month(s)  |  {start_date} → {preview_end}")
    st.info("ℹ️ No payment is recorded automatically. Use the Payments page to record fees.")

    if st.button("✅ Assign Membership", type="primary", use_container_width=True):
        ok, msg, sub_id = assign_membership(
            selected_member_id, selected_plan["plan_id"], start_date, to_decimal(agreed)
        )
        if ok:
            st.success(f"🎉 {msg} (Subscription ID: {sub_id})")
        else:
            st.error(f"❌ {msg}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — All subscriptions
# ══════════════════════════════════════════════════════════════════════════════
with tab_list:
    col_s, col_f = st.columns([3, 2])
    with col_s:
        sub_search = st.text_input("🔍 Search member name or phone", key="sub_search")
    with col_f:
        filter_opts = {
            "All": "all", "Active": "active",
            "Expiring Soon (7d)": "expiring_soon",
            "Expired": "expired", "Cancelled": "cancelled",
        }
        filter_label = st.selectbox("Status filter", list(filter_opts.keys()), key="sub_filter")

    try:
        subs = search_subscriptions(sub_search, filter_opts[filter_label])
    except Exception as e:
        st.error(f"Could not load subscriptions: {e}")
        subs = []

    if not subs:
        st.info("No subscriptions found.")
    else:
        df = pd.DataFrame(subs)
        df["agreed_fee"]  = df["agreed_fee"].apply(format_pkr)
        df["total_paid"]  = df["total_paid"].apply(format_pkr)
        df["balance_due"] = df["balance_due"].apply(format_pkr)
        display = {
            "subscription_id":"Sub ID", "full_name":"Member", "phone":"Phone",
            "plan_name":"Plan", "start_date":"Start", "end_date":"End",
            "derived_status":"Status", "agreed_fee":"Fee",
            "total_paid":"Paid", "balance_due":"Balance", "days_left":"Days Left",
        }
        df_s = df[[c for c in display if c in df.columns]].rename(columns=display)
        st.dataframe(df_s, use_container_width=True, hide_index=True)
        st.caption(f"{len(subs)} subscription(s)")

        csv = df_s.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("⬇️ Export CSV", data=csv,
                           file_name=f"fither_subscriptions_{date.today()}.csv", mime="text/csv")

        st.divider()
        st.markdown("**Cancel a Subscription**")
        cancel_id  = st.number_input("Subscription ID to cancel", min_value=1, step=1, format="%d")
        if st.button("❌ Cancel Subscription"):
            ok, msg = cancel_subscription(int(cancel_id))
            st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")
            if ok: st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Expiring soon
# ══════════════════════════════════════════════════════════════════════════════
with tab_expiring:
    st.markdown('<div class="section-header">Expiring in the Next 7 Days</div>', unsafe_allow_html=True)
    try:
        exp = search_subscriptions("", "expiring_soon")
    except Exception as e:
        st.error(f"Could not load data: {e}")
        exp = []

    if not exp:
        st.success("✅ No memberships expiring in the next 7 days. All good!")
    else:
        df_e = pd.DataFrame(exp)
        df_e["balance_due"] = df_e["balance_due"].apply(format_pkr)
        cols_e = {
            "full_name":"Member", "phone":"Phone", "plan_name":"Plan",
            "end_date":"Expires On", "days_left":"Days Left", "balance_due":"Balance Due",
        }
        st.dataframe(
            df_e[[c for c in cols_e if c in df_e.columns]].rename(columns=cols_e),
            use_container_width=True, hide_index=True,
        )
        st.warning(f"⚠️ {len(exp)} membership(s) expiring soon — consider contacting these members.")
