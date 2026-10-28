"""Executable evidence-boundary regressions; no model-output keyword grading."""
from collections import Counter
import hashlib
import json
from contextlib import redirect_stdout
from io import BytesIO, StringIO, TextIOWrapper
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

import research_state
from research_state import (Ledger, LedgerError, brief_markdown, file_hash, impact, main, next_routes,
                            pin_impact, project, restrict)


class ResearchStateTests(unittest.TestCase):
    def test_unknown_fields_rejected_before_any_append_but_legacy_replays(self):
        with self.assertRaisesRegex(LedgerError, "statment_artifact.*allowed fields"):
            self.claim(statment_artifact={"path": "proof.md", "locator": "claim"})
        self.assertEqual(len(self.ledger.read()["events"]), 0)
        self.claim()
        with self.assertRaisesRegex(LedgerError, "resolve.*allowed fields"):
            self.route(resolve=["A"])
        self.assertEqual(len(self.ledger.read()["events"]), 1)
        # Replay retains pre-gate semantics for existing append-only journals.
        path = self.root / ".mathbox/events/000001.json"
        event = json.loads(path.read_text())
        event["payload"]["legacy_note"] = "historical extension"
        event["sha256"] = research_state.digest({k: v for k, v in event.items() if k != "sha256"})
        path.write_text(json.dumps(event))
        self.assertEqual(self.ledger.read()["claims"]["A"]["legacy_note"], "historical extension")

    def test_batch_unknown_field_leaves_no_valid_prefix(self):
        good = {"type": "claim", "actor": "author", "payload": {
            "id": "A", "statement": "A", "hypotheses": [], "regime": "Z", "level": "chain", "dependencies": []}}
        bad = json.loads(json.dumps(good))
        bad["payload"].update(id="B", statment="typo")
        with self.assertRaisesRegex(LedgerError, "unknown claim payload fields"):
            self.ledger.record_many([good, bad])
        self.assertEqual(len(self.ledger.read()["events"]), 0)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.ledger = Ledger(self.root)
        self.ledger.initialize()
        (self.root / "proof.md").write_text("A complete argument under the registered contract.")
        (self.root / "review.md").write_text("A fresh derivation and explicit obligation report.")

    def record(self, kind, payload, actor="author"):
        return self.ledger.record({"type": kind, "actor": actor, "payload": payload})["event_id"]

    def claim(self, key="A", deps=None, **extra):
        return self.record("claim", dict(id=key, statement="Exact quantified assertion " + key,
                           hypotheses=["finite type"], regime="Z", level="chain", dependencies=deps or [], **extra))

    def evidence(self, key="A", kind="proof", **extra):
        return self.record("evidence", dict(claim=key, kind=kind, summary="Durable result",
                           artifacts=[{"path": "proof.md"}], **extra))

    def review(self, evidence, outcome="pass", actor="reviewer", independent=True):
        return self.record("review", dict(evidence=evidence, outcome=outcome, independent=independent,
                           summary="Report", artifact={"path": "review.md"}), actor)

    def view(self):
        return project(self.root, self.ledger.read())

    def deferred_packet(self):
        head = next(reversed(self.ledger.read()["events"].values()))
        return {
            "format": "mathbox-deferred-v1",
            "base": {"event_id": head["event_id"], "event_sha256": head["sha256"]},
            "artifacts": [
                {"path": "research/records/route.md", "content": "# Route\n\nA complete record.\n"},
                {"path": "proofs/new.md", "content": "# Proof\n\nA complete argument.\n"},
                {"path": "reviews/new.md", "content": "# Review\n\nChecked independently.\n"},
            ],
            "index_append": {"path": "research/index.md", "expected_tail": "- Earlier route\n",
                             "content": "- [New route](records/route.md) — conditional\n"},
            "proposals": [
                {"type": "evidence", "actor": "author", "alias": "new_proof",
                 "payload": {"claim": "A", "kind": "proof", "summary": "New argument",
                             "artifacts": [{"path": "proofs/new.md"}]}},
                {"type": "review", "actor": "reviewer",
                 "payload": {"evidence": {"$event": "new_proof"}, "outcome": "pass",
                             "independent": True, "summary": "Independent check",
                             "artifact": {"path": "reviews/new.md"}}},
            ],
        }

    def allow_deferred(self, roots=("proofs", "reviews", "research/records"),
                       indexes=("research/index.md",)):
        path = self.root / ".mathbox/config.json"
        config = json.loads(path.read_text(encoding="utf-8"))
        config["deferred"] = {"artifact_roots": list(roots), "index_files": list(indexes)}
        path.write_text(json.dumps(config), encoding="utf-8")

    def deferred_setup(self):
        self.claim()
        (self.root / "research").mkdir()
        (self.root / "research/index.md").write_text("# Routes\n- Earlier route\n")
        self.allow_deferred()
        return self.deferred_packet()

    def assert_deferred_untouched(self, events=1):
        self.assertEqual(len(self.ledger.read()["events"]), events)
        for name in ("proofs", "reviews", "research/records"):
            self.assertFalse((self.root / name).exists(), name)
        self.assertEqual((self.root / "research/index.md").read_text(), "# Routes\n- Earlier route\n")

    def ingest_cli(self, packet, *args):
        path = Path(self.temp.name) / "packet.json"
        path.write_text(json.dumps(packet), encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "ingest", str(path), *args]), 0)
        return json.loads(output.getvalue())

    def test_deferred_dry_run_and_ingest_pin_staged_content(self):
        packet = self.deferred_setup()
        before = (self.root / "research/index.md").read_bytes()
        preview = self.ledger.ingest(packet, dry_run=True)
        self.assertEqual(len(self.ledger.read()["events"]), 1)
        self.assertEqual((self.root / "research/index.md").read_bytes(), before)
        self.assertFalse((self.root / "proofs").exists())
        self.assertEqual(preview[1]["payload"]["evidence"], preview[0]["event_id"])
        self.assertEqual(preview[0]["payload"]["artifacts"][0]["sha256"],
                         hashlib.sha256(packet["artifacts"][1]["content"].encode()).hexdigest())
        events = self.ledger.ingest(packet)
        self.assertEqual(len(self.ledger.read()["events"]), 3)
        self.assertEqual(events[1]["payload"]["evidence"], events[0]["event_id"])
        self.assertEqual(file_hash(self.root / "proofs/new.md"),
                         preview[0]["payload"]["artifacts"][0]["sha256"])
        self.assertEqual(events[0]["payload"]["artifacts"][0]["sha256"],
                         preview[0]["payload"]["artifacts"][0]["sha256"])
        self.assertEqual((self.root / "research/index.md").read_text(),
                         before.decode() + packet["index_append"]["content"])
        self.assertEqual(self.view()["issues"], [])

    def test_deferred_stdin_is_utf8_and_output_is_compact(self):
        packet = self.deferred_setup()
        packet["proposals"] += [
            {"type": "claim", "actor": "author",
             "payload": {"id": f"N{number}", "statement": "Exact claim", "hypotheses": [],
                         "regime": "Z", "level": "chain", "dependencies": []}}
            for number in range(8)]
        # A cp1252 locale must not reinterpret the UTF-8 em dash in the index entry.
        stdin = TextIOWrapper(BytesIO(json.dumps(packet, ensure_ascii=False).encode("utf-8")),
                              encoding="cp1252")
        output = StringIO()
        with patch("sys.stdin", stdin), redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "ingest", "-"]), 0)
        summary = json.loads(output.getvalue())
        self.assertNotIn("events", summary)
        self.assertEqual((summary["count"], len(summary["sample"]), summary["receipts_omitted"]),
                         (10, 8, 2))
        self.assertEqual(summary["artifacts"], [a["path"] for a in packet["artifacts"]])
        self.assertEqual(summary["unverified_existing_pins"], [])
        self.assertEqual((self.root / "research/index.md").read_text(encoding="utf-8"),
                         "# Routes\n- Earlier route\n" + packet["index_append"]["content"])

    def test_deferred_empty_ledger_uses_null_base(self):
        packet = {"format": "mathbox-deferred-v1",
                  "base": {"event_id": None, "event_sha256": None},
                  "artifacts": [], "index_append": None,
                  "proposals": [{"type": "claim", "actor": "author",
                                 "payload": {"id": "A", "statement": "Exact claim",
                                             "hypotheses": [], "regime": "Z", "level": "chain",
                                             "dependencies": []}}]}
        self.assertEqual(self.ledger.ingest(packet)[0]["event_id"], "E000001")

    def test_deferred_writes_only_configured_documents(self):
        packet = self.deferred_setup()
        original = json.dumps(packet)
        (self.root / ".git").mkdir()
        (self.root / ".git/config").write_text("[core]\n")
        refused = {
            ".git/hooks/pre-commit": "hidden", ".github/workflows/x.yml": "hidden",
            ".claude/settings.json": "hidden", ".MATHBOX/events/000002.json": "hidden",
            "proofs/.latexmkrc": "hidden", "proofs/AGENTS.md": "instruction",
            "proofs/claude.md": "instruction", "proofs/conftest.py": "document",
            "proofs/new.md:stream": "document", "notes/new.md": "outside",
            "proofs": "outside",
        }
        for bad, reason in refused.items():
            packet = json.loads(original)
            packet["artifacts"][1]["path"] = bad
            with self.assertRaisesRegex(LedgerError, reason, msg=bad):
                self.ledger.ingest(packet)
        for bad, reason in {".git/config": "hidden", "proof.md": "not a configured"}.items():
            packet = json.loads(original)
            packet["index_append"] = {"path": bad, "expected_tail": "[core]\n",
                                      "content": "[alias] pwn = !echo INJECTED\n"}
            with self.assertRaisesRegex(LedgerError, reason, msg=bad):
                self.ledger.ingest(packet)
        self.assertEqual((self.root / ".git/config").read_text(), "[core]\n")
        self.assert_deferred_untouched()
        # The policy is local: an unconfigured or unsafe policy opens nothing.
        for roots in ((), (".git",), (".",), ("proofs/../.mathbox",)):
            self.allow_deferred(roots=roots)
            with self.assertRaises(LedgerError, msg=roots):
                self.ledger.ingest(json.loads(original))
        self.allow_deferred(indexes=())
        with self.assertRaisesRegex(LedgerError, "not a configured deferred index"):
            self.ledger.ingest(json.loads(original))
        self.assert_deferred_untouched()

    def test_deferred_existing_artifact_hash_is_checked_or_reported(self):
        packet = self.deferred_setup()
        artifacts = packet["proposals"][0]["payload"]["artifacts"]
        artifacts += [{"path": "proof.md", "sha256": file_hash(self.root / "proof.md")},
                      {"path": "./review.md"}]
        summary = self.ingest_cli(packet, "--dry-run")
        self.assertEqual(summary["unverified_existing_pins"], ["review.md"])
        artifacts[1]["sha256"] = "0" * 64
        with self.assertRaisesRegex(LedgerError, "differs from current content: proof.md"):
            self.ledger.ingest(packet)
        artifacts[1]["sha256"] = file_hash(self.root / "proof.md")
        for field, value in (("snapshot", {"A": 1}), ("sha256", "0" * 64)):
            payload = packet["proposals"][0]["payload"]
            payload[field] = value
            with self.assertRaisesRegex(LedgerError, "omit generated fields"):
                self.ledger.ingest(packet)
            del payload[field]
        self.assertEqual(len(self.ledger.ingest(packet)), 2)

    def test_deferred_index_append_is_visible_to_proposal_pins(self):
        packet = self.deferred_setup()
        packet["proposals"] = [{"type": "claim", "actor": "author",
                                "payload": {"id": "B", "statement": "Indexed claim",
                                            "hypotheses": [], "regime": "Z", "level": "chain",
                                            "dependencies": [],
                                            "statement_artifact": {"path": "research/index.md",
                                                                   "locator": "New route"}}}]
        preview = self.ledger.ingest(packet, dry_run=True)[0]
        event = self.ledger.ingest(packet)[0]
        expected = file_hash(self.root / "research/index.md")
        self.assertEqual(preview["payload"]["statement_artifact"]["sha256"], expected)
        self.assertEqual(event["payload"]["statement_artifact"]["sha256"], expected)
        self.assertEqual(self.view()["issues"], [])

    def test_deferred_index_append_never_stales_current_pins(self):
        self.deferred_setup()
        self.claim("B", statement_artifact={"path": "research/index.md", "locator": "Earlier route"})
        packet = self.deferred_packet()
        packet["proposals"][0]["payload"]["claim"] = "B"
        with self.assertRaisesRegex(LedgerError, r"would stale current pins of research/index.md \(E000002\)"):
            self.ledger.ingest(packet)
        self.assert_deferred_untouched(events=2)
        # A pin that is already stale is reported by check, not protected by refusing appends.
        (self.root / "research/index.md").write_text("# Routes\n- Earlier route\n- Manual edit\n")
        packet["index_append"]["expected_tail"] = "- Manual edit\n"
        packet["proposals"][0]["payload"]["claim"] = "A"
        self.assertEqual(len(self.ledger.ingest(packet)), 2)

    def test_evidence_requires_current_claim_contract(self):
        (self.root / "statement.md").write_text("Theorem A, exact version one.")
        self.claim(statement_artifact={"path": "statement.md", "locator": "Theorem A"})
        (self.root / "statement.md").write_text("Theorem A, materially revised.")
        with self.assertRaisesRegex(LedgerError, "record a claim revision"):
            self.evidence()
        self.claim(statement_artifact={"path": "statement.md", "locator": "Theorem A"},
                   reason="Statement revised")
        self.evidence()
        self.assertEqual(self.view()["issues"], [])

    def test_deferred_index_tail_is_the_last_newline_terminated_line(self):
        packet = self.deferred_setup()
        index = self.root / "research/index.md"
        for text in ("Only line\n", "# Routes\n- Earlier\x0croute note\n"):
            index.write_bytes(text.encode("utf-8"))
            packet["index_append"]["expected_tail"] = text.split("\n")[-2] + "\n"
            self.assertEqual(len(self.ledger.ingest(packet, dry_run=True)), 2)
            self.assertEqual(index.read_bytes(), text.encode("utf-8"))

    def test_deferred_crlf_index_keeps_its_line_endings(self):
        packet = self.deferred_setup()
        index = self.root / "research/index.md"
        index.write_bytes(b"# Routes\r\n- Earlier route\r\n")
        self.ledger.ingest(packet)
        entry = packet["index_append"]["content"].replace("\n", "\r\n").encode("utf-8")
        self.assertEqual(index.read_bytes(), b"# Routes\r\n- Earlier route\r\n" + entry)
        packet = self.deferred_packet()
        packet["artifacts"], packet["proposals"] = [], packet["proposals"][:1]
        packet["proposals"][0]["payload"]["artifacts"] = [{"path": "proof.md"}]
        packet["index_append"].update(expected_tail=packet["index_append"]["content"],
                                      content="- Bare CR\r inside\n")
        with self.assertRaisesRegex(LedgerError, "one nonempty newline-terminated entry"):
            self.ledger.ingest(packet)

    def test_deferred_stale_head_rejects_without_mutation(self):
        packet = self.deferred_setup()
        self.claim("B")
        with self.assertRaisesRegex(LedgerError, "stale deferred base"):
            self.ledger.ingest(packet)
        self.assert_deferred_untouched(events=2)

    def test_deferred_collision_escape_symlink_and_index_guard(self):
        packet = self.deferred_setup()
        original = json.dumps(packet)
        (self.root / "proofs").mkdir()
        (self.root / "proofs/new.md").write_text("Existing proof")
        with self.assertRaisesRegex(LedgerError, "already exists"):
            self.ledger.ingest(packet)
        (self.root / "proofs/new.md").unlink()
        for bad in ("../escape.md", ".mathbox/escape.md"):
            packet["artifacts"][1]["path"] = bad
            with self.assertRaises(LedgerError):
                self.ledger.ingest(packet)
        packet = json.loads(original)
        (self.root / "proofs/new.md").symlink_to(self.root / "proof.md")
        with self.assertRaisesRegex(LedgerError, "symlink"):
            self.ledger.ingest(packet)
        (self.root / "proofs/new.md").unlink()
        (self.root / "proofs").rmdir()
        (self.root / "proofs").symlink_to(self.root / "research", target_is_directory=True)
        with self.assertRaisesRegex(LedgerError, "symlink"):
            self.ledger.ingest(packet)
        (self.root / "proofs").unlink()
        packet["index_append"]["expected_tail"] = "- Different route\n"
        with self.assertRaisesRegex(LedgerError, "index tail mismatch"):
            self.ledger.ingest(packet)
        self.assert_deferred_untouched()

    def test_deferred_nested_artifacts_fail_validation(self):
        packet = self.deferred_setup()
        nested = {"path": "proofs/new.md/extra.md", "content": "Nested\n"}
        for position in (0, len(packet["artifacts"])):
            candidate = json.loads(json.dumps(packet))
            candidate["artifacts"].insert(position, nested)
            with self.assertRaisesRegex(LedgerError, "conflicts with another artifact"):
                self.ledger.ingest(candidate, dry_run=True)
        self.assert_deferred_untouched()

    @unittest.skipIf(os.name == "nt", "POSIX permission bits")
    def test_deferred_files_follow_umask_without_hard_links(self):
        packet = self.deferred_setup()
        previous = os.umask(0o022)
        try:
            with patch("os.link", side_effect=OSError("hard links unsupported")):
                self.ledger.ingest(packet)
        finally:
            os.umask(previous)
        self.assertEqual(stat.S_IMODE((self.root / "proofs/new.md").stat().st_mode), 0o644)
        self.assertEqual(self.view()["issues"], [])

    def test_deferred_failure_before_events_removes_its_files(self):
        packet = self.deferred_setup()
        with patch.object(self.ledger, "write_event", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(LedgerError, "no events; its files and index entry were removed"):
                self.ledger.ingest(packet)
        self.assert_deferred_untouched()
        original = research_state.write_new

        def editor_saves_index(path, data):
            original(path, data)
            (self.root / "research/index.md").write_text("# Routes\n- Earlier route\n- Saved\n")

        with patch("research_state.write_new", side_effect=editor_saves_index):
            with self.assertRaisesRegex(LedgerError, "index changed during ingest"):
                self.ledger.ingest(packet)
        self.assertFalse((self.root / "proofs").exists())
        self.assertFalse((self.root / "research/records").exists())
        (self.root / "research/index.md").write_text("# Routes\n- Earlier route\n")
        self.assertEqual(len(self.ledger.ingest(packet)), 2)

    def test_deferred_lone_surrogate_is_a_ledger_error(self):
        packet = self.deferred_setup()
        packet["artifacts"][1]["content"] = "\ud800"
        with self.assertRaisesRegex(LedgerError, "valid Unicode"):
            self.ledger.ingest(packet)
        with self.assertRaisesRegex(LedgerError, "valid Unicode"):
            self.ledger.record_many([{"type": "claim", "actor": "author\udc00", "payload": {}}])
        self.assert_deferred_untouched()

    def test_deferred_invalid_later_proposal_has_no_filesystem_effect(self):
        packet = self.deferred_setup()
        packet["proposals"][1]["payload"]["evidence"] = "E999999"
        with self.assertRaises(LedgerError):
            self.ledger.ingest(packet)
        self.assert_deferred_untouched()

    def test_deferred_interrupted_append_keeps_valid_prefix(self):
        packet = self.deferred_setup()
        original = self.ledger.write_event
        calls = 0
        def interrupt(event):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("simulated interruption")
            original(event)
        with patch.object(self.ledger, "write_event", side_effect=interrupt):
            with self.assertRaisesRegex(LedgerError, "after 1 of 2 events.*valid event prefix"):
                self.ledger.ingest(packet)
        self.assertEqual(len(self.ledger.read()["events"]), 2)
        self.assertTrue((self.root / "proofs/new.md").exists())
        self.assertIn("New route", (self.root / "research/index.md").read_text())
        with self.assertRaisesRegex(LedgerError, "stale deferred base"):
            self.ledger.ingest(packet)

    def test_writer_lock_release_never_hides_an_error(self):
        self.claim()
        lock = self.ledger.base / "write.lock"

        def lose_lock(event):
            lock.rmdir()  # e.g. someone removed a presumed-stale lock mid-write
            raise OSError("simulated failure")

        with patch.object(self.ledger, "write_event", side_effect=lose_lock):
            with self.assertRaisesRegex(LedgerError, "simulated failure"):
                self.claim("B")
        self.assertFalse(lock.exists())
        self.assertEqual(len(self.ledger.read()["events"]), 1)

    def test_read_does_not_initialize(self):
        other = self.root / "other"
        other.mkdir()
        with self.assertRaises(LedgerError):
            Ledger(other).read()
        self.assertEqual(list(other.iterdir()), [])

    def test_initialize_never_overwrites(self):
        self.claim()
        before = (self.ledger.events / "000001.json").read_bytes()
        with self.assertRaises(LedgerError):
            self.ledger.initialize()
        self.assertEqual(before, (self.ledger.events / "000001.json").read_bytes())

    def test_bounded_computation_cannot_discharge_universal_dependency(self):
        self.claim()
        self.evidence(kind="computation", assertion="Checked arities 0..6", bounds="0 <= arity <= 6",
                      non_claims=["Universal collapse remains open"])
        self.claim("B", ["A"])
        self.evidence("B")
        self.assertEqual(self.view()["claims"]["A"]["status"], "computation-recorded")
        self.assertEqual(self.view()["claims"]["B"]["status"], "conditional")

    def test_dependency_retraction_propagates_without_rewriting_history(self):
        self.claim()
        basis = self.evidence()
        self.claim("B", ["A"])
        self.evidence("B")
        self.assertEqual(self.view()["claims"]["B"]["status"], "proof-recorded")
        before = (self.ledger.events / "000002.json").read_bytes()
        self.record("retract", {"target": basis, "reason": "Invalid sign in proof"})
        self.assertEqual(self.view()["claims"]["B"]["status"], "conditional")
        self.assertEqual(before, (self.ledger.events / "000002.json").read_bytes())

    def test_transitive_revision_stales_evidence_and_audit(self):
        self.claim()
        self.evidence()
        self.claim("B", ["A"])
        self.evidence("B")
        self.claim("C", ["B"])
        c = self.evidence("C")
        self.review(c)
        self.assertEqual(self.view()["claims"]["C"]["review"], "independent-pass-recorded")
        self.claim(reason="Strengthen coefficient regime")
        claims = self.view()["claims"]
        self.assertEqual([claims[k]["status"] for k in "ABC"], ["stale"] * 3)
        self.assertEqual(claims["C"]["review"], "no-independent-pass-recorded")
        self.assertEqual(impact(claims, "A"), ["B", "C"])

    def test_changed_file_invalidates_evidence(self):
        self.claim()
        e = self.evidence()
        (self.root / "proof.md").write_text("Changed proof")
        self.assertEqual(self.view()["claims"]["A"]["status"], "stale")
        with self.assertRaises(LedgerError):
            self.review(e)

    def test_revalidated_evidence_can_supersede_stale_history(self):
        self.claim()
        old = self.evidence()
        self.claim(reason="Explicit contract revision")
        self.evidence(supersedes=[old])
        self.assertEqual(self.view()["claims"]["A"]["status"], "proof-recorded")
        self.assertEqual(self.view()["issues"], [])
        self.assertEqual(len(self.ledger.read()["events"]), 4)

    def test_lost_negative_review_cannot_rehabilitate_proof(self):
        self.claim()
        e = self.evidence()
        self.review(e, "fail")
        (self.root / "review.md").unlink()
        self.assertEqual(self.view()["claims"]["A"]["status"], "incomplete")
        self.assertTrue(self.view()["issues"])

    def test_failed_audit_blocks_claim_and_consumers(self):
        self.claim()
        e = self.evidence()
        self.claim("B", ["A"])
        self.evidence("B")
        r = self.review(e, "fail")
        self.assertEqual(self.view()["claims"]["A"]["status"], "incomplete")
        self.assertEqual(self.view()["claims"]["B"]["status"], "conditional")
        self.record("retract", {"target": r, "reason": "Reviewer corrected the alleged error"})
        self.assertEqual(self.view()["claims"]["B"]["status"], "proof-recorded")

    def test_conditional_review_does_not_certify(self):
        self.claim()
        e = self.evidence()
        self.review(e, "conditional")
        claim = self.view()["claims"]["A"]
        self.assertEqual(claim["status"], "conditional")
        self.assertEqual(claim["review"], "conditional-review-recorded")

    def test_conditional_computation_review_is_applied_and_retractable(self):
        self.claim()
        evidence = self.evidence(kind="computation", assertion="Checked one instance",
                                 bounds="One input", non_claims=["No general conclusion"])
        review = self.review(evidence, "conditional")
        claim = self.view()["claims"]["A"]
        self.assertEqual(claim["status"], "conditional")
        self.assertEqual(claim["review"], "conditional-review-recorded")
        self.assertEqual(claim["reviews"][review]["evidence"], evidence)
        self.record("retract", {"target": review, "reason": "Condition was resolved"})
        claim = self.view()["claims"]["A"]
        self.assertEqual(claim["status"], "computation-recorded")
        self.assertEqual(claim["reviews"], {})

    def test_conflicting_reviews_are_visible_with_reports(self):
        self.claim()
        evidence = self.evidence()
        passed = self.review(evidence)
        failed = self.review(evidence, "fail", independent=False)
        claim = self.view()["claims"]["A"]
        self.assertEqual(claim["status"], "incomplete")
        self.assertEqual(claim["review"], "conflicting-reviews-recorded")
        self.assertEqual(set(claim["reviews"]), {passed, failed})
        self.assertEqual(claim["reviews"][failed]["artifact"]["path"], "review.md")

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "handoff", "--goal", "A", "--full"]), 0)
        report = output.getvalue()
        for value in (passed, failed, "pass", "fail", "Report", "review.md"):
            self.assertIn(value, report)

    def test_review_independence_is_not_proof_strength(self):
        self.claim()
        e = self.evidence()
        with self.assertRaises(LedgerError):
            self.review(e, actor="author")
        self.review(e, actor="author", independent=False)
        self.assertEqual(self.view()["claims"]["A"]["review"], "no-independent-pass-recorded")
        self.review(e)
        c = self.view()["claims"]["A"]
        self.assertEqual(c["status"], "proof-recorded")
        self.assertEqual(c["review"], "independent-pass-recorded")

    def test_conditional_counterexample_requires_resolution(self):
        self.claim()
        e = self.evidence(kind="counterexample", hypothesis_check="Connectedness remains to be verified")
        r = self.review(e, "conditional")
        self.review(e, "pass")
        self.assertEqual(self.view()["claims"]["A"]["status"], "conditional")
        (self.root / "review.md").unlink()
        self.assertEqual(self.view()["claims"]["A"]["status"], "conditional")
        self.assertTrue(self.view()["issues"])
        self.record("retract", {"target": r, "reason": "Connectedness established"})
        self.assertEqual(self.view()["claims"]["A"]["status"], "counterexample-recorded")

    def test_unqualified_counterexample_still_refutes(self):
        self.claim()
        e = self.evidence(kind="counterexample", hypothesis_check="Witness under review")
        self.review(e, "conditional")
        self.evidence(kind="counterexample", hypothesis_check="Separate witness satisfies every hypothesis")
        self.assertEqual(self.view()["claims"]["A"]["status"], "counterexample-recorded")

    def test_conditional_counterexample_preserves_conflict(self):
        self.claim()
        self.evidence()
        e = self.evidence(kind="counterexample", hypothesis_check="Witness under review")
        self.review(e, "conditional")
        self.assertEqual(self.view()["claims"]["A"]["status"], "disputed")

    def test_competing_proof_and_counterexample_are_disputed(self):
        self.claim()
        self.evidence()
        self.evidence(kind="counterexample", hypothesis_check="Witness satisfies every hypothesis")
        self.assertEqual(self.view()["claims"]["A"]["status"], "disputed")

    def test_external_source_requires_exact_application(self):
        self.claim()
        with self.assertRaises(LedgerError):
            self.evidence(kind="source")
        self.evidence(kind="source", identifier="doi:example", version="v2", locator="Theorem 3",
                      translation="This is the same coefficient regime and natural map.")
        self.assertEqual(self.view()["claims"]["A"]["status"], "source-recorded")

    def test_invalid_event_never_enters_journal(self):
        self.claim()
        self.claim("B", ["A"])
        before = list(self.ledger.events.iterdir())
        with self.assertRaises(LedgerError):
            self.claim("A", ["B"], reason="Introduce a circular dependency")
        self.assertEqual(before, list(self.ledger.events.iterdir()))
        self.assertEqual(self.view()["claims"]["A"]["revision"], 1)

    def test_missing_dependency_is_rejected(self):
        with self.assertRaises(LedgerError):
            self.claim("A", ["UNKNOWN"])

    def test_path_escape_and_symlink_evidence_rejected(self):
        self.claim()
        for path in ("../proof.md", str(self.root / "proof.md")):
            with self.assertRaises(LedgerError):
                self.record("evidence", {"claim":"A", "kind":"proof", "summary":"Proof", "artifacts":[{"path":path}]})
        (self.root / "link.md").symlink_to(self.root / "proof.md")
        with self.assertRaises(LedgerError):
            self.ledger.pin({"path":"link.md"})

    def test_corruption_and_event_deletion_detected(self):
        self.claim()
        self.evidence()
        first = self.ledger.events / "000001.json"
        original = first.read_bytes()
        data = json.loads(original)
        data["payload"]["regime"] = "Q"
        first.write_text(json.dumps(data))
        with self.assertRaises(LedgerError):
            self.ledger.read()
        first.write_bytes(original)
        first.unlink()
        with self.assertRaises(LedgerError):
            self.ledger.read()

    def test_writer_lock_never_breaks_other_writer(self):
        lock = self.ledger.base / "write.lock"
        lock.mkdir()
        with self.assertRaises(LedgerError):
            self.claim()
        self.assertTrue(lock.is_dir())
        self.assertEqual(len(self.ledger.read()["events"]), 0)

    def route(self, rid="R", **extra):
        return self.record("route", dict(id=rid, claim="A", mechanism="integral-lift", question="Does the lift exist?",
                           discriminator="Compute its first obstruction", success="Construct lift", failure="Nonzero obstruction",
                           prerequisites=[], gain=4, cost=2, **extra))

    def test_failed_route_reopening_requires_new_input(self):
        self.claim()
        self.route()
        result = self.record("route-result", dict(route="R", outcome="failed", reason="Obstruction survives",
                                                  next_question="Does a different filtration remove it?"))
        with self.assertRaises(LedgerError):
            self.route("R2")
        before = {path.name: path.read_bytes() for path in self.ledger.events.glob("*.json")}
        self.route("R2", reopens=result, changed_input="New filtration changes the obstruction group")
        state = self.ledger.read()
        self.assertEqual([r["id"] for r in next_routes(state, self.view(), "A")], ["R2"])
        self.assertEqual(state["evidence"], {})
        for name, contents in before.items():
            self.assertEqual((self.ledger.events / name).read_bytes(), contents)

    def test_route_success_never_promotes_claim(self):
        self.claim()
        self.route()
        self.record("route-result", dict(route="R", outcome="succeeded", reason="Calculated a useful example",
                                         next_question="Can it be made uniform?"))
        self.assertEqual(self.view()["claims"]["A"]["status"], "conjectural")

    def test_inconclusive_run_keeps_route_available_for_later_continuation(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        self.record("route-run", {
            "id": "ANSATZ", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker",
            "work_scope": ["coefficient construction"],
        })
        next_question = "Derive the untried recurrence when the next session's budget is available"
        reason = "Recurrence remains untried; defer it until the next session"
        result = self.record("run-result", {
            "run": "ANSATZ", "outcome": "inconclusive",
            "reason": "Coefficient equations remain unresolved at the work package limit",
            "next_question": next_question, "result_revision": "revision-2",
        })
        continuation = self.record("route-reconcile", {
            "route": "R", "results": [result], "decision": "continue",
            "reason": reason, "next_question": next_question, "base_event": program,
            "base_revision": "revision-1", "current_revision": "revision-2", "conflicts": [],
        })

        def run(*args):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(self.root), *args]), 0)
            return output.getvalue()

        handoff = json.loads(run("--json", "handoff", "--goal", "A"))
        self.assertEqual([r["id"] for r in handoff["routes"]], ["R"])
        self.assertEqual(handoff["closed_routes"], [])
        self.assertEqual(handoff["state"]["runs"]["ANSATZ"]["status"], "inconclusive")
        expected = {"event_id": continuation, "next_question": next_question, "reason": reason}
        self.assertEqual(handoff["routes"][0]["continuation"], expected)
        self.assertEqual(json.loads(run("next", "--goal", "A"))[0]["continuation"], expected)
        self.assertIn(f"- R: ready; resolves A\n  Continue ({continuation}): {next_question}; "
                      f"reason: {reason}\n", run("handoff", "--goal", "A"))
        full = run("handoff", "--goal", "A", "--full")
        self.assertIn(f"  Continuation {continuation}: {next_question}\n"
                      f"  Continuation reason: {reason}\n", full)
        self.assertIn(f"- {continuation}: route R, continue; run results {result}; "
                      f"reason: {reason}; next question: {next_question}\n", full)
        self.record("route-run", {
            "id": "RECURRENCE", "program": "P", "route": "R", "base_event": continuation,
            "base_revision": "revision-2", "executor": "worker",
            "work_scope": ["recurrence construction"],
        })
        self.assertEqual(self.view()["runs"]["RECURRENCE"]["status"], "active")
        self.assertEqual(self.view()["claims"]["A"]["status"], "conjectural")
        self.assertEqual(len(self.ledger.read()["routes"]), 1)
        self.assertEqual(self.ledger.read()["evidence"], {})

    def test_handoff_retains_goal_relevant_closed_routes(self):
        self.claim()
        self.claim("B", ["A"])
        self.claim("UNRELATED")
        route_event = self.route()
        result = dict(route="R", outcome="failed", reason="Obstruction survives",
                      next_question="Does a different filtration remove it?")
        result_event = self.record("route-result", result)
        self.route("R2", reopens=result_event, changed_input="New filtration")
        unrelated = dict(self.ledger.read()["routes"]["R"]["payload"], id="OTHER", claim="UNRELATED")
        self.record("route", unrelated)
        self.record("route-result", dict(route="OTHER", outcome="blocked", reason="Unrelated obstruction",
                                         next_question="Unrelated question"))

        def run(*args):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(self.root), *args]), 0)
            return output.getvalue()

        before = {p.name: p.read_bytes() for p in self.ledger.events.iterdir()}
        handoff = json.loads(run("--json", "handoff", "--goal", "B"))
        self.assertEqual(set(handoff["state"]["claims"]), {"A", "B"})
        self.assertEqual([r["id"] for r in handoff["routes"]], ["R2"])
        self.assertEqual(handoff["closed_routes"], [dict(self.ledger.read()["routes"]["R"]["payload"],
                         resolves=["A"], event_id=route_event,
                         result=dict(result, event_id=result_event))])
        md = run("handoff", "--goal", "B", "--full")
        for value in ("integral-lift", "failed", result["reason"], result["next_question"], result_event):
            self.assertIn(value, md)
        self.assertNotIn("Unrelated obstruction", md)
        self.assertEqual([r["id"] for r in json.loads(run("--json", "handoff"))["closed_routes"]], ["R", "OTHER"])
        self.assertEqual([r["id"] for r in json.loads(run("next", "--goal", "B"))], ["R2"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.ledger.events.iterdir()})

    def test_goal_handoff_includes_route_context_without_changing_dependencies(self):
        self.claim("BASE")
        self.claim("AUX", ["BASE"])
        self.claim("GOAL")
        self.record("route", {
            "id": "R", "claim": "GOAL", "mechanism": "conditional construction",
            "question": "Does the auxiliary claim permit the construction?",
            "discriminator": "Check the auxiliary claim", "success": "Construct the object",
            "failure": "Auxiliary obstruction", "prerequisites": ["AUX"],
            "gain": 4, "cost": 2,
        })

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--json", "handoff",
                                   "--goal", "GOAL"]), 0)
        handoff = json.loads(output.getvalue())
        self.assertEqual(set(handoff["state"]["claims"]), {"GOAL"})
        self.assertEqual(set(handoff["state"]["route_context"]), {"AUX", "BASE"})
        self.assertEqual(handoff["state"]["claims"]["GOAL"]["dependencies"], [])
        self.assertEqual(handoff["routes"][0]["blocked_by"], ["AUX"])
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "handoff",
                                   "--goal", "GOAL", "--full"]), 0)
        markdown = output.getvalue()
        self.assertIn("## Route context", markdown)
        self.assertIn("### AUX", markdown)
        self.assertIn("Evidence status: conjectural", markdown)

    def test_parent_route_can_resolve_a_goal_obligation(self):
        self.claim("LEAF")
        self.claim("SIBLING")
        self.claim("PARENT", ["LEAF", "SIBLING"])
        route = self.record("route", {
            "id": "R", "claim": "PARENT", "resolves": ["LEAF"],
            "mechanism": "direct leaf argument", "question": "Can the leaf be proved directly?",
            "discriminator": "Construct the comparison", "success": "Prove the leaf",
            "failure": "Comparison obstruction", "prerequisites": [], "gain": 5, "cost": 2,
        })
        state = self.ledger.read()
        self.assertEqual([item["id"] for item in next_routes(state, self.view(), "LEAF")], ["R"])

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--json", "handoff",
                                   "--goal", "LEAF"]), 0)
        handoff = json.loads(output.getvalue())
        self.assertEqual(handoff["routes"][0]["resolves"], ["LEAF"])
        self.assertEqual(set(handoff["state"]["route_context"]), {"PARENT"})

        program = self.record("program", {
            "id": "P", "goal": "LEAF", "objective": "Resolve the leaf",
            "base_event": route, "base_revision": "revision-1",
        })
        self.record("route-run", {
            "id": "RUN", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker",
            "work_scope": ["direct leaf argument"],
        })
        projection = self.view()
        scoped = restrict(projection, self.ledger.read(), {"LEAF"})
        self.assertEqual(set(scoped["runs"]), {"RUN"})
        self.assertEqual(set(scoped["programs"]), {"P"})

    def test_route_resolves_only_owned_obligations_without_cloning_mechanisms(self):
        self.claim("LEAF")
        self.claim("OTHER")
        self.claim("PARENT", ["LEAF"])
        with self.assertRaises(LedgerError):
            self.record("route", {
                "id": "BAD", "claim": "PARENT", "resolves": ["OTHER"],
                "mechanism": "direct argument", "question": "Can it work?",
                "discriminator": "Check the map", "success": "Construct it",
                "failure": "Obstruction", "prerequisites": [], "gain": 3, "cost": 2,
            })
        self.record("route", {
            "id": "R", "claim": "PARENT", "resolves": ["LEAF"],
            "mechanism": "direct argument", "question": "Can it work?",
            "discriminator": "Check the map", "success": "Construct it",
            "failure": "Obstruction", "prerequisites": [], "gain": 3, "cost": 2,
        })
        with self.assertRaises(LedgerError):
            self.record("route", {
                "id": "COPY", "claim": "PARENT", "resolves": ["PARENT"],
                "mechanism": "direct argument", "question": "Can it work globally?",
                "discriminator": "Check the global map", "success": "Construct it",
                "failure": "Obstruction", "prerequisites": [], "gain": 3, "cost": 2,
            })

    def test_unresolved_dependency_downgrades_finite_evidence(self):
        self.claim()
        self.claim("B", ["A"])
        self.evidence("B", kind="computation", assertion="Checked arities 0..6", bounds="0 <= arity <= 6",
                      non_claims=["Universal collapse remains open"])
        claim = self.view()["claims"]["B"]
        self.assertEqual(claim["status"], "conditional")
        self.assertEqual(claim["blocked_by"], ["A"])

    def test_open_route_mechanism_is_not_silently_repeated(self):
        self.claim()
        self.route()
        with self.assertRaises(LedgerError):
            self.route("R2")
        self.assertEqual(list(self.ledger.read()["routes"]), ["R"])

    def test_goal_handoff_hides_unrelated_stale_records(self):
        (self.root / "other.md").write_text("An unrelated durable argument.")
        self.claim()
        self.evidence()
        self.claim("B", ["A"])
        self.claim("UNRELATED")
        stale = self.record("evidence", dict(claim="UNRELATED", kind="proof", summary="Unrelated result",
                                             artifacts=[{"path": "other.md"}]))
        report = self.review(stale)
        (self.root / "other.md").write_text("A different unrelated argument.")
        (self.root / "review.md").unlink()

        def run(*args):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(self.root), *args]), 0)
            return output.getvalue()

        handoff = json.loads(run("--json", "handoff", "--goal", "B"))
        self.assertEqual(set(handoff["state"]["claims"]), {"A", "B"})
        self.assertEqual(handoff["state"]["issues"], [])
        self.assertNotIn("other.md", run("handoff", "--goal", "B"))
        self.assertEqual({i["event"] for i in json.loads(run("--json", "status"))["issues"]}, {stale, report})

    def test_legacy_config_is_readable_with_neutral_projection(self):
        (self.ledger.base / "config.json").write_text('{"schema_version": 1}\n')
        self.claim()
        self.evidence()
        claim = self.view()["claims"]["A"]
        self.assertEqual(claim["status"], "proof-recorded")
        self.assertNotIn("proved", claim["status"])

    def test_check_summary_reports_counts_and_issue_details(self):
        self.claim()
        self.evidence()
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "check", "--summary"]), 0)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["events"], 2)
        self.assertEqual(summary["claims"], 1)
        self.assertEqual(summary["statuses"], {"proof-recorded": 1})
        self.assertEqual(summary["review_statuses"], {"no-independent-pass-recorded": 1})
        self.assertEqual(summary["issue_count"], 0)
        self.assertEqual(summary["issues"], [])
        (self.root / "proof.md").write_text("Changed proof")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "check", "--summary"]), 1)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["statuses"], {"stale": 1})
        self.assertEqual(summary["issue_count"], 1)
        self.assertEqual(summary["issues"][0]["event"], "E000002")

    def test_statement_artifact_binds_claim_and_transitive_evidence(self):
        (self.root / "statement.md").write_text("Theorem A, exact version one.")
        self.claim(statement_artifact={"path": "statement.md", "locator": "Theorem A"})
        evidence = self.evidence()
        self.claim("B", ["A"])
        self.evidence("B")
        self.assertEqual(self.view()["claims"]["B"]["status"], "proof-recorded")
        (self.root / "statement.md").write_text("Theorem A, materially revised.")
        view = self.view()
        self.assertEqual(view["claims"]["A"]["status"], "stale")
        self.assertEqual(view["claims"]["B"]["status"], "stale")
        self.assertTrue(any("statement contract" in issue["issue"] for issue in view["issues"]))
        with self.assertRaises(LedgerError):
            self.review(evidence)

    def test_computation_manifest_pins_dependency_and_result_closure(self):
        (self.root / "input.py").write_text("print(6 * 7)\n")
        (self.root / "result.json").write_text('{"answer": 42}\n')
        manifest = {
            "schema_version": 2,
            "claim_id": "A",
            "run": {"status": "completed", "exit_status": 0},
            "input_artifacts": [{
                "path": "input.py", "sha256": file_hash(self.root / "input.py"),
                "sha256_after": file_hash(self.root / "input.py"),
            }],
            "outputs": [{"path": "result.json", "sha256": file_hash(self.root / "result.json")}],
        }
        (self.root / "manifest.json").write_text(json.dumps(manifest))
        self.claim()
        event = self.record("evidence", {
            "claim": "A", "kind": "computation", "summary": "A bounded exact run",
            "artifacts": [], "manifest": {"path": "manifest.json"},
            "assertion": "The finite instance returns 42", "bounds": "One fixed input",
            "non_claims": ["No uniform assertion"],
        })
        payload = self.ledger.read()["evidence"][event]["payload"]
        self.assertEqual([a["path"] for a in payload["manifest_inputs"]], ["input.py"])
        self.assertEqual([a["path"] for a in payload["manifest_outputs"]], ["result.json"])
        self.assertEqual(self.view()["claims"]["A"]["status"], "computation-recorded")
        (self.root / "input.py").write_text("print(43)\n")
        self.assertEqual(self.view()["claims"]["A"]["status"], "stale")

    def test_computation_manifest_rejects_wrong_claim_and_input_output_overlap(self):
        (self.root / "artifact.txt").write_text("fixed")
        checksum = file_hash(self.root / "artifact.txt")
        self.claim()
        base = {
            "schema_version": 2, "claim_id": "OTHER",
            "run": {"status": "completed", "exit_status": 0},
            "input_artifacts": [{"path": "artifact.txt", "sha256": checksum,
                                 "sha256_after": checksum}],
            "outputs": [{"path": "artifact.txt", "sha256": checksum}],
        }
        (self.root / "manifest.json").write_text(json.dumps(base))
        proposal = {
            "claim": "A", "kind": "computation", "summary": "Finite run", "artifacts": [],
            "manifest": {"path": "manifest.json"}, "assertion": "Fixed check",
            "bounds": "One input", "non_claims": ["No general conclusion"],
        }
        with self.assertRaises(LedgerError):
            self.record("evidence", proposal)
        base["claim_id"] = "A"
        (self.root / "manifest.json").write_text(json.dumps(base))
        with self.assertRaises(LedgerError):
            self.record("evidence", proposal)
        (self.root / "result.txt").write_text("result")
        base["outputs"] = [{"path": "result.txt", "sha256": file_hash(self.root / "result.txt")}]
        base["schema_version"] = 1
        (self.root / "manifest.json").write_text(json.dumps(base))
        with self.assertRaises(LedgerError):
            self.record("evidence", proposal)
        base["schema_version"] = 2
        del base["input_artifacts"][0]["sha256_after"]
        (self.root / "manifest.json").write_text(json.dumps(base))
        with self.assertRaises(LedgerError):
            self.record("evidence", proposal)
        base["input_artifacts"][0]["sha256_after"] = checksum
        base["run"] = {"status": "failed", "exit_status": 1}
        (self.root / "manifest.json").write_text(json.dumps(base))
        with self.assertRaises(LedgerError):
            self.record("evidence", proposal)

    def test_program_parallel_runs_and_delayed_reconciliation(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        run_one = self.record("route-run", {
            "id": "RUN_ONE", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker-one",
            "work_scope": ["first synthetic branch"],
        })
        self.record("run-observation", {
            "run": "RUN_ONE", "state": "waiting", "summary": "Awaiting a finite check",
            "observed_revision": "revision-2",
        })
        run_two = self.record("route-run", {
            "id": "RUN_TWO", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker-two",
            "work_scope": ["second synthetic branch"],
        })
        run_one_result = self.record("run-result", {
            "run": "RUN_ONE", "outcome": "succeeded", "reason": "Constructed a candidate",
            "next_question": "Does the second branch agree?", "result_revision": "revision-2",
            "artifacts": [{"path": "proof.md"}],
        })
        self.record("route-reconcile", {
            "route": "R", "results": [run_one_result], "decision": "continue",
            "reason": "Wait for the parallel branch", "next_question": "Does it agree?",
            "base_event": program, "base_revision": "revision-1",
            "current_revision": "revision-2", "conflicts": [],
        })
        run_two_result = self.record("run-result", {
            "run": "RUN_TWO", "outcome": "abandoned", "reason": "Its prerequisite was absent",
            "next_question": "Can another branch avoid it?", "result_revision": "revision-3",
        })
        closure = self.record("route-reconcile", {
            "route": "R", "results": [run_one_result, run_two_result],
            "decision": "inconclusive", "reason": "The branches do not settle the goal",
            "next_question": "Open a route with changed input", "current_revision": "revision-3",
            "base_event": program, "base_revision": "revision-1",
            "conflicts": ["One candidate lacks an independent bridge"],
        })
        state = self.ledger.read()
        self.assertTrue(route_event)
        self.assertEqual(next_routes(state, self.view(), "A"), [])
        runs = self.view()["runs"]
        self.assertEqual(runs["RUN_ONE"]["status"], "succeeded")
        self.assertEqual(runs["RUN_TWO"]["status"], "abandoned")
        self.assertEqual(runs["RUN_ONE"]["last_observed"]["event_id"], run_one_result)
        with self.assertRaises(LedgerError):
            self.record("route-run", {
                "id": "TOO_LATE", "program": "P", "route": "R", "base_event": closure,
                "base_revision": "revision-3", "executor": "worker",
                "work_scope": ["new work after closure"],
            })
        self.record("program-result", {
            "program": "P", "outcome": "abandoned", "reason": "No live route remains",
            "next_action": "Reopen only with new mathematical input", "closed_revision": "revision-3",
        })
        self.assertEqual(self.view()["programs"]["P"]["status"], "abandoned")
        reopened = dict(id="R2", claim="A", mechanism="integral-lift",
                        question="Does changed input permit the lift?",
                        discriminator="Compute the revised obstruction", success="Construct lift",
                        failure="Nonzero obstruction", prerequisites=[], gain=4, cost=2,
                        reopens=closure, changed_input="A new filtration changes the obstruction group")
        self.record("route", reopened)

    def test_late_parallel_result_gets_explicit_disposition(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        for run in ("FAST", "SLOW"):
            self.record("route-run", {
                "id": run, "program": "P", "route": "R", "base_event": program,
                "base_revision": "revision-1", "executor": run.lower(),
                "work_scope": [run.lower() + " branch"],
            })
        fast = self.record("run-result", {
            "run": "FAST", "outcome": "failed", "reason": "A decisive obstruction",
            "next_question": "Can changed input remove it?", "result_revision": "revision-2",
        })
        self.record("route-reconcile", {
            "route": "R", "results": [fast], "decision": "failed",
            "reason": "The declared failure criterion was met",
            "next_question": "Change the input before reopening", "current_revision": "revision-2",
            "base_event": program, "base_revision": "revision-1", "conflicts": [],
        })
        slow = self.record("run-result", {
            "run": "SLOW", "outcome": "succeeded", "reason": "A delayed candidate arrived",
            "next_question": "Is it compatible with the obstruction?", "result_revision": "revision-1",
        })
        late = self.record("route-reconcile", {
            "route": "R", "results": [slow], "decision": "late-conflict",
            "reason": "The delayed result conflicts with the recorded closure",
            "next_question": "Audit the assumptions before reopening", "current_revision": "revision-3",
            "base_event": program, "base_revision": "revision-1",
            "conflicts": ["The workers used different auxiliary assumptions"],
        })
        projection = self.view()
        self.assertEqual(projection["runs"]["SLOW"]["status"], "succeeded")
        self.assertEqual(projection["reconciliations"][-1]["event_id"], late)
        self.assertEqual(projection["reconciliations"][-1]["decision"], "late-conflict")

    def test_unknown_observation_does_not_imply_liveness(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Inspect an imported launch",
            "base_event": route_event, "base_revision": "snapshot-old",
        })
        self.record("program-observation", {
            "program": "P", "state": "unknown", "summary": "No liveness signal is available",
            "observed_revision": "snapshot-current",
        })
        self.record("route-run", {
            "id": "RUN", "program": "P", "route": "R", "base_event": program,
            "base_revision": "snapshot-old", "executor": "imported-worker",
            "work_scope": ["historical launch"],
        })
        observation = self.record("run-observation", {
            "run": "RUN", "state": "unknown", "summary": "Execution state was not observed",
            "observed_revision": "snapshot-current",
        })
        view = self.view()
        self.assertEqual(view["programs"]["P"]["status"], "unknown")
        self.assertEqual(view["runs"]["RUN"]["status"], "unknown")
        self.assertEqual(view["runs"]["RUN"]["last_observed"]["event_id"], observation)
        with self.assertRaises(LedgerError):
            self.record("program-result", {
                "program": "P", "outcome": "abandoned", "reason": "Historical work stopped",
                "next_action": "Record the run disposition", "closed_revision": "snapshot-current",
            })

    def test_reconciliation_rejects_mixed_bases(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Compare two synthetic branches",
            "base_event": route_event, "base_revision": "snapshot-one",
        })
        results = []
        for run, base in (("ONE", program), ("TWO", route_event)):
            self.record("route-run", {
                "id": run, "program": "P", "route": "R", "base_event": base,
                "base_revision": "snapshot-one", "executor": run.lower(),
                "work_scope": [run.lower() + " branch"],
            })
            results.append(self.record("run-result", {
                "run": run, "outcome": "inconclusive", "reason": "No decisive result",
                "next_question": "Try another invariant", "result_revision": "snapshot-two",
            }))
        with self.assertRaises(LedgerError):
            self.record("route-reconcile", {
                "route": "R", "results": results, "decision": "continue",
                "base_event": program, "base_revision": "snapshot-one",
                "current_revision": "snapshot-two", "reason": "Compare the branches",
                "next_question": "Normalize their bases", "conflicts": ["Different ledger bases"],
            })

    def test_batch_prevalidates_and_resolves_prior_event_aliases(self):
        proposals = [
            {"type": "claim", "actor": "author", "payload": {
                "id": "A", "statement": "Exact quantified assertion A", "hypotheses": ["finite type"],
                "regime": "Z", "level": "chain", "dependencies": []}},
            {"alias": "proof_a", "type": "evidence", "actor": "author", "payload": {
                "claim": "A", "kind": "proof", "summary": "Durable result",
                "artifacts": [{"path": "proof.md"}]}},
            {"type": "review", "actor": "reviewer", "payload": {
                "evidence": {"$event": "proof_a"}, "outcome": "pass", "independent": True,
                "summary": "Fresh review", "artifact": {"path": "review.md"}}},
        ]
        preview = self.ledger.record_many(proposals, dry_run=True)
        self.assertEqual([e["event_id"] for e in preview], ["E000001", "E000002", "E000003"])
        self.assertEqual(list(self.ledger.events.iterdir()), [])
        events = self.ledger.record_many(proposals)
        self.assertEqual(events[2]["payload"]["evidence"], events[1]["event_id"])
        self.assertEqual(self.view()["claims"]["A"]["review"], "independent-pass-recorded")
        self.assertEqual(len(self.ledger.read()["events"]), 3)

    def test_invalid_batch_appends_nothing(self):
        good = {"type": "claim", "actor": "author", "payload": {
            "id": "A", "statement": "Exact quantified assertion A", "hypotheses": [],
            "regime": "Z", "level": "chain", "dependencies": []}}
        bad = {"type": "claim", "actor": "author", "payload": {
            "id": "B", "statement": "Exact quantified assertion B", "hypotheses": [],
            "regime": "Z", "level": "chain", "dependencies": ["MISSING"]}}
        with self.assertRaises(LedgerError):
            self.ledger.record_many([good, bad])
        self.assertEqual(list(self.ledger.events.iterdir()), [])

    def test_batch_cli_receipts_and_dry_run(self):
        proposals = [{"type": "claim", "actor": "author", "payload": {
            "id": "A", "statement": "Exact quantified assertion A", "hypotheses": [],
            "regime": "Z", "level": "chain", "dependencies": []}}]
        batch = self.root / "batch.json"
        batch.write_text(json.dumps(proposals), encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "record-batch",
                                   str(batch), "--dry-run"]), 0)
        self.assertTrue(json.loads(output.getvalue())["dry_run"])
        self.assertEqual(list(self.ledger.events.iterdir()), [])
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "record-batch", str(batch)]), 0)
        recorded = json.loads(output.getvalue())
        self.assertEqual(recorded["sample"][0]["event_id"], "E000001")
        self.assertEqual(recorded["count"], 1)
        self.assertNotIn("payload", recorded["sample"][0])
        self.assertEqual(len(self.ledger.read()["events"]), 1)

    def test_batch_receipts_name_subjects_and_pins(self):
        self.claim()
        evidence = self.evidence()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        self.record("route-run", {
            "id": "RUN", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker", "work_scope": ["one branch"],
        })
        proposals = [
            {"type": "retract", "actor": "author", "payload": {
                "target": evidence, "reason": "Sign error"}},
            {"type": "run-result", "actor": "worker", "payload": {
                "run": "RUN", "outcome": "failed", "reason": "Obstruction",
                "next_question": "Change the filtration?", "result_revision": "revision-2",
                "artifacts": [{"path": "./review.md"}]}},
        ]
        batch = self.root / "batch.json"
        batch.write_text(json.dumps(proposals), encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "record-batch",
                                   str(batch), "--dry-run"]), 0)
        sample = json.loads(output.getvalue())["sample"]
        self.assertEqual([item["subject"] for item in sample], [evidence, "RUN"])
        self.assertNotIn("pins", sample[0])
        self.assertEqual(sample[1]["pins"],
                         [{"path": "review.md", "sha256": file_hash(self.root / "review.md")}])

    def test_interrupted_batch_leaves_valid_prefix(self):
        proposals = [{"type": "claim", "actor": "author", "payload": {
            "id": key, "statement": "Exact assertion " + key, "hypotheses": [],
            "regime": "Z", "level": "chain", "dependencies": []}}
            for key in ("A", "B")]
        write_event = self.ledger.write_event

        def interrupt_second(event):
            if event["event_id"] == "E000002":
                raise OSError("synthetic disk interruption")
            write_event(event)

        with patch.object(self.ledger, "write_event", side_effect=interrupt_second):
            with self.assertRaisesRegex(LedgerError, "valid event prefix may remain"):
                self.ledger.record_many(proposals)
        self.assertEqual(list(self.ledger.read()["claims"]), ["A"])

    def test_large_batch_default_receipt_is_bounded(self):
        proposals = [{"type": "claim", "actor": "author", "payload": {
            "id": f"C{number:02d}", "statement": f"Exact assertion {number}",
            "hypotheses": [], "regime": "Z", "level": "chain", "dependencies": []}}
            for number in range(25)]
        batch = self.root / "batch.json"
        batch.write_text(json.dumps(proposals), encoding="utf-8")
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "record-batch", str(batch)]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["count"], 25)
        self.assertEqual(result["receipts_omitted"], 17)
        self.assertLess(len(output.getvalue()), 2500)

    def test_brief_reports_bound_output_and_preserve_full_access(self):
        for number in range(30):
            self.claim(f"C{number:02d}")
            self.evidence(f"C{number:02d}")
        (self.root / "proof.md").write_text("Changed proof")

        def run(*args):
            output = StringIO()
            with redirect_stdout(output):
                code = main(["--root", str(self.root), *args])
            return code, output.getvalue()

        code, status = run("status")
        self.assertEqual(code, 0)
        self.assertLess(len(status), 4000)
        self.assertIn("20 more claims", status)
        self.assertIn("22 more issues", status)
        code, summary_text = run("check", "--summary")
        self.assertEqual(code, 1)
        summary = json.loads(summary_text)
        self.assertEqual(summary["issue_count"], 30)
        self.assertEqual(summary["issues_omitted"], 22)
        self.assertEqual(len(summary["issues"]), 8)
        code, full = run("--json", "check")
        self.assertEqual(code, 1)
        self.assertEqual(len(json.loads(full)["issues"]), 30)

    def test_brief_view_stays_small_at_large_project_scale(self):
        projection = {
            "events": 1500,
            "claims": {f"C{number:03d}": {"status": "stale", "review": "no-independent-pass-recorded",
                                         "blocked_by": [], "reviews": {}}
                       for number in range(350)},
            "issues": [{"event": f"E{number:06d}", "issue": "changed proof artifact"}
                       for number in range(1700)],
            "route_context": {},
        }
        report = brief_markdown(projection)
        self.assertLess(len(report.encode("utf-8")), 10_000)
        self.assertIn("integrity/freshness issues: 1700", report)
        self.assertIn("1692 more issues", report)

    def test_brief_handoff_surfaces_runs_needing_attention(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        for run in ("DONE", "LIVE", "SETTLED"):
            self.record("route-run", {
                "id": run, "program": "P", "route": "R", "base_event": program,
                "base_revision": "revision-1", "executor": run.lower(),
                "work_scope": [run.lower() + " branch"],
            })
        settled = self.record("run-result", {
            "run": "SETTLED", "outcome": "inconclusive", "reason": "No decisive result",
            "next_question": "Try another invariant", "result_revision": "revision-2",
        })
        self.record("route-reconcile", {
            "route": "R", "results": [settled], "decision": "continue",
            "reason": "Wait for the other branches", "next_question": "Do they agree?",
            "base_event": program, "base_revision": "revision-1",
            "current_revision": "revision-2", "conflicts": [],
        })
        done = self.record("run-result", {
            "run": "DONE", "outcome": "succeeded", "reason": "Constructed a candidate",
            "next_question": "Does it generalize?", "result_revision": "revision-2",
            "artifacts": [{"path": "review.md"}],
        })
        (self.root / "review.md").write_text("Changed report")

        def run(*args):
            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["--root", str(self.root), *args]), 0)
            return output.getvalue()

        brief = run("handoff", "--goal", "A")
        self.assertIn("Programs: 1 (active 1); runs: 3 (active 1, inconclusive 1, stale-result 1); "
                      "reconciliations: 1; runs needing attention: 2.", brief)
        self.assertIn("Open programs: P (active).", brief)
        self.assertIn(f"- DONE: stale-result; route R; program P; result {done} unreconciled", brief)
        self.assertIn("- LIVE: active; route R; program P\n", brief)
        self.assertNotIn("- SETTLED:", brief)
        self.assertIn("- R: ready; resolves A; runs DONE (stale-result), LIVE (active)", brief)
        self.assertIn("runs needing attention: 2.", run("status"))
        self.assertIn(f"result {done} unreconciled", run("handoff", "--goal", "A", "--full"))

    def test_pin_impact_reports_direct_and_transitive_claims(self):
        self.claim("A", statement_artifact={"path": "proof.md", "locator": "Theorem A"})
        self.evidence("A")
        self.claim("B", ["A"])
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--json", "pin-impact", "proof.md"]), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["direct_claims"], ["A"])
        self.assertEqual(result["dependent_claims"], ["B"])
        self.assertEqual(result["evidence_events"], ["E000002"])
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "pin-impact", "proof.md", "--full"]), 0)
        self.assertEqual(json.loads(output.getvalue()), result)

    def pins(self, path):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--json", "pin-impact", path]), 0)
        return json.loads(output.getvalue())

    def test_pin_impact_matches_path_spellings(self):
        (self.root / "proofs").mkdir()
        (self.root / "proofs" / "a.md").write_text("A complete argument.")
        self.claim()
        evidence = self.record("evidence", dict(claim="A", kind="proof", summary="Durable result",
                               artifacts=[{"path": "./proofs//a.md"}]))
        state = self.ledger.read()
        self.assertEqual(state["evidence"][evidence]["payload"]["artifacts"][0]["path"], "proofs/a.md")
        self.assertEqual(self.pins("proofs/a.md")["evidence_events"], [evidence])
        self.assertEqual(self.pins("proofs/./a.md")["direct_claims"], ["A"])
        # Ledgers written before normalization keep the spelling that was typed.
        state["evidence"][evidence]["payload"]["artifacts"][0]["path"] = "./proofs//a.md"
        self.assertEqual(pin_impact(state, "proofs/a.md")["evidence_events"], [evidence])

    def test_pin_impact_reports_run_result_pins_and_skips_hashing(self):
        self.claim()
        route_event = self.route()
        program = self.record("program", {
            "id": "P", "goal": "A", "objective": "Resolve the synthetic goal",
            "base_event": route_event, "base_revision": "revision-1",
        })
        self.record("route-run", {
            "id": "RUN", "program": "P", "route": "R", "base_event": program,
            "base_revision": "revision-1", "executor": "worker", "work_scope": ["one branch"],
        })
        result = self.record("run-result", {
            "run": "RUN", "outcome": "succeeded", "reason": "Constructed a candidate",
            "next_question": "Does it generalize?", "result_revision": "revision-2",
            "artifacts": [{"path": "review.md"}],
        })
        with patch("research_state.file_hash", side_effect=AssertionError("hashed")):
            pinned = self.pins("review.md")
        self.assertEqual(pinned["run_result_events"], [result])
        self.assertEqual(pinned["runs"], ["RUN"])
        self.assertEqual(pinned["direct_claims"], [])


    def relocation(self, event, slot="artifacts/0", destination="archive/proof.md", **extra):
        pin = next(p for p in research_state.pin_references(self.ledger.read()["events"][event])
                   if p["slot"] == slot)
        pin.update(extra)
        return {"type": "artifact-relocation", "actor": "archivist", "payload": {
            "pins": [pin], "destination": {"path": destination}, "reason": "Archived unchanged bytes"}}

    def archive(self, path="proof.md", destination="archive/proof.md"):
        target = self.root / destination
        target.parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).rename(target)

    def tree_snapshot(self):
        return {p.relative_to(self.root).as_posix():
                (p.read_bytes() if p.is_file() else None, p.stat().st_mtime_ns, p.stat().st_mode)
                for p in self.root.rglob("*")}

    def json_command(self, *args, code=0):
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--root", str(self.root), "--json", *args]), code)
        return json.loads(output.getvalue())

    def test_relocation_missing_original_recovers_and_read_commands_are_read_only(self):
        self.claim()
        eid = self.evidence()
        original = (self.ledger.events / "000002.json").read_bytes()
        self.archive()
        self.assertEqual(self.json_command("check", code=1)["claims"]["A"]["status"], "stale")
        proposal = self.relocation(eid)
        before = self.tree_snapshot()
        self.ledger.record_many([proposal], dry_run=True)
        # Dry-run briefly takes the existing writer lock; no artifact or event changes.
        self.assertEqual({p: v for p, v in before.items() if p != ".mathbox"},
                         {p: v for p, v in self.tree_snapshot().items() if p != ".mathbox"})
        relocation = self.ledger.record(proposal)
        self.assertEqual((self.ledger.events / "000002.json").read_bytes(), original)
        self.assertFalse((self.root / "proof.md").exists())
        before = self.tree_snapshot()
        checked = self.json_command("check")
        self.assertEqual(checked["claims"]["A"]["status"], "proof-recorded")
        self.assertEqual(checked["issues"], [])
        info = checked["relocations"][0]
        self.assertEqual((info["event"], info["slot"], info["path"], info["effective_path"]),
                         (eid, "artifacts/0", "proof.md", "archive/proof.md"))
        self.assertEqual(info["relocation"]["event"], relocation["event_id"])
        self.assertEqual(info["relocation"]["actor"], "archivist")
        self.assertEqual(info["verification"], "verified")
        self.assertEqual(info["original_status"], "missing")
        self.assertEqual(self.json_command("status"), checked)
        self.assertEqual(self.json_command("handoff")["state"], checked)
        self.assertEqual(self.json_command("next", "--full")["state"], checked)
        self.json_command("impact", "A")
        for path in ("proof.md", "archive/proof.md"):
            self.assertEqual(self.pins(path)["evidence_events"], [eid])
        self.assertEqual(self.tree_snapshot(), before)

    def test_relocation_rejects_invalid_references_and_destination(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        good = self.relocation(eid)
        variants = []
        for key, value in (("event", "E999999"), ("slot", "artifacts/9"),
                           ("path", "another.md"), ("sha256", "0" * 64),
                           ("replaces", "E000001"), ("slot", "artifacts/00")):
            p = json.loads(json.dumps(good))
            p["payload"]["pins"][0][key] = value
            variants.append(p)
        missing_slot = json.loads(json.dumps(good))
        del missing_slot["payload"]["pins"][0]["slot"]
        variants.append(missing_slot)
        duplicate = json.loads(json.dumps(good))
        duplicate["payload"]["pins"] *= 2
        variants.append(duplicate)
        wrong_hash = json.loads(json.dumps(good))
        wrong_hash["payload"]["destination"]["sha256"] = "0" * 64
        variants.append(wrong_hash)
        for p in variants:
            with self.subTest(proposal=p), self.assertRaises(LedgerError):
                self.ledger.record(p)
        (self.root / "archive/proof.md").write_text("Different bytes")
        with self.assertRaisesRegex(LedgerError, "hash differs"):
            self.ledger.record(good)
        self.assertEqual(len(self.ledger.read()["events"]), 2)

    def test_relocation_same_path_different_hashes_and_duplicate_slots(self):
        self.claim()
        first = self.evidence()
        self.archive(destination="archive/first.md")
        (self.root / "proof.md").write_text("A different argument")
        second = self.record("evidence", dict(claim="A", kind="proof", summary="Second argument",
                             artifacts=[{"path": "proof.md"}, {"path": "proof.md"}]))
        self.archive(destination="archive/second.md")
        self.ledger.record(self.relocation(first, destination="archive/first.md"))
        self.assertEqual(self.view()["claims"]["A"]["evidence"][first]["issues"], [])
        self.assertEqual(len(self.view()["claims"]["A"]["evidence"][second]["issues"]), 2)
        p = self.relocation(second, destination="archive/second.md")
        p["payload"]["pins"] += self.relocation(second, "artifacts/1")["payload"]["pins"]
        self.ledger.record(p)
        self.assertEqual(self.view()["issues"], [])
        self.assertEqual(len(self.view()["relocations"]), 3)
        self.assertEqual(len(self.pins("proof.md")["references"]), 3)
        counts = self.json_command("check", "--summary")["relocation_counts"]
        self.assertEqual(counts["verified_references"], 3)
        self.assertEqual(counts["verified_destinations"], 2)
        # New evidence cannot discover an archive through an older pin.
        with self.assertRaisesRegex(LedgerError, "missing artifact"):
            self.evidence()

    def test_relocation_destination_failure_does_not_break_replay(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        self.ledger.record(self.relocation(eid))
        dest = self.root / "archive/proof.md"
        data = dest.read_bytes()
        for failure in ("changed", "missing", "directory", "symlink", "unreadable"):
            with self.subTest(failure=failure):
                if failure == "changed":
                    dest.write_text("wrong")
                elif failure == "missing":
                    dest.unlink()
                elif failure == "directory":
                    dest.unlink()
                    dest.mkdir()
                elif failure == "symlink":
                    dest.unlink()
                    dest.symlink_to(self.root / "review.md")
                def hash_file(path):
                    if failure == "unreadable" and path == dest:
                        raise PermissionError("synthetic unreadable archive")
                    return file_hash(path)
                with patch("research_state.file_hash", side_effect=hash_file):
                    self.assertEqual(len(self.ledger.read()["events"]), 3)
                    check = self.json_command("check", code=1)
                    self.assertEqual(check["claims"]["A"]["status"], "stale")
                    self.assertEqual(check["relocations"][0]["verification"], "failed")
                if dest.is_dir():
                    dest.rmdir()
                else:
                    dest.unlink(missing_ok=True)
                dest.write_bytes(data)
        self.assertEqual(self.view()["issues"], [])

    def test_relocation_original_conflict_and_both_matching(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        data = (self.root / "archive/proof.md").read_bytes()
        (self.root / "proof.md").write_text("changed")
        with self.assertRaisesRegex(LedgerError, "original conflict"):
            self.ledger.record(self.relocation(eid))
        (self.root / "proof.md").write_bytes(data)
        self.ledger.record(self.relocation(eid))
        self.assertEqual(self.view()["issues"], [])
        self.assertEqual(self.view()["relocations"][0]["original_status"], "matching")
        (self.root / "proof.md").write_text("changed again")
        self.assertIn("original conflict", self.view()["issues"][0]["issue"])
        (self.root / "proof.md").write_bytes(data)
        (self.root / "archive/proof.md").unlink()
        self.assertTrue(self.view()["issues"], "Matching original must not bypass broken declaration")

    def test_relocation_path_safety(self):
        self.claim()
        eid = self.evidence()
        (self.root / "alias").symlink_to(self.root, target_is_directory=True)
        (self.root / "dangling").symlink_to(self.root / "absent")
        for dest in ("../escape.md", str(self.root / "proof.md"), ".mathbox/config.json",
                     "alias/proof.md", "dangling", "./proof.md", "././proof.md", "."):
            with self.subTest(destination=dest), self.assertRaises(LedgerError):
                self.ledger.record(self.relocation(eid, destination=dest))
        self.archive()
        (self.root / "proof.md").symlink_to(self.root / "archive/proof.md")
        with self.assertRaisesRegex(LedgerError, "symlink"):
            self.ledger.record(self.relocation(eid))
        (self.root / "proof.md").unlink()
        self.ledger.record(self.relocation(eid))
        (self.root / "proof.md").symlink_to(self.root / "archive/proof.md")
        self.assertTrue(self.view()["issues"])

    def test_relocation_unreadable_original_is_not_treated_as_absent(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        self.ledger.record(self.relocation(eid))
        real_stat = Path.stat

        def strict_stat(path, *args, **kwargs):
            if path == self.root / "proof.md" and kwargs.get("follow_symlinks", True):
                raise PermissionError("synthetic unreadable original")
            return real_stat(path, *args, **kwargs)

        def hashes(root, name, overlays=None):
            # Reproduce Python versions where is_file() suppresses access errors.
            if name == "proof.md":
                return root / name, name, None
            return root / name, name, file_hash(root / name)

        with patch("research_state.current_hash", side_effect=hashes), patch.object(Path, "stat", strict_stat):
            view = self.view()
            self.assertEqual(view["claims"]["A"]["status"], "stale")
            self.assertEqual(view["relocations"][0]["original_status"], "unsafe-or-unreadable")

    def test_relocation_explicit_partial_replacement_and_history(self):
        self.claim()
        a, b = self.evidence(), self.evidence()
        self.archive()
        p = self.relocation(a)
        p["payload"]["pins"] += self.relocation(b)["payload"]["pins"]
        first = self.ledger.record(p)["event_id"]
        with self.assertRaisesRegex(LedgerError, "conflicting relocation"):
            self.ledger.record(p)
        self.archive("archive/proof.md", "archive/later.md")
        before = {f.name: f.read_bytes() for f in self.ledger.events.iterdir()}
        replacement = self.relocation(a, destination="archive/later.md", replaces=first)
        second = self.ledger.record(replacement)["event_id"]
        view = self.view()["claims"]["A"]["evidence"]
        self.assertFalse(view[a]["issues"])
        self.assertTrue(view[b]["issues"])
        with self.assertRaisesRegex(LedgerError, "conflicting relocation"):
            self.ledger.record(replacement)
        self.ledger.record(self.relocation(b, destination="archive/later.md", replaces=first))
        self.assertEqual(self.view()["issues"], [])
        for name, data in before.items():
            self.assertEqual((self.ledger.events / name).read_bytes(), data)
        self.assertEqual(self.ledger.read()["relocations"][(a, "artifacts/0")], second)
        self.assertEqual(self.pins("archive/proof.md")["references"], [])
        self.assertEqual(len(self.pins("archive/later.md")["references"]), 2)

    def test_relocation_manifest_closure_preserves_manifest_and_prerequisites(self):
        self.claim(statement_artifact={"path": "proof.md", "locator": "statement"})
        (self.root / "input.txt").write_text("2")
        (self.root / "output.txt").write_text("4")
        input_hash = file_hash(self.root / "input.txt")
        manifest = {"schema_version": 2, "claim_id": "A", "run": {"status": "completed", "exit_status": 0},
                    "input_artifacts": [{"path": "input.txt", "sha256": input_hash, "sha256_after": input_hash}],
                    "outputs": [{"path": "output.txt", "sha256": file_hash(self.root / "output.txt")}]}
        (self.root / "manifest.json").write_text(json.dumps(manifest))
        evidence = self.record("evidence", dict(claim="A", kind="computation", summary="Fixed input",
                               artifacts=[], manifest={"path": "manifest.json"}, assertion="2+2=4",
                               bounds="one integer", non_claims=["No uniform claim"]))
        pinned = self.ledger.read()["evidence"][evidence]
        originals = {path: (self.root / path).read_bytes() for path in
                     ("proof.md", "manifest.json", "input.txt", "output.txt")}
        declarations = []
        for eid, slot, path in (("E000001", "statement_artifact", "proof.md"),
                                (evidence, "manifest", "manifest.json"),
                                (evidence, "manifest_inputs/0", "input.txt"),
                                (evidence, "manifest_outputs/0", "output.txt")):
            self.archive(path, "archive/" + path)
            declarations.append(self.relocation(eid, slot, "archive/" + path))
        self.assertTrue(self.view()["issues"])
        self.ledger.record_many(declarations)
        self.assertEqual(self.view()["issues"], [])
        self.assertEqual(self.view()["claims"]["A"]["status"], "computation-recorded")
        self.assertEqual(self.ledger.read()["evidence"][evidence], pinned)
        for path, data in originals.items():
            self.assertEqual((self.root / "archive" / path).read_bytes(), data)
            self.assertFalse((self.root / path).exists())
        self.review(evidence)
        # Existing relocated claim contracts allow genuinely new explicitly pinned evidence.
        self.record("evidence", dict(claim="A", kind="proof", summary="New argument",
                    artifacts=[{"path": "review.md"}]))
        self.assertEqual(self.view()["claims"]["A"]["status"], "proof-recorded")

    def test_relocation_preserves_reviews_snapshots_dependencies_and_inactivity(self):
        self.claim()
        a = self.evidence()
        self.claim("B", ["A"])
        b = self.evidence("B")
        review = self.review(b, "conditional")
        self.archive()
        self.archive("review.md", "archive/review.md")
        for eid, slot, dest in ((a, "artifacts/0", "archive/proof.md"),
                                (b, "artifacts/0", "archive/proof.md"),
                                (review, "artifact", "archive/review.md")):
            self.ledger.record(self.relocation(eid, slot, dest))
        self.assertEqual(self.view()["claims"]["B"]["status"], "conditional")
        self.assertEqual(self.view()["claims"]["B"]["review"], "conditional-review-recorded")
        self.record("retract", {"target": a, "reason": "Invalid argument"})
        self.assertEqual(self.view()["claims"]["A"]["status"], "conjectural")
        self.assertEqual(self.view()["claims"]["B"]["blocked_by"], ["A"])
        self.assertFalse(self.view()["relocations"][0]["active_pin"])
        self.claim(reason="Different hypothesis")
        self.assertEqual(self.view()["claims"]["B"]["status"], "stale")
        self.assertIn("revision changed", self.view()["claims"]["B"]["evidence"][b]["issues"][0])
        with self.assertRaisesRegex(LedgerError, "stale evidence"):
            self.record("review", dict(evidence=b, outcome="pass", independent=False,
                        summary="Cannot bypass snapshot", artifact={"path": "archive/review.md"}))

    def test_relocation_failed_review_and_superseded_evidence_stay_inactive(self):
        self.claim()
        old = self.evidence()
        current = self.evidence(supersedes=[old])
        review = self.review(current, "fail")
        self.archive()
        self.archive("review.md", "archive/review.md")
        for eid, slot, dest in ((old, "artifacts/0", "archive/proof.md"),
                                (current, "artifacts/0", "archive/proof.md"),
                                (review, "artifact", "archive/review.md")):
            self.ledger.record(self.relocation(eid, slot, dest))
        self.assertNotIn(old, self.view()["claims"]["A"]["evidence"])
        self.assertEqual(self.view()["claims"]["A"]["status"], "incomplete")
        self.assertEqual(self.view()["claims"]["A"]["review"], "failed-review-recorded")
        self.record("retract", {"target": current, "reason": "Failed check"})
        (self.root / "archive/proof.md").unlink()
        self.assertEqual(self.view()["issues"], [])  # Inactive pins do not revive or gate freshness.
        self.assertEqual(self.view()["claims"]["A"]["status"], "conjectural")
        self.assertEqual(research_state.relocation_counts(self.view()["relocations"])["active_references"], 0)

    def test_relocation_deferred_rejected_and_effective_index_guarded(self):
        (self.root / "proof.md").write_text("Pinned entry\n")
        self.claim()
        eid = self.evidence()
        self.archive(destination="research/index.md")
        relocation = self.relocation(eid, destination="research/index.md")
        packet = self.deferred_packet()
        packet.update(artifacts=[], index_append=None, proposals=[relocation])
        for dry_run in (True, False):
            with self.assertRaisesRegex(LedgerError, "local-only"):
                self.ledger.ingest(packet, dry_run=dry_run)
        self.ledger.record(relocation)
        self.allow_deferred()
        packet = self.deferred_packet()
        packet["index_append"]["expected_tail"] = "Pinned entry\n"
        with self.assertRaisesRegex(LedgerError, "would stale current pins"):
            self.ledger.ingest(packet)
        # A staged report can review evidence through an existing registered archive.
        self.allow_deferred(roots=("research",))
        packet = self.deferred_packet()
        packet.update(index_append=None, artifacts=[{"path": "research/report.md", "content": "New report"}],
                      proposals=[{"type": "review", "actor": "reviewer", "payload": {
                          "evidence": eid, "outcome": "pass", "independent": True,
                          "summary": "Report", "artifact": {"path": "research/report.md"}}}])
        self.ledger.ingest(packet, dry_run=True)
        self.assertFalse((self.root / "research/report.md").exists())
        self.ledger.ingest(packet)
        self.assertEqual(self.view()["issues"], [])

    def relocation_fixture(self):
        """Write the files of the repository's synthetic eval fixture, which skills do not ship."""
        repo = Path(__file__).resolve().parents[3]
        if not (repo / "evals/cases.json").is_file():
            self.skipTest("repository eval fixtures are not installed with the skill")
        fixture = json.loads((repo / "evals/fixtures/artifact-relocation.json").read_text())
        for name, content in fixture["files"].items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return fixture

    def test_relocation_migration_fixture_and_completed_run(self):
        fixture = self.relocation_fixture()
        self.ledger.record_many(fixture["proposals"])
        prior = self.ledger.read()
        before = {p.name: p.read_bytes() for p in self.ledger.events.iterdir()}
        proposals = []
        for row in fixture["archives"]:
            refs = self.pins(row["path"])["references"]
            self.archive(row["path"], row["destination"])
            proposals.append({"type": "artifact-relocation", "actor": "archivist", "payload": {
                "pins": [{k: ref[k] for k in ("event", "slot", "path", "sha256")} for ref in refs],
                "destination": {"path": row["destination"]}, "reason": "Synthetic archive migration"}})
        self.assertEqual(self.view()["runs"]["RUN"]["status"], "stale-result")
        self.json_command("check", code=1)
        proposals_path = self.root / "relocations.json"
        proposals_path.write_text(json.dumps(proposals))
        self.json_command("record-batch", str(proposals_path), "--dry-run")
        self.assertEqual(len(self.ledger.read()["events"]), len(prior["events"]))
        self.json_command("record-batch", str(proposals_path))
        check = self.json_command("check")
        self.assertEqual(check["issues"], [])
        self.assertEqual(check["runs"]["RUN"]["status"], "succeeded")
        self.assertEqual(check["runs"]["RUN"]["terminal"]["outcome"], "succeeded")
        self.assertEqual(research_state.relocation_counts(check["relocations"])["verified_references"], 5)
        for name, data in before.items():
            self.assertEqual((self.ledger.events / name).read_bytes(), data)
        state = self.ledger.read()
        for key in ("claims", "evidence", "reviews", "run_results", "route_closures", "reconciliations"):
            self.assertEqual(state[key], prior[key])
        self.assertEqual(self.json_command("next"), [])  # Relocation cannot reopen a closed route.
        for command in (("status",), ("handoff", "--goal", "A"), ("next", "--full", "--goal", "A")):
            result = self.json_command(*command)
            view = result if command[0] == "status" else result["state"]
            self.assertEqual(view["runs"]["RUN"]["status"], "succeeded")
            self.assertEqual(view["relocations"], check["relocations"])
        impact = self.pins("archive/proof.txt")
        self.assertEqual(len(impact["references"]), 3)
        self.assertEqual(impact["runs"], ["RUN"])
        self.assertEqual(impact["direct_claims"], ["A"])
        for row in fixture["archives"]:
            self.assertFalse((self.root / row["path"]).exists())
        with self.assertRaisesRegex(LedgerError, "run already closed"):
            self.record("run-result", dict(prior["run_results"]["E000008"]["payload"], artifacts=[]))
        # The same resolver feeds readiness of a route depending on the recovered claim.
        self.claim("B", ["A"])
        self.record("route", dict(id="WAIT", claim="B", mechanism="use A", question="Apply A?",
                    discriminator="Check", success="Construction", failure="Obstruction",
                    prerequisites=["A"], gain=1, cost=1))
        self.assertTrue(self.json_command("next")[0]["ready"])
        self.assertEqual(self.pins("archive/proof.txt")["dependent_claims"], ["B"])
        (self.root / "archive/proof.txt").write_text("changed")
        self.assertFalse(self.json_command("next")[0]["ready"])


    def test_relocation_batch_prevalidation_aliases_and_structural_replay(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        (self.root / "archive/later.md").write_bytes((self.root / "archive/proof.md").read_bytes())
        first = dict(self.relocation(eid), alias="archive")
        second = self.relocation(eid, destination="archive/later.md", replaces={"$event": "archive"})
        invalid = self.relocation(eid, destination="archive/later.md")
        before = {p.name: p.read_bytes() for p in self.ledger.events.iterdir()}
        with self.assertRaisesRegex(LedgerError, "conflicting relocation"):
            self.ledger.record_many([first, invalid])
        self.assertEqual({p.name: p.read_bytes() for p in self.ledger.events.iterdir()}, before)
        events = self.ledger.record_many([first, second])
        self.assertEqual(events[1]["payload"]["pins"][0]["replaces"], events[0]["event_id"])
        state = self.ledger.read()
        # apply rejects conflicting replay without consulting the filesystem.
        forged = json.loads(json.dumps(events[0]))
        forged["event_id"] = "E999999"
        with patch("research_state.current_hash", side_effect=AssertionError("filesystem read")):
            with self.assertRaisesRegex(LedgerError, "conflicting relocation"):
                research_state.apply(state, forged)
            self.assertEqual(len(self.ledger.read()["events"]), 4)
        bad_slot = self.relocation(eid, destination="archive/later.md", replaces=events[1]["event_id"])
        bad_slot["payload"]["pins"][0]["event"] = events[1]["event_id"]
        bad_slot["payload"]["pins"][0]["slot"] = "destination"
        with self.assertRaisesRegex(LedgerError, "nonexistent relocation pin"):
            self.ledger.record(bad_slot)  # A declaration is not an alias-chain pin source.

    def test_relocation_deferred_artifacts_cannot_land_on_pinned_paths(self):
        (self.root / "proofs").mkdir()
        (self.root / "proofs/a.md").write_text("Original proof\n")
        self.claim()
        eid = self.record("evidence", dict(claim="A", kind="proof", summary="Proof",
                          artifacts=[{"path": "proofs/a.md"}]))
        self.archive("proofs/a.md", "proofs/archive/a.md")
        first = self.ledger.record(self.relocation(eid, destination="proofs/archive/a.md"))["event_id"]
        self.allow_deferred()
        archived = (self.root / "proofs/archive/a.md").read_text()

        def stage(path, content="Changed original\n"):
            packet = self.deferred_packet()
            packet.update(index_append=None, artifacts=[{"path": path, "content": content}],
                          proposals=[{"type": "claim", "actor": "author", "payload": {
                              "id": "U", "statement": "Unrelated", "hypotheses": [], "regime": "Z",
                              "level": "chain", "dependencies": []}}])
            return packet

        # Neither changed nor identical bytes, nor a case alias, may land on a relocated original.
        for path, content in (("proofs/a.md", "Changed original\n"), ("proofs/a.md", archived),
                              ("proofs/A.md", "Case alias\n")):
            with self.subTest(path=path, content=content):
                with self.assertRaisesRegex(LedgerError, "current pins depend on"):
                    self.ledger.ingest(stage(path, content))
                self.assertFalse((self.root / path).exists())
        (self.root / "proofs/archive/a.md").unlink()
        with self.assertRaisesRegex(LedgerError, "current pins depend on"):
            self.ledger.ingest(stage("proofs/archive/a.md", archived))
        (self.root / "proofs/archive/a.md").write_text(archived)
        self.assertEqual(self.view()["issues"], [])
        # A packet cannot silently restore a missing unrelocated pin either.
        (self.root / "proofs/b.md").write_text("Other proof\n")
        other = self.record("evidence", dict(claim="A", kind="proof", summary="Other",
                            artifacts=[{"path": "proofs/b.md"}]))
        (self.root / "proofs/b.md").unlink()
        with self.assertRaisesRegex(LedgerError, other):
            self.ledger.ingest(stage("proofs/b.md", "Other proof\n"))
        self.assertNotIn("U", self.ledger.read()["claims"])
        # A locally released original path is free for new content.
        self.ledger.record(self.relocation(eid, destination="proofs/archive/a.md",
                                           replaces=first, release_original=True))
        self.ledger.ingest(stage("proofs/a.md"))
        self.assertIn("U", self.ledger.read()["claims"])
        self.assertEqual([issue["event"] for issue in self.view()["issues"]], [other])

    def test_relocation_release_lets_original_path_hold_new_content(self):
        self.claim()
        eid = self.evidence()
        self.archive()
        first = self.ledger.record(self.relocation(eid))["event_id"]
        (self.root / "proof.md").write_text("A new version kept at the live path")
        self.assertIn("original conflict", self.view()["issues"][0]["issue"])
        with self.assertRaisesRegex(LedgerError, "original conflict"):
            self.ledger.record(self.relocation(eid, replaces=first))
        for flag in (False, "yes"):
            with self.subTest(release_original=flag), self.assertRaisesRegex(LedgerError, "release_original"):
                self.ledger.record(self.relocation(eid, replaces=first, release_original=flag))
        self.ledger.record(self.relocation(eid, replaces=first, release_original=True))
        view = self.view()
        self.assertEqual(view["issues"], [])
        self.assertEqual(view["claims"]["A"]["status"], "proof-recorded")
        info = view["relocations"][0]
        self.assertEqual((info["original_status"], info["verification"]), ("released", "verified"))
        self.assertTrue(info["relocation"]["original_released"])
        # The released path no longer pins anything; the archive still gates freshness.
        self.assertEqual(self.pins("proof.md")["references"], [])
        self.assertEqual(len(self.pins("archive/proof.md")["references"]), 1)
        (self.root / "archive/proof.md").write_text("damaged")
        self.assertEqual(self.view()["claims"]["A"]["status"], "stale")

    def test_relocation_release_recovers_completed_run_without_new_result(self):
        fixture = self.relocation_fixture()
        self.ledger.record_many(fixture["proposals"])
        events = {p.name: p.read_bytes() for p in self.ledger.events.iterdir()}
        pins = [{k: ref[k] for k in ("event", "slot", "path", "sha256")}
                for ref in self.pins("old/proof.txt")["references"]]
        # Archive the old version, then revise the live path in place.
        (self.root / "archive").mkdir()
        (self.root / "archive/proof.txt").write_bytes((self.root / "old/proof.txt").read_bytes())
        (self.root / "old/proof.txt").write_text("Next version kept at the live path\n")
        self.assertEqual(self.view()["runs"]["RUN"]["status"], "stale-result")
        proposal = {"type": "artifact-relocation", "actor": "archivist", "payload": {
            "pins": pins, "destination": {"path": "archive/proof.txt"},
            "reason": "Archived the old version before revising the live file"}}
        with self.assertRaisesRegex(LedgerError, "original conflict"):
            self.ledger.record(proposal)
        for pin in pins:
            pin["release_original"] = True
        self.ledger.record(proposal)
        check = self.json_command("check")
        self.assertEqual(check["issues"], [])
        self.assertEqual(check["runs"]["RUN"]["status"], "succeeded")
        self.assertEqual(len(self.ledger.read()["run_results"]), 1)
        for name, data in events.items():
            self.assertEqual((self.ledger.events / name).read_bytes(), data)

    def test_relocation_return_to_original_path_ends_it(self):
        self.claim()
        eid = self.evidence()
        with self.assertRaisesRegex(LedgerError, "self-relocation"):
            self.ledger.record(self.relocation(eid, destination="proof.md"))
        self.archive()
        first = self.ledger.record(self.relocation(eid))["event_id"]
        self.archive("archive/proof.md", "proof.md")
        self.assertIn("relocation destination", self.view()["issues"][0]["issue"])
        with self.assertRaisesRegex(LedgerError, "conflicting relocation"):
            self.ledger.record(self.relocation(eid, destination="proof.md"))
        with self.assertRaisesRegex(LedgerError, "cannot release"):
            self.ledger.record(self.relocation(eid, destination="proof.md", replaces=first,
                                              release_original=True))
        self.ledger.record(self.relocation(eid, destination="./proof.md", replaces=first))
        self.assertNotIn((eid, "artifacts/0"), self.ledger.read()["relocations"])
        view = self.view()
        self.assertEqual((view["issues"], view["relocations"]), ([], []))
        self.assertIsNone(self.pins("proof.md")["references"][0]["relocation"])
        # Ordinary pin semantics again: a later move stales it and starts a fresh declaration.
        self.archive()
        self.assertIn("missing or changed artifact", self.view()["issues"][0]["issue"])
        self.ledger.record(self.relocation(eid))
        self.assertEqual(self.view()["issues"], [])

    def test_relocation_original_below_replaced_directory_is_missing(self):
        (self.root / "proofs").mkdir()
        (self.root / "proofs/a.md").write_text("Original proof\n")
        self.claim()
        eid = self.record("evidence", dict(claim="A", kind="proof", summary="Proof",
                          artifacts=[{"path": "proofs/a.md"}]))
        self.archive("proofs/a.md")
        (self.root / "proofs").rmdir()
        (self.root / "proofs").write_text("A file where the directory was")
        self.ledger.record(self.relocation(eid))
        info = self.view()["relocations"][0]
        self.assertEqual((info["original_status"], info["verification"]), ("missing", "verified"))

    def test_relocation_rejects_case_unicode_link_and_ledger_aliases(self):
        (self.root / "café.md").write_text("Accented proof")
        self.claim()
        eid = self.evidence()
        accented = self.record("evidence", dict(claim="A", kind="proof", summary="Accented",
                               artifacts=[{"path": "café.md"}]))
        for event, original, alias in ((eid, "proof.md", "Proof.md"), (eid, "proof.md", "PROOF.MD"),
                                       (accented, "café.md", "café.md")):
            target = self.root / alias
            # On a case- or normalization-insensitive volume the alias already is the original.
            created = not target.exists()
            if created:
                target.write_bytes((self.root / original).read_bytes())
            with self.subTest(alias=alias), self.assertRaisesRegex(LedgerError, "only by case or Unicode"):
                self.ledger.record(self.relocation(event, destination=alias))
            if created:
                target.unlink()
        (self.root / "archive").mkdir()
        os.link(self.root / "proof.md", self.root / "archive/proof.md")
        with self.assertRaisesRegex(LedgerError, "same file"):
            self.ledger.record(self.relocation(eid))
        for path in (".MATHBOX/config.json", ".mathbox./config.json", ".Mathbox /x.md"):
            with self.subTest(path=path):
                with self.assertRaisesRegex(LedgerError, "outside the ledger"):
                    self.ledger.record(self.relocation(eid, destination=path))
                with self.assertRaisesRegex(LedgerError, "outside the ledger"):
                    self.record("evidence", dict(claim="A", kind="proof", summary="Ledger file",
                                artifacts=[{"path": path}]))
        self.assertEqual(len(self.ledger.read()["events"]), 3)

    def test_relocation_goal_view_keeps_inactive_records_alike(self):
        old_claim = self.claim(statement_artifact={"path": "proof.md", "locator": "old"})
        self.claim(reason="Revised", statement_artifact={"path": "review.md", "locator": "new"})
        old = self.evidence()
        review = self.review(old)
        current = self.evidence(supersedes=[old])
        self.record("retract", {"target": review, "reason": "Report withdrawn"})
        self.claim("B")
        self.record("evidence", dict(claim="B", kind="proof", summary="B", artifacts=[{"path": "review.md"}]))
        self.archive()
        (self.root / "archive/review.md").write_bytes((self.root / "review.md").read_bytes())
        for event, slot, destination in ((old_claim, "statement_artifact", "archive/proof.md"),
                                         (old, "artifacts/0", "archive/proof.md"),
                                         (current, "artifacts/0", "archive/proof.md"),
                                         (review, "artifact", "archive/review.md")):
            self.ledger.record(self.relocation(event, slot, destination))
        relocations = self.json_command("handoff", "--goal", "A")["state"]["relocations"]
        self.assertEqual({(r["event"], r["slot"]) for r in relocations},
                         {(old_claim, "statement_artifact"), (old, "artifacts/0"),
                          (current, "artifacts/0"), (review, "artifact")})
        inactive = [r for r in relocations if not r["active_pin"]]
        self.assertEqual(len(inactive), 3)
        self.assertEqual({r["verification"] for r in inactive}, {"not-checked"})
        self.assertEqual(self.json_command("handoff", "--goal", "B")["state"]["relocations"], [])

    def test_relocation_hashes_each_location_once(self):
        self.claim(statement_artifact={"path": "review.md", "locator": "statement"})
        old = self.evidence()
        current = self.evidence(supersedes=[old])
        extra = self.evidence()
        self.archive()
        hashed = Counter()

        def counting_hash(path):
            hashed[Path(path)] += 1
            return file_hash(path)

        proposal = self.relocation(old)
        for event in (current, extra):
            proposal["payload"]["pins"] += self.relocation(event)["payload"]["pins"]
        with patch("research_state.file_hash", side_effect=counting_hash):
            self.ledger.record(proposal)
        self.assertEqual(hashed[self.ledger.root / "archive/proof.md"], 1)
        resolved = Counter()
        real = research_state.resolve_pin

        def counting_resolve(root, state, pin, overlays=None):
            resolved[(pin["event"], pin["slot"])] += 1
            return real(root, state, pin, overlays)

        with patch("research_state.resolve_pin", side_effect=counting_resolve):
            view = self.view()
        self.assertEqual(view["issues"], [])
        # The statement contract recurs per evidence and relocations reuse issue checks.
        self.assertEqual(resolved, Counter({("E000001", "statement_artifact"): 1,
                                            (current, "artifacts/0"): 1, (extra, "artifacts/0"): 1}))

    def test_relocation_scope_and_historical_claim_remain_inactive(self):
        old = self.claim(statement_artifact={"path": "proof.md", "locator": "old"})
        self.claim(reason="New contract", statement_artifact={"path": "review.md", "locator": "new"})
        self.archive()
        self.ledger.record(self.relocation(old, "statement_artifact"))
        self.claim("B")
        other = self.record(
            "evidence", dict(claim="B", kind="proof", summary="B",
                             artifacts=[{"path": "review.md"}]))
        self.archive("review.md", "archive/review.md")
        self.ledger.record(self.relocation(other, destination="archive/review.md"))
        # Registering B's pin does not silently cover A's latest statement in the same file.
        checked = self.json_command("check", code=1)
        self.assertFalse(checked["relocations"][0]["active_pin"])
        self.assertEqual(checked["claims"]["A"]["revision"], 2)
        handoff = self.json_command("handoff", "--goal", "B")["state"]
        self.assertEqual(len(handoff["relocations"]), 1)
        self.assertEqual(handoff["relocations"][0]["event"], other)
        self.assertFalse(handoff["issues"])
        self.assertEqual(self.pins("archive/proof.md")["references"], [])


if __name__ == "__main__":
    unittest.main()
