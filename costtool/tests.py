"""Smoke tests: project runs, both primary tabs respond."""
from django.test import SimpleTestCase, TestCase


class SmokeTests(SimpleTestCase):
    def test_cost_estimate_tab_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cost Estimate')

    def test_immigration_tab_loads(self):
        response = self.client.get('/immigration/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Immigration')

    def test_both_tabs_present_on_each_page(self):
        for url in ('/', '/immigration/'):
            response = self.client.get(url)
            self.assertContains(response, 'Cost Estimate')
            self.assertContains(response, 'Immigration')
