# Validation of the v3 redesign

> **Scope:** This report records validation of releases 3.0.0 and 3.0.1. Its
> suite counts and validator output are those of 3.0.1 (2026-09-16), and it is
> not updated for later releases. Since then the regression suites have grown,
> and the root `CLAUDE.md` mentioned below was removed in 3.1.0. See the
> [changelog](CHANGELOG.md) for later changes, and run `python3 scripts/check.py`
> for current results.

This report distinguishes software regression results from actual model task
trials. It makes no comparative claim about solving frontier research problems.

## Executable checks

`python3 scripts/check.py` covers package identity/version/inventory, the
synthetic behavioral-fixture inventory, JSON, portable resource links, Python
syntax and four standard-library test suites:

| Suite | Cases | Important exercised behavior |
|---|---:|---|
| Research state | 41 | Neutral evidence projections, conditional computation reviews, visible review conflicts, obligation-aware routes, typed route context, compact checks, bound statement staleness, strict computation-manifest closure, transitive revision invalidation, program/run lifecycle, explicit unknown observations, common-base reconciliation, delayed results, journal integrity and path/writer boundaries |
| Computation provenance | 30 | Actual execution, declared scientific-result hashes, input/result collision controls, timeout and process descendants, bounded logs, optional POSIX resource caps, input mutation, stale hashes, shell metacharacters, atomic manifests, strict v2 validation and historical v1 compatibility/ambiguity handling |
| Repository inspector | 7 | Semantic filename aliases, computation-manifest inventory, mixed-log classification, declared path/cache conventions, conservative broken references, Git-state distinctions, missing compatibility bridges and refusal to inspect symlinked files |
| Existing literature cache | 17 | Existing cache ingestion, source retention, lookup and error-path regressions |

All 95 tests passed locally. The cache suite deliberately exercises an internal
error path and prints its injected error message; the test asserts the handled
failure and the suite passes. No mathematical theorem is inferred from this gate.

The Codex plugin validator and all ten skill validators pass. The repository
inspector smoke test and `git diff --check` pass. Claude's plugin and strict
marketplace validators pass; the plugin validator emits the expected warning
that the repository `CLAUDE.md` is not loaded as plugin context. Actual host
installation was not performed as part of source development. The GitHub workflow is
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
They also retain the status strings emitted by the helper at that time; the
current projection renders the same evidence categories with neutral
`*-recorded` labels.

## Targeted synthetic regression trials

Three additional fresh agents received only the named skill and one raw
synthetic fixture. They did not receive `evals/cases.json`, the expected answer,
or the redesign diagnosis. A separate review compared each returned derivation
with the checked-in obligations and critical-failure condition.

| Fixture | Independently observed result | Review |
|---|---|---|
| Surrogate domain | Computed the singular midpoint of the stated polynomial curve, rejected it as a path in the open cone, and distinguished the eigenvalue-clipped curve as a different object | Pass |
| Sampled enumeration | Counted the 16 actually visited inputs out of 64, restricted the conclusion to that subset, and required full enumeration or a proved coverage reduction | Pass |
| Parallel reconciliation | Used the common checkpoint rather than display order, preserved both raw returns, exposed their shared-path collision, and deferred shared-state mutation until mathematical reconciliation | Pass |

All three avoided their critical failure. These trials establish behavior on
those small fixtures only. The fixture correction and rerun are part of the
record: the first surrogate-domain draft accidentally described an impossible
singular affine segment between positive-definite endpoints; it was replaced by
an explicit non-affine polynomial curve before the passing result above. Only
synthetic public inputs were used for these trials.

## Limits of the evaluation

The bounded-tower, absolute-grading and novelty-vocabulary fixtures remain for
future independent runs. The complete collection of natural-language trigger
and behavioral probes was structurally validated, not batch-scored by an LLM
judge. No performance comparison with v2, formal-verifier integration, Windows
process-tree test or actual open-problem success is claimed.

The journal trusts declared mathematical dependencies and evidence kinds. Hashes
cannot authenticate the correctness of a proof or a reviewer's independence.
The experiment runner pins explicitly supplied inputs and declared result files,
and records requested resource caps. Address-space and CPU caps are per process,
thread caps remain cooperative, and declared mathematical bounds plus external
software dependencies still need review. Historical v1 validation reports its
missing provenance rather than inventing it. These are deliberate boundaries,
documented in the skills and command contracts.
