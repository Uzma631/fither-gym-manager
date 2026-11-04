"""
services/dashboard_service.py — KPI queries for the FitHer Gym Dashboard.

All figures are calculated from MySQL queries; nothing is hardcoded.
Business rules:
  - A member is 'active' if they have a non-cancelled subscription covering today.
  - 'Expiring soon' = active subscriptions whose end_date is within 7 days.
  - Monthly collections = payments with payment_date in the current calendar month.
  - Outstanding balance = SUM(agreed_fee) - SUM(payments) across all non-cancelled subs.
  - Members are never double-counted.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection
from utils.money_utils import to_decimal
from decimal import Decimal


def get_dashboard_kpis() -> dict:
    """
    Return a dict of KPI values for the dashboard.
    All values come from MySQL.  Returns safe defaults on error.
    """
    defaults = {
        "total_members": 0,
        "active_members": 0,
        "expiring_soon": 0,
        "expired_memberships": 0,
        "monthly_collections": Decimal("0.00"),
        "total_outstanding": Decimal("0.00"),
        "error": None,
    }

    sql = """
        SELECT
            -- Total registered members
            (SELECT COUNT(*) FROM members) AS total_members,

            -- Active members: those with a non-cancelled subscription covering today
            (SELECT COUNT(DISTINCT member_id)
             FROM subscriptions
             WHERE status != 'cancelled'
               AND CURDATE() BETWEEN start_date AND end_date
            ) AS active_members,

            -- Expiring within next 7 days (among active subs)
            (SELECT COUNT(*)
             FROM subscriptions
             WHERE status != 'cancelled'
               AND CURDATE() BETWEEN start_date AND end_date
               AND end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ) AS expiring_soon,

            -- Expired: non-cancelled subs with end_date in the past
            (SELECT COUNT(*)
             FROM subscriptions
             WHERE status != 'cancelled'
               AND end_date < CURDATE()
            ) AS expired_memberships,

            -- Payments collected this calendar month
            (SELECT COALESCE(SUM(amount), 0)
             FROM payments
             WHERE YEAR(payment_date)  = YEAR(CURDATE())
               AND MONTH(payment_date) = MONTH(CURDATE())
            ) AS monthly_collections,

            -- Total outstanding balance across all non-cancelled subscriptions
            (SELECT COALESCE(
                SUM(s.agreed_fee) - SUM(COALESCE(p.total_paid, 0)),
                0
             )
             FROM subscriptions s
             LEFT JOIN (
                 SELECT subscription_id, SUM(amount) AS total_paid
                 FROM payments
                 GROUP BY subscription_id
             ) p ON s.subscription_id = p.subscription_id
             WHERE s.status != 'cancelled'
            ) AS total_outstanding
    """

    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()
        return {
            "total_members":      int(row["total_members"] or 0),
            "active_members":     int(row["active_members"] or 0),
            "expiring_soon":      int(row["expiring_soon"] or 0),
            "expired_memberships":int(row["expired_memberships"] or 0),
            "monthly_collections":to_decimal(row["monthly_collections"]),
            "total_outstanding":  to_decimal(row["total_outstanding"]),
            "error": None,
        }
    except Exception as e:
        defaults["error"] = str(e)
        return defaults


def get_expiring_soon_list(days: int = 7) -> list[dict]:
    """Return subscriptions expiring within `days` calendar days."""
    sql = """
        SELECT
            m.full_name,
            m.phone,
            p.plan_name,
            s.end_date,
            DATEDIFF(s.end_date, CURDATE()) AS days_left
        FROM subscriptions s
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
        WHERE s.status != 'cancelled'
          AND CURDATE() BETWEEN s.start_date AND s.end_date
          AND s.end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        ORDER BY s.end_date ASC
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (days,))
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception:
        return []


def get_recent_payments(limit: int = 10) -> list[dict]:
    """Return the most recent payment transactions."""
    sql = """
        SELECT
            py.payment_date,
            py.amount,
            py.payment_method,
            m.full_name,
            p.plan_name
        FROM payments py
        JOIN subscriptions s ON py.subscription_id = s.subscription_id
        JOIN members m ON s.member_id = m.member_id
        JOIN membership_plans p ON s.plan_id = p.plan_id
        ORDER BY py.payment_date DESC, py.created_at DESC
        LIMIT %s
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (limit,))
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception:
        return []
