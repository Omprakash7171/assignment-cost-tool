"""Input validation for the calculation engine (spec S02/S03/S04).

``validate_inputs`` is the single gate every engine entry point passes
through. It rejects internally inconsistent or out-of-range inputs with a
:class:`~calculator.exceptions.CalculatorValidationError` carrying a message
that is safe to show to a user, so a calculation can never proceed on data
that would produce a misleading result.

Checks performed:

  * the FX rate (CHF per GBP) is a finite number greater than zero;
  * every money field is a finite number (no NaN / Infinity) and not negative;
  * the assignment end date falls after the start date;
  * the number of children is a non-negative integer.
"""
from datetime import date
from decimal import Decimal

from .exceptions import CalculatorValidationError
from .rounding import dec

MONEY_FIELDS = (
    ("base salary", "base_salary_home"),
    ("bonus", "bonus_home"),
    ("housing", "housing_gbp_month"),
    ("relocation allowance", "relocation_home"),
    ("moving costs", "moving_gbp"),
    ("temporary accommodation", "temp_accom_gbp"),
)


def _finite_decimal(name, value):
    """Coerce ``value`` to Decimal, rejecting NaN and infinities."""
    try:
        number = dec(value)
    except Exception as exc:  # pragma: no cover - defensive
        raise CalculatorValidationError(
            "{0} must be a number.".format(name)
        ) from exc
    if not number.is_finite():
        raise CalculatorValidationError(
            "{0} must be a finite number.".format(name)
        )
    return number


def validate_inputs(inputs):
    """Raise :class:`CalculatorValidationError` if ``inputs`` is unusable."""
    fx = _finite_decimal("Exchange rate", inputs.fx_gbp_to_home)
    if fx <= 0:
        raise CalculatorValidationError("Exchange rate must be greater than zero.")

    for label, attr in MONEY_FIELDS:
        value = _finite_decimal(label, getattr(inputs, attr))
        if value < 0:
            raise CalculatorValidationError(
                "{0} must not be negative.".format(label)
            )

    start = inputs.start_date
    end = inputs.end_date
    if not isinstance(start, date) or not isinstance(end, date):
        raise CalculatorValidationError("Assignment dates must be valid dates.")
    if end <= start:
        raise CalculatorValidationError("End date must be after start date.")

    children = inputs.children
    if not isinstance(children, int) or isinstance(children, bool):
        raise CalculatorValidationError("Number of children must be a whole number.")
    if children < 0:
        raise CalculatorValidationError("Number of children must not be negative.")


__all__ = ["MONEY_FIELDS", "validate_inputs"]
