"""
utils/validators.py — Input validation helpers for FitHer Gym Manager.

All validation functions return (is_valid: bool, error_message: str).
An empty error_message means the input is valid.
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


# ---------------------------------------------------------------------------
# Phone number validation
# Accepts Pakistani mobile numbers in these formats:
#   03xxxxxxxxx  (11 digits starting with 03)
#   +923xxxxxxxxx
#   923xxxxxxxxx
# Also accepts plain local formats with spaces/dashes which are normalised.
# ---------------------------------------------------------------------------
_PK_PHONE_RE = re.compile(
    r"^(?:\+92|92|0)3[0-9]{9}$"
)


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate a Pakistani mobile phone number."""
    if not phone or not phone.strip():
        return False, "Phone number is required."
    cleaned = re.sub(r"[\s\-()]", "", phone.strip())
    if not _PK_PHONE_RE.match(cleaned):
        return False, (
            "Please enter a valid Pakistani mobile number "
            "(e.g. 03001234567 or +923001234567)."
        )
    return True, ""


def normalise_phone(phone: str) -> str:
    """Strip spaces/dashes and return a clean phone string."""
    return re.sub(r"[\s\-()]", "", phone.strip())


# ---------------------------------------------------------------------------
# Name validation
# ---------------------------------------------------------------------------

def validate_full_name(name: str) -> tuple[bool, str]:
    """Validate that a full name is present and reasonable."""
    if not name or not name.strip():
        return False, "Full name is required."
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters."
    if len(name.strip()) > 150:
        return False, "Name must not exceed 150 characters."
    # Allow letters, spaces, dots, apostrophes, hyphens (common in names)
    if not re.match(r"^[A-Za-z\u0600-\u06FF .'\-]+$", name.strip()):
        return False, "Name contains invalid characters."
    return True, ""


# ---------------------------------------------------------------------------
# Date validation
# ---------------------------------------------------------------------------

def validate_date_not_future(d: date, field_name: str = "Date") -> tuple[bool, str]:
    """Validate that a date is not in the future."""
    if d > date.today():
        return False, f"{field_name} cannot be in the future."
    return True, ""


def validate_date_not_past_too_far(d: date, years: int = 10) -> tuple[bool, str]:
    """Validate that a date is not unreasonably far in the past."""
    from datetime import timedelta
    limit = date.today().replace(year=date.today().year - years)
    if d < limit:
        return False, f"Date is too far in the past (more than {years} years ago)."
    return True, ""


# ---------------------------------------------------------------------------
# Money / amount validation
# ---------------------------------------------------------------------------

def validate_positive_decimal(value: str | float | Decimal, field_name: str = "Amount") -> tuple[bool, str]:
    """Validate that a value is a positive decimal number."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return False, f"{field_name} must be a valid number."
    if d <= 0:
        return False, f"{field_name} must be greater than zero."
    if d > Decimal("9999999.99"):
        return False, f"{field_name} seems unrealistically large."
    return True, ""


def validate_payment_amount(
    payment_amount: Decimal,
    outstanding_balance: Decimal,
    field_name: str = "Payment amount",
) -> tuple[bool, str]:
    """
    Ensure a payment does not exceed the outstanding balance.
    Returns an error if payment_amount > outstanding_balance.
    """
    ok, msg = validate_positive_decimal(payment_amount, field_name)
    if not ok:
        return False, msg
    if outstanding_balance <= Decimal("0"):
        return False, "This subscription has no outstanding balance. No payment is needed."
    if payment_amount > outstanding_balance:
        return (
            False,
            f"{field_name} (Rs {payment_amount:,.2f}) exceeds the outstanding balance "
            f"(Rs {outstanding_balance:,.2f}). Please enter an amount equal to or less "
            f"than the balance."
        )
    return True, ""


# ---------------------------------------------------------------------------
# Notes / text
# ---------------------------------------------------------------------------

def validate_notes(notes: str, max_length: int = 500) -> tuple[bool, str]:
    """Optional field — only check length."""
    if notes and len(notes) > max_length:
        return False, f"Notes must not exceed {max_length} characters."
    return True, ""
