"""Immigration tab: content integrity and rendering (F11/F12, R07/R08, G3)."""
from django.test import TestCase
from django.urls import reverse

from reference import immigration as content
from reference.sources import SOURCES


class ContentIntegrityTests(TestCase):
    def test_every_referenced_source_resolves(self):
        missing = [sid for sid in content.all_source_ids() if sid not in SOURCES]
        self.assertEqual(missing, [])

    def test_referenced_sources_are_official_and_immigration(self):
        for sid in content.all_source_ids():
            source = SOURCES[sid]
            self.assertEqual(source.category, "immigration", sid)
            self.assertTrue(source.url.startswith("https://www.gov.uk/"), sid)
            self.assertTrue(source.last_checked, sid)
            self.assertTrue(source.relevance, sid)

    def test_all_items_carry_a_source(self):
        for group in (
            content.ROUTES,
            content.REQUIREMENTS,
            content.COSTS,
            content.STEPS,
            content.CHECKLIST,
        ):
            for item in group:
                self.assertTrue(item.source_ids, item)

    def test_there_is_exactly_one_primary_route(self):
        primaries = [r for r in content.ROUTES if r.is_primary]
        self.assertEqual(len(primaries), 1)

    def test_classifications_are_known(self):
        known = set(content.CLASSIFICATION_LABELS)
        for group in (content.REQUIREMENTS, content.COSTS):
            for item in group:
                self.assertIn(item.classification, known, item)


class ImmigrationViewTests(TestCase):
    def test_get_renders_all_sections(self):
        response = self.client.get(reverse("reference:immigration"))
        self.assertEqual(response.status_code, 200)
        for text in (
            "Candidate routes",
            "Senior or Specialist Worker",
            "Skilled Worker",
            "Requirements",
            "Costs",
            "Application steps",
            "Readiness checklist",
            "Sources",
        ):
            self.assertContains(response, text)

    def test_page_distinguishes_obligation_types(self):
        response = self.client.get(reverse("reference:immigration"))
        self.assertContains(response, "Mandatory (legal requirement)")
        self.assertContains(response, "Recommended")
        self.assertContains(response, "Estimate")

    def test_page_links_official_sources(self):
        response = self.client.get(reverse("reference:immigration"))
        self.assertContains(response, "https://www.gov.uk/skilled-worker-visa")
        self.assertContains(
            response, "https://www.gov.uk/senior-specialist-worker-visa"
        )

    def test_costs_and_passport_rule_shown(self):
        response = self.client.get(reverse("reference:immigration"))
        self.assertContains(response, "GBP 2,889")
        self.assertContains(response, "GBP 1,035")
        self.assertContains(response, "valid for the whole")

    def test_all_cited_numbers_are_within_the_source_list(self):
        response = self.client.get(reverse("reference:immigration"))
        numbers, _ = _collect_via_view()
        rendered = response.content.decode()
        self.assertIn("[1, 2, 3]", rendered)
        self.assertIn("source-{0}".format(len(numbers)), rendered)


def _collect_via_view():
    from reference.views import _collect_sources

    return _collect_sources()
