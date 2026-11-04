"""
services/payment_service.py — Payment recording and querying for FitHer Gym Manager.

Key rules:
  - A subscription may have multiple partial payments.
  - A payment must not exceed the outstanding balance; this is validated here.
  - Outstanding balance = agreed_fee − SUM(payments).
  - No payment records are ever overwritten.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from decimal import Decimal

from database.connection import db_connection
from utils.money_utils import to_decimal, outstanding_balance
from utils.validators import validate_payment_amount


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_subscription_payment_summary(subscription_id: int) -> dict | None:
    """
    Return a summary dict with agreed_fee, total_paid, and balance_due
    for the given subscription, or None if not found.
    """
    sql = """
        SELECT
            s.subscription_id,
            s.agreed_fee,
            s.status,
            s.start_date,
            s.end_date,
            m.full_name,
            m.phone,
            p.plan_name,
            COALESCE(SUM(py.amount), 0) AS total_paid
        FROM subscriptions s
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
        LEFT JOIN payments py ON s.subscription_id = py.subscription_id
        WHERE s.subscription_id = %s
        GROUP BY s.subscription_id, s.agreed_fee, s.status, s.start_date,
                 s.end_date, m.full_name, m.phone, p.plan_name
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (subscription_id,))
            row = cursor.fetchone()
            cursor.close()
        if row:
            row["balance_due"] = outstanding_balance(row["agreed_fee"], row["total_paid"])
            row["agreed_fee"]  = to_decimal(row["agreed_fee"])
            row["total_paid"]  = to_decimal(row["total_paid"])
        return row
    except Exception as e:
        raise RuntimeError(f"Error fetching payment summary: {e}") from e


def get_payments_for_subscription(subscription_id: int) -> list[dict]:
    """Return all payment records for a subscription, newest first."""
    sql = """
        SELECT payment_id, amount, payment_date, payment_method, notes, created_at
        FROM payments
        WHERE subscription_id = %s
        ORDER BY payment_date DESC, created_at DESC
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (subscription_id,))
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching payments: {e}") from e


# ---------------------------------------------------------------------------
# CREATE payment
# ---------------------------------------------------------------------------

def record_payment(
    subscription_id: int,
    amount: Decimal,
    payment_date: date,
    payment_method: str,
    notes: str = "",
) -> tuple[bool, str, int | None]:
    """
    Record a payment against a subscription.

    Validates:
      - Amount is positive.
      - Amount does not exceed the outstanding balance.
      - Payment method is one of the allowed values.

    Returns:
        (success, message, payment_id)
    """
    # Re-fetch current balance
    summary = get_subscription_payment_summary(subscription_id)
    if not summary:
        return False, "Subscription not found.", None

    amount_dec = to_decimal(amount)
    balance = summary["balance_due"]

    ok, msg = validate_payment_amount(amount_dec, balance)
    if not ok:
        return False, msg, None

    allowed_methods = ["Cash", "Bank Transfer", "Other"]
    if payment_method not in allowed_methods:
        return False, f"Payment method must be one of: {', '.join(allowed_methods)}.", None

    if payment_date > date.today():
        return False, "Payment date cannot be in the future.", None

    sql = """
        INSERT INTO payments (subscription_id, amount, payment_date, payment_method, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                subscription_id,
                str(amount_dec),
                payment_date,
                payment_method,
                notes.strip() if notes else None,
            ))
            new_id = cursor.lastrowid
            cursor.close()
        return True, f"Payment of Rs {amount_dec:,.2f} recorded successfully.", new_id
    except Exception as e:
        return False, f"Database error while recording payment: {e}", None


# ---------------------------------------------------------------------------
# READ payments (filtered list)
# ---------------------------------------------------------------------------

def search_payments(
    query: str = "",
    method_filter: str = "all",
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[dict]:
    """Return payments with member and subscription details, with optional filters."""
    params = []
    where_parts = []

    sql = """
        SELECT
            py.payment_id,
            py.amount,
            py.payment_date,
            py.payment_method,
            py.notes,
            py.created_at,
            m.full_name,
            m.phone,
            p.plan_name,
            s.subscription_id,
            s.agreed_fee,
            s.start_date AS sub_start,
            s.end_date   AS sub_end
        FROM payments py
        JOIN subscriptions s ON py.subscription_id = s.subscription_id
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
    """

    if query and query.strip():
        where_parts.append("(m.full_name LIKE %s OR m.phone LIKE %s)")
        like = f"%{query.strip()}%"
        params.extend([like, like])

    if method_filter and method_filter != "all":
        where_parts.append("py.payment_method = %s")
        params.append(method_filter)

    if date_from:
        where_parts.append("py.payment_date >= %s")
        params.append(date_from)

    if date_to:
        where_parts.append("py.payment_date <= %s")
        params.append(date_to)

    if where_parts:
        sql += " WHERE " + " AND ".join(where_parts)

    sql += " ORDER BY py.payment_date DESC, py.created_at DESC"

    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error searching payments: {e}") from e


def get_subscriptions_with_balance(query: str = "") -> list[dict]:
    """
    Return subscriptions that have an outstanding balance > 0,
    with member details.  Used for the payment entry dropdown.
    """
    params = []
    sql = """
        SELECT
            s.subscription_id,
            m.full_name,
            m.phone,
            p.plan_name,
            s.start_date,
            s.end_date,
            s.agreed_fee,
            COALESCE(SUM(py.amount), 0) AS total_paid,
            (s.agreed_fee - COALESCE(SUM(py.amount), 0)) AS balance_due
        FROM subscriptions s
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
        LEFT JOIN payments py ON s.subscription_id = py.subscription_id
    """
    where_parts = ["s.status != 'cancelled'"]

    if query and query.strip():
        where_parts.append("(m.full_name LIKE %s OR m.phone LIKE %s)")
        like = f"%{query.strip()}%"
        params.extend([like, like])

    sql += " WHERE " + " AND ".join(where_parts)
    sql += """
        GROUP BY s.subscription_id, m.full_name, m.phone, p.plan_name,
                 s.start_date, s.end_date, s.agreed_fee
        HAVING balance_due > 0
        ORDER BY m.full_name ASC
    """

    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching subscriptions with balance: {e}") from e
