"""Server-side form for the Cost Estimate tab.

Thin validation layer: it maps submitted values onto the engine's
:class:`~calculator.models.AssignmentInputs`. No financial logic lives here
(spec E01).
"""
from decimal import Decimal

from django import forms

from calculator import AssignmentInputs

MARITAL_CHOICES = (
    ("single", "Single"),
    ("married", "Married / civil partnership"),
    ("other", "Other"),
)

NATIONALITY_CHOICES = (
    ("Swiss", "Swiss"),
    ("British", "British"),
    ("Other", "Other"),
)

COUNTRY_CHOICES = (
    ("Switzerland", "Switzerland"),
    ("United Kingdom", "United Kingdom"),
    ("Other", "Other"),
)


def supplied_case_initial():
    """Initial values that reproduce the exact supplied test case (T01-T10)."""
    defaults = AssignmentInputs()
    return {
        "home_country": defaults.home_country,
        "home_city": defaults.home_city,
        "host_country": defaults.host_country,
        "host_city": defaults.host_city,
        "start_date": defaults.start_date,
        "end_date": defaults.end_date,
        "nationality": defaults.nationality,
        "marital_status": defaults.marital_status,
        "children": defaults.children,
        "uk_tax_resident_year1": defaults.uk_tax_resident_year1,
        "uk_tax_resident_year2": defaults.uk_tax_resident_year2,
        "base_salary_home": defaults.base_salary_home,
        "bonus_home": defaults.bonus_home,
        "fx_gbp_to_home": defaults.fx_gbp_to_home,
        "housing_gbp_month": defaults.housing_gbp_month,
        "relocation_home": defaults.relocation_home,
        "moving_gbp": defaults.moving_gbp,
        "temp_accom_gbp": defaults.temp_accom_gbp,
    }


def alternative_case_initial():
    """A variant of the supplied case used to seed the scenario comparison."""
    data = supplied_case_initial()
    data.update(
        {
            "base_salary_home": Decimal("165000"),
            "housing_gbp_month": Decimal("3500"),
        }
    )
    return data


def _money_input():
    return forms.NumberInput(attrs={"class": "input", "step": "0.01", "min": "0"})


class AssignmentForm(forms.Form):
    """Input form for one assignment."""

    # --- Locations and period ----------------------------------------------
    home_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Home country")
    home_city = forms.CharField(label="Home city", max_length=80)
    host_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Host country")
    host_city = forms.CharField(label="Host city", max_length=80)
    start_date = forms.DateField(
        label="Assignment start", widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = forms.DateField(
        label="Assignment end", widget=forms.DateInput(attrs={"type": "date"})
    )

    # --- Employee -----------------------------------------------------------
    nationality = forms.ChoiceField(choices=NATIONALITY_CHOICES, label="Nationality")
    marital_status = forms.ChoiceField(choices=MARITAL_CHOICES, label="Marital status")
    children = forms.IntegerField(
        label="Children",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "input", "step": "1", "min": "0"}),
    )
    uk_tax_resident_year1 = forms.BooleanField(
        label="UK tax resident in year 1", required=False
    )
    uk_tax_resident_year2 = forms.BooleanField(
        label="UK tax resident in year 2", required=False
    )

    # --- Pay (home currency) ------------------------------------------------
    base_salary_home = forms.DecimalField(
        label="Base salary (CHF/year)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )
    bonus_home = forms.DecimalField(
        label="Bonus (CHF/year)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )
    fx_gbp_to_home = forms.DecimalField(
        label="Exchange rate (CHF per GBP 1)",
        min_value=Decimal("0.0001"),
        max_digits=10,
        decimal_places=4,
        widget=forms.NumberInput(
            attrs={"class": "input", "step": "0.0001", "min": "0.0001"}
        ),
    )

    # --- Benefits -----------------------------------------------------------
    housing_gbp_month = forms.DecimalField(
        label="Housing (GBP/month)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )
    relocation_home = forms.DecimalField(
        label="Relocation allowance (CHF, year 1)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )
    moving_gbp = forms.DecimalField(
        label="Moving costs (GBP, year 1)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )
    temp_accom_gbp = forms.DecimalField(
        label="Temporary accommodation (GBP, year 1)",
        min_value=Decimal("0"),
        max_digits=12,
        decimal_places=2,
        widget=_money_input(),
    )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        end = cleaned.get("end_date")
        if start and end and end <= start:
            self.add_error("end_date", "End date must be after the start date.")
        return cleaned

    def clean_fx_gbp_to_home(self):
        fx = self.cleaned_data["fx_gbp_to_home"]
        if fx <= 0:
            raise forms.ValidationError("Exchange rate must be greater than zero.")
        return fx

    def to_inputs(self):
        """Return an :class:`AssignmentInputs` from validated data."""
        if not self.is_valid():
            raise ValueError("form must be valid before calling to_inputs()")
        d = self.cleaned_data
        return AssignmentInputs(
            home_country=d["home_country"],
            home_city=d["home_city"],
            host_country=d["host_country"],
            host_city=d["host_city"],
            start_date=d["start_date"],
            end_date=d["end_date"],
            nationality=d["nationality"],
            marital_status=d["marital_status"],
            children=d["children"],
            uk_tax_resident_year1=d["uk_tax_resident_year1"],
            uk_tax_resident_year2=d["uk_tax_resident_year2"],
            base_salary_home=d["base_salary_home"],
            bonus_home=d["bonus_home"],
            fx_gbp_to_home=d["fx_gbp_to_home"],
            housing_gbp_month=d["housing_gbp_month"],
            relocation_home=d["relocation_home"],
            moving_gbp=d["moving_gbp"],
            temp_accom_gbp=d["temp_accom_gbp"],
        )
