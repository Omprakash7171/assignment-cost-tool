"""Gross-up solver: fixed point (P06), safe non-convergence (P07), history (E10)."""
import unittest
from decimal import Decimal

from calculator.exceptions import NonConvergenceError
from calculator.grossup import solve_gross_up
from calculator.uk_tax import compute_uk_tax


class GrossUpTests(unittest.TestCase):
    def test_fixed_point_holds_within_tolerance(self):
        for net in ("40000", "90000", "160000", "300000"):
            result = solve_gross_up(Decimal(net), compute_uk_tax)
            residual = abs(result.tax - compute_uk_tax(result.gross))
            self.assertLessEqual(residual, result.tolerance)

    def test_gross_is_net_plus_tax(self):
        result = solve_gross_up(Decimal("160000"), compute_uk_tax)
        self.assertEqual(result.gross, result.net_target + result.tax)

    def test_history_records_every_iteration(self):
        result = solve_gross_up(Decimal("160000"), compute_uk_tax)
        self.assertEqual(len(result.history), result.iterations)
        self.assertTrue(result.converged)
        # Error must shrink towards the tolerance.
        self.assertLess(result.history[-1].error, result.history[0].error)

    def test_non_convergence_raises_and_reports_history(self):
        def divergent(income):
            # Marginal "rate" of 200% never reaches a fixed point.
            return income * Decimal("2")

        with self.assertRaises(NonConvergenceError) as ctx:
            solve_gross_up(Decimal("1000"), divergent, max_iterations=10)
        self.assertEqual(len(ctx.exception.history), 10)

    def test_zero_net_target(self):
        result = solve_gross_up(Decimal("0"), compute_uk_tax)
        self.assertEqual(result.tax, Decimal("0"))
        self.assertTrue(result.converged)


if __name__ == "__main__":
    unittest.main()
