#!/usr/bin/env python3
"""Synthetic regression tests for the read-only repository inspector."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from inspect_repo import brief_markdown, classify_research_log, git_state, inspect, markdown


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative: str, content: str = "# Synthetic fixture\n") -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_semantic_aliases_manifests_duplicates_without_bridge(self):
        for name in (
            "PLAN.md", "STATUS.md", "notes/STATUS-team.md", "OUTLINE.md",
            "MANIFEST.md", "THEOREMS.md", "FACT_INVENTORY.md",
            "HANDOFF-next.md", "notes/TEAM_HANDOFF.md", "AGENTS.md",
        ):
            self.write(name)
        manifest = {
            "schema_version": 1,
            "claim_id": "C-SYNTHETIC",
            "mathematics": {},
            "run": {},
            "outputs": [],
        }
        self.write("computations/bounded_run_manifest.json", json.dumps(manifest))
        self.write("research/manifests/2030-01-02-bounded-run.json", json.dumps(manifest))

        result = inspect(self.root, 5)
        roles = result["semantic_roles"]
        self.assertEqual({item["path"] for item in roles["plan"]}, {"PLAN.md"})
        self.assertEqual({item["path"] for item in roles["outline"]}, {"OUTLINE.md"})
        self.assertEqual({item["path"] for item in roles["theorem_inventory"]}, {"THEOREMS.md"})
        self.assertEqual({item["path"] for item in roles["fact_inventory"]}, {"FACT_INVENTORY.md"})
        self.assertTrue(result["live_state_candidates"]["duplicate_dashboard_candidates"])
        self.assertTrue(result["live_state_candidates"]["duplicate_handoff_candidates"])
        self.assertIsNone(result["claude_bridge"]["issue"])
        self.assertFalse(result["claude_bridge"]["claude_exists"])
        self.assertEqual(len(result["computation_manifests"]), 2)
        self.assertTrue(all(item["classification"] == "mathbox-like" for item in result["computation_manifests"]))

    def test_broken_links_and_backtick_paths_are_conservative(self):
        self.write("PLAN.md")
        self.write(
            "docs/guide.md",
            "[working](../PLAN.md) and [missing](missing.md)\n"
            "See `proof/missing.tex`, but mathematical `x/y` is not a path candidate.\n"
            "```text\n[example](not-real.md) and `docs/not-real.md`\n```\n",
        )

        result = inspect(self.root, 5)
        found = {(item["kind"], item["reference"]) for item in result["broken_path_references"]}
        self.assertEqual(found, {
            ("markdown-link", "missing.md"),
            ("backtick-path", "proof/missing.tex"),
        })

    def test_brief_report_counts_historical_candidates_without_dumping_them(self):
        self.write("docs/live.md", "\n".join(f"[missing](missing-{i}.md)" for i in range(12)))
        self.write("research/imports/old.md", "\n".join(f"[old](missing-{i}.md)" for i in range(310)))
        result = inspect(self.root, 5)
        brief = brief_markdown(result)
        self.assertIn("Current-path candidates: 12; historical-path candidates: 310", brief)
        self.assertIn("4 more current-path candidates", brief)
        self.assertNotIn("research/imports/old.md:1", brief)
        self.assertIn("research/imports/old.md:1", markdown(result))
        self.assertLess(len(brief), 4000)

    def test_brief_report_keeps_route_record_links_current(self):
        self.write("research/records/2026-01-01-route.md", "[proof](../../proofs/moved.tex)\n")
        self.write("research/legacy/old-log.md", "[old](missing.md)\n")
        brief = brief_markdown(inspect(self.root, 5))
        self.assertIn("Current-path candidates: 1; historical-path candidates: 1", brief)
        self.assertIn("research/records/2026-01-01-route.md:1", brief)

    def test_brief_report_keeps_classifications_and_skill_findings(self):
        self.write("RESEARCH_LOG.md", "# Research log\n\n## 2030-01-01\n\n- **Route**: lift\n")
        self.write("skills/foo/SKILL.md", "---\nname: foo\n---\n")
        self.write(".claude/skills/bar/SKILL.md", "---\nname: bar\n---\n")
        self.write("Makefile", "check:\n\ttrue\n")
        self.write("research/manifests/run.json", "{}")
        brief = brief_markdown(inspect(self.root, 5))
        self.assertIn("`RESEARCH_LOG.md` — long-form-legacy;", brief)
        self.assertIn("`research/manifests/run.json` — location/name-candidate;", brief)
        self.assertIn("## Misplaced root skills (1)", brief)
        self.assertIn("`skills/foo/SKILL.md`", brief)
        self.assertIn("## Project skill files (1)", brief)
        self.assertIn("## Build/verification manifests (1)", brief)

    def test_live_summary_reports_checkpoint_markers_without_promoting_snapshots(self):
        self.write("RESEARCH_STATUS.md", "# Current status\n\n## Previous checkpoint 2030-01-01\n\n## 2030-01-02 update\n")
        self.write("research/migrations/status-before.md", "# Historical snapshot\n")
        result = inspect(self.root, 5)
        self.assertEqual(result["live_state_candidates"]["dashboard_candidates"], ["RESEARCH_STATUS.md"])
        self.assertEqual(result["live_state_candidates"]["summary_sizes"][0]["checkpoint_markers"], 2)
        self.assertIn("2 dated/previous checkpoint marker(s), tentative", brief_markdown(result))

    def test_log_classification_uses_structure_not_length(self):
        compact = self.write(
            "compact/RESEARCH_LOG.md",
            "# Research log\n\n- 2030-01-02 — [Route](records/route.md) — open.\n",
        )
        long_form = self.write(
            "legacy/RESEARCH_LOG.md",
            "# Research log\n\n## 2030-01-02 -- route\n\n- **Idea:** Test a boundary case.\n- **Outcome:** Inconclusive.\n",
        )
        mixed = self.write(
            "mixed/RESEARCH_LOG.md",
            "# Research log\n\n- 2030-01-01 — [Old route](records/old.md).\n"
            "## 2030-01-02 -- new route\n\n- **Target:** A synthetic claim.\n",
        )

        self.assertEqual(classify_research_log(compact)["classification"], "compact-linked-index")
        self.assertEqual(classify_research_log(long_form)["classification"], "long-form-legacy")
        self.assertEqual(classify_research_log(mixed)["classification"], "mixed")

    def test_declared_map_and_alternate_source_cache_are_reported(self):
        self.write(
            "AGENTS.md",
            "# Instructions\n\n- **Project map:** `docs/path-map.json`\n"
            "- **Local literature cache:** `refs/papers/`\n",
        )
        self.write("CLAUDE.md", "@AGENTS.md\n")
        self.write("docs/path-map.json", "{}\n")
        self.write("refs/papers/source.pdf", "synthetic, not a real source\n")
        self.write("refs/papers/STATUS.md", "# Cache content must not be inventoried\n")

        result = inspect(self.root, 5)
        declared = {(item["role"], item["path"]) for item in result["declared_paths"]}
        self.assertIn(("project_map", "docs/path-map.json"), declared)
        self.assertIn(("source_cache", "refs/papers"), declared)
        alternate = {item["path"]: item for item in result["source_cache_conventions"]}
        self.assertTrue(alternate["refs/papers"]["declared"])
        self.assertEqual(alternate["refs/papers"]["confidence"], "high")
        self.assertEqual(result["project_maps"][0]["path"], "docs/path-map.json")
        self.assertNotIn("refs/papers/STATUS.md", {item["path"] for item in result["research_role_files"]})
        self.assertIsNone(result["claude_bridge"]["issue"])

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_git_clean_is_distinct_from_unavailable(self):
        self.assertEqual(git_state(self.root)["state"], "unavailable")
        subprocess.run(
            ["git", "init", "-q", str(self.root)], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(git_state(self.root)["state"], "clean")
        self.write("PLAN.md")
        self.assertEqual(git_state(self.root)["state"], "dirty")

    def test_existing_claude_file_without_import_is_flagged(self):
        self.write("AGENTS.md")
        self.write("CLAUDE.md", "# Separate duplicated instructions\n")
        result = inspect(self.root, 5)
        self.assertEqual(result["claude_bridge"]["issue"], "CLAUDE.md does not import @AGENTS.md")

    def test_symlinked_files_are_not_read_or_classified(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "STATUS.md"
        target.write_text("# External material\n", encoding="utf-8")
        link = self.root / "STATUS-linked.md"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        result = inspect(self.root, 5)
        self.assertNotIn(
            "STATUS-linked.md",
            {item["path"] for item in result["research_role_files"]},
        )


if __name__ == "__main__":
    unittest.main()
