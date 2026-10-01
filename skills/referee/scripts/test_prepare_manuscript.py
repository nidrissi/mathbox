"""Direct preparation regressions; no credentials, network or behavior keyword grading."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import prepare_manuscript as prep


def paper(body, preamble=""):
    return preamble + "\\begin{document}\n" + body + "\\end{document}\n"


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.main = self.root / "paper.tex"

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path

    def prepare(self, text=None, previous=None):
        if text is not None:
            self.put("paper.tex", text)
        return prep.prepare(self.main, self.root, previous)

    def snapshot(self, name, text, previous=None):
        result = self.prepare(text, previous)
        out = self.root / name
        prep.write_snapshot(out, *result)
        return result[0], out / "manifest.json"

    def test_comment_mask_preserves_offsets_lines_and_escape_parity(self):
        text = "50\\% done % hide\r\n" + r"\\% comment" + "\nbody\n"
        masked = prep.mask_non_content(text)
        self.assertEqual(len(masked), len(text))
        self.assertEqual([i for i, c in enumerate(masked) if c in "\r\n"],
                         [i for i, c in enumerate(text) if c in "\r\n"])
        self.assertIn("done", masked)
        self.assertNotIn("hide", masked)
        self.assertNotIn("comment", masked)
        self.assertIn("body", masked)

    def test_fake_sections_in_comments_literals_and_escaped_commands(self):
        text = paper("\\section{Real}\nbefore\n% \\section{Comment}\n"
                     "\\begin{verbatim}\n\\section{References}\n% literal\n\\end{verbatim}\n"
                     r"\verb|\section{Inline}| \lstinline!\section{Listing}! \\section{Escaped}"
                     "\nafter\n\\section{Last}\nend\n")
        manifest, tex, _ = self.prepare(text)
        self.assertEqual([u["title"] for u in manifest["units"]], ["Real", "Last"])
        first = manifest["units"][0]
        self.assertIn("after", tex[first["expanded_start"]:first["expanded_end"]])

    def test_commented_literal_opener_does_not_swallow_real_section(self):
        text = paper("% \\begin{verbatim}\n\\section{Real}\nbody\n% \\end{verbatim}\n")
        manifest, _, _ = self.prepare(text)
        self.assertEqual([u["title"] for u in manifest["units"]], ["Real"])

    def test_literal_environment_variants(self):
        for env in sorted(prep.LITERAL_ENVS):
            for star in ("", "*"):
                with self.subTest(env=env + star):
                    text = paper(f"\\section{{Real}}\n\\begin{{{env}{star}}}\n"
                                 f"\\section{{Fake}}\n\\end{{{env}{star}}}\n")
                    manifest, _, _ = self.prepare(text)
                    self.assertEqual([u["title"] for u in manifest["units"]], ["Real"])

    def test_nested_titles_short_titles_and_stars(self):
        title = r"The {nested {case}} of $\mathbb{Z}$"
        manifest, _, _ = self.prepare(paper("\\section*[Short]{" + title + "}\nbody\n"))
        self.assertEqual(manifest["units"][0]["title"], title)

    def test_nested_input_include_dotted_and_braceless_forms(self):
        self.put("parts/a.tex", "\\section{One}\nA\n\\input b\n")
        self.put("parts/b.tex", "B\n\\input{../shared.2}\n")
        self.put("shared.2.tex", "C\n")
        manifest, tex, _ = self.prepare(paper("\\input{parts/a}\n\\include{shared.2}\n"))
        self.assertIn("A\nB\nC", tex)
        self.assertEqual(tex.count("C\n"), 2)
        self.assertEqual(len(manifest["sources"]), 4)
        self.assertEqual(manifest["units"][0]["location"], {"path": "parts/a.tex", "line": 1})

    def test_root_first_lookup(self):
        self.put("choice.tex", "ROOT\n")
        self.put("parts/choice.tex", "SIBLING\n")
        self.put("parts/a.tex", "\\input{choice}\n")
        _, tex, _ = self.prepare(paper("\\input{parts/a}\n"))
        self.assertIn("ROOT", tex)
        self.assertNotIn("SIBLING", tex)

    def test_main_path_is_project_relative_when_root_is_supplied(self):
        self.put("paper.tex", paper("\\section{Main}\nproject body\n"))
        manifest, tex, _ = prep.prepare(Path("paper.tex"), self.root)
        self.assertEqual(manifest["main"], "paper.tex")
        self.assertIn("project body", tex)

    def test_fake_inputs_are_never_read(self):
        text = paper("% \\input{missing}\n\\begin{verbatim}\n\\include{missing}\n"
                     "\\end{verbatim}\n" + r"\verb|\input{missing}|" + "\nbody\n")
        manifest, tex, _ = self.prepare(text)
        self.assertEqual(len(manifest["sources"]), 1)
        self.assertIn(r"\input{missing}", tex)

    def test_input_without_final_newline_cannot_swallow_following_section(self):
        for child in ("Text % final comment", r"\somecommand"):
            with self.subTest(child=child):
                self.put("sub.tex", child)
                manifest, tex, _ = self.prepare(paper("\\input{sub}\\section{Real}\nbody\n"))
                self.assertEqual([u["title"] for u in manifest["units"] if u["kind"] == "section"], ["Real"])
                self.assertIn(child + "\n\\section{Real}", tex)
                synthetic = [span for span in manifest["source_map"] if span.get("synthetic")]
                self.assertEqual(len(synthetic), 1)
                self.assertIsNone(synthetic[0]["path"])
                self.assertEqual(prep.locate(manifest["source_map"], tex, synthetic[0]["expanded_start"]),
                                 {"path": None, "line": None})

    def test_cycles_are_errors_and_repeated_noncycles_are_valid(self):
        self.put("a.tex", "A\n\\input{b}\n")
        self.put("b.tex", "B\n\\input{a}\n")
        with self.assertRaisesRegex(prep.PreparationError, "Circular"):
            self.prepare(paper("\\input{a}\n"))
        self.put("b.tex", "B\n")
        _, tex, _ = self.prepare(paper("\\input{a}\n\\input{a}\n"))
        self.assertEqual(tex.count("A\n"), 2)
        self.assertEqual(tex.count("B\n"), 2)

    def test_boundary_is_checked_before_reading_absolute_parent_or_symlink(self):
        outside = self.put("outside.tex", "PRIVATE SENTINEL\n")
        project = self.root / "project"
        project.mkdir()
        source = project / "main.tex"
        (project / "linked.tex").symlink_to(outside)
        original_read = Path.read_bytes
        reads = []

        def observed(path):
            reads.append(path.resolve())
            return original_read(path)

        for reference in (str(outside), "../outside", "linked"):
            with self.subTest(reference=reference):
                source.write_text(paper(f"\\input{{{reference}}}\n"), encoding="utf-8")
                with patch.object(Path, "read_bytes", observed):
                    with self.assertRaisesRegex(prep.PreparationError, "outside project"):
                        prep.prepare(source, project)
        self.assertNotIn(outside, reads)
        with self.assertRaises(prep.PreparationError):
            prep.prepare(outside, project)

    def test_missing_dynamic_invalid_utf8_and_depth_size_failures(self):
        for text in (paper("\\input{missing}\n"), paper(r"\input{\filename}")):
            with self.subTest(text=text), self.assertRaises(prep.PreparationError):
                self.prepare(text)
        self.main.write_bytes(b"bad \xe9")
        with self.assertRaisesRegex(prep.PreparationError, "UTF-8"):
            self.prepare()
        self.put("a.tex", "body\n")
        with patch.object(prep, "MAX_INPUT_DEPTH", 1):
            with self.assertRaisesRegex(prep.PreparationError, "nesting"):
                self.prepare(paper("\\input{a}\n"))
        with patch.object(prep, "MAX_EXPANDED_CHARS", 20):
            with self.assertRaisesRegex(prep.PreparationError, "size limit"):
                self.prepare("x" * 21)

    def test_unclosed_literal_is_not_a_clean_snapshot(self):
        with self.assertRaisesRegex(prep.PreparationError, "Unclosed"):
            self.prepare(paper("\\begin{verbatim}\nbody\n"))

    def test_source_map_reconstructs_every_original_fragment(self):
        self.put("sub.tex", "α\r\n\\section{Included}\nβ\n")
        manifest, tex, _ = self.prepare(paper("Start\n\\input{sub}\nTail\n"))
        cursor = 0
        for span in manifest["source_map"]:
            self.assertEqual(span["expanded_start"], cursor)
            raw = (self.root / span["path"]).read_bytes().decode("utf-8")
            self.assertEqual(tex[span["expanded_start"]:span["expanded_end"]],
                             raw[span["source_start"]:span["source_end"]])
            cursor = span["expanded_end"]
        self.assertEqual(cursor, len(tex))

    def test_front_matter_and_sectionless_body_are_retained(self):
        manifest, tex, _ = self.prepare(paper("Short but substantive.\n\\section{Main}\nbody\n"))
        self.assertEqual(manifest["units"][0]["kind"], "front-matter")
        manifest, _, _ = self.prepare(paper("\\chapter{One}\nbody\n"))
        self.assertEqual(len(manifest["units"]), 1)
        self.assertEqual(manifest["units"][0]["kind"], "body")

    def test_skipped_bibliography_is_retained_and_does_not_swallow_appendix(self):
        for title in ("References", "bibliography", "Acknowledgments", r"\emph{Acknowledgements}"):
            with self.subTest(title=title):
                manifest, tex, _ = self.prepare(paper("\\section{Main}\nmath\n\\section*{" + title
                    + "}\nretained\n\\section{Appendix}\nmore math\n"))
                self.assertEqual([u["reviewable"] for u in manifest["units"]], [True, False, True])
                self.assertIn("retained", tex)
        manifest, _, _ = self.prepare(paper("\\section{Main}\nmath\n\\begin{thebibliography}{1}\n"
                                           "reference\n\\end{thebibliography}\n"))
        self.assertEqual([u["reviewable"] for u in manifest["units"]], [True, False])

    def test_context_ignores_fake_title_and_finds_labels_and_custom_statements(self):
        text = paper("\\begin{abstract}Real abstract\\end{abstract}\n"
                     "\\section{Main}\n\\begin{prop}\\label{p:real}Statement\\end{prop}\n"
                     "\\begin{verbatim}\\begin{theorem}Fake\\end{theorem}\\end{verbatim}\n",
                     "% \\title{Wrong}\n\\title{The {nested} title}\n\\newtheorem{prop}{Proposition}\n")
        _, _, ctx = self.prepare(text)
        context = json.loads(ctx)
        self.assertEqual(context["title"], "The {nested} title")
        self.assertEqual(context["abstracts"][0]["text"], "Real abstract")
        self.assertEqual([s["label"] for s in context["statements"]], ["p:real"])

    def test_deterministic_snapshots_and_hashes(self):
        text = paper("\\section{Main}\nα\n")
        first, _ = self.snapshot("run1", text)
        second, _ = self.snapshot("run2", text)
        self.assertEqual(first, second)
        for path in (self.root / "run1").rglob("*"):
            if path.is_file():
                self.assertEqual(path.read_bytes(), (self.root / "run2" / path.relative_to(self.root / "run1")).read_bytes())
        self.assertEqual(first["source_sha256"], prep.digest(text))

    def test_insertion_deletion_and_last_section_keep_neighbor_identity(self):
        base = paper("\\section{A}\na\n\\section{B}\nb\n")
        original, previous = self.snapshot("old", base)
        extended = paper("\\section{New}\nnew\n\\section{A}\na\n\\section{B}\nb\n\\section{Last}\nlast\n")
        current, _, _ = self.prepare(extended, previous)
        self.assertEqual(len(current["comparison"]["candidate_unchanged"]), 2)
        self.assertEqual(len(current["comparison"]["added"]), 2)
        self.assertTrue(current["comparison"]["whole_paper_invalidated"])
        deleted, _, _ = self.prepare(paper("\\section{B}\nb\n"), previous)
        self.assertEqual(deleted["comparison"]["candidate_unchanged"], [original["units"][1]["id"]])
        self.assertEqual(deleted["comparison"]["removed"], [original["units"][0]["id"]])
        self.assertTrue((previous.parent / original["units"][0]["file"]).is_file())

    def test_changed_context_does_not_certify_identical_unit(self):
        body = "\\section{Main}\nUses the convention.\n"
        old, previous = self.snapshot("old", paper(body, "\\def\\domain{A}\n"))
        new, _, _ = self.prepare(paper(body, "\\def\\domain{B}\n"), previous)
        self.assertEqual(new["units"][0]["id"], old["units"][0]["id"])
        self.assertTrue(new["comparison"]["global_context_changed"])
        self.assertTrue(new["comparison"]["whole_paper_invalidated"])
        self.assertTrue(new["comparison"]["reuse_requires_context_check"])

    def test_duplicate_units_have_unique_ids_and_ambiguous_reuse(self):
        text = paper("\\section{Same}\nbody\n\\section{Same}\nbody\n")
        old, previous = self.snapshot("old", text)
        new, _, _ = self.prepare(text, previous)
        self.assertEqual(len({u["id"] for u in old["units"]}), 2)
        self.assertEqual(new["comparison"]["candidate_unchanged"], [])
        self.assertEqual(len(new["comparison"]["ambiguous"]), 2)

    def test_unchanged_snapshot_does_not_invalidate_whole_paper(self):
        text = paper("\\section{Main}\nbody\n")
        _, previous = self.snapshot("old", text)
        manifest, _, _ = self.prepare(text, previous)
        self.assertFalse(manifest["comparison"]["whole_paper_invalidated"])

    def test_contract_change_and_untrusted_previous_metadata(self):
        text = paper("\\section{Main}\nbody\n")
        old, previous = self.snapshot("old", text)
        with patch.object(prep, "contract_digest", return_value="0" * 64):
            new, _, _ = self.prepare(text, previous)
            self.assertTrue(new["comparison"]["contract_changed"])
            self.assertTrue(new["comparison"]["whole_paper_invalidated"])
        old["units"][0]["id"] = "../../victim"
        previous.write_text(json.dumps(old), encoding="utf-8")
        with self.assertRaises(prep.PreparationError):
            self.prepare(text, previous)

    def test_output_symlink_and_occupied_directory_are_never_overwritten(self):
        result = self.prepare(paper("body\n"))
        victim = self.put("victim", "sentinel")
        out = self.root / "out"
        out.symlink_to(victim)
        with self.assertRaisesRegex(prep.PreparationError, "symbolic"):
            prep.write_snapshot(out, *result)
        self.assertEqual(victim.read_text(), "sentinel")
        out.unlink()
        out.mkdir()
        with self.assertRaisesRegex(prep.PreparationError, "new snapshot"):
            prep.write_snapshot(out, *result)
        (self.root / "parent-link").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(prep.PreparationError, "symbolic"):
            prep.write_snapshot(self.root / "parent-link" / "new", *result)

    def test_cli_failure_has_no_snapshot_and_success_is_readable(self):
        self.put("paper.tex", paper("\\input{missing}\n"))
        out = self.root / "out"
        with redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            self.assertEqual(prep.main([str(self.main), "--output", str(out)]), 2)
        self.assertFalse(out.exists())
        self.put("paper.tex", paper("\\section{Main}\nbody\n"))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(prep.main([str(self.main), "--output", str(out)]), 0)
        manifest = json.loads((out / "manifest.json").read_text())
        self.assertEqual(manifest["schema_version"], 1)
        self.assertEqual(prep.digest((out / "full-source.tex").read_text()), manifest["source_sha256"])


if __name__ == "__main__":
    unittest.main()
