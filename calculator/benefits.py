"""Assignment benefit classification and FX conversion.

Classification is a documented modelling decision per benefit (spec F05/E12):

  * Housing (employer-paid accommodation)          -> BIK (taxable)
  * Temporary accommodation (year 1)               -> BIK (assumption)
  * Relocation allowance (cash)                    -> TAXABLE_CASH
  * Moving costs (qualifying relocation expenses)  -> NOT_TAXABLE (s.270A ITEPA)
"""
from decimal import Decimal

from .models import (
    BIK,
    NOT_TAXABLE,
    TAXABLE_CASH,
    YearBenefit,
)
from .rounding import dec

MONTHS_PER_YEAR = 12

# Source ids (see reference/sources.py)
SRC_LIVING_ACCOMMODATION = ("uk_living_accommodation",)
SRC_RELOCATION = ("uk_relocation_exemption",)


def chf_to_gbp(amount_chf, fx_gbp_to_home):
    """Convert CHF to GBP given the CHF-per-GBP rate."""
    return dec(amount_chf) / dec(fx_gbp_to_home)


def gbp_to_chf(amount_gbp, fx_gbp_to_home):
    """Convert GBP to CHF given the CHF-per-GBP rate."""
    return dec(amount_gbp) * dec(fx_gbp_to_home)


def build_year_benefits(inputs, year):
    """Resolve the benefit set for ``year`` (1 or 2) with GBP values."""
    fx = inputs.fx_gbp_to_home
    benefits = []

    # Housing: employer pays the rent direct to the landlord (both years).
    housing_gbp = dec(inputs.housing_gbp_month) * MONTHS_PER_YEAR
    benefits.append(
        YearBenefit(
            label="Housing (employer-paid accommodation)",
            classification=BIK,
            currency="GBP",
            amount_native=housing_gbp,
            amount_gbp=housing_gbp,
            year=year,
            derivation="{0} GBP/month x 12".format(inputs.housing_gbp_month),
            note="Living-accommodation benefit; reported on P11D, Class 1A NIC.",
            source_ids=SRC_LIVING_ACCOMMODATION,
        )
    )

    if year == 1:
        # Temporary accommodation during relocation (4 weeks).
        temp_gbp = dec(inputs.temp_accom_gbp)
        benefits.append(
            YearBenefit(
                label="Temporary accommodation",
                classification=BIK,
                currency="GBP",
                amount_native=temp_gbp,
                amount_gbp=temp_gbp,
                year=year,
                derivation="supplied amount",
                note="Treated as a taxable benefit in kind (assumption).",
                source_ids=SRC_LIVING_ACCOMMODATION,
            )
        )

        # Relocation allowance (cash).
        reloc_home = dec(inputs.relocation_home)
        reloc_gbp = chf_to_gbp(reloc_home, fx)
        benefits.append(
            YearBenefit(
                label="Relocation allowance (cash)",
                classification=TAXABLE_CASH,
                currency="CHF",
                amount_native=reloc_home,
                amount_gbp=reloc_gbp,
                year=year,
                derivation="CHF {0} / {1}".format(reloc_home, fx),
                note="Cash allowance; taxable earnings (Class 1 NIC).",
                source_ids=SRC_RELOCATION,
            )
        )

        # Moving costs (qualifying relocation expenses exemption, up to GBP 8,000).
        moving_gbp = dec(inputs.moving_gbp)
        benefits.append(
            YearBenefit(
                label="Moving costs",
                classification=NOT_TAXABLE,
                currency="GBP",
                amount_native=moving_gbp,
                amount_gbp=moving_gbp,
                year=year,
                derivation="supplied amount",
                note="Qualifying relocation expenses, exempt up to GBP 8,000.",
                source_ids=SRC_RELOCATION,
            )
        )

    return benefits
