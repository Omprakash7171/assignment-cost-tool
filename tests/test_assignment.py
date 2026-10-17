"""Supplied test case (P01), year-one-only benefits (P02), FX (P03),
totals reconciliation (P09)."""
import unittest
from decimal import Decimal

from calculator import AssignmentInputs, run_assignment
from calculator.benefits import chf_to_gbp, gbp_to_chf
from calculator.uk_tax import compute_uk_tax

TOL = Decimal("0.01")


def supplied_case():
    """The exact case from spec T01-T10 (all defaults)."""
    return AssignmentInputs(
        base_salary_home=Decimal("150000"),
        bonus_home=Decimal("20000"),
        fx_gbp_to_home=Decimal("1.10"),
        housing_gbp_month=Decimal("3000"),
        relocation_home=Decimal("5000"),
        moving_gbp=Decimal("6000"),
        temp_accom_gbp=Decimal("4000"),
        start_date=__import__("datetime").date(2026, 4, 6),
        end_date=__import__("datetime").date(2028, 4, 5),
    )


class TestCaseRunTests(unittest.TestCase):
    def setUp(self):
        self.result = run_assignment(supplied_case())

    def test_generates_both_years(self):
        self.assertEqual(len(self.result.years), 2)
        self.assertEqual([y.year for y in self.result.years], [1, 2])

    def test_currency_conversion(self):
        self.assertEqual(chf_to_gbp(Decimal("110"), Decimal("1.10")), Decimal("100"))
        self.assertEqual(gbp_to_chf(Decimal("100"), Decimal("1.10")), Decimal("110"))

    def test_year_two_excludes_one_off_benefits(self):
        year2_labels = [line.label for line in self.result.years[1].section_b]
        self.assertEqual(year2_labels, ["Housing (employer-paid accommodation)"])

    def test_year_one_includes_all_benefits(self):
        labels = [line.label for line in self.result.years[0].section_b]
        self.assertIn("Housing (employer-paid accommodation)", labels)
        self.assertIn("Relocation allowance (cash)", labels)
        self.assertIn("Moving costs", labels)
        self.assertIn("Temporary accommodation", labels)

    def test_gross_up_fixed_point_each_year(self):
        for year in self.result.years:
            gross = year.net_target_i_gbp + year.employer_tax_t_gbp
            self.assertLessEqual(
                abs(year.employer_tax_t_gbp - compute_uk_tax(gross)), TOL
            )

    def test_net_target_formula(self):
        for year in self.result.years:
            self.assertLessEqual(
                abs(
                    year.net_target_i_gbp
                    - (year.net_home_pay_gbp + year.taxable_benefits_gbp)
                ),
                TOL,
            )

    def test_annual_totals_reconcile(self):
        for year in self.result.years:
            expected = (
                year.net_home_pay_gbp
                + year.benefit_cost_gbp
                + year.employer_tax_t_gbp
                + year.employer_nic_gbp
                + year.class1a_nic_gbp
            )
            self.assertLessEqual(abs(year.total_employer_cost_gbp - expected), TOL)

    def test_whole_assignment_totals(self):
        expected = sum(
            (y.total_employer_cost_gbp for y in self.result.years), Decimal("0")
        )
        self.assertLessEqual(
            abs(self.result.total_employer_cost_gbp - expected), TOL
        )
        self.assertLessEqual(
            abs(
                self.result.cost_multiple
                - self.result.total_employer_cost_gbp / self.result.total_home_pay_gbp
            ),
            TOL,
        )


class ValidationTests(unittest.TestCase):
    def test_zero_fx_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            run_assignment(AssignmentInputs(fx_gbp_to_home=Decimal("0")))

    def test_negative_salary_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            run_assignment(AssignmentInputs(base_salary_home=Decimal("-1")))

    def test_end_before_start_rejected(self):
        import datetime

        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            run_assignment(
                AssignmentInputs(
                    start_date=datetime.date(2028, 1, 1),
                    end_date=datetime.date(2026, 1, 1),
                )
            )


class ValidationModuleTests(unittest.TestCase):
    """Strengthened input gate in calculator/validation.py."""

    def _run(self, **kwargs):
        return run_assignment(AssignmentInputs(**kwargs))

    def test_nan_fx_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            self._run(fx_gbp_to_home=Decimal("NaN"))

    def test_infinite_fx_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            self._run(fx_gbp_to_home=Decimal("Infinity"))

    def test_nan_salary_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            self._run(base_salary_home=Decimal("NaN"))

    def test_negative_children_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            self._run(children=-1)

    def test_float_children_rejected(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError):
            self._run(children=1.5)

    def test_validate_inputs_usable_standalone(self):
        from calculator import validate_inputs

        validate_inputs(AssignmentInputs())  # supplied case must pass

    def test_error_messages_are_readable(self):
        from calculator.exceptions import CalculatorValidationError

        with self.assertRaises(CalculatorValidationError) as ctx:
            self._run(fx_gbp_to_home=Decimal("0"))
        self.assertIn("Exchange rate", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
