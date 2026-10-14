"""Decimal policy for the engine.

All arithmetic is performed with :class:`decimal.Decimal`. Full precision is
preserved through the calculation; conversion to a two-decimal display value
happens only at the presentation boundary via :func:`money` (spec E09).
"""
from decimal import ROUND_HALF_UP, Decimal, getcontext

# Ample working precision; intermediate results are never truncated.
getcontext().prec = 28

TWO_PLACES = Decimal("0.01")


def dec(value):
    """Coerce ``value`` (int, float, str, Decimal) to :class:`Decimal`.

    Floats are converted via their string representation to avoid binary
    rounding surprises.
    """
    if isinstance(value, Decimal):
        return value
    if isinstance(value, float):
        return Decimal(str(value))
    return Decimal(value)


def money(value):
    """Quantise ``value`` to two decimal places, half-up, for display."""
    return dec(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def money_str(value):
    """Return ``value`` as a fixed two-decimal string (no currency symbol)."""
    return str(money(value))
