"""Employer/employee charges per documented assumptions (P08)."""
import unittest
from decimal import Decimal

from calculator.employee_nic import employee_class1_nic
from calculator.employer_charges import (
    class1a_nic,
    employer_class1_nic,
)


class EmployerNicTests(unittest.TestCase):
    def test_below_secondary_threshold(self):
        self.assertEqual(employer_class1_nic(Decimal("5000")), Decimal("0"))
        self.assertEqual(employer_class1_nic(Decimal("3000")), Decimal("0"))

    def test_above_secondary_threshold(self):
        self.assertEqual(employer_class1_nic(Decimal("6000")), Decimal("150"))

    def test_no_upper_cap(self):
        self.assertEqual(employer_class1_nic(Decimal("105000")), Decimal("15000"))

    def test_class1a_on_bik(self):
        self.assertEqual(class1a_nic(Decimal("40000")), Decimal("6000"))
        self.assertEqual(class1a_nic(Decimal("0")), Decimal("0"))


class EmployeeNicMemoTests(unittest.TestCase):
    def test_below_primary_threshold(self):
        self.assertEqual(employee_class1_nic(Decimal("12000")), Decimal("0"))

    def test_main_rate_band(self):
        # 8% on earnings between 12,570 and 50,270.
        self.assertEqual(employee_class1_nic(Decimal("50270")), Decimal("3016"))

    def test_upper_rate(self):
        expected = Decimal("0.08") * (Decimal("50270") - Decimal("12570"))
        expected += Decimal("0.02") * (Decimal("100000") - Decimal("50270"))
        self.assertEqual(employee_class1_nic(Decimal("100000")), expected)


if __name__ == "__main__":
    unittest.main()
