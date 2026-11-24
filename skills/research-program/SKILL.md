---
name: research-program
description: >-
  Pursue a substantial mathematical goal across multiple proof, counterexample, literature and computational routes, or close out one named program or phase by compacting its live status and history. Use for sustained investigation, several approaches, continuing after failed routes until a goal is reached, or an authorized program/phase closeout. Do not use for a single bounded attempt, explanation, proofreading, a read-only project retrospective, or migrating instructions or a flat research log into program indexes.
---

# Sustained mathematical research

Own the user's mathematical objective across route changes. A route ending does
not end the assignment. Produce mathematics, not unexecuted suggestions. Do not
promise solutions to open problems or relabel exhausted attempts.
For closeout-only requests reconcile recorded results; start new routes only
if requested. Route repository-wide history restructuring to available
`research-init`. If unavailable, report migration pending and preserve existing
history. Resolve specialist skills using the names exposed by the current host.

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
For work that may cross sessions, branches or delegated agents, name the
checkpoint and record its exact Git revision or ledger event. Identify each
dirty or untracked input actually used by path and content hash or preserved
copy. If neither a Git revision nor a ledger event identifies the inputs,
use a named snapshot with paths and hashes or preserved content. Record a
verified empty ledger head separately when relevant. Use checkpoint identity
to determine ancestry.

Use existing project records, starting with the current summary and nearest
relevant records rather than the complete status/history archive. When an
executable `.mathbox/` ledger is present, use the available `research-state`
skill's brief goal handoff and freshness check; open full claim/review details
only for the active decision. Initialize a `.mathbox/` ledger only when useful
and authorized; absence never blocks research. Read [program protocol](references/program-protocol.md) for
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
Treat alternatives as routes and jointly required lemmas as dependencies;
identify a route's resolved sub-obligation without changing its owner.
Run the decisive check, then pursue the promising route to a substantive
checkpoint using the available `research-attempt` skill if host invocation rules
permit. Otherwise follow the minimal route-record and evidence contract in the
program protocol. Apply the one-route boundary to each work package. Execute the
breadth requested, including independent deliverables that remain useful after
the target is resolved.

For parallel work, assign an owner, base checkpoint and disjoint write scope;
require actual inputs and hashes in each return. The coordinator checks and
reconciles proposed updates and handles persistence as described below.
Preserve incompatible evidence; arrival order establishes no supersession.

Allocate effort by expected information gain, relevance to the goal and cost.
Do not fabricate success probabilities. Attack high-impact uncertain
dependencies before polishing downstream consequences. Formulate auxiliary
lemmas that remove shared bottlenecks. Transfer techniques across fields only
after writing the actual source-to-target dictionary.

Use the available `literature-check` and `computation-audit` skills for
source-dependent implications and load-bearing experiments. If a specialist
skill is unavailable, carry out the relevant exact-source or finite-evidence
check directly with available tools and disclose its limits. Continue the
mathematical work within those limits.

## Change direction on evidence

After a route checkpoint, ask what mathematical information changed. Preserve
the strongest surviving statement and distinguish a false lemma, a failed
method, an implementation bug, and an inaccessible source.

- For a candidate counterexample, check the witness against every hypothesis
  and verify that it violates the exact conclusion under the target's
  quantifiers. Once certified, report the target as refuted and stop trying to
  prove it. If the witness refutes only an auxiliary lemma, revisit only routes and
  deductions that rely on it and continue viable work on the target.
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

An inconclusive attempt alone does not close its route. Before closing an
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
the underlying mathematics.

## Persist and report

Before saving a durable record, proof, report or authored JSON, follow
[attribution.md](references/attribution.md).

Keep proofs in durable mathematical files, finite runs in computation records,
failed mechanisms in linked route records, and current status in one live view.
When persistence is authorized but this host cannot execute or write, propose
one `research-state` deferred packet only when there is a valid ledger proposal
and you have verified an initialized ledger and inspected its head and policy in
`.mathbox/config.json`. Pin the observed event ID and digest (both null for a
verified empty ledger). Use only permitted destinations for new artifacts and
at most one guarded index entry. Include the ledger proposals and state that
ingest is pending. If a prerequisite is unavailable, the required writes fall
outside policy, or the work calls for no new ledger event, return the findings
or closeout, input identities and pending filing steps in a chat handoff.
Update only state that actually changed; replace old dashboard checkpoint prose
with links only once it has a durable home and the project permits, and do not
rewrite indexed history.
User-authorized repository deliverables remain part of completion.

Integrate into a manuscript only on explicit request and after audit; integration
is not validation. Route novelty questions through literature-check; a failed
search is not novelty.

At a substantial program or phase boundary, or an explicit compaction request,
follow [program closeout](references/program-closeout.md); it does not close an
unresolved goal. Repository-wide flat-index restructuring belongs to research-init.

Lead with whether the original goal was reached and the exact result. State the
proof/review status, decisive mechanism, files and meaningful checks. If it
remains open, distinguish partial results from the goal, list executed routes
with their precise obstructions, and preserve a [continuation handoff](references/handoff.md).
When all presently available routes are exhausted, or tools/resources block
every remaining continuation, say so honestly; leave blocked routes open with
their deferred next steps. Never invent progress to satisfy “do not stop”.
