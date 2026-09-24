---
name: research-state
description: >-
  Track exact mathematical claims, evidence revisions, dependency impact, audit provenance, research routes, and parallel or delayed executions in a local append-only ledger. Use when a project has a .mathbox ledger or the user asks for executable research-state tracking, stale-evidence detection, run reconciliation, or a dependency-aware handoff generated from recorded events. Do not initialize state for a casual math question, replace proof auditing with metadata validation, or write a prose project retrospective from status files.
---

# Executable research state

Use the project's existing authority rules. The ledger checks recorded evidence,
not mathematical truth. Its generated labels say only what evidence was
recorded: for example, `proof-recorded` is not a declaration that a theorem is
proved under the project's vocabulary. Review status remains separate. Apply
the project's promotion and approval policy outside this mechanical projection.

Read [ledger.md](references/ledger.md) before recording events. The portable,
standard-library helper is [research_state.py](scripts/research_state.py).
Resolve its installed location; all artifact paths are relative to the research
project supplied with `--root`, never to the installed skill.

## Read before changing state

For an existing initialized ledger, run `--root PROJECT check --summary`, then
`--root PROJECT handoff --goal CLAIM` when that goal has been registered. These default
reports are brief: they give counts, actionable IDs, and an explicit omitted
count, including runs that are live, `stale-result`, or awaiting
reconciliation. Use `--full` after the subcommand or `--json` before it when the exact
claim contract, review, route result, or complete issue list is needed. Do not
paste a full projection into the live dashboard. For an authorized new project,
create its directory, initialize and register claims first; do not run handoff
against nonexistent state. `status`, `check`, `impact`, `pin-impact`, `next`, and
`handoff` are read-only and never initialize a ledger. `--json` goes before the
subcommand.

After resolving this skill's script as `TOOL`, use this small command map:

```bash
python3 "$TOOL" --root PROJECT check --summary
python3 "$TOOL" --root PROJECT handoff --goal CLAIM
python3 "$TOOL" --root PROJECT pin-impact PATH
python3 "$TOOL" --root PROJECT record PROPOSAL.json
python3 "$TOOL" --root PROJECT record-batch PROPOSALS.json --dry-run
python3 "$TOOL" --root PROJECT record-batch PROPOSALS.json
python3 "$TOOL" --root PROJECT ingest PACKET.json --dry-run
python3 "$TOOL" --root PROJECT ingest PACKET.json
```

`pin-impact` is read-only; use it before editing a file pinned by many claims.
The two batch calls preview and then append distinct events. Read the compact
batch contract in [ledger.md](references/ledger.md) before using them.

## When state is writable only later

If the host can inspect the repository and exact ledger head but cannot execute
the helper or write project files, and persistence is authorized, follow the
[deferred handoff contract](references/deferred-handoff.md). Return one complete
`mathbox-deferred-v1` packet with every new durable artifact needed by the
proposed events, at most one guarded index entry, and a batch of proposals.
Create files and append entries only where the project's `.mathbox/config.json`
opens them to deferred packets. Pin the packet to the exact inspected ledger
event ID and hash. Use batch aliases for new event references. Never invent
event IDs, artifact hashes, timestamps, or snapshots; the local ingest command
generates them. Put the packet in the
last fenced `json` block, with no omissions or text after it. Distinguish the
mathematical finding reached from the state actually recorded: until local
ingest succeeds, say explicitly that the packet has not been applied.

Inspect the actual evidence behind important statuses. A changed proof or
dependency invalidates the affected evidence snapshot. A retracted dependency
or current counterexample record blocks downstream proofs without rewriting
history. Run `impact CLAIM` before revising a load-bearing statement.

## Record only material changes

Initialize `.mathbox/` only when the user has authorized useful project setup or
state tracking. Existing prose projects can keep their current format; the
ledger is optional. For a migration, follow [migration.md](references/migration.md).

Write a proposal JSON and use `record FILE`. A research session is not itself
an event: record only mathematical state that changed. An already registered
bounded route can close with one route-result when closure is justified;
an unfinished attempt alone does not justify closure. Program/run lifecycle
events are for work that actually spans executors, branches, delayed returns,
or sessions. Do not revise claims, repeat evidence, or add a review merely to
mirror a route record.
For several necessary events, use `record-batch FILE` after its dry-run; this
keeps the event types separate while avoiding repeated whole-journal reads.
Register exact claims before their evidence and dependencies before consumers.
When a manuscript or theorem file controls the claim wording, bind it with an
optional `statement_artifact` and locator. Evidence needs durable artifact
paths; the helper hashes them and
records all transitive claim revisions. A source record needs an exact
identifier, version, locator and translation. A computation needs its
assertion, bounds and non-claims. It never becomes a
universal proof merely because its command succeeded.

For a computation manifest that declares hashed inputs and outputs, use the
optional `manifest` field. The ledger then pins the manifest and its declared
file closure and checks that `claim_id` matches and the run completed. This is a
freshness/linkage check, not a replacement for the computation manifest
validator or an audit of the mathematical interpretation.

Record separate review events linked to the exact evidence event and a durable
report. An independence declaration must describe a real fresh review; a
different actor name alone does not establish independence. The author cannot
declare an independent audit of their own evidence. A failed review remains
active until explicitly retracted with a reason or replaced by new evidence.
Inspect the projected active review events and report paths, especially when
conditional, failed and passing reviews coexist; a one-line review label is not
a substitute for those conditions.

Whole-file bindings stale on any byte change, including typography. Prefer a
stable claim-scoped artifact when it faithfully states the authoritative claim;
use `pin-impact` to see the declared fanout of an existing whole-file pin.
Never refresh a hash on the strength of a formatting label alone.

Correct a claim by recording a new claim revision with a reason. Correct bad
evidence/reviews with a retraction and new events. Never edit/delete numbered
events, refresh hashes merely to silence a warning, or reinterpret a changed
statement as already proved. Keep proof details outside the ledger.

## Use routes to support decisions

Record a route's owning claim and, when different, the exact obligations it
`resolves`, plus its mechanism, decisive question/test, prerequisites,
success/failure criteria and rough gain/cost estimates. Keep alternative routes
distinct from jointly required claim dependencies. `next` orders ready
routes by a transparent heuristic; use mathematical judgment over its ordering.
Separate an attempt's outcome from route closure. Close a route with its exact
outcome, obstruction or scoped reason, and next question. Before closing an
unresolved route, account for known continuations and explain why none remains
executable within the route's stated scope. An inconclusive attempt, resource
limit or priority change alone does not justify closure. Keep untried or
deferred continuations in the route record and current handoff with their next
steps and resumption conditions. Reopening a closed route requires its prior
result and a `changed_input` addressing any recorded obstruction; resuming an
open route's unfinished work does not require a new mathematical input.

For sustained or parallel work, record a program and a distinct route run for
each executor. Pin the ledger base event and external revision at which each run
started; observations supply the last-seen revision, and run results close or
abandon executions without automatically closing the mathematical route.
Reconcile an inconclusive run with `continue` when the route remains open,
including when its next action is deferred; `next` and `handoff` show that
reconciliation's next step and reason under the route. A later run uses the
same route ID. A route event cannot hold a deferred step: when a ledger route's
unfinished continuation must survive to a later session, record the attempt as
a run with its result and a `continue` reconciliation. A prose record alone
leaves the generated handoff showing only the route's original question. Do not
add run events to mirror an attempt whose follow-up finishes in the same
session. To correct an earlier premature closure that recorded no obstruction,
use the append-only reopening contract in [ledger.md](references/ledger.md);
identify the overlooked continuation rather than inventing new mathematics.
Relabelling a `failed` result or recorded obstruction as premature does not
reopen it.
Reconcile completed runs serially in the one writer's ledger. Record conflicts
and give delayed results an explicit late disposition rather than reconstructing
or merging numbered event streams. See [ledger.md](references/ledger.md) for the
event contracts.

## Report and persist

Commit ledger events with the corresponding proof/source/report artifacts only
under the project's Git authorization. Keep licensed/private source caches
under their own existing retention policy; the ledger stores references only.
Do not create a second manually maintained claims dashboard. Prefer a generated
view in the designated live status location when migration is authorized.

Report changed claims, active review conditions and conflicts, stale evidence,
affected dependents, and route-only context kept outside the theorem dependency
graph. A clean `check` means bookkeeping integrity and current artifact hashes,
not a proof audit.
For genuine correctness decisions, use the mathematical specialist workflow.
