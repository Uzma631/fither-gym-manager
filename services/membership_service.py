"""
services/membership_service.py — Subscription/membership operations.

Business rules implemented here:
  - end_date is always calculated from start_date + plan duration (inclusive).
  - Creating a new subscription never overwrites an old one.
  - Warn (but allow with confirmation) if a member already has an active subscription.
  - Status in the DB is kept in sync but the application always re-derives
    live status from dates.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from decimal import Decimal

from database.connection import db_connection
from utils.date_utils import calculate_end_date, is_subscription_active
from utils.money_utils import to_decimal


# ---------------------------------------------------------------------------
# Plans
# ---------------------------------------------------------------------------

def get_active_plans() -> list[dict]:
    """Return all active membership plans."""
    sql = """
        SELECT plan_id, plan_name, duration_months, price, description
        FROM membership_plans
        WHERE is_active = 1
        ORDER BY duration_months ASC
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching plans: {e}") from e


def get_all_plans() -> list[dict]:
    """Return all plans including inactive ones (for management view)."""
    sql = """
        SELECT plan_id, plan_name, duration_months, price, description, is_active
        FROM membership_plans
        ORDER BY is_active DESC, duration_months ASC
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching plans: {e}") from e


# ---------------------------------------------------------------------------
# Check for overlapping active subscription
# ---------------------------------------------------------------------------

def get_active_subscription_for_member(member_id: int) -> dict | None:
    """
    Return the currently active subscription for a member, or None.
    Uses date ranges to determine activity — not just the stored status.
    """
    sql = """
        SELECT s.subscription_id, p.plan_name, s.start_date, s.end_date,
               s.agreed_fee, s.status
        FROM subscriptions s
        JOIN membership_plans p ON s.plan_id = p.plan_id
        WHERE s.member_id = %s
          AND s.status != 'cancelled'
          AND CURDATE() BETWEEN s.start_date AND s.end_date
        ORDER BY s.start_date DESC
        LIMIT 1
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (member_id,))
            row = cursor.fetchone()
            cursor.close()
        return row
    except Exception as e:
        raise RuntimeError(f"Error checking active subscription: {e}") from e


# ---------------------------------------------------------------------------
# CREATE subscription
# ---------------------------------------------------------------------------

def assign_membership(
    member_id: int,
    plan_id: int,
    start_date: date,
    agreed_fee: Decimal,
) -> tuple[bool, str, int | None]:
    """
    Assign a membership plan to a member.

    - Calculates end_date automatically from the plan's duration_months.
    - Stores agreed_fee (may differ from plan.price if a discount was given).
    - Does NOT auto-record a payment.
    - Returns (success, message, subscription_id).

    NOTE: Caller should check get_active_subscription_for_member() first and
          display a warning if one exists.  This function creates the record
          regardless (to support intentional overlapping with explicit confirm).
    """
    if start_date > date.today() + __import__('datetime').timedelta(days=365):
        return False, "Start date seems unreasonably far in the future.", None

    # Fetch plan details
    sql_plan = "SELECT plan_id, duration_months, price FROM membership_plans WHERE plan_id = %s AND is_active = 1"
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql_plan, (plan_id,))
            plan = cursor.fetchone()
            cursor.close()
    except Exception as e:
        return False, f"Database error: {e}", None

    if not plan:
        return False, "Selected plan not found or is inactive.", None

    fee = to_decimal(agreed_fee)
    if fee <= Decimal("0"):
        return False, "Agreed fee must be greater than zero.", None

    end_date = calculate_end_date(start_date, plan["duration_months"])

    sql_insert = """
        INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, agreed_fee, status)
        VALUES (%s, %s, %s, %s, %s, 'active')
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_insert, (member_id, plan_id, start_date, end_date, str(fee)))
            new_id = cursor.lastrowid
            cursor.close()
        return True, f"Membership assigned. Valid from {start_date} to {end_date}.", new_id
    except Exception as e:
        return False, f"Database error while assigning membership: {e}", None


# ---------------------------------------------------------------------------
# READ subscriptions
# ---------------------------------------------------------------------------

def search_subscriptions(query: str = "", filter_status: str = "all") -> list[dict]:
    """
    Return subscriptions with member name and plan details.
    filter_status: 'all', 'active', 'expiring_soon', 'expired', 'cancelled'
    """
    params = []
    where_parts = []

    base_sql = """
        SELECT
            s.subscription_id,
            m.member_id,
            m.full_name,
            m.phone,
            p.plan_name,
            s.start_date,
            s.end_date,
            s.agreed_fee,
            s.status,
            COALESCE(SUM(py.amount), 0) AS total_paid,
            (s.agreed_fee - COALESCE(SUM(py.amount), 0)) AS balance_due,
            CASE
                WHEN s.status = 'cancelled' THEN 'Cancelled'
                WHEN CURDATE() BETWEEN s.start_date AND s.end_date THEN 'Active'
                ELSE 'Expired'
            END AS derived_status,
            DATEDIFF(s.end_date, CURDATE()) AS days_left
        FROM subscriptions s
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
        LEFT JOIN payments py ON s.subscription_id = py.subscription_id
    """

    if query and query.strip():
        where_parts.append("(m.full_name LIKE %s OR m.phone LIKE %s)")
        like = f"%{query.strip()}%"
        params.extend([like, like])

    if filter_status == "active":
        where_parts.append("s.status != 'cancelled' AND CURDATE() BETWEEN s.start_date AND s.end_date")
    elif filter_status == "expiring_soon":
        where_parts.append(
            "s.status != 'cancelled' AND CURDATE() BETWEEN s.start_date AND s.end_date "
            "AND s.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)"
        )
    elif filter_status == "expired":
        where_parts.append("s.status != 'cancelled' AND s.end_date < CURDATE()")
    elif filter_status == "cancelled":
        where_parts.append("s.status = 'cancelled'")

    if where_parts:
        base_sql += " WHERE " + " AND ".join(where_parts)

    base_sql += """
        GROUP BY s.subscription_id, m.member_id, m.full_name, m.phone,
                 p.plan_name, s.start_date, s.end_date, s.agreed_fee, s.status
        ORDER BY s.start_date DESC
    """

    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(base_sql, params)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error searching subscriptions: {e}") from e


def cancel_subscription(subscription_id: int) -> tuple[bool, str]:
    """Mark a subscription as cancelled."""
    sql = "UPDATE subscriptions SET status = 'cancelled' WHERE subscription_id = %s"
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (subscription_id,))
            affected = cursor.rowcount
            cursor.close()
        if affected == 0:
            return False, "Subscription not found."
        return True, "Subscription cancelled."
    except Exception as e:
        return False, f"Database error: {e}"
