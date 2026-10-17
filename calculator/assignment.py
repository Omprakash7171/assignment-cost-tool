"""Per-year orchestration: assemble sections A-D and the headline totals.

Model (documented in docs/RESEARCH.md):

  GP  gross home pay (CHF)              = base salary + bonus
  SS  employee AHV/IV/EO + ALV (CHF)
  HT  hypothetical Swiss income tax (CHF)
  NP  net home pay (GBP)                = (GP - SS - HT) / fx
  B   taxable assignment benefits (GBP) = BIK + taxable cash
  I   net amount to keep the employee whole = NP + B
  T   employer-paid UK tax              solves T = UKTax(I + T)
  Gross UK pay = I + T

  Total employer cost = NP + benefits paid for + T + employer NIC + Class 1A.

The framework is a *net* cost model: the employer pays the employee their home
net pay, bears the UK tax that keeps them whole, provides the assignment
benefits, and pays the associated employer NICs.
"""
from decimal import Decimal

from .benefits import build_year_benefits, chf_to_gbp
from .employee_nic import employee_class1_nic
from .employer_charges import (
    ASSUMPTIONS as EMPLOYER_CHARGE_ASSUMPTIONS,
    class1a_nic,
    employer_class1_nic,
)
from .grossup import solve_gross_up
from .models import (
    BIK,
    TAXABLE_CASH,
    AssignmentResult,
    MoneyLine,
    YearBenefit,
    YearResult,
)
from .rounding import dec
from .swiss_social import compute_swiss_social
from .swiss_tax import DEFAULT_DEDUCTION_POLICY, compute_swiss_tax
from .uk_tax import compute_uk_tax
from .validation import validate_inputs

YEAR_LABELS = {1: "2026/27", 2: "2027/28"}

ASSUMPTIONS = (
    "UK 2026/27 rates and thresholds are applied to both assignment years "
    "(spec T10).",
    "The employee's own Class 1 NIC is shown as a memo only and is not "
    "grossed up or deducted from the net home-pay target.",
    "Hypothetical Swiss income tax is computed on salary + bonus in Zurich "
    "using the 2026 federal (Form 58c) and Zurich section 35 tariffs, with "
    "estimated standard deductions; the FTA/ZH calculators are the "
    "authoritative reference.",
    "The one-off foreign relocation allowance and moving/temporary-accommodation "
    "costs are treated as assignment benefits on the UK side, not as recurring "
    "home salary, so they do not enter the hypothetical Swiss tax base.",
    "Temporary accommodation is treated as a taxable benefit in kind "
    "(assumption; a temporary-workplace exemption may apply for up to 24 "
    "months).",
    "The employer-provided flat is a living-accommodation benefit in kind; its "
    "cash equivalent is taken equal to the rent paid.",
) + EMPLOYER_CHARGE_ASSUMPTIONS


def _run_year(inputs, year):
    fx = inputs.fx_gbp_to_home
    label = YEAR_LABELS.get(year, "year {0}".format(year))

    employment_income_home = dec(inputs.base_salary_home) + dec(inputs.bonus_home)
    social = compute_swiss_social(employment_income_home)
    swiss = compute_swiss_tax(
        employment_income_home,
        social.total,
        policy=DEFAULT_DEDUCTION_POLICY,
    )

    net_home_pay_home = employment_income_home - social.total - swiss.total
    net_home_pay_gbp = chf_to_gbp(net_home_pay_home, fx)

    benefits = build_year_benefits(inputs, year)
    benefit_cost_gbp = sum((b.amount_gbp for b in benefits), Decimal("0"))
    taxable_benefits_gbp = sum(
        (b.amount_gbp for b in benefits if b.classification in (TAXABLE_CASH, BIK)),
        Decimal("0"),
    )
    bik_gbp = sum(
        (b.amount_gbp for b in benefits if b.classification == BIK),
        Decimal("0"),
    )
    cash_taxable_gbp = sum(
        (b.amount_gbp for b in benefits if b.classification == TAXABLE_CASH),
        Decimal("0"),
    )

    # Net amount the employee must keep whole (spec E02).
    i_gbp = net_home_pay_gbp + taxable_benefits_gbp

    # Employer-paid UK income tax via iterative gross-up (spec E03/E06).
    gross_up = solve_gross_up(i_gbp, compute_uk_tax)
    tax_t = gross_up.tax
    gross_uk_pay = i_gbp + tax_t

    # Employer NIC: Class 1 on cash earnings (gross pay minus in-kind benefits);
    # Class 1A on benefits in kind.
    class1_earnings = gross_uk_pay - bik_gbp
    employer_nic = employer_class1_nic(class1_earnings)
    class1a = class1a_nic(bik_gbp)

    total_cost = (
        net_home_pay_gbp
        + benefit_cost_gbp
        + tax_t
        + employer_nic
        + class1a
    )

    # --- Sections -----------------------------------------------------------
    section_a = [
        MoneyLine(
            label="Base salary",
            amount=chf_to_gbp(inputs.base_salary_home, fx),
            section="A", year=year,
            derivation="CHF {0} / {1}".format(inputs.base_salary_home, fx),
        ),
        MoneyLine(
            label="Bonus",
            amount=chf_to_gbp(inputs.bonus_home, fx),
            section="A", year=year,
            derivation="CHF {0} / {1}".format(inputs.bonus_home, fx),
        ),
        MoneyLine(
            label="Gross home pay",
            amount=chf_to_gbp(employment_income_home, fx),
            section="A", year=year,
            derivation="CHF {0} / {1}".format(employment_income_home, fx),
        ),
        MoneyLine(
            label="Less: hypothetical Swiss income tax",
            amount=-chf_to_gbp(swiss.total, fx),
            section="A", year=year,
            derivation="Federal + Zurich cantonal/communal on CHF {0}".format(
                swiss.taxable_income
            ),
            source_ids=("estv_58c_2026", "zh_stg_35", "zh_stgb_34_1"),
        ),
        MoneyLine(
            label="Less: hypothetical Swiss social security",
            amount=-chf_to_gbp(social.total, fx),
            section="A", year=year,
            derivation="AHV/IV/EO 5.3% + ALV 1.1% (capped) on CHF {0}".format(
                employment_income_home
            ),
            source_ids=("ahv_iv_eo_2026", "alv_2026"),
        ),
        MoneyLine(
            label="Net home pay",
            amount=net_home_pay_gbp,
            section="A", year=year,
            derivation="(GP - Swiss tax - Swiss social security) / fx",
        ),
    ]

    section_b = [
        MoneyLine(
            label=b.label,
            amount=b.amount_gbp,
            section="B", year=year,
            currency=b.currency,
            classification=b.classification,
            derivation=b.derivation,
            source_ids=b.source_ids,
        )
        for b in benefits
    ]

    employee_nic = employee_class1_nic(class1_earnings)
    section_c = [
        MoneyLine(
            label="Employer-paid UK income tax (gross-up)",
            amount=tax_t,
            section="C", year=year,
            derivation="T = UKTax(I + T); converged in {0} iterations".format(
                gross_up.iterations
            ),
            source_ids=("hmrc_hs212", "hmrc_paye72028", "uk_income_tax_2026_27"),
        ),
        MoneyLine(
            label="Employer Class 1 NIC",
            amount=employer_nic,
            section="C", year=year,
            derivation="15% x (Class 1 earnings - GBP 5,000)",
            source_ids=("uk_employer_rates_2026_27",),
        ),
        MoneyLine(
            label="Employer Class 1A NIC",
            amount=class1a,
            section="C", year=year,
            derivation="15% x benefits in kind",
            source_ids=("uk_employer_rates_2026_27",),
        ),
        MoneyLine(
            label="Employee Class 1 NIC (memo, not grossed up)",
            amount=employee_nic,
            section="C", year=year,
            classification="MEMO",
            source_ids=("uk_employer_rates_2026_27",),
        ),
    ]

    section_d = [
        MoneyLine(
            label="Hypothetical Swiss income tax",
            amount=chf_to_gbp(swiss.total, fx),
            section="D", year=year,
            derivation="restates the deduction already applied in Section A",
            source_ids=("estv_58c_2026", "zh_stg_35"),
        ),
        MoneyLine(
            label="Hypothetical Swiss social security",
            amount=chf_to_gbp(social.total, fx),
            section="D", year=year,
            derivation="restates the deduction already applied in Section A",
            source_ids=("ahv_iv_eo_2026", "alv_2026"),
        ),
        MoneyLine(
            label="Effect: Swiss deductions reduce net home pay and hence the "
            "employer-paid UK tax",
            amount=-(chf_to_gbp(swiss.total + social.total, fx)),
            section="D", year=year,
            derivation="deductions no longer borne by the employee at home",
        ),
    ]

    result = YearResult(
        year=year,
        year_label=label,
        section_a=section_a,
        section_b=section_b,
        section_c=section_c,
        section_d=section_d,
        benefits=list(benefits),
        home_gross_pay_home=employment_income_home,
        home_gross_pay_gbp=chf_to_gbp(employment_income_home, fx),
        swiss_social_home=social.total,
        swiss_tax_home=swiss.total,
        net_home_pay_home=net_home_pay_home,
        net_home_pay_gbp=net_home_pay_gbp,
        taxable_benefits_gbp=taxable_benefits_gbp,
        net_target_i_gbp=i_gbp,
        employer_tax_t_gbp=tax_t,
        gross_uk_pay_gbp=gross_uk_pay,
        employer_nic_gbp=employer_nic,
        class1a_nic_gbp=class1a,
        benefit_cost_gbp=benefit_cost_gbp,
        total_employer_cost_gbp=total_cost,
    )

    swiss_detail = {
        "employment_income_home": employment_income_home,
        "social_total_home": social.total,
        "ahv_iv_eo_home": social.ahv_iv_eo,
        "alv_home": social.alv,
        "alv_base_home": social.alv_base,
        "taxable_income_home": swiss.taxable_income,
        "federal_tax_home": swiss.federal,
        "cantonal_communal_tax_home": swiss.cantonal_communal,
        "simple_cantonal_tax_home": swiss.simple_cantonal_tax,
        "swiss_total_tax_home": swiss.total,
        "combined_steuerfuss": "0.95 canton + 1.19 city = 2.14",
    }

    return result, gross_up, swiss_detail


def run_assignment(inputs):
    """Run the full two-year assignment and return an :class:`AssignmentResult`."""
    validate_inputs(inputs)

    years = []
    history = {}
    swiss_details = {}
    for year in (1, 2):
        year_result, gross_up, detail = _run_year(inputs, year)
        years.append(year_result)
        history[year] = gross_up
        swiss_details[year] = detail

    total_cost = sum((y.total_employer_cost_gbp for y in years), Decimal("0"))
    total_home = sum((y.home_gross_pay_gbp for y in years), Decimal("0"))
    multiple = total_cost / total_home if total_home else Decimal("0")

    return AssignmentResult(
        inputs=inputs,
        years=years,
        total_employer_cost_gbp=total_cost,
        total_home_pay_gbp=total_home,
        cost_multiple=multiple,
        assumptions=list(ASSUMPTIONS),
        gross_up_history=history,
        swiss_detail=swiss_details,
    )
