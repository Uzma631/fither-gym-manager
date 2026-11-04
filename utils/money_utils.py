"""
utils/money_utils.py — Money formatting helpers for FitHer Gym Manager.

All monetary values are stored as DECIMAL in MySQL and handled as
Python Decimal objects to avoid floating-point rounding errors.
"""

from decimal import Decimal, ROUND_HALF_UP


TWO_PLACES = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """
    Convert any numeric-like value to a Decimal rounded to 2 decimal places.
    Accepts int, float, str, or Decimal.
    """
    if value is None:
        return Decimal("0.00")
    try:
        return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")


def format_pkr(amount) -> str:
    """Format a monetary amount as a Pakistani Rupee string, e.g. 'Rs 2,500.00'."""
    d = to_decimal(amount)
    return f"Rs {d:,.2f}"


def outstanding_balance(agreed_fee, total_paid) -> Decimal:
    """
    Calculate the outstanding balance for a subscription.

    outstanding = agreed_fee - total_paid
    Never returns a negative value (overpayment is clamped to 0).
    """
    fee  = to_decimal(agreed_fee)
    paid = to_decimal(total_paid)
    balance = fee - paid
    return balance if balance > Decimal("0") else Decimal("0.00")
