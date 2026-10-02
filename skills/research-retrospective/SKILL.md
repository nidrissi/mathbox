---
name: research-retrospective
description: >-
  Reconcile a mathematical research repository's current claims, proofs, computations, status, literature dependencies, and failed routes, then recommend the next bounded research moves. Use only when the user asks for a project review, weekly/monthly retrospective, prioritization, a prose project handoff, or “what should I do next?”. Do not use to write a program closeout, migrate research history, operate a .mathbox ledger, or generate its dependency-aware handoff. Default to read-only.
---

# Research retrospective

Produce a decision-quality view of the project, not a chronological summary.
Default to no edits unless the user asks to reconcile files.

## Establish authority

1. Determine repository root and applicable instructions.
2. Resolve charter, live status, claims, conventions, literature record, durable
   proofs, computations, verification, research-history index, and detailed
   record directory.
   Verify that referenced live-role paths exist and expose competing aliases or
   broken authority links.
3. Read the current summary and search the history entry point; follow relevant
   program/phase links to closeouts and designated route indexes. Do not load a long dashboard, claims inventory or index in full just
   to find the latest state. Open only the proof or research records needed to
   verify conflicts or load-bearing claims.
4. Do not choose a newer timestamp over stronger evidence. Expose unresolved
   authority conflicts.
5. Compare the live dashboard's review/checkpoint revision with later changes to
   authoritative manuscripts, proofs and declared deliverables. A stale date is
   a prompt to inspect, not by itself proof that the mathematics changed.

If `.mathbox/` is present, use the available `research-state` skill's brief
read-only check and goal handoff, then inspect full details for affected claims,
review conditions and routes. Use `impact CLAIM` for a named claim's
dependents and `pin-impact PATH` for the pins of a named file. Reconstruct
affected proofs from artifacts;
do not merely repeat generated labels. Do not initialize or migrate state as a
side effect of a read-only retrospective.

Do not start broad literature searches to fill a retrospective. Use available
`literature-check` (`mathbox:literature-check` in plugin installations), or an
exact-source fallback if unavailable, only for a necessary bounded source question;
otherwise propose it as a next route.

If `RESEARCH_LOG.md` still contains long-form legacy entries, read only the
relevant embedded entries and support a mixture of legacy prose and new links.
Report the pending migration through the available `research-init` skill
(`mathbox:research-init` in plugin installations), or report it pending if unavailable, but do not perform or
require it as a precondition for the retrospective.

## Build the portfolio

For each active claim or work package, record:

- exact target, evidence label and strongest currently supported statement;
- durable evidence and review status;
- load-bearing dependencies;
- first unresolved implication or smallest counterexample;
- recent route and why it succeeded or stopped;
- expected scientific value, cost, and risk;
- whether it lies on the current critical path.

Manuscript inclusion, bounded computation and failed search cannot upgrade
evidence labels. Report omitted-issue counts from brief ledger checks.

Identify duplicated efforts, stale claims, abandoned routes with reusable
information, and mutable facts incorrectly embedded in instructions.
For external or long computations, distinguish the last observed process state
from current state. A launch record without a live process, scheduler result or
later observation is `unknown`, not `running`.

Group failed routes by their first failed mechanism rather than title. Identify
shared unresolved dependencies and what mathematical change would reopen each
route. Distinguish new evidence from more prose, repeated bounded cases, and
rediscovery of already recorded obstructions.

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
verification gaps. Report general plugin-skill bugs to the user or Mathbox issue tracker;
project rules belong in the repository.

Treat a live status dashboard as current state, not verification history. Flag
stacked dated verification narratives as a context sink. When reconciliation
edits are requested, keep the latest full current summary. Replace an older
narrative with a link only when it already has a durable home (indexed record,
manifest or closeout), edit policy permits it and `pin-impact` shows no conflict.
Otherwise leave it and report pending research-program closeout or research-init
migration. Reconcile existing facts and rephrase next actions without changing
their mathematical obligations; do not undertake compaction here.
Do not rewrite indexed records or their history-index entries; append a linked
correction record when history itself needs correction.

Flag broken links to purported live dashboards, conflicts between the designated
authority and existing files, and completed deliverables still described as
unresolved. Do not repair these during a read-only retrospective; identify the
minimal reconciliation set.

## Output

Lead with a concise project verdict. Then provide:

1. claim/work-package table;
2. contradictions or stale records;
3. critical path and principal blocker;
4. recommended routes in priority order;
5. files to reconcile, only if edits were requested;
6. the best next prompt for available `research-attempt` or, for multiple routes,
   `research-program` (`mathbox:<name>` in plugin installations); if unavailable,
   give an equivalent self-contained research prompt.
