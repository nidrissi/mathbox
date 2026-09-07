---
name: research-state
description: >-
  Track exact mathematical claims, evidence revisions, dependency impact, audit provenance, and research routes in a local append-only ledger. Use when a project has a .mathbox ledger or the user asks for executable research-state tracking, stale-evidence detection, or a dependency-aware handoff. Do not initialize state for a casual math question or replace proof auditing with metadata validation.
---

# Executable research state

Use the project's existing authority rules. The ledger checks recorded evidence,
not mathematical truth. Its `proved` label means a durable proof was recorded
and its declared dependencies are supported; it does not mean the script
verified the argument. Review status is a separate field.

Read [ledger.md](references/ledger.md) before recording events. The portable,
standard-library helper is [research_state.py](scripts/research_state.py).
Resolve its installed location; all artifact paths are relative to the research
project supplied with `--root`, never to the installed skill.

## Read before changing state

For an existing initialized ledger, run `--root PROJECT check`, then `--root
PROJECT handoff --goal CLAIM` when that goal has been registered. For an authorized
new project, create its directory, initialize and register claims first; do not
run handoff against nonexistent state. `status`, `check`, `impact`, `next`, and `handoff` are read-only
and never initialize a ledger. `--json` goes before the subcommand.

Inspect the actual evidence behind important statuses. A changed proof or
dependency invalidates the affected evidence snapshot. A retracted or refuted
dependency blocks downstream proofs without rewriting history. Run `impact
CLAIM` before revising a load-bearing statement.

## Record only material changes

Initialize `.mathbox/` only when the user has authorized useful project setup or
state tracking. Existing prose projects can keep their current format; the
ledger is optional. For a migration, follow [migration.md](references/migration.md).

Write a proposal JSON and use `record FILE`. Register exact claims before their
evidence and dependencies before consumers. Evidence needs durable artifact
paths; the helper hashes them and records all transitive claim revisions. A
source record needs an exact identifier, version, locator and translation. A
computation needs its assertion, bounds and non-claims. It never becomes a
universal proof merely because its command succeeded.

Record separate review events linked to the exact evidence event and a durable
report. An independence declaration must describe a real fresh review; a
different actor name alone does not establish independence. The author cannot
declare an independent audit of their own evidence. A failed review remains
active until explicitly retracted with a reason or replaced by new evidence.

Correct a claim by recording a new claim revision with a reason. Correct bad
evidence/reviews with a retraction and new events. Never edit/delete numbered
events, refresh hashes merely to silence a warning, or reinterpret a changed
statement as already proved. Keep proof details outside the ledger.

## Use routes to support decisions

Record a route's target, mechanism, decisive question/test, prerequisites,
success/failure criteria and rough gain/cost estimates. `next` orders ready
routes by a transparent heuristic; use mathematical judgment over its ordering.
Close routes with the exact outcome, obstruction and next question. Reopening
a completed mechanism requires the prior result and the new mathematical input.

## Report and persist

Commit ledger events with the corresponding proof/source/report artifacts only
under the project's Git authorization. Keep licensed/private source caches
under their own existing retention policy; the ledger stores references only.
Do not create a second manually maintained claims dashboard. Prefer a generated
view in the designated live status location when migration is authorized.

Report changed claims, stale evidence and affected dependents. A clean `check`
means bookkeeping integrity and current artifact hashes, not a proof audit.
For genuine correctness decisions, use the mathematical specialist workflow.
