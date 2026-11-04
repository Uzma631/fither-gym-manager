"""
tests/test_membership_dates.py — Unit tests for membership date calculations.

Run with:  python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date, timedelta
from utils.date_utils import (
    calculate_end_date, is_subscription_active, is_expiring_soon,
    days_remaining, current_month_range,
)


# ── End date calculation ──────────────────────────────────────────────────────

class TestCalculateEndDate:

    def test_one_month_basic(self):
        start = date(2024, 10, 10)
        end = calculate_end_date(start, 1)
        # 1 month from Oct 10 = Nov 9 (inclusive)
        assert end == date(2024, 11, 9)

    def test_three_months_basic(self):
        start = date(2024, 10, 10)
        end = calculate_end_date(start, 3)
        assert end == date(2025, 1, 9)

    def test_six_months_basic(self):
        start = date(2024, 1, 1)
        end = calculate_end_date(start, 6)
        assert end == date(2024, 6, 30)

    def test_month_end_jan_to_feb_leap_year(self):
        # Jan 31 + 1 month: target month is March, end day = 31-1 = 30
        # → Feb 29 is the result because nominal_day=30, clamped to Feb's last day (29 in 2024)
        start = date(2024, 1, 31)
        end = calculate_end_date(start, 1)
        assert end == date(2024, 2, 29)

    def test_month_end_jan_to_feb_non_leap(self):
        # Jan 31 + 1 month: nominal end day = 30, clamped to Feb 28 (2023, non-leap)
        start = date(2023, 1, 31)
        end = calculate_end_date(start, 1)
        assert end == date(2023, 2, 28)

    def test_month_end_march_31_three_months(self):
        # Mar 31 + 3 months → target June, nominal day = 30, June has 30 days → Jun 30
        start = date(2024, 3, 31)
        end = calculate_end_date(start, 3)
        assert end == date(2024, 6, 30)

    def test_year_boundary(self):
        start = date(2024, 11, 15)
        end = calculate_end_date(start, 1)
        assert end == date(2024, 12, 14)

    def test_invalid_duration_raises(self):
        with pytest.raises(ValueError):
            calculate_end_date(date(2024, 1, 1), 0)

    def test_invalid_negative_duration_raises(self):
        with pytest.raises(ValueError):
            calculate_end_date(date(2024, 1, 1), -1)


# ── Active status checks ──────────────────────────────────────────────────────

class TestIsSubscriptionActive:

    REF = date(2024, 10, 15)   # Fixed "today" for tests

    def test_active_subscription(self):
        assert is_subscription_active(
            date(2024, 10, 1), date(2024, 10, 31), "active", self.REF
        ) is True

    def test_expired_subscription(self):
        assert is_subscription_active(
            date(2024, 9, 1), date(2024, 9, 30), "active", self.REF
        ) is False

    def test_future_subscription_not_yet_started(self):
        assert is_subscription_active(
            date(2024, 10, 20), date(2024, 11, 19), "active", self.REF
        ) is False

    def test_cancelled_subscription_is_not_active(self):
        assert is_subscription_active(
            date(2024, 10, 1), date(2024, 10, 31), "cancelled", self.REF
        ) is False

    def test_boundary_first_day(self):
        # Reference = start date exactly
        assert is_subscription_active(
            self.REF, date(2024, 11, 14), "active", self.REF
        ) is True

    def test_boundary_last_day(self):
        # Reference = end date exactly
        assert is_subscription_active(
            date(2024, 9, 15), self.REF, "active", self.REF
        ) is True

    def test_expired_stored_status_but_dates_active(self):
        # Stored status = 'expired' but dates say active → active (dates win for non-cancelled)
        assert is_subscription_active(
            date(2024, 10, 1), date(2024, 10, 31), "expired", self.REF
        ) is True


# ── Expiring soon ─────────────────────────────────────────────────────────────

class TestIsExpiringSoon:

    REF = date(2024, 10, 15)

    def test_expires_today(self):
        assert is_expiring_soon(self.REF, 7, self.REF) is True

    def test_expires_in_7_days(self):
        assert is_expiring_soon(self.REF + timedelta(days=7), 7, self.REF) is True

    def test_expires_in_8_days_not_soon(self):
        assert is_expiring_soon(self.REF + timedelta(days=8), 7, self.REF) is False

    def test_already_expired(self):
        assert is_expiring_soon(self.REF - timedelta(days=1), 7, self.REF) is False


# ── Days remaining ────────────────────────────────────────────────────────────

class TestDaysRemaining:

    REF = date(2024, 10, 15)

    def test_7_days_remaining(self):
        assert days_remaining(self.REF + timedelta(days=7), self.REF) == 7

    def test_expired_returns_zero(self):
        assert days_remaining(self.REF - timedelta(days=1), self.REF) == 0

    def test_expires_today_returns_zero(self):
        assert days_remaining(self.REF, self.REF) == 0


# ── Current month range ───────────────────────────────────────────────────────

class TestCurrentMonthRange:

    def test_october_range(self):
        first, last = current_month_range(date(2024, 10, 15))
        assert first == date(2024, 10, 1)
        assert last  == date(2024, 10, 31)

    def test_february_leap_year(self):
        first, last = current_month_range(date(2024, 2, 10))
        assert first == date(2024, 2, 1)
        assert last  == date(2024, 2, 29)

    def test_february_non_leap(self):
        first, last = current_month_range(date(2023, 2, 10))
        assert first == date(2023, 2, 1)
        assert last  == date(2023, 2, 28)

    def test_december_range(self):
        first, last = current_month_range(date(2024, 12, 1))
        assert first == date(2024, 12, 1)
        assert last  == date(2024, 12, 31)
