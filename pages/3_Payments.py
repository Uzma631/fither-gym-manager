"""
pages/3_Payments.py — Payment recording and history page.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date

from services.payment_service import (
    record_payment, get_subscription_payment_summary,
    get_payments_for_subscription, search_payments,
    get_subscriptions_with_balance,
)
from utils.money_utils import format_pkr, to_decimal
from utils.styles import inject_styles, render_sidebar
from config import PAYMENT_METHODS

st.set_page_config(page_title="Payments — FitHer", page_icon="💳", layout="wide")
inject_styles()
render_sidebar()

st.markdown("""
<div class="gym-hero">
    <div class="gym-hero-title">💳 Payment Management</div>
    <div class="gym-hero-sub">Record · History · Monthly Summary</div>
</div>
""", unsafe_allow_html=True)

tab_record, tab_history, tab_summary = st.tabs([
    "➕  Record Payment", "📋  Payment History", "📊  Monthly Summary"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Record payment
# ══════════════════════════════════════════════════════════════════════════════
with tab_record:
    st.markdown('<div class="section-header">Record a Fee Payment</div>', unsafe_allow_html=True)

    pay_search = st.text_input("🔍 Search member", key="pay_search",
                               placeholder="Leave blank to see all with outstanding balance")
    try:
        subs_balance = get_subscriptions_with_balance(pay_search)
    except Exception as e:
        st.error(f"Could not load subscriptions: {e}")
        subs_balance = []

    if not subs_balance:
        if pay_search:
            st.info("No subscriptions with outstanding balance found.")
        else:
            st.success("✅ All subscriptions are fully paid! No outstanding balances.")
        st.stop()

    sub_opts = {
        f"{s['full_name']} — {s['plan_name']} | Balance: {format_pkr(s['balance_due'])} (ID {s['subscription_id']})": s['subscription_id']
        for s in subs_balance
    }
    selected_sub_label = st.selectbox("Select Subscription *", list(sub_opts.keys()))
    selected_sub_id    = sub_opts[selected_sub_label]

    try:
        summary = get_subscription_payment_summary(selected_sub_id)
    except Exception as e:
        st.error(f"Could not load subscription details: {e}")
        summary = None

    if summary:
        # Payment summary card
        st.markdown(f"""
        <div class="pay-summary">
            <div style="font-size:1.05rem; font-weight:800; color:#E040FB; margin-bottom:10px;">
                {summary['full_name']} &nbsp;·&nbsp; {summary['plan_name']}
            </div>
            <div style="font-size:0.82rem; color:#888; margin-bottom:14px;">
                Period: {summary['start_date']} → {summary['end_date']}
            </div>
            <div style="display:flex; gap:40px;">
                <div>
                    <div style="font-size:0.70rem; color:#666; text-transform:uppercase; letter-spacing:0.08em;">Agreed Fee</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#F0F0F0;">{format_pkr(summary['agreed_fee'])}</div>
                </div>
                <div>
                    <div style="font-size:0.70rem; color:#666; text-transform:uppercase; letter-spacing:0.08em;">Paid So Far</div>
                    <div style="font-size:1.3rem; font-weight:700; color:#00E676;">{format_pkr(summary['total_paid'])}</div>
                </div>
                <div>
                    <div style="font-size:0.70rem; color:#666; text-transform:uppercase; letter-spacing:0.08em;">Outstanding</div>
                    <div style="font-size:1.6rem; font-weight:900; color:#FF4081;">{format_pkr(summary['balance_due'])}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("payment_form", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                pay_amount = st.number_input(
                    "Payment Amount (Rs) *", min_value=1.0,
                    max_value=float(summary["balance_due"]) + 0.01,
                    value=float(summary["balance_due"]), step=100.0,
                )
            with col2:
                pay_date   = st.date_input("Payment Date *", value=date.today(), max_value=date.today())
            with col3:
                pay_method = st.selectbox("Method *", PAYMENT_METHODS)
            pay_notes = st.text_area("Notes (optional)", max_chars=300)

            if st.form_submit_button("💾 Record Payment", type="primary", use_container_width=True):
                ok, msg, pay_id = record_payment(
                    selected_sub_id, to_decimal(pay_amount), pay_date, pay_method, pay_notes
                )
                if ok:
                    st.success(f"🎉 {msg} (Payment ID: {pay_id})")
                    new_s = get_subscription_payment_summary(selected_sub_id)
                    if new_s:
                        st.info(f"Updated balance: **{format_pkr(new_s['balance_due'])}** | Total paid: **{format_pkr(new_s['total_paid'])}**")
                else:
                    st.error(f"❌ {msg}")

        # Payment history for this subscription
        st.divider()
        st.markdown("**Payment History for This Subscription**")
        try:
            ph = get_payments_for_subscription(selected_sub_id)
        except Exception as e:
            st.error(f"{e}")
            ph = []

        if not ph:
            st.info("No payments recorded yet for this subscription.")
        else:
            df_ph = pd.DataFrame(ph)
            df_ph["amount"] = df_ph["amount"].apply(format_pkr)
            df_ph = df_ph.rename(columns={
                "payment_id":"ID", "amount":"Amount", "payment_date":"Date",
                "payment_method":"Method", "notes":"Notes",
            })
            st.dataframe(df_ph[["ID","Date","Amount","Method","Notes"]], use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Payment history
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    st.markdown('<div class="section-header">Payment History</div>', unsafe_allow_html=True)

    col_s, col_m, col_d1, col_d2 = st.columns([2, 1, 1, 1])
    with col_s:
        hist_search = st.text_input("🔍 Member name or phone", key="hist_search")
    with col_m:
        mf_label    = st.selectbox("Method", ["All"] + PAYMENT_METHODS, key="hist_method")
        mf          = None if mf_label == "All" else mf_label
    with col_d1:
        date_from   = st.date_input("From", value=date.today().replace(day=1), key="hist_from")
    with col_d2:
        date_to     = st.date_input("To",   value=date.today(), key="hist_to")

    try:
        payments = search_payments(hist_search, mf or "all", date_from, date_to)
    except Exception as e:
        st.error(f"Could not load payments: {e}")
        payments = []

    if not payments:
        st.info("No payments found for the selected filters.")
    else:
        df_p = pd.DataFrame(payments)
        df_p["amount"] = df_p["amount"].apply(format_pkr)
        display = {
            "payment_id":"ID", "payment_date":"Date", "full_name":"Member",
            "plan_name":"Plan", "amount":"Amount", "payment_method":"Method", "notes":"Notes",
        }
        df_h = df_p[[c for c in display if c in df_p.columns]].rename(columns=display)
        st.dataframe(df_h, use_container_width=True, hide_index=True)
        st.caption(f"{len(payments)} payment(s)")
        st.download_button("⬇️ Export CSV",
                           data=df_h.to_csv(index=False, encoding="utf-8-sig"),
                           file_name=f"fither_payments_{date.today()}.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Monthly summary
# ══════════════════════════════════════════════════════════════════════════════
with tab_summary:
    st.markdown('<div class="section-header">Monthly Collections</div>', unsafe_allow_html=True)
    today        = date.today()
    first_of_month = today.replace(day=1)

    try:
        month_pays = search_payments(date_from=first_of_month, date_to=today)
    except Exception as e:
        st.error(f"{e}")
        month_pays = []

    if not month_pays:
        st.info(f"No payments recorded for {today.strftime('%B %Y')} yet.")
    else:
        total = sum(float(p["amount"]) for p in month_pays)
        st.metric(f"Total Collected — {today.strftime('%B %Y')}", format_pkr(total))

        df_mo = pd.DataFrame(month_pays)
        method_totals = (
            df_mo.groupby("payment_method")["amount"]
            .apply(lambda x: sum(float(v) for v in x))
            .reset_index()
        )
        method_totals.columns = ["Method", "Total (Rs)"]
        method_totals["Total (Rs)"] = method_totals["Total (Rs)"].apply(lambda v: f"Rs {v:,.2f}")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("**By Payment Method**")
            st.dataframe(method_totals, use_container_width=True, hide_index=True)
        with col2:
            df_mo["amount"] = df_mo["amount"].apply(format_pkr)
            df_mo2 = df_mo.rename(columns={"payment_date":"Date","full_name":"Member",
                                            "amount":"Amount","payment_method":"Method"})
            st.markdown("**Individual Transactions**")
            st.dataframe(df_mo2[["Date","Member","Amount","Method"]], use_container_width=True, hide_index=True)
