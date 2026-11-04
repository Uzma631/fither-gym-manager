"""
tests/test_payment_calculations.py — Unit tests for payment and balance logic.

Run with:  python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from decimal import Decimal
from utils.money_utils import to_decimal, outstanding_balance, format_pkr
from utils.validators import validate_payment_amount


# ── to_decimal ────────────────────────────────────────────────────────────────

class TestToDecimal:

    def test_from_int(self):
        assert to_decimal(2500) == Decimal("2500.00")

    def test_from_float(self):
        # Floating point should be converted correctly via str()
        result = to_decimal(2500.50)
        assert result == Decimal("2500.50")

    def test_from_string(self):
        assert to_decimal("6500.00") == Decimal("6500.00")

    def test_from_decimal(self):
        assert to_decimal(Decimal("11000.00")) == Decimal("11000.00")

    def test_none_returns_zero(self):
        assert to_decimal(None) == Decimal("0.00")

    def test_rounding_half_up(self):
        # 2500.005 rounds to 2500.01
        assert to_decimal("2500.005") == Decimal("2500.01")


# ── outstanding_balance ───────────────────────────────────────────────────────

class TestOutstandingBalance:

    def test_full_payment_zero_balance(self):
        bal = outstanding_balance("2500.00", "2500.00")
        assert bal == Decimal("0.00")

    def test_partial_payment(self):
        bal = outstanding_balance("6500.00", "3000.00")
        assert bal == Decimal("3500.00")

    def test_no_payment(self):
        bal = outstanding_balance("2500.00", "0")
        assert bal == Decimal("2500.00")

    def test_overpayment_clamped_to_zero(self):
        # Should never happen (validation prevents it), but guard is here
        bal = outstanding_balance("2500.00", "3000.00")
        assert bal == Decimal("0.00")

    def test_large_amounts(self):
        bal = outstanding_balance("11000.00", "5500.00")
        assert bal == Decimal("5500.00")


# ── format_pkr ────────────────────────────────────────────────────────────────

class TestFormatPkr:

    def test_basic_format(self):
        assert format_pkr("2500") == "Rs 2,500.00"

    def test_large_amount(self):
        assert format_pkr("11000") == "Rs 11,000.00"

    def test_zero(self):
        assert format_pkr("0") == "Rs 0.00"

    def test_decimal_amount(self):
        assert format_pkr("2500.50") == "Rs 2,500.50"


# ── Payment amount validation (integration with business rules) ───────────────

class TestPaymentAmountBusinessRules:

    def test_full_payment_accepted(self):
        ok, msg = validate_payment_amount(Decimal("2500.00"), Decimal("2500.00"))
        assert ok is True

    def test_partial_payment_accepted(self):
        ok, msg = validate_payment_amount(Decimal("1000.00"), Decimal("2500.00"))
        assert ok is True

    def test_penny_payment_accepted(self):
        ok, msg = validate_payment_amount(Decimal("0.01"), Decimal("100.00"))
        assert ok is True

    def test_overpayment_rejected_with_message(self):
        ok, msg = validate_payment_amount(Decimal("3000.00"), Decimal("2500.00"))
        assert ok is False
        assert "3,000.00" in msg or "3000" in msg
        assert "2,500.00" in msg or "2500" in msg

    def test_zero_payment_rejected(self):
        ok, msg = validate_payment_amount(Decimal("0.00"), Decimal("2500.00"))
        assert ok is False

    def test_zero_outstanding_balance_rejects_any_payment(self):
        ok, msg = validate_payment_amount(Decimal("100.00"), Decimal("0.00"))
        assert ok is False

    def test_negative_amount_rejected(self):
        ok, msg = validate_payment_amount(Decimal("-100.00"), Decimal("2500.00"))
        assert ok is False

    # Subscription with no payments — balance should equal full agreed fee
    def test_no_payments_balance_equals_agreed_fee(self):
        agreed_fee = Decimal("6500.00")
        total_paid = Decimal("0.00")
        balance = outstanding_balance(agreed_fee, total_paid)
        assert balance == agreed_fee

    # After two partial payments
    def test_multiple_partial_payments(self):
        agreed_fee = Decimal("6500.00")
        payment1   = Decimal("3000.00")
        payment2   = Decimal("2000.00")
        total_paid = payment1 + payment2
        balance = outstanding_balance(agreed_fee, total_paid)
        assert balance == Decimal("1500.00")

    # Member with no subscriptions — no balance concept; check we don't crash
    def test_no_subscription_means_no_balance(self):
        # outstanding_balance should safely return 0 if both inputs are 0
        bal = outstanding_balance("0", "0")
        assert bal == Decimal("0.00")
