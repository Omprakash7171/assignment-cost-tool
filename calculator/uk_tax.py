"""UK income tax, 2026/27 rates (applied to both assignment years per spec T10).

Source: GOV.UK "Income Tax rates and Personal Allowances" and
"Rates and thresholds for employers 2026 to 2027" (see reference/sources.py).

Bands are applied to *taxable income* (total income minus the personal
allowance). The personal allowance is reduced by GBP 1 for every GBP 2 of
income above GBP 100,000, reaching zero at GBP 125,140.
"""
from decimal import Decimal

from .rounding import dec

PERSONAL_ALLOWANCE = Decimal("12570")
PA_TAPER_THRESHOLD = Decimal("100000")
PA_TAPER_LENGTH = Decimal("125140")  # income at which the PA is fully withdrawn

BASIC_RATE = Decimal("0.20")
BASIC_BAND = Decimal("37700")        # width of the basic-rate band (taxable)

HIGHER_RATE = Decimal("0.40")
ADDITIONAL_RATE = Decimal("0.45")
ADDITIONAL_THRESHOLD = Decimal("125140")  # taxable income above which 45% applies


def personal_allowance_for(income):
    """Personal allowance after the GBP 100,000 taper."""
    income = dec(income)
    if income <= PA_TAPER_THRESHOLD:
        return PERSONAL_ALLOWANCE
    reduction = (income - PA_TAPER_THRESHOLD) / 2
    return max(Decimal("0"), PERSONAL_ALLOWANCE - reduction)


def compute_uk_tax(income):
    """Progressive UK income tax on ``income`` (gross, before tax)."""
    income = dec(income)
    if income <= 0:
        return Decimal("0")

    allowance = personal_allowance_for(income)
    taxable = max(Decimal("0"), income - allowance)

    tax = Decimal("0")

    basic = min(taxable, BASIC_BAND)
    tax += BASIC_RATE * basic

    if taxable > BASIC_BAND:
        higher_slice = min(taxable, ADDITIONAL_THRESHOLD) - BASIC_BAND
        tax += HIGHER_RATE * higher_slice

    if taxable > ADDITIONAL_THRESHOLD:
        tax += ADDITIONAL_RATE * (taxable - ADDITIONAL_THRESHOLD)

    return tax
