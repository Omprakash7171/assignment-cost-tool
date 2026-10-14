"""Input/output dataclasses for the calculation engine.

These are plain dataclasses (no ORM). ``Decimal`` is used for every money
value so that precision is preserved end to end.
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional, Tuple


# --- Benefit classification -------------------------------------------------
TAXABLE_CASH = "TAXABLE_CASH"
BIK = "BIK"
NOT_TAXABLE = "NOT_TAXABLE"
DEDUCTION = "DEDUCTION"

CLASSIFICATION_LABELS = {
    TAXABLE_CASH: "Taxable cash",
    BIK: "Benefit in kind",
    NOT_TAXABLE: "Not taxable",
    DEDUCTION: "Deduction",
}


@dataclass(frozen=True)
class Benefit:
    """A single assignment benefit as supplied by the user.

    ``amount`` is expressed in ``currency`` (``GBP`` or ``CHF``). The
    classification is a *documented modelling decision*, not a user input
    (spec F05/E12).
    """

    label: str
    amount: Decimal
    currency: str
    classification: str
    year: int
    recurring: bool = False
    note: str = ""
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AssignmentInputs:
    """Complete, validated input for one assignment."""

    # Locations and period
    home_country: str = "Switzerland"
    home_city: str = "Zurich"
    host_country: str = "United Kingdom"
    host_city: str = "London"
    start_date: date = date(2026, 4, 6)
    end_date: date = date(2028, 4, 5)

    # Employee
    nationality: str = "Swiss"
    marital_status: str = "single"
    children: int = 0
    uk_tax_resident_year1: bool = True
    uk_tax_resident_year2: bool = True

    # Pay (home currency, CHF)
    base_salary_home: Decimal = Decimal("150000")
    bonus_home: Decimal = Decimal("20000")

    # FX: CHF per 1 GBP (editable, applied to both years by default)
    fx_gbp_to_home: Decimal = Decimal("1.10")

    # Benefits
    housing_gbp_month: Decimal = Decimal("3000")
    relocation_home: Decimal = Decimal("5000")   # CHF, year 1 only
    moving_gbp: Decimal = Decimal("6000")        # GBP, year 1 only
    temp_accom_gbp: Decimal = Decimal("4000")    # GBP, year 1 only

    # UK rate year (spec: 2026/27 rates used for both years)
    uk_tax_year_label: str = "2026/27"

    # Employer social security position (see RESEARCH.md, T13)
    employer_social_security_uk: bool = True


@dataclass(frozen=True)
class YearBenefit:
    """A benefit resolved to a single tax year with GBP and native amounts."""

    label: str
    classification: str
    currency: str
    amount_native: Decimal
    amount_gbp: Decimal
    year: int
    derivation: str = ""
    note: str = ""
    source_ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MoneyLine:
    """One rendered row in sections A/B/C/D."""

    label: str
    amount: Decimal                 # primary amount (GBP unless currency != GBP)
    section: str = ""
    year: int = 0
    currency: str = "GBP"
    classification: str = ""
    derivation: str = ""
    source_ids: Tuple[str, ...] = ()


@dataclass
class YearResult:
    """All figures for one UK tax year."""

    year: int
    year_label: str

    section_a: list = field(default_factory=list)
    section_b: list = field(default_factory=list)
    section_c: list = field(default_factory=list)
    section_d: list = field(default_factory=list)
    benefits: list = field(default_factory=list)  # YearBenefit records

    home_gross_pay_home: Decimal = Decimal("0")   # CHF
    home_gross_pay_gbp: Decimal = Decimal("0")    # GBP
    swiss_social_home: Decimal = Decimal("0")     # CHF
    swiss_tax_home: Decimal = Decimal("0")        # CHF
    net_home_pay_home: Decimal = Decimal("0")     # CHF
    net_home_pay_gbp: Decimal = Decimal("0")      # GBP

    taxable_benefits_gbp: Decimal = Decimal("0")
    net_target_i_gbp: Decimal = Decimal("0")      # I
    employer_tax_t_gbp: Decimal = Decimal("0")    # T
    gross_uk_pay_gbp: Decimal = Decimal("0")      # I + T
    employer_nic_gbp: Decimal = Decimal("0")
    class1a_nic_gbp: Decimal = Decimal("0")
    benefit_cost_gbp: Decimal = Decimal("0")
    total_employer_cost_gbp: Decimal = Decimal("0")


@dataclass
class AssignmentResult:
    """Whole-assignment result across both tax years."""

    inputs: AssignmentInputs
    years: list = field(default_factory=list)
    total_employer_cost_gbp: Decimal = Decimal("0")
    total_home_pay_gbp: Decimal = Decimal("0")
    cost_multiple: Decimal = Decimal("0")
    assumptions: list = field(default_factory=list)
    gross_up_history: dict = field(default_factory=dict)
    swiss_detail: dict = field(default_factory=dict)
