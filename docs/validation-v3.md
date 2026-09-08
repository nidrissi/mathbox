# Validation of the v3 redesign

This report distinguishes software regression results from actual model task
trials. It makes no comparative claim about solving frontier research problems.

## Executable checks

`python3 scripts/check.py` covers package identity/version/inventory, JSON,
portable resource links, Python syntax and three standard-library test suites:

| Suite | Cases | Important exercised behavior |
|---|---:|---|
| Research state | 27 | Transitive revision invalidation, retraction, negative/conditional audits, conflicting evidence, supersession, journal integrity, path boundaries, writer contention, unresolved dependencies under finite evidence, duplicate open mechanisms, and goal-scoped route and staleness filtering |
| Computation provenance | 21 | Actual execution, failed assertions, timeout, process descendants, process-group signalling bounds, bounded logs, input mutation, stale and missing hashes, software version records, shell metacharacters, launch failure, no overwrite, empty-template rejection and v1 compatibility |
| Existing literature cache | 17 | Existing cache ingestion, source retention, lookup and error-path regressions |

All 65 tests passed locally. The cache suite deliberately exercises an internal
error path and prints its injected error message; the test asserts the handled
failure and the suite passes. No mathematical theorem is inferred from this gate.

The Codex plugin validator and all ten skill validators pass. The repository
inspector smoke test and `git diff --check` pass. Claude's plugin and strict
marketplace validators pass, the latter with the expected warning that the
repository `CLAUDE.md` is not loaded as plugin context. Actual host installation
was not performed as part of source development. The GitHub workflow is
configured to run the same gate on Python 3.10 and 3.13. Remote CI was not run
during this validation: the available connection rejected publication with
HTTP 403, so no pull request was created.

## Fresh task trials

Three fresh agents received only task-local instructions and raw inputs. They
did not inherit the redesign diagnosis or expected answers. All writes were
restricted to isolated temporary projects; the audit tasks were read-only.
These ran against the working v3 draft, before the final usability clarification
and additional deterministic regression fixes.

| Trial | Observed result | Scope |
|---|---|---|
| Sustained research program | Executed three distinct proofs of the prime/binomial-divisibility characterization; completed the original quantifiers; explicitly separated self-review from independent audit | Elementary theorem; not a frontier research benchmark |
| Claim-state revision | Recorded two supported integer claims; widening the base claim to rationals made both proof snapshots stale; an exact rational witness refuted the widened claim; produced a valid dependent recovery route | Seven journal events, actual CLI commands and unchanged historical proofs |
| Mathematical proof audits | Refuted the rational-to-mod-p rank claim at p=2 with both cohomology groups computed; refuted the equivariant comparison by the intertwining equation | Two supplied raw arguments; no source lookup or write effects |

The program proof was inspected after the trial. Its three mechanisms are prime
valuation, polynomial reduction and a lift modulo p², and cyclic subset orbits.
The finite checks through n=128 support examples and implementation only; they
are not the universal proof. The proof trial called its own audit self-review.

The state trial exposed a real instruction problem: the initial “check before
changing state” instruction caused unnecessary errors when the project and goal
did not yet exist. The skill now gives an explicit bootstrap path before asking
for an existing ledger handoff. The schema proposals themselves all succeeded
on their first submission.

Reviewable trial evidence is retained under [evals/results/v3](../evals/results/v3/):
the complete mathematical derivation, finite-result summary, state execution
notes and exact journal events. The notes refer to the trial's original isolated
project paths; those are historical observations, not required install paths.

## Limits of the evaluation

The new bounded-tower fixture is supplied for future independent runs and was
not executed in these task trials. The complete collection of natural-language
trigger and behavioral probes was structurally validated, not batch-scored by
an LLM judge. No performance comparison with v2, formal-verifier integration,
Windows process-tree test or actual open-problem success is claimed.

The journal trusts declared mathematical dependencies and evidence kinds. Hashes
cannot authenticate the correctness of a proof or a reviewer's independence.
The experiment runner pins explicitly supplied inputs and captures execution;
its declared mathematical bounds and external software dependencies still need
review. These are deliberate boundaries, documented in the skills and command
contracts.
