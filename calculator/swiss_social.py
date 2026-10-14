"""Hypothetical Swiss social security: AHV/IV/EO + ALV (spec T12, exclude BVG).

Employee contributions 2026:
  * AHV/IV/EO combined = 5.3% of salary (AHV 4.35 + IV 0.70 + EO 0.25);
    **no ceiling** - every franc of salary is liable.
  * ALV (unemployment insurance) = 1.1% of salary, capped at the annual
    insured ceiling of CHF 148,200.

Occupational pension (BVG / 2nd pillar) is deliberately excluded (spec T12).
Sources: reference/sources.py (AHV/IV and ALV entries).
"""
from dataclasses import dataclass
from decimal import Decimal

from .rounding import dec

AHV_IV_EO_RATE = Decimal("0.053")
ALV_RATE = Decimal("0.011")
ALV_CEILING = Decimal("148200")  # CHF per year (12 x 12,350)


@dataclass(frozen=True)
class SwissSocial:
    ahv_iv_eo: Decimal
    alv: Decimal
    alv_base: Decimal
    total: Decimal


def compute_swiss_social(employment_income):
    """Employee AHV/IV/EO + ALV on ``employment_income`` (CHF, annual)."""
    income = dec(employment_income)
    if income < 0:
        raise ValueError("employment income must not be negative")

    ahv = AHV_IV_EO_RATE * income
    alv_base = min(income, ALV_CEILING)
    alv = ALV_RATE * alv_base

    return SwissSocial(
        ahv_iv_eo=ahv,
        alv=alv,
        alv_base=alv_base,
        total=ahv + alv,
    )
