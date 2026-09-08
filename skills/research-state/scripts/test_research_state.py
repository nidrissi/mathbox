"""Executable evidence-boundary regressions; no model-output keyword grading."""
import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from research_state import Ledger, LedgerError, impact, main, next_routes, project


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
        self.assertEqual(self.view()["claims"]["A"]["status"], "computationally-verified")
        self.assertEqual(self.view()["claims"]["B"]["status"], "conditional")

    def test_dependency_retraction_propagates_without_rewriting_history(self):
        self.claim()
        basis = self.evidence()
        self.claim("B", ["A"])
        self.evidence("B")
        self.assertEqual(self.view()["claims"]["B"]["status"], "proved")
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
        self.assertEqual(self.view()["claims"]["C"]["review"], "independently-audited")
        self.claim(reason="Strengthen coefficient regime")
        claims = self.view()["claims"]
        self.assertEqual([claims[k]["status"] for k in "ABC"], ["stale"] * 3)
        self.assertEqual(claims["C"]["review"], "not-independently-audited")
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
        self.assertEqual(self.view()["claims"]["A"]["status"], "proved")
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
        self.assertEqual(self.view()["claims"]["B"]["status"], "proved")

    def test_conditional_review_does_not_certify(self):
        self.claim()
        e = self.evidence()
        self.review(e, "conditional")
        self.assertEqual(self.view()["claims"]["A"]["status"], "conditional")

    def test_review_independence_is_not_proof_strength(self):
        self.claim()
        e = self.evidence()
        with self.assertRaises(LedgerError):
            self.review(e, actor="author")
        self.review(e, actor="author", independent=False)
        self.assertEqual(self.view()["claims"]["A"]["review"], "not-independently-audited")
        self.review(e)
        c = self.view()["claims"]["A"]
        self.assertEqual(c["status"], "proved")
        self.assertEqual(c["review"], "independently-audited")

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
        self.assertEqual(self.view()["claims"]["A"]["status"], "refuted")

    def test_unqualified_counterexample_still_refutes(self):
        self.claim()
        e = self.evidence(kind="counterexample", hypothesis_check="Witness under review")
        self.review(e, "conditional")
        self.evidence(kind="counterexample", hypothesis_check="Separate witness satisfies every hypothesis")
        self.assertEqual(self.view()["claims"]["A"]["status"], "refuted")

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
        self.assertEqual(self.view()["claims"]["A"]["status"], "externally-proved")

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
                         event_id=route_event, result=dict(result, event_id=result_event))])
        md = run("handoff", "--goal", "B")
        for value in ("integral-lift", "failed", result["reason"], result["next_question"], result_event):
            self.assertIn(value, md)
        self.assertNotIn("Unrelated obstruction", md)
        self.assertEqual([r["id"] for r in json.loads(run("--json", "handoff"))["closed_routes"]], ["R", "OTHER"])
        self.assertEqual([r["id"] for r in json.loads(run("next", "--goal", "B"))], ["R2"])
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.ledger.events.iterdir()})


if __name__ == "__main__":
    unittest.main()
