"""Executable evidence-boundary regressions; no model-output keyword grading."""
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research_state import (Ledger, LedgerError, brief_markdown, file_hash, impact, main, next_routes,
                            pin_impact, project, restrict)


class ResearchStateTests(unittest.TestCase):
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
        self.route("R2", reopens=result, changed_input="New filtration changes the obstruction group")
        state = self.ledger.read()
        self.assertEqual([r["id"] for r in next_routes(state, self.view(), "A")], ["R2"])

    def test_route_success_never_promotes_claim(self):
        self.claim()
        self.route()
        self.record("route-result", dict(route="R", outcome="succeeded", reason="Calculated a useful example",
                                         next_question="Can it be made uniform?"))
        self.assertEqual(self.view()["claims"]["A"]["status"], "conjectural")

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


if __name__ == "__main__":
    unittest.main()
