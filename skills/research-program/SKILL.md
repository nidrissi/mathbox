---
name: research-program
description: >-
  Pursue a substantial mathematical research goal across multiple proof, counterexample, literature, and computational routes. Use when the user asks for sustained investigation, several approaches, a breakthrough, or continuation until a goal is reached. Coordinate successive research attempts and preserve their evidence. Do not use for a single bounded lemma attempt, ordinary explanation, proofreading, or a read-only project retrospective.
---

# Sustained mathematical research

Own the user's mathematical objective across route changes. A route ending is
not the assignment ending. Produce mathematics, not a portfolio of unexecuted
suggestions. Do not promise a solution to an open problem or relabel an exhausted
attempt as one.

## Establish the target once

Read project instructions, exact target, current evidence and nearest relevant
failed routes. Separate the requested theorem from weaker useful results. Fix
quantifiers, equivalence notion, coefficient regime, ranges, naturality and
conventions in a target contract. If the supplied conjecture has several
plausible meanings, work on common implications while resolving the material
ambiguity from sources or the user.

Record what would count as a proof or a counterexample and what would only be
partial progress. Retain this contract after compaction and user status queries.
“By any means” expands mathematical methods, not tool permissions or access.
For work that may cross sessions, branches or delegated agents, record a
checkpoint identifier and the exact Git revision or ledger event from which the
work starts. A timestamp or display order is not a reliable ancestry relation.

Use existing project records. When an executable `.mathbox/` ledger is present,
use the available `research-state` skill for a goal-scoped handoff and stale
evidence check. Initialize it only when useful and authorized; its absence never
blocks research. Read [program protocol](references/program-protocol.md) for
route selection and checkpoints.

## Build and execute a diverse portfolio

For a broad unresolved goal, initially identify three plausible routes unless
the user specifies another number or the problem makes fewer meaningful.
Different vocabulary for the same missing lemma is one route. Prefer routes
with different failure mechanisms; include a serious attempt to falsify the
target when a counterexample would settle it.

For each route, state the central mathematical move, its first uncertain
implication, the cheapest discriminating check, and success/failure criteria.
Treat alternative mechanisms as a portfolio and jointly required lemmas as
claim dependencies. When a route is recorded under a parent goal but directly
advances a named sub-obligation, identify that obligation explicitly rather than
retargeting the route or duplicating the mechanism.
Run the decisive check, then pursue the promising route to a substantive
checkpoint using `research-attempt` if available. Its one-route boundary applies
to each work package, not to this whole program. Follow the user's breadth
requirement: if they ask to try every proposed route, execute each one.

When routes run in parallel, give each one an owner, base checkpoint and
disjoint write scope. Require returned artifacts to identify that base and their
actual inputs. Reconcile them against the common base; do not infer chronology
or supersession from response order, directory names or wall-clock completion.
Preserve incompatible results as competing evidence until their mathematics is
resolved.

Allocate effort by expected information gain, relevance to the goal and cost.
Do not fabricate numerical success probabilities. Attack high-impact uncertain
dependencies before polishing their downstream consequences. Formulate auxiliary
lemmas that remove shared bottlenecks. Transfer techniques across fields only
after writing the actual source-to-target dictionary.

Use `literature-check` for source-dependent implications and `computation-audit`
for load-bearing experiments. If a specialist skill is unavailable, carry out
the relevant exact-source or finite-evidence check directly with available
tools and disclose its limits; an absent workflow package is not a mathematical
obstruction.

## Change direction on evidence

After a route checkpoint, ask what mathematical information changed. Preserve
the strongest surviving statement and distinguish a false lemma, a failed
method, an implementation bug, and an inaccessible source.

- On success, extract a structural mechanism and attack the remaining gap to
  the actual goal. Do not silently replace that goal with the weaker result.
- On failure, save a reusable obstruction and revise the portfolio. A failed
  proof route does not refute the target.
- On no progress, identify a materially different input, construction,
  invariant or source. Reopening an old route requires that explicit change.
- Another finite case is useful only if it distinguishes alternatives, checks
  an independent invariant, or reaches a new regime.

Continue successive cycles while there is an executable, plausible route within
the authorized resources. Do not stop just because the initial three failed.
Likewise, a substantial partial theorem is a checkpoint, not completion, when
the target contract still contains unresolved named implications.
Use checkpoints to preserve work while continuing. When the user specifies
time/resource bounds, honor them; otherwise choose bounded individual
experiments without imposing an arbitrary global attempt quota.

## Audit candidate breakthroughs

Before treating the goal as achieved, reconstruct the complete argument from
the current definitions and pinned evidence. Check every external leaf, range,
limiting argument and comparison map. Run `proof-audit` if available.

When fresh-agent review is available and delegation is authorized, give the
reviewer the exact claim, raw proof and required sources without the author's
verdict or route narrative. Request an independent derivation of the critical
step. Otherwise perform a separate adversarial pass and label it self-review.
Agreement between agents is not a proof certificate. Resolve disagreements by
the underlying mathematics. Use [the handoff contract](references/handoff.md)
when delegating or resuming.

## Persist and report

Keep proofs in durable mathematical files, finite runs in computation records,
failed mechanisms in linked route records, and current status in one live view.
Update only state that actually changed; do not rewrite indexed history.
User-authorized repository deliverables remain part of completion.

For a long or externally executed route, distinguish queued, running,
last-observed, completed, failed, timed out and abandoned states. Do not keep a
route marked running merely because a prior session launched it. Record the
last observation and execution identifier without treating process completion
as mathematical success.

Lead with whether the original goal was reached and the exact result. State the
proof/review status, decisive mechanism, files and meaningful checks. If it
remains open, distinguish partial results from the goal, list executed routes
with their precise obstructions, and preserve an executable next handoff.
When all presently available routes are exhausted or tools/resources block
continuation, say so honestly; never invent progress to satisfy “do not stop”.
