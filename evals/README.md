# Evaluating Mathbox

There are three different validation surfaces:

1. `python3 scripts/check.py`: deterministic packaging, syntax and executable
   state/experiment/cache/manuscript-preparation regressions. These verify
   software contracts, not mathematical performance.
2. `skills/*/evals/trigger-evals.json`: routing probes. A correct task answer does
   not establish that the right skill was selected.
3. `skills/*/evals/evals.json` and the raw fixtures below: behavioral mathematical
   tasks. Evaluate actual derivations, commands, persisted artifacts and scope.
   Do not score these by searching for reassuring phrases.

## Routing protocol

Assume the complete suite is installed; record the host and invocation policy.
First collect query text without expected labels. Record the direct entry point
before evaluating correctness: following a specialist internally does not mean
it should have been the original entry point. Compare risky pairs in both directions.

Run two separate probes: task applicability from descriptions/body boundaries,
and actual host selection. For explicit-only skills, a positive applies when the
skill is explicitly named or supplied as the evaluation's entry point. On Codex,
an unadorned positive task may match that skill but produce no automatic load;
score this as policy-consistent rather than a false negative. Claude's wording
boundary may allow an explicit task request, but actual loaded skill identity
must still be recorded. Do not infer selection from reassuring report language.
A routing replay by an agent with a supplied catalog is a simulated applicability
trial, not evidence of automatic selection in another live host.

## Independent task protocol

Start a fresh agent/session with the named skill, the task and raw fixture only.
Keep expected answers, rubric and the author's diagnosis out of its context.
Use an isolated temporary project; do not let generated artifacts from one case
contaminate another. Run only authorized local operations. Give unavailable
source/software conditions honestly, not as invented test outcomes.

After execution, a separate reviewer checks the mathematical derivation and
observable effects against `cases.json`. Record skill revision, task, tool
availability, actual artifacts, reviewer and verdict. A self-review is not an
independent audit. Missing tools are a capability limitation, not a mathematical
failure. Success means satisfying the task contract, not following a fixed number
of tool calls or reproducing a preferred proof.

## Raw fixtures

| File | User task |
|---|---|
| `fixtures/modular-rank.md` | Audit the implication and determine the strongest justified conclusion. |
| `fixtures/equivariant-map.md` | Audit the equivariant comparison under the exact assumptions. |
| `fixtures/bounded-tower.md` | Pursue a decisive proof or counterexample route for the full target. |
| `fixtures/prime-binomial.md` | Execute three distinct approaches and settle the quantified claim. |
| `fixtures/sampled-enumeration.md` | Audit a finite sweep whose iterator skips most inputs. |
| `fixtures/surrogate-domain.md` | Detect a computation performed on a regularized substitute for the claimed object. |
| `fixtures/absolute-grading.md` | Detect an absolute degree error hidden by parity-only tests. |
| `fixtures/novelty-vocabulary.md` | Recheck novelty using historical terminology and citation chains. |
| `fixtures/parallel-reconciliation.md` | Reconcile conflicting parallel returns from a common checkpoint. |
| `fixtures/inconclusive-continuation.md` | Resume a recurrence program after one inconclusive attempt with another continuation untried. |
| `fixtures/referee-core.tex` | Referee a whole manuscript across correctness, edge cases, notation, exposition and claim calibration. |
| `fixtures/referee-context.tex` | Reconcile a local undefined-notation suspicion against an earlier definition. |
| `fixtures/referee-exposition.tex` | Assess a correct telescoping proof with little strategic signposting. |
| `fixtures/referee-source.tex` | Review a coefficient extension with an unavailable synthetic source. |
| `fixtures/referee-enumeration.tex` | Review a theorem supported by a filtered binary enumeration. |

For `referee-context`, a reconciliation trial may supply the user-visible prior
local finding "tau is undefined in the Identity section" together with the raw
manuscript. Keep the grader's disposition and diagnosis out of solver context.
Record a raw suspicion separately from the final conclusion. Routing trials
must likewise record the selected entry point, not infer it from report wording.

Model-assignment trials reuse `referee-context.tex` with user/project preferences
and the host's actual available controls. Inspect native launch arguments and
returns as well as coverage, reconciliation and the report; a requested model
is not a confirmed execution identity. Cases 11–14 in the referee skill cover
native selection, partial fallbacks, inherited settings and historical reuse.
Keep expected outcomes out of the fresh solver context. If a trial simulates
a host limitation, label it explicitly; it is not evidence that a different
harness was actually exercised.

These cases test specific failure mechanisms using synthetic, publishable
artifacts. They contain no project-derived names, paths, statements, outputs or
provenance. They are not a validated measure of frontier research success. Keep
confidential held-out project tasks outside this repository and report only
aggregate outcomes before making comparative performance claims. See
[`suite review validation`](results/suite-review-2026-10-02/README.md) for the
current implementation's bounded trials and remaining acceptance coverage,
[`docs/validation-v3.md`](../docs/validation-v3.md) for the actual forward-testing
scope of the v3 redesign and
[`docs/referee-validation.md`](../docs/referee-validation.md) for the referee
integration, raw trial records and API-free Math Scout comparison.
