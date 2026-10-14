"""Employee Class 1 National Insurance (memo line only).

The employee's own NIC is shown for transparency. It is **not** deducted from
the net home pay target ``I`` and is deliberately not grossed up, because the
specification grosses up UK income tax only (see RESEARCH.md, assumption A6).
"""
from decimal import Decimal

from .rounding import dec

PRIMARY_THRESHOLD = Decimal("12570")  # GBP per year (2026/27)
UPPER_EARNINGS_LIMIT = Decimal("50270")
MAIN_RATE = Decimal("0.08")
UPPER_RATE = Decimal("0.02")


def employee_class1_nic(earnings):
    """Employee Class 1 NIC on ``earnings`` (GBP, annual)."""
    earnings = dec(earnings)
    if earnings <= PRIMARY_THRESHOLD:
        return Decimal("0")
    main = min(earnings, UPPER_EARNINGS_LIMIT) - PRIMARY_THRESHOLD
    nic = MAIN_RATE * main
    if earnings > UPPER_EARNINGS_LIMIT:
        nic += UPPER_RATE * (earnings - UPPER_EARNINGS_LIMIT)
    return nic
