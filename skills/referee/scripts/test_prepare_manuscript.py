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
    def test_contract_file_revisions_are_portable_and_compare_individually(self):
        text = paper("\\section{Main}\nbody\n")
        old, previous = self.snapshot("old", text)
        contracts = old["contract_files"]
        self.assertIn("references/reviewers/correctness.md", contracts)
        self.assertTrue(all(not Path(name).is_absolute() for name in contracts))
        changed = dict(contracts)
        changed["references/reviewers/correctness.md"] = "0" * 64
        with patch.object(prep, "contract_files", return_value=changed), patch.object(prep, "contract_digest", return_value="1" * 64):
            new, _, _ = self.prepare(text, previous)
        self.assertEqual(new["comparison"]["contract_files_changed"], ["references/reviewers/correctness.md"])
        old.pop("contract_files")
        previous.write_text(json.dumps(old))
        legacy, _, _ = self.prepare(text, previous)
        self.assertIsNone(legacy["comparison"]["contract_files_changed"])
        old["contract_files"] = {"../../outside": "0" * 64}
        previous.write_text(json.dumps(old))
        with self.assertRaisesRegex(prep.PreparationError, "contract_files"):
            self.prepare(text, previous)

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

    def test_comments_before_input_arguments_are_skipped(self):
        self.put("child.tex", "CHILD\n")
        _, tex, _ = self.prepare(paper("\\input % ignored { \\input{missing}\n{child}\n"
                                      "\\input % ignored\nchild\n"))
        self.assertEqual(tex.count("CHILD"), 2)

    def test_main_directory_first_lookup(self):
        self.put("choice.tex", "ROOT\n")
        self.put("parts/choice.tex", "SIBLING\n")
        self.put("parts/a.tex", "\\input{choice}\n")
        _, tex, _ = self.prepare(paper("\\input{parts/a}\n"))
        self.assertIn("ROOT", tex)
        self.assertNotIn("SIBLING", tex)

    def test_wider_root_resolves_inputs_from_main_directory(self):
        self.put("intro.tex", "DECOY\n")
        self.put("paper/intro.tex", "REAL INTRO\n")
        self.put("paper/sections/a.tex", "A\n\\input{sections/b}\n")
        self.put("paper/sections/b.tex", "B FROM MAIN DIRECTORY\n")
        main = self.put("paper/main.tex", paper("\\input{intro}\n\\input{sections/a}\n"))
        manifest, tex, _ = prep.prepare(main, self.root)
        self.assertIn("REAL INTRO", tex)
        self.assertNotIn("DECOY", tex)
        self.assertIn("B FROM MAIN DIRECTORY", tex)
        self.assertEqual(manifest["main"], "paper/main.tex")

    def test_symlink_main_uses_entry_directory_and_canonical_source_identity(self):
        target = self.put("src/paper.tex", paper("\\input{intro}\n"))
        self.put("intro.tex", "ENTRY INTRO\n")
        self.put("src/intro.tex", "TARGET DECOY\n")
        self.main.symlink_to(target)
        for main, root in ((self.main, None), (self.main, self.root),
                           (Path("paper.tex"), self.root)):
            with self.subTest(main=main, root=root):
                manifest, tex, _ = prep.prepare(main, root)
                self.assertIn("ENTRY INTRO", tex)
                self.assertNotIn("TARGET DECOY", tex)
                self.assertEqual(manifest["main"], "src/paper.tex")
                self.assertEqual([s["path"] for s in manifest["sources"]],
                                 ["intro.tex", "src/paper.tex"])

    def test_tex_suffix_is_tried_first_and_include_supplies_it(self):
        self.put("foo", "EXTENSIONLESS\n")
        self.put("foo.tex", "TEXFILE\n")
        _, tex, _ = self.prepare(paper("\\input{foo}\n"))
        self.assertIn("TEXFILE", tex)
        self.assertNotIn("EXTENSIONLESS", tex)
        (self.root / "foo.tex").unlink()
        _, tex, _ = self.prepare(paper("\\input{foo}\n"))
        self.assertIn("EXTENSIONLESS", tex)
        with self.assertRaisesRegex(prep.PreparationError, "Cannot find"):
            self.prepare(paper("\\include{foo}\n"))
        # LaTeX strips an explicit .tex suffix before \include appends one.
        self.put("chapter.tex", "CHAPTER\n")
        _, tex, _ = self.prepare(paper("\\include{chapter.tex}\n"))
        self.assertIn("CHAPTER", tex)

    def test_text_after_end_document_or_endinput_is_not_expanded(self):
        self.put("chapter.tex", "kept\n\\endinput\nscrap \\input{gone}\n\\section{Scrap}\n")
        text = paper("\\section{Main}\n\\input{chapter}\nafter\n") + "\\input{olddraft}\n\\section{Old}\n"
        manifest, tex, _ = self.prepare(text)
        self.assertEqual([s["path"] for s in manifest["sources"]], ["chapter.tex", "paper.tex"])
        self.assertIn("kept\n\\endinput\n", tex)
        self.assertIn("after", tex)
        for absent in ("scrap", "olddraft", "Old"):
            self.assertNotIn(absent, tex)
        self.assertEqual([u["title"] for u in manifest["units"]], ["Main"])
        # \end{document} inside an input also ends the document for its callers.
        self.put("last.tex", "last\n\\end{document}\n\\input{gone}\n")
        _, tex, _ = self.prepare("\\begin{document}\n\\input{last}\n\\input{gone}\ntrailing\n")
        self.assertTrue(tex.endswith("last\n\\end{document}\n"))

    def test_stops_inside_definitions_and_endinput_line_are_honored(self):
        self.put("sub.tex", "SUB\n")
        self.put("rest.tex", "REST\n")
        text = paper("\\section{Main}\n\\input{rest}\n",
                     "\\newcommand{\\finish}{\\end{document}}\n\\def\\stop{\\endinput}\n")
        _, tex, _ = self.prepare(text)
        self.assertIn("REST", tex)
        self.put("chapter.tex", "\\endinput \\input{sub}\nlater\n")
        _, tex, _ = self.prepare(paper("\\input{chapter}\n"))
        self.assertIn("SUB", tex)
        self.assertNotIn("later", tex)

    def test_unfinished_drafts_after_stops_are_not_scanned(self):
        for draft in (r"\verb|draft", r"\lstinline{draft", r"\begin{verbatim}",
                      r"\begin{draft", r"\input{draft"):
            for newline in ("\n", "\r", "\r\n"):
                with self.subTest(draft=draft, newline=repr(newline)):
                    text = "\\begin{document}" + newline + "kept" + newline
                    for tail in (draft + newline, newline + draft):
                        _, tex, _ = self.prepare(text + "\\end{document}" + tail)
                        self.assertEqual(tex, text + "\\end{document}" + newline)
                    self.put("child.tex", "child\\endinput" + newline + draft)
                    _, tex, _ = self.prepare(paper("\\input{child}\ncaller\n"))
                    self.assertIn("child\\endinput" + newline, tex)
                    self.assertIn("caller", tex)
                    self.assertNotIn(draft, tex)
        # Material on the endinput line is still read by TeX.
        self.put("child.tex", "\\endinput \\verb|draft\n")
        with self.assertRaisesRegex(prep.PreparationError, "Unclosed inline"):
            self.prepare(paper("\\input{child}\n"))

    def test_child_document_stop_prevents_scanning_caller_draft(self):
        self.put("last.tex", "last\\end{document}\\verb|draft\n")
        manifest, tex, _ = self.prepare("\\begin{document}\n\\input{last}\\begin{unfinished")
        self.assertEqual(tex, "\\begin{document}\nlast\\end{document}\n")
        for span in manifest["source_map"]:
            raw = (self.root / span["path"]).read_text(encoding="utf-8")
            self.assertEqual(tex[span["expanded_start"]:span["expanded_end"]],
                             raw[span["source_start"]:span["source_end"]])

    def test_carriage_return_line_ends_terminate_comments(self):
        self.put("sub.tex", "SUB\r")
        text = "\\begin{document}\r% note\r\\section{A}\ra\r\\input{sub}\r\\section{B}\rb\r\\end{document}\r"
        manifest, tex, _ = self.prepare(text)
        self.assertEqual([u["title"] for u in manifest["units"]], ["A", "B"])
        self.assertIn("SUB", tex)
        self.assertEqual([u["location"] for u in manifest["units"]],
                         [{"path": "paper.tex", "line": 3}, {"path": "paper.tex", "line": 6}])

    def test_brace_delimited_lstinline(self):
        manifest, _, _ = self.prepare(paper("\\section{Main}\nUse \\lstinline{x = {1}} here.\n"))
        self.assertEqual([u["title"] for u in manifest["units"]], ["Main"])
        masked = prep.mask_non_content(r"\lstinline{x} and $\frac{1}{2}$ \lstinline[a]{\section{F}}")
        self.assertIn(r"$\frac{1}{2}$", masked)
        self.assertNotIn("section", masked)
        with self.assertRaisesRegex(prep.PreparationError, "Unclosed inline"):
            prep.mask_non_content("\\lstinline{x\n}")

    def test_alltt_keeps_commands_and_literal_percent(self):
        self.put("sub.tex", "SUB\n")
        self.put("pct.tex", "PCT\n")
        manifest, tex, _ = self.prepare(paper("\\section{Main}\n\\begin{alltt}\n\\input{sub}\n"
                                              "50% \\input{pct}\n\\end{alltt}\n% \\input{gone}\n"))
        self.assertIn("SUB", tex)
        self.assertIn("PCT", tex)
        self.assertEqual(len(manifest["sources"]), 3)

    def test_alltt_state_is_inherited_by_nested_inputs_and_snapshot_hashes(self):
        self.put("child.tex", "50% \\input{nested}\n")
        self.put("nested.tex", "75% \\input{extra}\n")
        self.put("extra.tex", "EXTRA\n")
        text = paper("\\begin{alltt}\n\\input{child}\n\\end{alltt}\n")
        manifest, previous = self.snapshot("old", text)
        self.assertEqual([s["path"] for s in manifest["sources"]],
                         ["child.tex", "extra.tex", "nested.tex", "paper.tex"])
        self.put("extra.tex", "CHANGED EXTRA\n")
        current, tex, _ = self.prepare(text, previous)
        self.assertIn("CHANGED EXTRA", tex)
        self.assertNotEqual(current["source_files_sha256"], manifest["source_files_sha256"])
        self.assertTrue(current["comparison"]["whole_paper_invalidated"])

    def test_cached_plans_distinguish_incoming_alltt_state(self):
        self.put("child.tex", "50% \\input{extra}\n")
        self.put("extra.tex", "EXTRA\n")
        _, tex, _ = self.prepare(paper("\\input{child}\n\\begin{alltt}\n"
                                      "\\input{child}\n\\input{child}\n\\end{alltt}\n"
                                      "\\input{child}\n"))
        self.assertEqual(tex.count("EXTRA"), 2)
        self.assertEqual(tex.count(r"\input{extra}"), 2)

    def test_alltt_state_changes_in_children_apply_to_callers(self):
        self.put("open.tex", "\\begin{alltt}\n")
        self.put("close.tex", "\\end{alltt}\n")
        self.put("extra.tex", "EXTRA\n")
        _, tex, _ = self.prepare(paper("\\input{open}\n50% \\input{extra}\n"
                                      "\\input{close}\n50% \\input{missing}\n"))
        self.assertIn("EXTRA", tex)
        self.assertIn(r"\input{missing}", tex)

    def test_repeated_inputs_are_planned_once_and_expansions_are_capped(self):
        for index in range(20):
            self.put(f"f{index}.tex", f"\\input{{f{index + 1}}}\\input{{f{index + 1}}}\n")
        self.put("f20.tex", "")
        reads, scans = [], []
        original_read = Path.read_bytes
        original_scan = prep.LexicalScanner.scan

        def counted_read(path):
            reads.append(path)
            return original_read(path)

        def counted_scan(scanner, *args, **kwargs):
            scans.append(scanner)
            return original_scan(scanner, *args, **kwargs)

        with patch.object(Path, "read_bytes", counted_read), \
                patch.object(prep.LexicalScanner, "scan", counted_scan):
            with self.assertRaisesRegex(prep.PreparationError, "input expansions"):
                self.prepare(paper("\\input{f0}\n"))
        self.assertEqual(len(reads), 22)
        self.assertEqual(len(set(reads)), 22)
        # At most three segments per binary input file, two in the main file.
        self.assertLessEqual(len(scans), 63)
        with patch.object(prep, "MAX_INPUT_EXPANSIONS", 2):
            self.put("leaf.tex", "leaf\n")
            with self.assertRaisesRegex(prep.PreparationError, "More than 2"):
                self.prepare(paper("\\input{leaf}\\input{leaf}\\input{leaf}\n"))

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
        # TeX would read the escaping linked.tex, so an in-tree fallback is unsafe.
        (project / "linked").write_text("IN-TREE DECOY\n", encoding="utf-8")
        source.write_text(paper("\\input{linked}\n"), encoding="utf-8")
        with self.assertRaisesRegex(prep.PreparationError, "outside project"):
            prep.prepare(source, project)

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

    def test_statement_label_ignores_nested_environment_labels(self):
        inner = "\\begin{equation}\\label{eq:inner}x\\end{equation}"
        text = paper(f"\\begin{{theorem}}A {inner}\\end{{theorem}}\n"
                     f"\\begin{{lemma}}{inner}\\label{{lem:own}}B\\end{{lemma}}\n")
        _, _, ctx = self.prepare(text)
        self.assertEqual([s["label"] for s in json.loads(ctx)["statements"]], [None, "lem:own"])

    def test_global_context_hash_ignores_moved_but_unchanged_context(self):
        statement = "\\section{B}\n\\begin{theorem}\\label{t}Claim.\\end{theorem}\n"
        _, previous = self.snapshot("old", paper("\\section{A}\ntypo\n" + statement))
        moved, _, _ = self.prepare(paper("\\section{A}\ntypo fixed\n" + statement), previous)
        self.assertFalse(moved["comparison"]["global_context_changed"])
        self.assertTrue(moved["comparison"]["whole_paper_invalidated"])
        edited, _, _ = self.prepare(paper("\\section{A}\ntypo\n" + statement.replace("Claim", "Stronger")),
                                    previous)
        self.assertTrue(edited["comparison"]["global_context_changed"])

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

    def test_renamed_main_still_compares_units(self):
        text = paper("\\section{Main}\nbody\n")
        old, previous = self.snapshot("old", text)
        renamed = self.put("paper-v2.tex", text)
        new, _, _ = prep.prepare(renamed, self.root, previous)
        comparison = new["comparison"]
        self.assertEqual((comparison["previous_main"], comparison["main_changed"]), ("paper.tex", True))
        self.assertTrue(comparison["whole_paper_invalidated"])
        self.assertEqual(comparison["candidate_unchanged"], [old["units"][0]["id"]])
        old["main"] = None
        previous.write_text(json.dumps(old), encoding="utf-8")
        with self.assertRaisesRegex(prep.PreparationError, "main"):
            prep.prepare(renamed, self.root, previous)

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
        (self.root / "dangling").symlink_to(self.root / "missing")
        with self.assertRaisesRegex(prep.PreparationError, "symbolic"):
            prep.write_snapshot(self.root / "dangling", *result)
        self.assertFalse((self.root / "missing").exists())

    def test_existing_linked_parents_are_used_as_is(self):
        # Like macOS /var -> /private/var or a symlinked home directory.
        result = self.prepare(paper("body\n"))
        real = self.root / "real"
        real.mkdir()
        (self.root / "link").symlink_to(real, target_is_directory=True)
        prep.write_snapshot(self.root / "link" / "reviews" / "run", *result)
        self.assertTrue((real / "reviews" / "run" / "manifest.json").is_file())

    def test_output_inside_mathbox_is_refused(self):
        result = self.prepare(paper("body\n"))
        (self.root / ".mathbox").mkdir()
        (self.root / "alias").symlink_to(self.root / ".mathbox", target_is_directory=True)
        for out in (".mathbox/referee/run", ".MathBox./run", "alias/run"):
            with self.subTest(out=out), self.assertRaisesRegex(prep.PreparationError, ".mathbox"):
                prep.write_snapshot(self.root / out, *result)
        self.assertEqual(list((self.root / ".mathbox").iterdir()), [])

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
