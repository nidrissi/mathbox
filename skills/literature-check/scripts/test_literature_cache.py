#!/usr/bin/env python3
"""Focused standard-library tests for literature_cache.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("literature_cache.py")
SPEC = importlib.util.spec_from_file_location("literature_cache", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot import {SCRIPT}")
CACHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CACHE)


class LiteratureCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="mathbox-literature-cache-")
        self.base = Path(self.temporary.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "-C", str(self.repo), "init", "-q"], check=True)
        self.pdf = self.base / "fixture.pdf"
        self.pdf.write_bytes(b"%PDF-1.4\npublic-domain test fixture\n%%EOF\n")
        self.text = self.base / "fixture.txt"
        self.text.write_text("Grothendieck spectral sequence fixture text\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def invoke(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments, "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    def run_cache(self, *arguments: str, expected: int = 0) -> dict:
        process = self.invoke(*arguments)
        self.assertEqual(process.returncode, expected, process.stderr or process.stdout)
        return json.loads(process.stdout)

    def records_dir(self) -> Path:
        return self.repo / ".research-cache/literature/records"

    def add_fixture(self, *, no_extract: bool = False) -> dict:
        arguments = [
            "add", "--root", str(self.repo), "--pdf", str(self.pdf),
            "--id", "doi:https://doi.org/10.1000/ABC",
            "--id", "arxiv:2401.00001v2", "--title", "Fixture Paper",
            "--author", "A. Author", "--version", "v2",
            "--retention-basis", "public-domain test fixture",
        ]
        if no_extract:
            arguments.append("--no-extract")
        else:
            arguments.extend(("--text", str(self.text), "--text-tool", "fixture-extractor"))
        return self.run_cache(*arguments)

    def add_pdf(self, name: str, body: str, *identifier: str) -> dict:
        pdf = self.base / f"{name}.pdf"
        pdf.write_bytes(f"%PDF-1.4\n{body}\n%%EOF\n".encode())
        arguments = ["add", "--root", str(self.repo), "--pdf", str(pdf), "--title", name,
                     "--retention-basis", "test fixture", "--no-extract"]
        for item in identifier:
            arguments.extend(("--id", item))
        return self.run_cache(*arguments)

    def test_ingest_deduplicate_find_and_ignore(self) -> None:
        initialized = self.run_cache("init", "--root", str(self.repo))
        self.assertTrue(initialized["git_ignored"])

        added = self.add_fixture()
        updated = self.add_fixture()
        self.assertEqual(added["action"], "added")
        self.assertEqual(added["record"]["extraction"]["tool"], "fixture-extractor")
        self.assertEqual(updated["action"], "updated")
        self.assertEqual(len(list(self.records_dir().glob("*.json"))), 1)

        doi = self.run_cache(
            "find", "--root", str(self.repo), "--id", "doi:10.1000/abc"
        )
        self.assertEqual(doi["count"], 1)
        self.assertEqual(doi["matches"][0]["match"], "exact-identifier")

        wrong_version = self.run_cache(
            "find", "--root", str(self.repo), "--id", "arxiv:2401.00001v3"
        )
        self.assertEqual(wrong_version["count"], 1)
        self.assertEqual(wrong_version["matches"][0]["match"], "arxiv-version-candidate")

        full_text = self.run_cache(
            "find", "--root", str(self.repo), "--query", "spectral sequence"
        )
        self.assertEqual(full_text["matches"][0]["match"], "text")
        self.assertIn("spectral sequence", full_text["matches"][0]["snippet"])

        status = subprocess.run(
            ["git", "-C", str(self.repo), "status", "--short"],
            stdout=subprocess.PIPE, text=True, check=True,
        )
        self.assertEqual(status.stdout, "")

    def test_pdf_only_is_valid_without_extractor(self) -> None:
        result = self.add_fixture(no_extract=True)
        self.assertEqual(result["record"]["extraction"]["status"], "not-requested")
        self.assertNotIn("text", result["record"])
        verified = self.run_cache("verify", "--root", str(self.repo))
        self.assertTrue(verified["valid"])

        with mock.patch.object(CACHE.shutil, "which", return_value=None):
            text, provenance = CACHE.extract_text(self.pdf, None, False)
        self.assertIsNone(text)
        self.assertEqual(provenance["status"], "unavailable")

    def test_verify_detects_corrupt_text(self) -> None:
        result = self.add_fixture()
        digest = result["record"]["sha256"]
        cached_text = self.repo / ".research-cache/literature/text" / f"{digest}.txt"
        cached_text.write_text("changed\n", encoding="utf-8")
        verified = self.run_cache("verify", "--root", str(self.repo), expected=1)
        self.assertFalse(verified["valid"])
        self.assertIn(
            "text hash mismatch or unreadable", {item["issue"] for item in verified["issues"]}
        )

    def test_ingest_refuses_when_ignore_cannot_be_verified(self) -> None:
        with mock.patch.object(CACHE, "git_ignore_source", return_value=None):
            with self.assertRaisesRegex(CACHE.CacheError, "refusing to store sources"):
                CACHE.initialize(self.repo)

    def test_identifier_normalization(self) -> None:
        self.assertEqual(
            CACHE.normalize_identifier("doi:https://doi.org/10.1000/ABC"),
            "doi:10.1000/abc",
        )
        self.assertEqual(
            CACHE.normalize_identifier("arxiv:https://arxiv.org/pdf/2401.00001v2.pdf"),
            "arxiv:2401.00001v2",
        )

    def test_repository_rule_is_distinguished_from_the_cache_rule(self) -> None:
        own = self.run_cache("init", "--root", str(self.repo))
        self.assertTrue(own["git_ignored"])
        self.assertFalse(own["git_ignore_repository_rule"])
        self.assertEqual(own["git_ignore_source"], ".research-cache/.gitignore")
        self.assertTrue(any("add /.research-cache/" in item for item in own["warnings"]))

        (self.repo / ".gitignore").write_text("/.research-cache/\n", encoding="utf-8")
        tracked = self.run_cache("init", "--root", str(self.repo))
        self.assertTrue(tracked["git_ignore_repository_rule"])
        self.assertNotIn("warnings", tracked)

    def test_read_only_commands_do_not_create_the_cache(self) -> None:
        found = self.run_cache("find", "--root", str(self.repo), "--query", "anything")
        self.assertFalse(found["cache_present"])
        self.assertEqual(found["count"], 0)
        verified = self.run_cache("verify", "--root", str(self.repo))
        self.assertFalse(verified["cache_present"])
        self.assertFalse((self.repo / ".research-cache").exists())

    def test_malformed_artifact_entry_is_not_reported_as_an_orphan(self) -> None:
        digest = self.add_fixture(no_extract=True)["record"]["sha256"]
        record_path = self.records_dir() / f"{digest}.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["pdf"] = "not-a-dict"
        record_path.write_text(json.dumps(record), encoding="utf-8")

        verified = self.run_cache("verify", "--root", str(self.repo), expected=1)
        issues = [item["issue"] for item in verified["issues"]]
        self.assertIn("invalid pdf entry in cache record", issues)
        self.assertNotIn("orphaned artifact", issues)

        # The same record must not crash a lookup either.
        found = self.run_cache("find", "--root", str(self.repo), "--query", "Fixture")
        self.assertEqual(found["count"], 1)
        self.assertIsNone(found["matches"][0]["pdf_path"])
        self.assertIn("invalid pdf entry in cache record", found["matches"][0]["issues"])

    def test_stray_artifact_is_still_reported_as_an_orphan(self) -> None:
        self.add_fixture(no_extract=True)
        (self.repo / ".research-cache/literature/text/deadbeef.txt").write_text("x", encoding="utf-8")
        verified = self.run_cache("verify", "--root", str(self.repo), expected=1)
        self.assertEqual(
            [item for item in verified["issues"] if item["issue"] == "orphaned artifact"],
            [{"path": "text/deadbeef.txt", "issue": "orphaned artifact"}],
        )

    def test_unreadable_record_does_not_abort_a_search(self) -> None:
        self.add_fixture(no_extract=True)
        self.add_pdf("second", "another fixture", "doi:10.1000/second")
        broken = self.records_dir() / f"{'a' * 64}.json"
        broken.write_text("not json", encoding="utf-8")

        found = self.run_cache("find", "--root", str(self.repo), "--query", "Fixture")
        self.assertEqual(found["count"], 1)
        self.assertEqual([item["record"] for item in found["unreadable_records"]], [broken.name])

    def test_find_by_identifier_honours_limit(self) -> None:
        for index in (1, 2, 3):
            self.add_pdf(f"version-{index}", f"body {index}", f"arxiv:2401.09999v{index}")
        unbounded = self.run_cache("find", "--root", str(self.repo), "--id", "arxiv:2401.09999v9")
        self.assertEqual(unbounded["count"], 3)
        bounded = self.run_cache(
            "find", "--root", str(self.repo), "--id", "arxiv:2401.09999v9", "--limit", "1"
        )
        self.assertEqual(bounded["count"], 1)

    def test_text_tool_requires_text_on_every_path(self) -> None:
        self.add_fixture()
        process = self.invoke(
            "add", "--root", str(self.repo), "--pdf", str(self.pdf),
            "--retention-basis", "test fixture", "--text-tool", "other-extractor",
        )
        self.assertEqual(process.returncode, CACHE.EXIT_ERROR)
        self.assertIn("--text-tool requires --text", json.loads(process.stdout)["error"])

    def test_metadata_conflict_needs_an_explicit_override(self) -> None:
        self.add_fixture(no_extract=True)
        conflicting = [
            "add", "--root", str(self.repo), "--pdf", str(self.pdf),
            "--title", "Fixture Paper (revised)",
            "--retention-basis", "test fixture", "--no-extract",
        ]
        refused = self.run_cache(*conflicting, expected=CACHE.EXIT_ERROR)
        self.assertIn("--replace-metadata", refused["error"])
        replaced = self.run_cache(*conflicting, "--replace-metadata")
        self.assertEqual(replaced["record"]["title"], "Fixture Paper (revised)")

    def test_refuses_to_write_an_artifact_git_already_tracks(self) -> None:
        digest = self.add_fixture(no_extract=True)["record"]["sha256"]
        artifact = f".research-cache/literature/pdf/{digest}.pdf"
        subprocess.run(["git", "-C", str(self.repo), "add", "-f", artifact], check=True)
        subprocess.run(
            ["git", "-C", str(self.repo), "-c", "user.email=t@example.invalid",
             "-c", "user.name=Test", "commit", "-qm", "track artifact"],
            check=True,
        )
        refused = self.run_cache(
            "add", "--root", str(self.repo), "--pdf", str(self.pdf),
            "--retention-basis", "test fixture", "--no-extract",
            expected=CACHE.EXIT_ERROR,
        )
        self.assertIn("because Git does not ignore it", refused["error"])

    def test_snippet_stays_bounded_and_shows_a_long_match(self) -> None:
        query = "the composite of two left exact functors between abelian categories " * 3
        text = f"{'lead ' * 40}{query}{' trail' * 40}"
        snippet = CACHE.bounded_snippet(text, query)
        self.assertIsNotNone(snippet)
        self.assertLessEqual(len(snippet), 260)
        self.assertIn("the composite of two left exact", snippet)
        self.assertIn("abelian categories", snippet)

    def test_date_checked_uses_utc(self) -> None:
        record = self.add_fixture(no_extract=True)["record"]
        self.assertEqual(record["date_checked"], CACHE.utc_today())
        self.assertTrue(record["updated_at"].startswith(record["date_checked"]))

    def test_unexpected_failure_uses_a_distinct_exit_status(self) -> None:
        with mock.patch.object(CACHE, "open_cache", side_effect=ValueError("boom")):
            status = CACHE.main(["find", "--root", str(self.repo), "--query", "x"])
        self.assertEqual(status, CACHE.EXIT_INTERNAL)
        self.assertNotEqual(status, CACHE.EXIT_INVALID)


if __name__ == "__main__":
    unittest.main()
