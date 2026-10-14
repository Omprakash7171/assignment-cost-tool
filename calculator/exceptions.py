"""Typed exceptions raised by the calculation engine.

The views map these to readable messages; they must never leak a traceback to
the user (spec S05).
"""


class CalculatorError(Exception):
    """Base class for every expected engine failure."""


class CalculatorValidationError(CalculatorError):
    """Raised when inputs are internally inconsistent or out of range."""


class NonConvergenceError(CalculatorError):
    """Raised when the gross-up iteration fails to reach a fixed point.

    Raised instead of returning a partial/approximate figure so that no
    misleading result is ever displayed (spec E08/S04).
    """

    def __init__(self, message, history=None):
        super().__init__(message)
        self.history = tuple(history or ())
