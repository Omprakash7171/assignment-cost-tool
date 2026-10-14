"""Hypothetical Swiss tax and social security.

Federal anchors and Zurich brackets are checked against the official 2026
tariffs (ESTV Form 58c; ZH StG section 35). This is the basis for acceptance
gate G13 / check C14.
"""
import unittest
from decimal import Decimal

from calculator.swiss_social import ALV_CEILING, compute_swiss_social
from calculator.swiss_tax import (
    federal_tax,
    zh_simple_tax,
    zh_total_tax,
)


class SwissSocialTests(unittest.TestCase):
    def test_ahv_has_no_ceiling(self):
        result = compute_swiss_social(Decimal("300000"))
        self.assertEqual(result.ahv_iv_eo, Decimal("0.053") * Decimal("300000"))

    def test_alv_is_capped(self):
        result = compute_swiss_social(Decimal("300000"))
        self.assertEqual(result.alv_base, ALV_CEILING)
        self.assertEqual(result.alv, Decimal("0.011") * ALV_CEILING)

    def test_typical_income(self):
        result = compute_swiss_social(Decimal("170000"))
        self.assertEqual(result.ahv_iv_eo, Decimal("9010.00"))
        self.assertEqual(result.alv, Decimal("1630.20"))
        self.assertEqual(result.total, Decimal("10640.20"))

    def test_income_below_ceiling(self):
        result = compute_swiss_social(Decimal("100000"))
        self.assertEqual(result.alv, Decimal("1100"))


class FederalTariffTests(unittest.TestCase):
    def test_tax_free_band(self):
        self.assertEqual(federal_tax(Decimal("15200")), Decimal("0"))
        self.assertEqual(federal_tax(Decimal("10000")), Decimal("0"))

    def test_published_anchors(self):
        self.assertEqual(federal_tax(Decimal("33200")), Decimal("138.60"))
        self.assertEqual(federal_tax(Decimal("43400")), Decimal("228.36"))
        self.assertEqual(federal_tax(Decimal("58000")), Decimal("612.00"))
        self.assertEqual(federal_tax(Decimal("76200")), Decimal("1152.50"))
        self.assertEqual(federal_tax(Decimal("82100")), Decimal("1502.95"))
        self.assertEqual(federal_tax(Decimal("108900")), Decimal("3271.75"))
        self.assertEqual(federal_tax(Decimal("141500")), Decimal("6140.55"))
        self.assertEqual(federal_tax(Decimal("185100")), Decimal("10936.55"))
        self.assertEqual(federal_tax(Decimal("793900")), Decimal("91298.15"))

    def test_uniform_top_rate(self):
        self.assertEqual(federal_tax(Decimal("800000")), Decimal("92000"))
        self.assertEqual(federal_tax(Decimal("950000")), Decimal("109250"))

    def test_interpolation_between_anchors(self):
        # Halfway across the 141,500-185,100 segment (11%).
        value = Decimal("141500") + (Decimal("185100") - Decimal("141500")) / 2
        expected = Decimal("6140.55") + Decimal("0.11") * (
            value - Decimal("141500")
        )
        self.assertEqual(federal_tax(value), expected)


class ZurichTariffTests(unittest.TestCase):
    def test_tax_free_band(self):
        self.assertEqual(zh_simple_tax(Decimal("7000")), Decimal("0"))

    def test_first_bracket(self):
        self.assertEqual(zh_simple_tax(Decimal("12000")), Decimal("100"))

    def test_full_grundtarif_sum(self):
        # Sum of every bracket of section 35 (1) at the top of the table.
        self.assertEqual(zh_simple_tax(Decimal("266700")), Decimal("24655"))

    def test_top_rate(self):
        expected = Decimal("24655") + Decimal("0.13") * Decimal("300")
        self.assertEqual(zh_simple_tax(Decimal("267000")), expected)

    def test_combined_steuerfuss(self):
        self.assertEqual(
            zh_total_tax(Decimal("266700")),
            Decimal("24655") * Decimal("2.14"),
        )


if __name__ == "__main__":
    unittest.main()
