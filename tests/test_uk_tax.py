"""UK income tax: band boundaries (P04) and personal-allowance taper (P05)."""
import unittest
from decimal import Decimal

from calculator.uk_tax import (
    compute_uk_tax,
    personal_allowance_for,
)


class PersonalAllowanceTaperTests(unittest.TestCase):
    def test_full_allowance_up_to_100k(self):
        self.assertEqual(personal_allowance_for(Decimal("0")), Decimal("12570"))
        self.assertEqual(personal_allowance_for(Decimal("100000")), Decimal("12570"))

    def test_taper_by_one_for_every_two(self):
        self.assertEqual(personal_allowance_for(Decimal("110000")), Decimal("7570"))
        self.assertEqual(personal_allowance_for(Decimal("120000")), Decimal("2570"))

    def test_allowance_fully_withdrawn(self):
        self.assertEqual(personal_allowance_for(Decimal("125140")), Decimal("0"))
        self.assertEqual(personal_allowance_for(Decimal("200000")), Decimal("0"))


class BandBoundaryTests(unittest.TestCase):
    def test_no_tax_below_personal_allowance(self):
        self.assertEqual(compute_uk_tax(Decimal("12570")), Decimal("0"))

    def test_basic_rate_ceiling(self):
        # Taxable income reaches the basic band limit (PA + 37,700).
        self.assertEqual(compute_uk_tax(Decimal("50270")), Decimal("7540"))

    def test_higher_rate_boundary(self):
        # At income 100,000 the allowance is full: taxable 87,430.
        expected = Decimal("0.20") * Decimal("37700") + Decimal("0.40") * (
            Decimal("87430") - Decimal("37700")
        )
        self.assertEqual(compute_uk_tax(Decimal("100000")), expected)

    def test_additional_rate_threshold(self):
        # At 125,140 the allowance is zero: taxable 125,140.
        expected = Decimal("0.20") * Decimal("37700") + Decimal("0.40") * (
            Decimal("125140") - Decimal("37700")
        )
        self.assertEqual(compute_uk_tax(Decimal("125140")), expected)

    def test_additional_rate_applies_above_threshold(self):
        expected = (
            Decimal("0.20") * Decimal("37700")
            + Decimal("0.40") * (Decimal("125140") - Decimal("37700"))
            + Decimal("0.45") * (Decimal("200000") - Decimal("125140"))
        )
        self.assertEqual(compute_uk_tax(Decimal("200000")), expected)

    def test_monotonic_nondecreasing(self):
        previous = Decimal("-1")
        income = Decimal("0")
        while income <= 300000:
            tax = compute_uk_tax(income)
            self.assertGreaterEqual(tax, previous)
            previous = tax
            income += Decimal("1000")


if __name__ == "__main__":
    unittest.main()
