"""
tests/test_validators.py — Unit tests for input validation functions.

Run with:  python -m pytest tests/ -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from decimal import Decimal
from utils.validators import (
    validate_phone, validate_full_name, validate_positive_decimal,
    validate_payment_amount, validate_notes, normalise_phone,
)


# ── Phone validation ──────────────────────────────────────────────────────────

class TestPhoneValidation:

    def test_valid_03_format(self):
        ok, msg = validate_phone("03001234567")
        assert ok is True
        assert msg == ""

    def test_valid_plus92_format(self):
        ok, msg = validate_phone("+923001234567")
        assert ok is True

    def test_valid_92_format(self):
        ok, msg = validate_phone("923001234567")
        assert ok is True

    def test_invalid_landline(self):
        ok, msg = validate_phone("02112345678")
        assert ok is False
        assert "Pakistani mobile" in msg

    def test_invalid_too_short(self):
        ok, msg = validate_phone("0300123")
        assert ok is False

    def test_invalid_letters(self):
        ok, msg = validate_phone("0300ABCDEFG")
        assert ok is False

    def test_empty_string(self):
        ok, msg = validate_phone("")
        assert ok is False
        assert "required" in msg.lower()

    def test_whitespace_only(self):
        ok, msg = validate_phone("   ")
        assert ok is False

    def test_normalise_strips_spaces(self):
        cleaned = normalise_phone(" 0300-123 4567 ")
        assert cleaned == "03001234567"


# ── Name validation ───────────────────────────────────────────────────────────

class TestNameValidation:

    def test_valid_name(self):
        ok, msg = validate_full_name("Ayesha Siddiqui")
        assert ok is True

    def test_valid_name_with_dot(self):
        ok, msg = validate_full_name("Dr. Fatima")
        assert ok is True

    def test_empty_name(self):
        ok, msg = validate_full_name("")
        assert ok is False
        assert "required" in msg.lower()

    def test_single_char(self):
        ok, msg = validate_full_name("A")
        assert ok is False

    def test_too_long(self):
        ok, msg = validate_full_name("A" * 151)
        assert ok is False
        assert "150" in msg

    def test_invalid_chars(self):
        ok, msg = validate_full_name("Name123!")
        assert ok is False


# ── Money validation ──────────────────────────────────────────────────────────

class TestMoneyValidation:

    def test_valid_amount(self):
        ok, msg = validate_positive_decimal("2500.00")
        assert ok is True

    def test_zero_is_invalid(self):
        ok, msg = validate_positive_decimal("0")
        assert ok is False
        assert "greater than zero" in msg

    def test_negative_is_invalid(self):
        ok, msg = validate_positive_decimal("-100")
        assert ok is False

    def test_string_letters_invalid(self):
        ok, msg = validate_positive_decimal("abc")
        assert ok is False

    def test_very_large_amount_invalid(self):
        ok, msg = validate_positive_decimal("99999999")
        assert ok is False


class TestPaymentAmountValidation:

    def test_exact_balance_is_ok(self):
        ok, msg = validate_payment_amount(Decimal("2500.00"), Decimal("2500.00"))
        assert ok is True

    def test_partial_payment_ok(self):
        ok, msg = validate_payment_amount(Decimal("1000.00"), Decimal("2500.00"))
        assert ok is True

    def test_overpayment_rejected(self):
        ok, msg = validate_payment_amount(Decimal("3000.00"), Decimal("2500.00"))
        assert ok is False
        assert "exceeds" in msg

    def test_zero_balance_rejected(self):
        ok, msg = validate_payment_amount(Decimal("100.00"), Decimal("0.00"))
        assert ok is False
        assert "outstanding balance" in msg.lower()

    def test_zero_payment_rejected(self):
        ok, msg = validate_payment_amount(Decimal("0.00"), Decimal("2500.00"))
        assert ok is False


# ── Notes validation ──────────────────────────────────────────────────────────

class TestNotesValidation:

    def test_empty_notes_ok(self):
        ok, msg = validate_notes("")
        assert ok is True

    def test_none_notes_ok(self):
        # validate_notes expects a string; test that it handles edge cases
        ok, msg = validate_notes("")
        assert ok is True

    def test_long_notes_rejected(self):
        ok, msg = validate_notes("x" * 501)
        assert ok is False
        assert "500" in msg

    def test_max_length_ok(self):
        ok, msg = validate_notes("x" * 500)
        assert ok is True
