---
name: research-retrospective
description: >-
  Reconcile a mathematical research repository's current claims, proofs, computations, status, literature dependencies, and failed routes, then recommend the next bounded research moves. Use only when the user asks for a project review, handoff, weekly/monthly retrospective, prioritization, or “what should I do next?”. Default to read-only.
disable-model-invocation: true
metadata:
  suite: math-research-skills
  version: "2.0.0"
---

# Research retrospective

Produce a decision-quality view of the project, not a chronological summary.
Default to no edits unless the user asks to reconcile files.

## Establish authority

1. Determine repository root and applicable instructions.
2. Resolve charter, live status, claims, conventions, literature ledger, durable
   proofs, computations, verification, and research log.
3. Read current summaries first, then inspect only the proof/log entries needed
   to verify conflicts or load-bearing claims.
4. Do not choose a newer timestamp over stronger evidence. Expose unresolved
   authority conflicts.

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

Recommend at most three bounded actions. Each must include:

- exact target;
- why it dominates nearby alternatives;
- cheapest decisive test;
- success and failure criteria;
- expected durable output;
- dependencies and resource needs;
- stopping condition.

Balance one high-leverage route with lower-risk publishable or computational
work when the project permits. Do not keep a deliverable hostage to an unrelated
open flagship problem.

## Review the AI workflow

Note recurring guidance failures, false skill triggers, context sinks, duplicated
records, non-reproducible computations, or verification gaps. General skill
bugs belong in the user-wide suite feedback ledger; project rules belong in the
repository.

## Output

Lead with a concise project verdict. Then provide:

1. claim/work-package table;
2. contradictions or stale records;
3. critical path and principal blocker;
4. recommended routes in priority order;
5. files to reconcile, only if edits were requested;
6. the single best next prompt for `research-attempt`.
