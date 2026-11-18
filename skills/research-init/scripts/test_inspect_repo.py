#!/usr/bin/env python3
"""Synthetic regression tests for the read-only repository inspector."""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from inspect_repo import brief_markdown, classify_research_log, git_state, inspect, markdown, unfenced_lines


class InspectorTests(unittest.TestCase):
    def test_brief_declared_paths_remain_bounded_with_explicit_overflow(self):
        self.write("AGENTS.md", "\n".join(f"- **Claims:** `claims/c{i}.md`" for i in range(30)))
        result = inspect(self.root, 5)
        brief = brief_markdown(result)
        self.assertIn("Declared paths: 30.", brief)
        self.assertIn("22 more; inspect --full", brief)
        self.assertNotIn("`claims/c29.md`", brief)
        self.assertIn("claims/c29.md", markdown(result))

    def test_filled_template_declares_every_live_role_and_fences_are_not_history(self):
        assets = Path(__file__).resolve().parents[1] / "assets"
        template = (assets / "AGENTS.template.md").read_text()
        paths = {"CHARTER_FILE": "PROJECT_CHARTER.md", "STATUS_FILE": "RESEARCH_STATUS.md",
                 "CLAIMS_FILE": "CLAIMS.md", "CONVENTIONS_FILE": "CONVENTIONS.md",
                 "LITERATURE_FILE": "LITERATURE.md", "RESEARCH_LOG": "RESEARCH_LOG.md",
                 "RESEARCH_RECORDS": "research/records", "VERIFICATION_FILE": "VERIFICATION.md",
                 "ROUTE_INDEX_LOCATION": "research/routes.md"}
        for key, value in paths.items():
            template = template.replace("{{" + key + "}}", value)
            if key != "RESEARCH_RECORDS":
                self.write(value)
        self.write("AGENTS.md", template)
        result = inspect(self.root, 5)
        roles = {entry["role"] for entry in result["declared_paths"]}
        self.assertTrue({"charter", "status", "claims", "verification", "route_index"} <= roles)
        self.assertIn("declared_paths", markdown(result))
        self.assertIn("research/routes.md", brief_markdown(result))
        log = self.write("log.md", (assets / "RESEARCH_LOG.template.md").read_text())
        classification = classify_research_log(log)
        self.assertEqual(classification["linked_entries"], 0)
        self.assertEqual(classification["route_markers"], 0)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        # Resolve so path guards still match when the temporary directory sits
        # behind a symlink (for example /var -> /private/var on macOS).
        self.root = Path(self.temporary.name).resolve()

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

    def test_verification_commands_are_not_declared_paths(self):
        self.write("AGENTS.md", "- **Verification:** `python3 scripts/check.py`\n"
                   "- **Verification commands:** `pytest`\n"
                   "- **Verification:** `make`\n"
                   "- **Verification:** `scripts/check.py; exit`\n"
                   "- **Verification:** `VERIFICATION.md`\n"
                   "- **Claims:** `claims/current.md`\n"
                   "```markdown\n- **Status:** `example/STATUS.md`\n```\n")
        result = inspect(self.root, 5)
        self.assertEqual({(entry["role"], entry["path"]) for entry in result["declared_paths"]},
                         {("verification", "VERIFICATION.md"), ("claims", "claims/current.md")})
        self.assertNotIn("python3 scripts/check.py", brief_markdown(result))

    def test_nested_fence_examples_do_not_hide_real_history_or_links(self):
        for marker in ("`", "~"):
            for length in (3, 4):
                with self.subTest(marker=marker, length=length):
                    opener = marker * length
                    other = "~" if marker == "`" else "`"
                    text = (f"{opener}markdown\n{marker * 3}python\n"
                            "[fake](fake.md)\n- **Route**: example\n"
                            f"{opener}still-content\n{other * 3}\n"
                            + ("```\n[fake too](fake-too.md)\n" if length == 4 else "")
                            + f"{opener}  \n"
                            "## 2030-01-02\n- **Route**: Real route\n"
                            "- [Record](records/real.md)\n")
                    path = self.write("RESEARCH_LOG.md", text)
                    result = inspect(self.root, 5)
                    classified = classify_research_log(path)
                    self.assertEqual(classified["classification"], "mixed")
                    self.assertEqual(classified["linked_entries"], 1)
                    self.assertEqual(classified["route_markers"], 2)
                    findings = result["broken_path_references"]
                    self.assertEqual([entry["reference"] for entry in findings], ["records/real.md"])
                    self.assertEqual(findings[0]["line"], len(text.splitlines()))

    def test_unfenced_lines_handles_fence_lengths_kinds_and_unclosed_blocks(self):
        text = ("before\n````markdown\n```python\ninside\n```\n~~~~\n"
                "````comment\n`````\nafter\n~~~text\n```\nunclosed\n")
        self.assertEqual(list(unfenced_lines(text)), [(1, "before"), (9, "after")])

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

    def test_brief_report_bounds_manifests_and_keeps_full_semantic_details_optional(self):
        for number in range(30):
            self.write(f"research/manifests/run-{number:02d}.json", "{}")
            self.write(f"research/records/claim-{number:02d}.md", "# Claim\n")
        result = inspect(self.root, 5)
        brief = brief_markdown(result)
        self.assertIn("## Computation manifests (30)", brief)
        self.assertIn("22 more; use --full or --format json", brief)
        self.assertNotIn("run-29.json", brief)
        self.assertNotIn('"semantic_roles"', brief)
        self.assertIn("run-29.json", markdown(result))
        self.assertIn('"semantic_roles"', markdown(result))

    def test_local_copy_of_every_canonical_skill_is_an_override(self):
        for name in ("referee", "research-state"):
            self.write(f".claude/skills/{name}/SKILL.md", f"---\nname: {name}\n---\n")
        self.write(".claude/skills/project-only/SKILL.md", "---\nname: project-only\n---\n")
        self.assertEqual(inspect(self.root, 5)["canonical_name_overrides"], ["referee", "research-state"])

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

    def test_designated_cache_and_symlinked_direct_sources_never_open(self):
        external = tempfile.TemporaryDirectory()
        self.addCleanup(external.cleanup)
        outside = Path(external.name).resolve()
        (outside / "config.json").write_text("{}")
        private = outside / "private.md"
        private.write_text("- **Status:** `private.md`\n")
        cache = self.root / "papers/local"
        self.write("papers/local/STATUS.md")
        self.write("papers/local/map.json", "{}")
        declared_cache = self.root / "Local Papers"
        self.write("Local Papers/Extract.txt", "[private](some-source.md)")
        (self.root / "docs").mkdir()
        self.write("AGENTS.md", "- **Project map:** `docs/../papers/local/map.json`\n"
                   "- **Local literature cache:** `Local Papers/`\n")
        (self.root / "CLAUDE.md").symlink_to(private)
        (self.root / ".mathbox").symlink_to(outside, target_is_directory=True)

        real_open = Path.open
        def guarded_open(path, *args, **kwargs):
            self.assertFalse(path.resolve().is_relative_to(cache), path)
            self.assertFalse(path.resolve().is_relative_to(outside), path)
            self.assertFalse(path.resolve().is_relative_to(declared_cache), path)
            return real_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            result = inspect(self.root, 5, ("papers/local",))
            self.assertEqual(result["skipped_direct_paths"], [".mathbox/config.json", "CLAUDE.md"])
            self.assertIsNone(result["research_ledger"]["exists"])
            self.assertEqual(result["research_ledger"]["status"], "unverified")
            self.assertIn("Research ledger: unverified", brief_markdown(result))
            self.assertIn("unverified; metadata inspection skipped", markdown(result))
            self.assertIn("Local Papers", [item["path"] for item in result["source_cache_conventions"]])
            self.assertEqual([(item["path"], item["basis"]) for item in result["project_maps"]],
                             [("docs/../papers/local/map.json",
                               "declared in AGENTS.md; not inspected: inside a source cache")])
            self.assertIn("not inspected: inside a source cache", brief_markdown(result))
            self.assertFalse(result["live_state_candidates"]["dashboard_candidates"])
            self.assertIn("CLAUDE.md", brief_markdown(result))
            (self.root / "AGENTS.md").unlink()
            (self.root / "AGENTS.md").symlink_to(private)
            result = inspect(self.root, 5, ("papers/local", "Local Papers"))
            self.assertIn("AGENTS.md", result["skipped_direct_paths"])
            self.assertFalse(result["declared_paths"])

    def test_declared_cache_spellings_resolve_to_the_directory_and_are_pruned(self):
        self.write("Local Papers/STATUS.md")
        self.write("Literal%20Dir/STATUS.md")
        real_open = Path.open

        def guarded_open(path, *args, **kwargs):
            for cache in ("Local Papers", "Literal%20Dir"):
                self.assertFalse(path.resolve().is_relative_to(self.root / cache), path)
            return real_open(path, *args, **kwargs)

        for spelling in ("Local Papers/", "<Local Papers/>", "Local%20Papers/", "<Local%20Papers>"):
            with self.subTest(spelling=spelling):
                self.write("AGENTS.md", f"- **Literature cache:** `{spelling}`\n"
                           "- **Source cache:** `Literal%20Dir/`\n")
                with patch.object(Path, "open", guarded_open):
                    result = inspect(self.root, 5)
                caches = {item["path"]: item for item in result["source_cache_conventions"]}
                self.assertTrue(caches["Local Papers"]["exists"])
                self.assertTrue(caches["Local Papers"]["declared"])
                self.assertTrue(caches["Literal%20Dir"]["exists"])
                self.assertEqual(result["live_state_candidates"]["dashboard_candidates"], [])

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_cache_declared_as_scan_root_is_rejected_not_applied(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        self.write("AGENTS.md", "- **Literature cache:** `./`\n- **Paper cache:** `notes/..`\n")
        self.write("STATUS.md")
        self.write("notes/STATUS.md")
        self.write(".mathbox/config.json", "{}")
        result = inspect(self.root, 5)
        self.assertEqual([(item["path"], item["line"], item["reason"])
                          for item in result["rejected_cache_declarations"]],
                         [(".", 1, "resolves to the scan root"),
                          ("notes/..", 2, "resolves to the scan root")])
        self.assertNotIn(".", [item["path"] for item in result["source_cache_conventions"]])
        self.assertEqual(result["git"]["state"], "dirty")
        self.assertEqual(result["git"]["status_excludes"], [".research-cache/literature"])
        self.assertEqual(result["live_state_candidates"]["dashboard_candidates"],
                         ["STATUS.md", "notes/STATUS.md"])
        self.assertIn("AGENTS.md", {item["path"] for item in result["instructions"]})
        self.assertEqual(result["research_ledger"]["status"], "present")
        self.assertIn("Rejected source-cache declaration `.` (AGENTS.md:1)", brief_markdown(result))
        self.assertIn("Rejected source-cache declaration `notes/..`", markdown(result))

    def test_declared_project_map_accepts_in_root_parent_component(self):
        (self.root / "docs").mkdir()
        self.write("navigation.json", "{}\n")
        self.write("AGENTS.md", "- **Project map:** `docs/../navigation.json`\n")
        self.assertEqual(inspect(self.root, 5)["project_maps"], [
            {"path": "docs/../navigation.json", "bytes": 3, "lines": 1,
             "basis": "declared in AGENTS.md"},
        ])

    def test_declared_project_maps_outside_the_read_policy_stay_reported(self):
        self.write("docs/build/map.md")
        self.write("docs/real/map.md")
        self.write("navigation.json", "{}\n")
        (self.root / "alias").symlink_to(self.root / "docs/real", target_is_directory=True)
        (self.root / "docs_alias").symlink_to(self.root / "docs", target_is_directory=True)
        self.write("AGENTS.md", "- **Project map:** `docs/real/../build/map.md`\n"
                   "- **Code map:** `alias/map.md`\n"
                   "- **Project map:** `docs_alias/../navigation.json`\n"
                   "- **Repository map:** `docs/missing.md`\n")
        bases = {item["path"]: item["basis"] for item in inspect(self.root, 5)["project_maps"]}
        self.assertEqual(bases, {
            "docs/real/../build/map.md": "declared in AGENTS.md; not inspected: under an excluded directory",
            "alias/map.md": "declared in AGENTS.md; not inspected: symlinked or outside the scan root",
            "docs_alias/../navigation.json": "declared in AGENTS.md; not inspected: symlinked or outside the scan root",
            "docs/missing.md": "declared in AGENTS.md; missing",
        })

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_tracked_rule_must_match_the_index_and_survive_tracked_cache_entries(self):
        def git(*args):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

        def coverage():
            result = inspect(self.root, 5, ("papers/local",))
            return next(item for item in result["source_cache_conventions"] if item["path"] == "papers/local")

        git("init", "-q")
        self.write("papers/local/a.pdf", "synthetic")
        self.write(".gitignore", "/papers/local/\n")
        git("add", "--", ".gitignore")
        git("add", "-f", "--", "papers/local/a.pdf")
        cache = coverage()
        self.assertTrue(cache["git_ignored"])
        self.assertTrue(cache["repository_ignore_rule"])
        self.assertEqual(cache["ignore_rule_source"], ".gitignore")
        self.assertEqual(cache["tracked_entries"], 1)

        self.write(".gitignore", "*.log\n")
        git("add", "--", ".gitignore")
        self.write(".gitignore", "*.log\n/papers/local/\n")  # unstaged rule
        cache = coverage()
        self.assertTrue(cache["git_ignored"])
        self.assertFalse(cache["repository_ignore_rule"])
        git("add", "--", ".gitignore")
        self.assertTrue(coverage()["repository_ignore_rule"])

        self.write("papers/.gitignore", "*.tmp\n")
        git("add", "--", "papers/.gitignore")
        self.write("docs/.gitignore", "*.aux\n")
        git("add", "--", "docs/.gitignore")
        self.write("docs/.gitignore", "*.aux\n*.out\n")  # unrelated unstaged edit
        self.assertTrue(coverage()["repository_ignore_rule"])
        (self.root / "papers/.gitignore").unlink()  # an applicable tracked file now differs
        self.assertFalse(coverage()["repository_ignore_rule"])

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_unanswerable_ignore_checks_stay_unverified(self):
        import inspect_repo

        subprocess.run(["git", "init", "-q", str(self.root)], check=True, capture_output=True)
        (self.root / "vendor2/cache").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.root / "vendor2")], check=True, capture_output=True)
        result = inspect(self.root, 5, ("vendor2/cache",))
        cache = next(item for item in result["source_cache_conventions"] if item["path"] == "vendor2/cache")
        self.assertIsNone(cache["git_ignored"])
        self.assertEqual(cache["coverage_note"], "inside a nested repository or submodule")
        self.assertIn("Git ignore coverage unverified (inside a nested repository or submodule)",
                      brief_markdown(result))

        (self.root / "papers/local").mkdir(parents=True)
        real = inspect_repo.git_run

        def failing(root, *args, **kwargs):
            if "check-ignore" in args:
                return subprocess.CompletedProcess(args, 128, "", "")
            return real(root, *args, **kwargs)

        with patch.object(inspect_repo, "git_run", failing):
            result = inspect(self.root, 5, ("papers/local",))
        cache = next(item for item in result["source_cache_conventions"] if item["path"] == "papers/local")
        self.assertIsNone(cache["git_ignored"])
        self.assertEqual(cache["coverage_note"], "git check-ignore failed")

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_cache_directory_requires_effective_tracked_project_rule(self):
        def git(*args):
            subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

        def alternate():
            result = inspect(self.root, 5, ("papers/local",))
            return next(item for item in result["source_cache_conventions"] if item["path"] == "papers/local")

        git("init", "-q")
        rules = self.write("global-ignore", "*.pdf\n")
        git("config", "core.excludesFile", str(rules))
        self.write(".gitignore", "/papers/local/\n")
        self.assertIsNone(alternate()["git_ignored"])
        self.write(".gitignore", "")
        (self.root / "papers/local").mkdir(parents=True)
        self.assertFalse(alternate()["git_ignored"])
        rules.write_text("papers/local/\n")
        self.assertTrue(alternate()["git_ignored"])
        self.assertFalse(alternate()["repository_ignore_rule"])
        self.write(".gitignore", "/papers/local/\n")
        self.assertFalse(alternate()["repository_ignore_rule"])
        git("add", "--", ".gitignore")
        self.assertTrue(alternate()["repository_ignore_rule"])
        self.write(".gitignore", "/papers/local/*\n!/papers/local/keep.txt\n")
        rules.write_text("")
        git("add", "--", ".gitignore")
        git("check-ignore", "--", "papers/local/new.pdf")
        keep_check = subprocess.run(["git", "-C", str(self.root), "check-ignore", "-q",
                                     "--", "papers/local/keep.txt"])
        self.assertEqual(keep_check.returncode, 1)
        self.assertFalse(alternate()["repository_ignore_rule"])
        self.write(".gitignore", "/papers/local/\n!/papers/local/\n")
        self.assertFalse(alternate()["repository_ignore_rule"])

    @unittest.skipUnless(sys.platform == "linux" and shutil.which("git"), "requires Linux inotify and Git")
    def test_git_status_does_not_open_tracked_cache_file(self):
        def git(*args):
            return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

        cache_dir = "papers/[private]"
        cached = self.write(f"{cache_dir}/paper.pdf", "synthetic cached content")
        self.write("STATUS.md")
        git("init", "-q")
        git("add", "--", ".")
        os.utime(cached, (946684800, 946684800))  # Force a content comparison on an unscoped refresh.
        libc = ctypes.CDLL(None, use_errno=True)
        watcher = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        self.assertGreaterEqual(watcher, 0)
        self.addCleanup(os.close, watcher)
        self.assertGreaterEqual(libc.inotify_add_watch(watcher, os.fsencode(cached), 0x20), 0)  # IN_OPEN
        git("--no-optional-locks", "status", "--short")
        self.assertTrue(os.read(watcher, 4096))
        with patch.dict(os.environ, GIT_LITERAL_PATHSPECS="1"):
            result = inspect(self.root, 5, (cache_dir,))
        self.assertIn("STATUS.md", result["git_status"])
        self.assertNotIn("paper.pdf", result["git_status"])
        self.assertIn(cache_dir, result["git"]["status_excludes"])
        cache = next(item for item in result["source_cache_conventions"] if item["path"] == cache_dir)
        self.assertEqual(cache["tracked_entries"], 1)
        self.assertIn("already tracked index entries: 1", brief_markdown(result))
        with self.assertRaises(BlockingIOError):
            os.read(watcher, 4096)

    def test_depth_and_non_git_coverage_remain_explicit(self):
        self.write("a/b/c/d/e/f/STATUS.md")
        self.write("AGENTS.md", "- **Status:** `a/b/c/d/e/f/STATUS.md`\n")
        result = inspect(self.root, 5)
        self.assertIsNone(result["literature_cache"]["git_ignored"])
        self.assertIn("Git ignore coverage unverified", brief_markdown(result))
        self.assertIn("scan depth 5", brief_markdown(result))
        self.assertEqual(result["live_state_candidates"]["dashboard_candidates"], [])
        self.assertEqual(result["declared_paths"][0]["path"], "a/b/c/d/e/f/STATUS.md")
        self.assertEqual(inspect(self.root, 6)["live_state_candidates"]["dashboard_candidates"],
                         ["a/b/c/d/e/f/STATUS.md"])

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
