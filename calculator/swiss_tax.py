"""Hypothetical Swiss income tax: federal + Zurich cantonal + communal.

The employee is single, resident in the city of Zurich and pays no church tax
(spec T11). The tax that *would* have been due in Switzerland is computed from
the official 2026 tariffs:

  * Federal direct tax (DBG) single tariff - ESTV Form 58c 2026.
  * Zurich cantonal tariff, section 35 (1) "Grundtarif" - ZH StG 631.1.
  * Zurich Steuerfuss 2026: canton 95% + city 119% of the "einfache
    Staatssteuer" (simple tax); church tax is excluded.

The DBG tariff is applied as cumulative anchors with linear interpolation
between the published points (exact at every published point). Above
CHF 793,900 the federal tax is a uniform 11.5% of the whole taxable income,
as stated on Form 58c.
"""
from dataclasses import dataclass
from decimal import Decimal

from .rounding import dec

# --- Federal direct tax (DBG), single persons, 2026 -------------------------
# (taxable income, cumulative tax at that income)
FEDERAL_SINGLE_ANCHORS = (
    (Decimal("0"), Decimal("0")),
    (Decimal("15200"), Decimal("0")),
    (Decimal("33200"), Decimal("138.60")),
    (Decimal("43400"), Decimal("228.36")),
    (Decimal("58000"), Decimal("612.00")),
    (Decimal("76200"), Decimal("1152.50")),
    (Decimal("82100"), Decimal("1502.95")),
    (Decimal("108900"), Decimal("3271.75")),
    (Decimal("141500"), Decimal("6140.55")),
    (Decimal("185100"), Decimal("10936.55")),
    (Decimal("793900"), Decimal("91298.15")),
)
FEDERAL_TOP_INCOME = FEDERAL_SINGLE_ANCHORS[-1][0]
FEDERAL_TOP_RATE = Decimal("0.115")  # uniform above CHF 793,900

# --- Zurich cantonal "Grundtarif" (section 35 (1)) --------------------------
# (bracket width, marginal rate). The first entry is the tax-free amount.
ZH_GRUNDTARIF = (
    ("width", Decimal("7000"), Decimal("0.00")),
    ("width", Decimal("5000"), Decimal("0.02")),
    ("width", Decimal("4800"), Decimal("0.03")),
    ("width", Decimal("8000"), Decimal("0.04")),
    ("width", Decimal("9700"), Decimal("0.05")),
    ("width", Decimal("11200"), Decimal("0.06")),
    ("width", Decimal("13100"), Decimal("0.07")),
    ("width", Decimal("17600"), Decimal("0.08")),
    ("width", Decimal("34000"), Decimal("0.09")),
    ("width", Decimal("33700"), Decimal("0.10")),
    ("width", Decimal("53300"), Decimal("0.11")),
    ("width", Decimal("69300"), Decimal("0.12")),
)
ZH_TOP_RATE = Decimal("0.13")

# --- Zurich Steuerfuss 2026 (fraction of the simple tax) --------------------
ZH_CANTON_STEUERFUSS = Decimal("0.95")
ZH_CITY_STEUERFUSS = Decimal("1.19")
ZH_COMBINED_FACTOR = ZH_CANTON_STEUERFUSS + ZH_CITY_STEUERFUSS  # 2.14


@dataclass(frozen=True)
class SwissDeductionPolicy:
    """Deductions applied to gross employment income to reach the tax base.

    These are *estimates* used only for the hypothetical home-country tax; the
    figures are disclosed as assumptions in the UI (spec E13). No children and
    no church membership, so neither the child deduction (DBG/StG) nor church
    tax applies.
    """

    professional_expenses: Decimal = Decimal("4000")
    insurance_premium_deduction: Decimal = Decimal("2900")
    label: str = (
        "Estimated standard deductions (professional expenses and insurance "
        "premiums); health-insurance premiums and pillar 3a are not modelled."
    )


DEFAULT_DEDUCTION_POLICY = SwissDeductionPolicy()


def federal_tax(taxable_income):
    """Federal direct tax (DBG single tariff) on ``taxable_income`` (CHF)."""
    taxable_income = dec(taxable_income)
    if taxable_income <= 0:
        return Decimal("0")

    if taxable_income > FEDERAL_TOP_INCOME:
        return FEDERAL_TOP_RATE * taxable_income

    for (x0, y0), (x1, y1) in zip(FEDERAL_SINGLE_ANCHORS, FEDERAL_SINGLE_ANCHORS[1:]):
        if x0 <= taxable_income <= x1:
            if x1 == x0:
                return y0
            slope = (y1 - y0) / (x1 - x0)
            return y0 + slope * (taxable_income - x0)
    # taxable_income between 0 and the first anchor (already handled by x0=0)
    return Decimal("0")


def zh_simple_tax(taxable_income):
    """Zurich cantonal 'einfache Staatssteuer' (section 35 (1) Grundtarif)."""
    taxable_income = dec(taxable_income)
    if taxable_income <= 0:
        return Decimal("0")

    tax = Decimal("0")
    remaining = taxable_income
    for _kind, width, rate in ZH_GRUNDTARIF:
        slice_ = min(remaining, width)
        tax += rate * slice_
        remaining -= slice_
        if remaining <= 0:
            return tax
    # income above the last bracket (CHF 266,700)
    tax += ZH_TOP_RATE * remaining
    return tax


def zh_total_tax(taxable_income):
    """Cantonal + communal Zurich income tax (no church tax)."""
    return zh_simple_tax(taxable_income) * ZH_COMBINED_FACTOR


@dataclass(frozen=True)
class SwissTax:
    taxable_income: Decimal
    federal: Decimal
    cantonal_communal: Decimal
    simple_cantonal_tax: Decimal
    total: Decimal


def compute_swiss_tax(
    employment_income,
    social_security_total,
    policy=DEFAULT_DEDUCTION_POLICY,
):
    """Hypothetical Swiss total income tax on ``employment_income`` (CHF).

    ``social_security_total`` is the employee AHV/IV/EO + ALV contribution,
    which is deductible from income.
    """
    employment_income = dec(employment_income)
    social_security_total = dec(social_security_total)

    taxable = (
        employment_income
        - social_security_total
        - policy.professional_expenses
        - policy.insurance_premium_deduction
    )
    taxable = max(Decimal("0"), taxable)

    federal = federal_tax(taxable)
    simple = zh_simple_tax(taxable)
    cantonal_communal = simple * ZH_COMBINED_FACTOR

    return SwissTax(
        taxable_income=taxable,
        federal=federal,
        cantonal_communal=cantonal_communal,
        simple_cantonal_tax=simple,
        total=federal + cantonal_communal,
    )
