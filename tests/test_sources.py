"""Source registry integrity.

Supports acceptance gate G3/C3: every source id referenced by a rendered money
line resolves to an official entry with a URL, relevance, effective period and
last-checked date.
"""
import unittest

from calculator import AssignmentInputs, run_assignment
from reference.sources import SOURCES, all_sources, get_source


class SourceRegistryTests(unittest.TestCase):
    def test_all_sources_have_required_fields(self):
        for source in all_sources():
            self.assertTrue(source.title)
            self.assertTrue(source.url.startswith("http"))
            self.assertTrue(source.relevance)
            self.assertTrue(source.effective)
            self.assertTrue(source.last_checked)
            self.assertIn(source.category, ("tax", "immigration"))

    def test_get_source_roundtrip(self):
        self.assertEqual(get_source("zh_stg_35").id, "zh_stg_35")

    def test_every_rendered_source_id_exists(self):
        result = run_assignment(AssignmentInputs())
        referenced = set()
        for year in result.years:
            for section in (year.section_a, year.section_b, year.section_c, year.section_d):
                for line in section:
                    for sid in line.source_ids:
                        referenced.add(sid)
        self.assertTrue(referenced)
        for sid in referenced:
            self.assertIn(sid, SOURCES, "missing source entry for {0}".format(sid))


if __name__ == "__main__":
    unittest.main()
