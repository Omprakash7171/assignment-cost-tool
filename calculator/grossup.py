"""Iterative tax-on-tax gross-up solver (spec E03/E06/E07/E10).

The employer bears the employee's UK income tax. We solve the fixed point

    T = UKTax(I + T)

where ``I`` is the net amount the employee is to receive (net home pay plus
taxable assignment benefits) and ``T`` is the employer-paid UK income tax. The
gross taxable pay is therefore ``I + T``.

Because the UK marginal tax rate is below 100%, the map ``T -> UKTax(I + T)``
is a contraction and the iteration converges geometrically. The full iteration
history is retained for the audit trail.
"""
from dataclasses import dataclass
from decimal import Decimal

from .exceptions import NonConvergenceError
from .rounding import dec

DEFAULT_TOLERANCE = Decimal("0.01")
DEFAULT_MAX_ITERATIONS = 100


@dataclass(frozen=True)
class IterationRecord:
    iteration: int
    gross: Decimal
    tax: Decimal
    error: Decimal


@dataclass(frozen=True)
class GrossUpResult:
    net_target: Decimal
    tax: Decimal
    gross: Decimal
    history: tuple
    converged: bool
    iterations: int
    tolerance: Decimal


def solve_gross_up(
    net_target,
    tax_function,
    tolerance=DEFAULT_TOLERANCE,
    max_iterations=DEFAULT_MAX_ITERATIONS,
):
    """Return the employer-paid tax ``T`` with ``T == tax_function(I + T)``.

    Raises :class:`~calculator.exceptions.NonConvergenceError` if no fixed
    point is found within ``max_iterations``.
    """
    net_target = dec(net_target)
    tolerance = dec(tolerance)

    tax = tax_function(net_target)
    history = []

    for iteration in range(1, max_iterations + 1):
        gross = net_target + tax
        new_tax = tax_function(gross)
        error = abs(new_tax - tax)
        history.append(
            IterationRecord(
                iteration=iteration,
                gross=gross,
                tax=new_tax,
                error=error,
            )
        )
        tax = new_tax
        if error <= tolerance:
            return GrossUpResult(
                net_target=net_target,
                tax=tax,
                gross=net_target + tax,
                history=tuple(history),
                converged=True,
                iterations=iteration,
                tolerance=tolerance,
            )

    raise NonConvergenceError(
        "Gross-up did not converge within {0} iterations (tolerance {1}).".format(
            max_iterations, tolerance
        ),
        history=history,
    )
