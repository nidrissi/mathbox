"""Mechanical contract checks, independent of model behavior and math grading."""
import unittest

from check import skill_frontmatter, trigger_contract


class PackageContractTests(unittest.TestCase):
    def test_frontmatter_allows_only_portable_fields_once(self):
        valid = "---\nname: sample\ndescription: >-\n  A bounded task.\n---\n"
        self.assertEqual(skill_frontmatter(valid, "sample"), "A bounded task.")
        for bad in (valid.replace("---\n", "---\nmetadata: host\n", 1),
                    valid.replace("description:", "description: x\ndescription:"),
                    valid.replace("A bounded task.", "x" * 1025),
                    valid.replace("name: sample", "name: other")):
            with self.subTest(bad=bad[:80]), self.assertRaises(ValueError):
                skill_frontmatter(bad, "sample")

    def test_trigger_shapes_and_duplicate_queries(self):
        valid = [{"query": "Audit this computation.", "should_trigger": True}]
        trigger_contract(valid)
        for bad in ([], {}, [{"query": "", "should_trigger": True}],
                    [{"query": "x", "should_trigger": 1}],
                    [{"query": "x", "should_trigger": False, "extra": "ignored"}],
                    valid + valid):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                trigger_contract(bad)

    def test_description_rejects_non_scalar_and_counts_plain_continuation(self):
        for description in ("\n  nested: value", " true", " [one, two]",
                            " Brief.\n  " + "x" * 1025,
                            " >-\n  A" + " " * 1025 + "B"):
            body = "---\nname: sample\ndescription:" + description + "\n---\n"
            with self.subTest(description=description[:40]), self.assertRaises(ValueError):
                skill_frontmatter(body, "sample")
        body = "---\nname: sample\ndescription: Brief.\n  Continued.\n---\n"
        self.assertEqual(skill_frontmatter(body, "sample"), "Brief. Continued.")

    def test_description_counts_decoded_quotes_and_preserves_literal_newlines(self):
        for scalar in ('"A \\u03bb task."', "'A λ task.'", ">-\n  A λ task."):
            body = "---\nname: sample\ndescription: " + scalar + "\n---\n"
            self.assertEqual(skill_frontmatter(body, "sample"), "A λ task.")
        literal = "---\nname: sample\ndescription: |-\n  First.\n  Second.\n---\n"
        self.assertEqual(skill_frontmatter(literal, "sample"), "First.\nSecond.")
