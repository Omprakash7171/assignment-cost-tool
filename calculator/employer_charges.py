"""Employer UK charges: Class 1 and Class 1A National Insurance.

Documented assumptions (spec E12):
  * Employer Class 1 NIC = 15% on gross Class 1 earnings above the secondary
    threshold of GBP 5,000/year. There is no upper cap for employer NIC.
  * Employer Class 1A NIC = 15% on the cash equivalent of benefits in kind.
  * The Employment Allowance is **not** applied (conservative; the employer is
    a UK subsidiary whose NIC bill is assumed to exceed the GBP 100,000
    eligibility ceiling).
  * The Apprenticeship Levy is **not** applied (pay bill assumed below the
    GBP 3m threshold).
"""
from decimal import Decimal

from .rounding import dec

EMPLOYER_NIC_RATE = Decimal("0.15")
SECONDARY_THRESHOLD = Decimal("5000")  # GBP per year (2026/27)
CLASS1A_NIC_RATE = Decimal("0.15")

ASSUMPTIONS = (
    "Employer Class 1 NIC at 15% above the GBP 5,000 secondary threshold.",
    "Employer Class 1A NIC at 15% on benefits in kind.",
    "Employment Allowance not applied (conservative).",
    "Apprenticeship Levy not applied (pay bill below threshold).",
)


def employer_class1_nic(class1_earnings):
    """Employer Class 1 NIC on ``class1_earnings`` (GBP, annual)."""
    earnings = dec(class1_earnings)
    return EMPLOYER_NIC_RATE * max(Decimal("0"), earnings - SECONDARY_THRESHOLD)


def class1a_nic(benefits_in_kind):
    """Employer Class 1A NIC on the total BIK cash equivalent (GBP)."""
    return CLASS1A_NIC_RATE * max(Decimal("0"), dec(benefits_in_kind))
