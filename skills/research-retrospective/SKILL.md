---
name: research-retrospective
description: >-
  Reconcile a mathematical research repository's current claims, proofs, computations, status, literature dependencies, and failed routes, then recommend the next bounded research moves. Use only when the user asks for a project review, handoff, weekly/monthly retrospective, prioritization, or “what should I do next?”. Default to read-only.
---

# Research retrospective

Produce a decision-quality view of the project, not a chronological summary.
Default to no edits unless the user asks to reconcile files.

## Establish authority

1. Determine repository root and applicable instructions.
2. Resolve charter, live status, claims, conventions, literature ledger, durable
   proofs, computations, verification, research-history index, and detailed
   record directory.
3. Read current summaries and the compact history index first, then open only
   the proof or research records needed to verify conflicts or load-bearing
   claims.
4. Do not choose a newer timestamp over stronger evidence. Expose unresolved
   authority conflicts.

Do not start a broad literature search merely to complete a retrospective. If
the requested review cannot be decided without establishing what a load-bearing
external mathematical source says, route that bounded source question through
the available `literature-check` skill (`mathbox:literature-check` in plugin
installations), which checks an authorized project-local cache before fetching.
Otherwise record the unresolved source check as a candidate next route.

If `RESEARCH_LOG.md` still contains long-form legacy entries, read only the
relevant embedded entries and support a mixture of legacy prose and new links.
Report the pending `mathbox:research-init` migration, but do not perform or
require it as a precondition for the retrospective.

## Build the portfolio

For each active claim or work package, record:

- exact target and current evidence label;
- durable evidence and review status;
- load-bearing dependencies;
- first unresolved implication or smallest counterexample;
- recent route and why it succeeded or stopped;
- expected scientific value, cost, and risk;
- whether it lies on the current critical path.

Identify duplicated efforts, stale claims, abandoned routes with reusable
information, and mutable facts incorrectly embedded in instructions.

## Select next routes

Recommend at most three bounded research routes. Each must include:

- exact unresolved mathematical question;
- why it dominates nearby alternatives;
- when current evidence is bounded, the uniform route or obstruction it
  suggests;
- cheapest decisive test and, when bounded, the alternatives it distinguishes;
- success and failure criteria;
- expected durable output;
- dependencies and resource needs;
- stopping condition.

Balance one high-leverage route with lower-risk publishable or computational
work when the project permits. Do not keep a deliverable hostage to an unrelated
open flagship problem.

## Review the AI workflow

Note recurring guidance failures, false `mathbox` plugin skill triggers,
context sinks, duplicated records, non-reproducible computations, or
verification gaps. General plugin-skill bugs belong in the `mathbox` feedback
ledger; project rules belong in the repository.

Treat a live status dashboard as current state, not verification history. Flag
stacked dated verification narratives as a context sink. When reconciliation
edits are requested, keep the latest full current summary and replace older
narratives with links to immutable research records or computation manifests.
Do not rewrite indexed records or their history-index entries; append a linked
correction record when history itself needs correction.

## Output

Lead with a concise project verdict. Then provide:

1. claim/work-package table;
2. contradictions or stale records;
3. critical path and principal blocker;
4. recommended routes in priority order;
5. files to reconcile, only if edits were requested;
6. the single best next prompt for the `mathbox:research-attempt` plugin skill.
