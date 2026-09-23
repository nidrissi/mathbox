# Evaluating Mathbox

There are three different validation surfaces:

1. `python3 scripts/check.py`: deterministic packaging, syntax and executable
   state/experiment/cache regressions. These verify software contracts, not
   mathematical performance.
2. `skills/*/evals/trigger-evals.json`: routing probes. A correct task answer does
   not establish that the right skill was selected.
3. `skills/*/evals/evals.json` and the raw fixtures below: behavioral mathematical
   tasks. Evaluate actual derivations, commands, persisted artifacts and scope.
   Do not score these by searching for reassuring phrases.

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

These cases test specific failure mechanisms using synthetic, publishable
artifacts. They contain no project-derived names, paths, statements, outputs or
provenance. They are not a validated measure of frontier research success. Keep
confidential held-out project tasks outside this repository and report only
aggregate outcomes before making comparative performance claims. See
`docs/validation-v3.md` for the actual forward-testing scope of this redesign.
