"""Mechanical contract checks, independent of model behavior and math grading."""
import copy
import unittest

from check import codex_marketplace_contract, skill_frontmatter, trigger_contract


class PackageContractTests(unittest.TestCase):
    def test_codex_marketplace_preserves_install_source_and_manifest_identity(self):
        manifest = {"name": "sample", "interface": {
            "displayName": "Sample", "category": "Education & Research",
        }}
        marketplace = {
            "name": "sample-market",
            "interface": {"displayName": "Sample"},
            "plugins": [{
                "name": "sample",
                "source": {"source": "local", "path": "./"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Education & Research",
            }],
        }
        codex_marketplace_contract(marketplace, manifest, "sample-market")
        mutations = (
            ((), "name", "other-market"),
            (("interface",), "displayName", "Other"),
            ((), "plugins", []),
            ((), "plugins", marketplace["plugins"] * 2),
            (("plugins", 0), "name", "other-plugin"),
            (("plugins", 0), "source", "."),
            (("plugins", 0, "source"), "path", "./skills/"),
            (("plugins", 0, "source"), "path", "./../other-plugin"),
            (("plugins", 0), "policy", {}),
            (("plugins", 0, "policy"), "installation", "NOT_AVAILABLE"),
            (("plugins", 0), "category", "Other"),
        )
        for path, key, value in mutations:
            bad = copy.deepcopy(marketplace)
            target = bad
            for part in path:
                target = target[part]
            target[key] = value
            with self.subTest(path=path, key=key, value=value), self.assertRaises(ValueError):
                codex_marketplace_contract(bad, manifest, "sample-market")

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

    def test_description_rejects_invalid_plain_yaml(self):
        for scalar in ("@task", "`task", "%task", "- task", "? task", ",task",
                       "Use this for:\n  a task", "Brief.\n  Continued:",
                       "Brief.\n\tContinued."):
            body = f"---\nname: sample\ndescription: {scalar}\n---\n"
            with self.subTest(scalar=scalar), self.assertRaises(ValueError):
                skill_frontmatter(body, "sample")
        for scalar in ("-task", "@task", "`task", "%task", "Use this for:"):
            body = f"---\nname: sample\ndescription: '{scalar}'\n---\n"
            self.assertEqual(skill_frontmatter(body, "sample"), scalar)

    def test_block_folding_preserves_paragraphs_and_more_indented_lines(self):
        cases = (
            ("  First.\n  Second.\n", "First. Second."),
            ("  First.\n\n  Second.\n", "First.\nSecond."),
            ("  First.\n\n\n  Second.\n", "First.\n\nSecond."),
            ("\n  First.\n", "\nFirst."),
            ("  First.\n    Indented.\n  Last.\n", "First.\n  Indented.\nLast."),
            ("  First.\n\n    Indented.\n\n  Last.\n", "First.\n\n  Indented.\n\nLast."),
            ("  First.\n    \n  Last.\n", "First.\n  \nLast."),
            ("  First.\n\n\n", "First."),
        )
        for block, expected in cases:
            for style in (">-", ">"):
                body = f"---\nname: sample\ndescription: {style}\n{block}---\n"
                with self.subTest(block=block, style=style):
                    self.assertEqual(skill_frontmatter(body, "sample"),
                                     expected + ("\n" if style == ">" else ""))

    def test_description_limit_uses_folded_yaml_value(self):
        scalar = "  " + "A" * 500 + "\n\n  " + "B" * 523 + "\n"
        body = f"---\nname: sample\ndescription: >-\n{scalar}---\n"
        self.assertEqual(len(skill_frontmatter(body, "sample")), 1024)
        for bad in (body.replace("description: >-", "description: >"),
                    body.replace("B" * 523, "B" * 524)):
            with self.assertRaises(ValueError):
                skill_frontmatter(bad, "sample")

    def test_block_description_rejects_yaml_indentation_errors(self):
        for block in ("    First.\n  Less indented.\n", "   \n  First.\n",
                      "\tFirst.\n"):
            body = f"---\nname: sample\ndescription: >-\n{block}---\n"
            with self.subTest(block=block), self.assertRaises(ValueError):
                skill_frontmatter(body, "sample")
