"""
utils/date_utils.py — Date calculation helpers for FitHer Gym Manager.

Date convention used throughout this project:
  - start_date is INCLUSIVE (member starts using the gym on this day).
  - end_date   is INCLUSIVE (last valid day of membership).
  - A 1-month membership starting 2024-10-10 ends 2024-11-09.
  - A 3-month membership starting 2024-10-10 ends 2025-01-09.

This module centralises all date arithmetic so the rule is applied
consistently in one place.
"""

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


def calculate_end_date(start_date: date, duration_months: int) -> date:
    """
    Calculate the inclusive end date for a membership.

    Convention: a 1-month membership starting on day D ends on day D-1 of
    the following month.  When the target month is shorter, the end date
    is clamped to that month's last day.

    Examples:
      - 2024-10-10 + 1 month → 2024-11-09
      - 2024-01-31 + 1 month → 2024-02-29 (leap) or 2024-02-28 (non-leap)
      - 2024-03-31 + 3 months → 2024-06-30  (June has no 31st)
      - 2024-01-01 + 6 months → 2024-06-30

    Algorithm:
      1. Compute the "nominal" end day = start.day - 1 in the target month.
      2. If day - 1 == 0, use the last day of the *previous* month instead
         (i.e. the target month's last day becomes the anchor).
      3. Clamp to the last day of the target month if needed.

    Args:
        start_date:       The first day of the membership (inclusive).
        duration_months:  Number of calendar months the plan covers.

    Returns:
        The last day of the membership period (inclusive).
    """
    if duration_months <= 0:
        raise ValueError("duration_months must be a positive integer.")

    # Target year/month after adding duration
    target = start_date + relativedelta(months=duration_months)
    target_year  = target.year
    target_month = target.month

    # Nominal end day = start.day - 1
    nominal_day = start_date.day - 1

    if nominal_day <= 0:
        # Start is the 1st → end is the last day of the previous month
        # i.e., the day before the target month's 1st
        import calendar
        prev_month = target_month - 1 if target_month > 1 else 12
        prev_year  = target_year if target_month > 1 else target_year - 1
        last_day_of_prev = calendar.monthrange(prev_year, prev_month)[1]
        return date(prev_year, prev_month, last_day_of_prev)
    else:
        # Clamp to the last day of the target month
        import calendar
        last_day = calendar.monthrange(target_year, target_month)[1]
        actual_day = min(nominal_day, last_day)
        return date(target_year, target_month, actual_day)


def is_subscription_active(
    start_date: date,
    end_date: date,
    status: str,
    reference_date: date | None = None,
) -> bool:
    """
    Determine whether a subscription is currently active.

    A subscription is considered active if ALL of the following are true:
      1. Its stored status is 'active' (not 'cancelled').
      2. today is >= start_date.
      3. today is <= end_date (i.e. not yet expired).

    The stored status is authoritative only for the 'cancelled' state.
    Expiry is always derived from the dates, not from the stored status.

    Args:
        start_date:     Inclusive start date of the subscription.
        end_date:       Inclusive end date of the subscription.
        status:         Stored status string ('active', 'expired', 'cancelled').
        reference_date: Date to use as "today" (defaults to date.today()).

    Returns:
        True if the subscription is active on reference_date.
    """
    today = reference_date or date.today()
    if status == "cancelled":
        return False
    return start_date <= today <= end_date


def is_expiring_soon(end_date: date, warning_days: int = 7, reference_date: date | None = None) -> bool:
    """
    Return True if the subscription's end_date is within the next warning_days
    calendar days from reference_date (inclusive of today and end_date).
    """
    today = reference_date or date.today()
    return today <= end_date <= today + timedelta(days=warning_days)


def days_remaining(end_date: date, reference_date: date | None = None) -> int:
    """
    Return the number of days remaining in a subscription.
    Returns 0 if already expired, negative values are clamped to 0.
    """
    today = reference_date or date.today()
    delta = (end_date - today).days
    return max(delta, 0)


def current_month_range(reference_date: date | None = None) -> tuple[date, date]:
    """
    Return the first and last day of the current calendar month.
    Useful for monthly payment collection queries.
    """
    today = reference_date or date.today()
    first = today.replace(day=1)
    # Last day: go to next month's 1st and subtract 1 day
    last = (first + relativedelta(months=1)) - timedelta(days=1)
    return first, last
