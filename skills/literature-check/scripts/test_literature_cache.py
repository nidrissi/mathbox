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

    def run_cache(self, *arguments: str, expected: int = 0) -> dict:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), *arguments, "--format", "json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, expected, process.stderr or process.stdout)
        return json.loads(process.stdout)

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

    def test_ingest_deduplicate_find_and_ignore(self) -> None:
        initialized = self.run_cache("init", "--root", str(self.repo))
        self.assertTrue(initialized["git_ignored"])

        added = self.add_fixture()
        updated = self.add_fixture()
        self.assertEqual(added["action"], "added")
        self.assertEqual(added["record"]["extraction"]["tool"], "fixture-extractor")
        self.assertEqual(updated["action"], "updated")
        record_files = list((self.repo / ".research-cache/literature/records").glob("*.json"))
        self.assertEqual(len(record_files), 1)

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
        self.assertIn("text hash mismatch", {item["issue"] for item in verified["issues"]})

    def test_ingest_refuses_when_ignore_cannot_be_verified(self) -> None:
        with mock.patch.object(CACHE, "git_ignores", return_value=False):
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


if __name__ == "__main__":
    unittest.main()
