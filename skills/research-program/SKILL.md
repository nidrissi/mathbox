---
name: research-program
description: >-
  Pursue or close out a substantial mathematical research program across multiple proof, counterexample, literature, and computational routes. Use when the user asks for sustained investigation, several approaches, continuation until a goal is reached, or an authorized closeout of one named program or phase that compacts its live status and history. Coordinate successive attempts and preserve their evidence. Do not use for a single bounded lemma attempt, ordinary explanation, proofreading, a read-only project retrospective, or a repository-wide migration of instructions or a flat research log into program indexes.
---

# Sustained mathematical research

Own the user's mathematical objective across route changes. A route ending is
not the assignment ending. Produce mathematics, not a portfolio of unexecuted
suggestions. Do not promise a solution to an open problem or relabel an exhausted
attempt as one.
For a closeout-only request, reconcile recorded results and compact the handoff;
do not start new mathematical routes unless the user also requested research.
A closeout covers one named program or phase. Restructuring the repository's
history across programs, such as turning a flat research log into program
indexes, is a `research-init` migration; its closeouts follow this skill's
closeout contract.

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

Use existing project records, starting with the current summary and nearest
relevant records rather than the complete status/history archive. When an
executable `.mathbox/` ledger is present, use the available `research-state`
skill's brief goal handoff and freshness check; open full claim/review details
only for the active decision. Before starting a run, inspect live, stale, and
unreconciled runs of the same route. Recheck stale results that bear on the
decision and reconcile completed results before relying on them. Compare a
proposed run's work scope with live runs to avoid duplicate work. Distinct
parallel runs may proceed from an explicit base with disjoint write scopes
without closing existing live runs.
Initialize it only when useful and authorized; its absence never blocks
research. Read [program protocol](references/program-protocol.md) for
route selection and checkpoints when executing routes; for a closeout-only
request, go to [program closeout](references/program-closeout.md).

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

When routes or runs execute in parallel, give each one an owner, base
checkpoint and disjoint write scope. Require returned artifacts to identify
that base and their actual inputs. Reconcile them against the common base; do
not infer chronology or supersession from response order, directory names or
wall-clock completion.
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
- On no progress, record the first unresolved implication and distinguish the
  attempt's limits from evidence against the mechanism. Try an untested
  continuation or identify a different input, construction, invariant or source.
  Repeating a mechanism with an established obstruction requires a change that
  addresses that obstruction. Resuming unfinished work needs no new premise,
  but it must change something at the recorded stuck step: a narrower sub-step,
  another method or tool, or more resources. Do not rerun a stalled step
  unchanged; when resumptions keep stalling there, record that step as the
  route's bottleneck and reprioritize the portfolio.
- Another finite case is useful only if it distinguishes alternatives, checks
  an independent invariant, or reaches a new regime.

An inconclusive attempt does not by itself close its route. Before closing an
unresolved route, account for the proposed continuations: what was tried, what
remains untried, what evidence rules one out, and what is deferred with a reason
and resumption condition. An obstruction to one construction closes only that
construction unless it applies to the whole mechanism. Keep a route open while a plausible
continuation remains; execute it within the authorized resources or preserve it
in the handoff. A continuation that awaits time, tools, access or priority is
deferred, not exhausted; keep its route open. Reserve terminal `inconclusive`
for a scoped route whose known continuations have all been tried or ruled out
by evidence, with no further plausible continuation identified; state the scope
and reason without claiming impossibility.

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
When persistence is authorized but this host cannot execute or write, use the
`research-state` deferred-handoff contract for new durable artifacts, one
guarded index entry, and ledger proposals; state that ingest remains pending.
Update only state that actually changed; replace old dashboard checkpoint prose
with links only once it has a durable home and the project permits, and do not
rewrite indexed history.
User-authorized repository deliverables remain part of completion.

At a substantial program boundary, or when the user explicitly requests
compaction, follow [program closeout](references/program-closeout.md). Produce
one linked synthesis of decisive outcomes and a small current decision view;
keep route records and ledger events intact. Closeout is not required after
every session and does not close an unresolved mathematical goal. If the
history index has become a long flat list, use the project's hierarchical
program/route index policy rather than copying all routes into the live view.
For retrospective closeout, distinguish the historical cutoff from the later
assessment; do not attribute later evidence to the old program.

For a long or externally executed route, distinguish queued, running,
last-observed, completed, failed, timed out and abandoned states. Do not keep a
route marked running merely because a prior session launched it. Record the
last observation and execution identifier without treating process completion
as mathematical success.

Lead with whether the original goal was reached and the exact result. State the
proof/review status, decisive mechanism, files and meaningful checks. If it
remains open, distinguish partial results from the goal, list executed routes
with their precise obstructions, and preserve an executable next handoff.
When all presently available routes are exhausted, or tools/resources block
every remaining continuation, say so honestly; leave blocked routes open with
their deferred next steps. Never invent progress to satisfy “do not stop”.
