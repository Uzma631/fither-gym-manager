"""
services/member_service.py — Member CRUD operations for FitHer Gym Manager.

All queries use parameterized statements (no string interpolation in SQL).
All money values use Decimal.  All database connections use the context manager.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from decimal import Decimal

from database.connection import db_connection
from utils.validators import validate_full_name, validate_phone, normalise_phone, validate_notes
from utils.money_utils import to_decimal


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def create_member(
    full_name: str,
    phone: str,
    joining_date: date,
    gender: str = "Female",
    notes: str = "",
) -> tuple[bool, str, int | None]:
    """
    Insert a new member record.

    Returns:
        (success, message, new_member_id)
    """
    # Validate inputs
    ok, msg = validate_full_name(full_name)
    if not ok:
        return False, msg, None

    ok, msg = validate_phone(phone)
    if not ok:
        return False, msg, None

    if joining_date > date.today():
        return False, "Joining date cannot be in the future.", None

    ok, msg = validate_notes(notes or "")
    if not ok:
        return False, msg, None

    clean_phone = normalise_phone(phone)

    sql = """
        INSERT INTO members (full_name, phone, joining_date, gender, notes)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                full_name.strip(),
                clean_phone,
                joining_date,
                gender,
                notes.strip() if notes else None,
            ))
            new_id = cursor.lastrowid
            cursor.close()
        return True, "Member registered successfully.", new_id
    except Exception as e:
        return False, f"Database error while saving member: {e}", None


# ---------------------------------------------------------------------------
# READ — single member
# ---------------------------------------------------------------------------

def get_member_by_id(member_id: int) -> dict | None:
    """Return a single member dict or None if not found."""
    sql = """
        SELECT member_id, full_name, phone, joining_date, gender, notes, created_at
        FROM members
        WHERE member_id = %s
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (member_id,))
            row = cursor.fetchone()
            cursor.close()
        return row
    except Exception:
        return None


# ---------------------------------------------------------------------------
# READ — list / search
# ---------------------------------------------------------------------------

def search_members(query: str = "", status_filter: str = "all") -> list[dict]:
    """
    Return members matching the search query (name or phone).
    status_filter can be 'all', 'active', 'expired', 'never_subscribed'.

    Active/expired is derived from subscription dates at query time.
    """
    params = []

    base_sql = """
        SELECT
            m.member_id,
            m.full_name,
            m.phone,
            m.joining_date,
            m.gender,
            m.notes,
            -- Derive current membership status from dates
            CASE
                WHEN s.subscription_id IS NULL THEN 'Never Subscribed'
                WHEN s.status = 'cancelled'    THEN 'Cancelled'
                WHEN CURDATE() BETWEEN s.start_date AND s.end_date THEN 'Active'
                ELSE 'Expired'
            END AS membership_status,
            s.end_date AS subscription_end_date,
            p.plan_name AS current_plan
        FROM members m
        LEFT JOIN (
            -- Most recent non-cancelled subscription per member
            SELECT sub.*
            FROM subscriptions sub
            INNER JOIN (
                SELECT member_id, MAX(start_date) AS max_start
                FROM subscriptions
                WHERE status != 'cancelled'
                GROUP BY member_id
            ) latest ON sub.member_id = latest.member_id
                     AND sub.start_date = latest.max_start
        ) s ON m.member_id = s.member_id
        LEFT JOIN membership_plans p ON s.plan_id = p.plan_id
    """

    where_clauses = []

    if query and query.strip():
        where_clauses.append("(m.full_name LIKE %s OR m.phone LIKE %s)")
        like = f"%{query.strip()}%"
        params.extend([like, like])

    if status_filter == "active":
        where_clauses.append(
            "s.subscription_id IS NOT NULL AND s.status != 'cancelled' "
            "AND CURDATE() BETWEEN s.start_date AND s.end_date"
        )
    elif status_filter == "expired":
        where_clauses.append(
            "s.subscription_id IS NOT NULL AND s.status != 'cancelled' "
            "AND s.end_date < CURDATE()"
        )
    elif status_filter == "never_subscribed":
        where_clauses.append("s.subscription_id IS NULL")

    if where_clauses:
        base_sql += " WHERE " + " AND ".join(where_clauses)

    base_sql += " ORDER BY m.full_name ASC"

    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(base_sql, params)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error searching members: {e}") from e


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_member(
    member_id: int,
    full_name: str,
    phone: str,
    notes: str = "",
) -> tuple[bool, str]:
    """
    Update a member's editable fields (name, phone, notes).
    Returns (success, message).
    """
    ok, msg = validate_full_name(full_name)
    if not ok:
        return False, msg

    ok, msg = validate_phone(phone)
    if not ok:
        return False, msg

    ok, msg = validate_notes(notes or "")
    if not ok:
        return False, msg

    clean_phone = normalise_phone(phone)

    sql = """
        UPDATE members
        SET full_name = %s, phone = %s, notes = %s
        WHERE member_id = %s
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (
                full_name.strip(),
                clean_phone,
                notes.strip() if notes else None,
                member_id,
            ))
            affected = cursor.rowcount
            cursor.close()
        if affected == 0:
            return False, "Member not found."
        return True, "Member details updated successfully."
    except Exception as e:
        return False, f"Database error while updating member: {e}"


# ---------------------------------------------------------------------------
# Member subscription history (used on detail page)
# ---------------------------------------------------------------------------

def get_member_subscription_history(member_id: int) -> list[dict]:
    """Return all subscriptions for a member with payment summaries."""
    sql = """
        SELECT
            s.subscription_id,
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
            END AS derived_status
        FROM subscriptions s
        JOIN membership_plans p ON s.plan_id = p.plan_id
        LEFT JOIN payments py ON s.subscription_id = py.subscription_id
        WHERE s.member_id = %s
        GROUP BY s.subscription_id, p.plan_name, s.start_date, s.end_date,
                 s.agreed_fee, s.status
        ORDER BY s.start_date DESC
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (member_id,))
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching subscription history: {e}") from e


def get_all_members_simple() -> list[dict]:
    """Return a minimal list of all members for dropdowns."""
    sql = "SELECT member_id, full_name, phone FROM members ORDER BY full_name ASC"
    try:
        with db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()
        return rows
    except Exception as e:
        raise RuntimeError(f"Error fetching members: {e}") from e
