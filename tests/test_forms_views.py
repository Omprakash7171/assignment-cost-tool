"""Form validation and view rendering (P10, plus G3 source rendering)."""
from django.test import TestCase
from django.urls import reverse

from costtool.forms import AssignmentForm, supplied_case_initial
from costtool.views import cost_estimate  # noqa: F401  (import check)


def valid_post_data():
    return {
        "home_country": "Switzerland",
        "home_city": "Zurich",
        "host_country": "United Kingdom",
        "host_city": "London",
        "start_date": "2026-04-06",
        "end_date": "2028-04-05",
        "nationality": "Swiss",
        "marital_status": "single",
        "children": "0",
        "uk_tax_resident_year1": "on",
        "uk_tax_resident_year2": "on",
        "base_salary_home": "150000",
        "bonus_home": "20000",
        "fx_gbp_to_home": "1.10",
        "housing_gbp_month": "3000",
        "relocation_home": "5000",
        "moving_gbp": "6000",
        "temp_accom_gbp": "4000",
    }


class FormTests(TestCase):
    def test_supplied_case_initial_matches_defaults(self):
        initial = supplied_case_initial()
        self.assertEqual(str(initial["base_salary_home"]), "150000")
        self.assertEqual(str(initial["fx_gbp_to_home"]), "1.10")

    def test_valid_form_maps_to_inputs(self):
        form = AssignmentForm(data=valid_post_data())
        self.assertTrue(form.is_valid(), form.errors)
        inputs = form.to_inputs()
        self.assertEqual(str(inputs.base_salary_home), "150000")
        self.assertEqual(str(inputs.housing_gbp_month), "3000")

    def test_zero_exchange_rate_rejected(self):
        data = valid_post_data()
        data["fx_gbp_to_home"] = "0"
        form = AssignmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("fx_gbp_to_home", form.errors)

    def test_negative_salary_rejected(self):
        data = valid_post_data()
        data["base_salary_home"] = "-100"
        form = AssignmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("base_salary_home", form.errors)

    def test_end_before_start_rejected(self):
        data = valid_post_data()
        data["end_date"] = "2025-01-01"
        form = AssignmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_missing_required_field_rejected(self):
        data = valid_post_data()
        data["base_salary_home"] = ""
        form = AssignmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("base_salary_home", form.errors)


class ViewTests(TestCase):
    def test_get_renders_form_with_defaults(self):
        response = self.client.get(reverse("costtool:cost_estimate"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cost Estimate")
        self.assertContains(response, 'value="150000"')
        self.assertContains(response, 'value="1.10"')
        # No results until submitted.
        self.assertNotContains(response, "Total employer cost")

    def test_post_supplied_case_renders_results(self):
        response = self.client.post(
            reverse("costtool:cost_estimate"), valid_post_data()
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total employer cost")
        self.assertContains(response, "2026/27")
        self.assertContains(response, "2027/28")
        self.assertContains(response, "Section A")
        self.assertContains(response, "Section B")
        # Headline figures from the engine.
        self.assertContains(response, "600,410.73")
        self.assertContains(response, "312,139.25")

    def test_results_include_official_source_links(self):
        response = self.client.post(
            reverse("costtool:cost_estimate"), valid_post_data()
        )
        self.assertContains(response, "https://www.gov.uk/")
        self.assertContains(response, "Sources")

    def test_invalid_post_renders_errors_without_results(self):
        data = valid_post_data()
        data["fx_gbp_to_home"] = "0"
        response = self.client.post(reverse("costtool:cost_estimate"), data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Total employer cost")
        self.assertContains(response, "field")

    def test_year_two_absent_relocation_benefit(self):
        response = self.client.post(
            reverse("costtool:cost_estimate"), valid_post_data()
        )
        content = response.content.decode()
        # The Section B benefit appears once (year 1), not twice.
        self.assertEqual(content.count("Relocation allowance (cash)"), 1)


class Html5JsCoverageTests(TestCase):
    """Client-side (HTML5 + JS) coverage for F13/X03."""

    def test_numeric_inputs_use_html5_constraints(self):
        response = self.client.get(reverse("costtool:cost_estimate"))
        content = response.content.decode()
        # Native constraint validation: typed numbers with bounds.
        self.assertIn('type="number"', content)
        self.assertIn('step="0.01"', content)
        self.assertIn('min="0"', content)
        self.assertIn('type="date"', content)
        self.assertIn('step="0.0001"', content)

    def test_required_fields_marked_for_client_validation(self):
        response = self.client.get(reverse("costtool:cost_estimate"))
        content = response.content.decode()
        # Django emits the HTML5 required attribute on required fields.
        self.assertIn('required', content)

    def test_layout_scripts_and_labels_present(self):
        response = self.client.get(reverse("costtool:cost_estimate"))
        content = response.content.decode()
        self.assertIn("/static/js/app.js", content)
        self.assertIn("/static/css/app.css", content)
        self.assertIn("<label", content)
        self.assertIn('lang="en-GB"', content)

    def test_error_state_is_rendered_readably(self):
        data = valid_post_data()
        data["fx_gbp_to_home"] = "0"
        response = self.client.post(reverse("costtool:cost_estimate"), data)
        content = response.content.decode()
        self.assertIn('class="error"', content)
        self.assertIn('role="alert"', content)
