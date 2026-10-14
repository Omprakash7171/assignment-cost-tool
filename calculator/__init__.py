"""Pure-Python calculation engine for the Assignment Cost Tool.

This package contains no Django imports. It is a deterministic function of an
:class:`~calculator.models.AssignmentInputs` instance and can be exercised from
plain ``unittest`` tests, the CSV exporter and the scenario comparison alike.

Entry point: :func:`calculator.assignment.run_assignment`.
"""
from .assignment import run_assignment
from .exceptions import (
    CalculatorError,
    CalculatorValidationError,
    NonConvergenceError,
)
from .models import (
    AssignmentInputs,
    AssignmentResult,
    Benefit,
    MoneyLine,
    YearBenefit,
    YearResult,
)

__all__ = [
    "run_assignment",
    "CalculatorError",
    "CalculatorValidationError",
    "NonConvergenceError",
    "AssignmentInputs",
    "AssignmentResult",
    "Benefit",
    "MoneyLine",
    "YearBenefit",
    "YearResult",
]
