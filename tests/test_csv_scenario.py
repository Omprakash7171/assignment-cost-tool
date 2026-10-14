"""CSV export (spec X04 / P12) and scenario comparison (X02 / P11)."""
from django.test import TestCase
from django.urls import reverse

from calculator import AssignmentInputs, run_assignment
from costtool.exporters import build_csv
from costtool.forms import AssignmentForm
from reference.sources import get_source
from tests.test_forms_views import valid_post_data


class CsvExportTests(TestCase):
    def test_build_csv_contains_annual_data_and_sources(self):
        result = run_assignment(AssignmentInputs())
        source_numbers = {"uk_income_tax_2026_27": 1, "hmrc_hs212": 2}
        records = [get_source("uk_income_tax_2026_27")]
        body = build_csv(result, source_numbers, records)
        self.assertIn("Year,Section,Item,Currency,Amount,Classification,Sources", body)
        self.assertIn("2026/27", body)
        self.assertIn("2027/28", body)
        self.assertIn("600410.73", body)  # whole-assignment total
        self.assertIn("312139.25", body)  # year-1 employer cost
        self.assertIn("Sources", body)
        self.assertIn("https://www.gov.uk/", body)

    def test_csv_export_post_returns_attachment(self):
        response = self.client.post(
            reverse("costtool:csv_export"), valid_post_data()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment", response["Content-Disposition"])
        body = response.content.decode()
        self.assertIn("Total employer cost (both years)", body)
        self.assertIn("600410.73", body)

    def test_csv_export_get_uses_supplied_case(self):
        response = self.client.get(reverse("costtool:csv_export"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/csv"))
        self.assertIn("600410.73", response.content.decode())

    def test_csv_export_invalid_input_reports_errors(self):
        data = valid_post_data()
        data["fx_gbp_to_home"] = "0"
        response = self.client.post(reverse("costtool:csv_export"), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/html"))
        self.assertNotIn("attachment", response.get("Content-Disposition", ""))

    def test_calculate_and_download_buttons_have_distinct_actions(self):
        # Both buttons live in the one form and target the right URLs, so
        # clicking "Calculate cost" always calculates (never downloads).
        response = self.client.get(reverse("costtool:cost_estimate"))
        content = response.content.decode()
        self.assertIn('id="estimate-form"', content)
        self.assertIn(
            'formaction="{0}"'.format(reverse("costtool:cost_estimate")), content
        )
        self.assertIn(
            'formaction="{0}"'.format(reverse("costtool:csv_export")), content
        )
        self.assertIn("Calculate cost", content)
        self.assertIn("Download CSV", content)


def _prefixed(prefix, data):
    return {"{0}-{1}".format(prefix, key): value for key, value in data.items()}


def _alt_data():
    data = valid_post_data()
    data["base_salary_home"] = "165000"
    data["housing_gbp_month"] = "3500"
    return data


class ScenarioCompareTests(TestCase):
    def test_get_renders_two_prefilled_forms(self):
        response = self.client.get(reverse("costtool:scenario_compare"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compare scenarios")
        self.assertContains(response, "Baseline")
        self.assertContains(response, "Alternative")
        # Prefixed field names present for both columns.
        self.assertContains(response, 'name="base-base_salary_home"')
        self.assertContains(response, 'name="alt-base_salary_home"')

    def test_identical_scenarios_have_zero_difference(self):
        data = dict(_prefixed("base", valid_post_data()))
        data.update(_prefixed("alt", valid_post_data()))
        response = self.client.post(reverse("costtool:scenario_compare"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Comparison")
        self.assertContains(response, "identical")

    def test_scenarios_reuse_engine_and_show_difference(self):
        data = dict(_prefixed("base", valid_post_data()))
        data.update(_prefixed("alt", _alt_data()))
        response = self.client.post(reverse("costtool:scenario_compare"), data)
        self.assertEqual(response.status_code, 200)

        # Expected figures come straight from the same engine (P11).
        base_result = run_assignment(AssignmentInputs())
        alt_form = AssignmentForm(data=_alt_data())
        self.assertTrue(alt_form.is_valid(), alt_form.errors)
        alt_result = run_assignment(alt_form.to_inputs())

        content = response.content.decode()
        self.assertIn("{0:,.2f}".format(base_result.total_employer_cost_gbp), content)
        self.assertIn("{0:,.2f}".format(alt_result.total_employer_cost_gbp), content)
        # The changed inputs are called out.
        self.assertIn("Base salary (CHF/year)", content)
