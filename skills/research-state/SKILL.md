---
name: research-state
description: >-
  Read or update a local append-only .mathbox ledger of exact claims, evidence revisions, dependency impact, review provenance, routes and parallel or delayed runs. Use when the user asks to set up, check, record in or reconcile such a ledger, detect stale evidence, or generate its dependency-aware handoff. Do not use merely because a ledger exists, for a casual math question, as a substitute for proof auditing, or for a prose retrospective from status files.
---

# Executable research state

Follow project authority rules. The ledger checks recorded evidence, artifact
freshness and dependencies, not mathematical truth. `proof-recorded` describes
bookkeeping rather than a theorem proved under the project's vocabulary.
Apply project promotion and approval policy separately; review status remains
separate from evidence.

Read [ledger.md](references/ledger.md) before interpreting labels or recording
events. Resolve [research_state.py](scripts/research_state.py) as `TOOL` in this
installed skill. All artifact paths are relative to the project supplied with
`--root`; put `--json` before the subcommand for complete structured output.

## Read before changing state

For initialized state, start with `check --summary`, then `handoff --goal CLAIM`
for a registered goal. Without a registered goal use `status`, or an unfiltered
`handoff`. Check summaries contain counts and sampled issues with omitted counts;
brief status/handoff views also list live, stale and unreconciled runs needing
attention. Open `--full` details only for relevant contracts, reviews or issues;
compare complete issue lists when a change could hide a new issue in the sample.

```bash
python3 "$TOOL" --root PROJECT check --summary
python3 "$TOOL" --root PROJECT status
python3 "$TOOL" --root PROJECT handoff --goal CLAIM
python3 "$TOOL" --root PROJECT impact CLAIM
python3 "$TOOL" --root PROJECT pin-impact PATH
python3 "$TOOL" --root PROJECT record PROPOSAL.json
python3 "$TOOL" --root PROJECT record-batch PROPOSALS.json --dry-run
python3 "$TOOL" --root PROJECT record-batch PROPOSALS.json
python3 "$TOOL" --root PROJECT ingest PACKET.json --dry-run
python3 "$TOOL" --root PROJECT ingest PACKET.json
```

`status`, `check`, `impact`, `pin-impact`, `next` and `handoff` are read-only and
never initialize state. Create an authorized new project, initialize and register
claims before querying its goal. Inspect actual proof/source/computation artifacts
behind important labels. Changed proofs or dependencies invalidate snapshots;
retracted dependency evidence or current counterexamples block downstream proofs
without rewriting history. Run `impact CLAIM` before revising a load-bearing
statement and `pin-impact PATH` before editing a pinned file.

## When state is writable only later

When persistence is authorized and the host can inspect the exact ledger head
but cannot execute or write, follow [deferred-packet.md](references/deferred-packet.md).
Never invent IDs or hashes. Return the complete packet in the final JSON fence
and say it is unapplied; obey the inspected local write policy.

## Record only material changes

Initialize `.mathbox/` only for useful, authorized setup or state tracking;
existing prose projects may keep their format. Follow [migration.md](references/migration.md)
for adoption. A session alone needs no event. Record changed contracts, evidence,
reviews and justified route outcomes, rather than duplicating route narratives.
Program/run lifecycle events serve work spanning executors, branches, delayed
returns or sessions.

Write ordinary proposals with `type`, `actor` and `payload`; use `record FILE`,
or preview a dependency-ordered `record-batch` before appending distinct events.
Unknown payload keys are rejected on new writes; existing journals still replay.
Register dependency claims before consumers and exact claims before evidence.
Bind authoritative wording with `statement_artifact` and locator when useful.
The helper hashes durable artifacts and captures transitive claim revisions;
never supply generated snapshots. Source evidence needs exact identifier,
version, locator and translation. Computation evidence needs assertion, bounds
and non-claims; successful execution is not a universal proof.

A `manifest` links a version-2 computation record, its hashed input/output closure,
matching `claim_id`, and completed run. Validate it with computation-audit first:
linkage checks do not validate its scientific interpretation. Version-1 manifests
may be pinned only as ordinary artifacts, without automatic closure.

Record reviews separately against exact evidence and a durable report. Genuine
independence requires fresh review of raw evidence; a different actor name alone
is insufficient, and an author cannot independently audit their own evidence.
Inspect active review objects and reports when passing, conditional and failed
reviews coexist. Failed or conditional reviews remain challenges even if their
reports disappear. Resolve them through an explicit justified retraction or
actually revalidated replacement evidence, never a silent hash refresh.

Whole-file pins stale on any byte change, including typography. Prefer faithful,
stable claim-scoped artifacts where available; inspect fanout with `pin-impact`.
Revise a claim with a new revision and reason. After real revalidation, record new
evidence with `supersedes: [old IDs]`; retract only erroneous evidence or review
records. Keep proof details outside the ledger. Never edit/delete numbered events,
refresh hashes to silence warnings, or treat a changed statement as already proved.

## Use routes to support decisions

Record owning claim, optional `resolves` obligations, mechanism, decisive question
and discriminator, prerequisites, success/failure criteria and rough gain/cost.
Separate alternative routes from jointly required theorem dependencies. `next`
ranks ready recorded routes heuristically; mathematical judgment sets priority.
Repeated owner/mechanism pairs require the documented reopening contract, not
renaming to evade it.

Separate attempt outcome from route disposition. Inconclusiveness, resource limits
or priority changes never alone justify closure. Preserve untried or deferred
continuations with next action and resumption condition. Close only with the exact
obstruction or scoped reason no continuation remains. Reopening rules and event
fields are in [executions.md](references/executions.md) and the ledger reference.

When an open route's continuation must outlive this session, use an existing open
program whose goal covers it, or register one if absent. Record missing
`route-run`, `run-result` and `route-reconcile` events with `decision: continue`,
reusing applicable records. Cited runs and their reconciliation share `base_event`
and `base_revision`; a run result inherits its base through its run and has no
base fields. The program retains its starting checkpoint, which may differ from
a later execution's base. `next` and `handoff` show the latest continuation's
reason and next step. A prose record alone cannot update that generated view.
Do not add lifecycle events solely for follow-up completed in the same session.

For parallel/delayed work, assign distinct executions with owner, actual inputs,
base and write scope. Reconcile serially in the single writer's ledger, record
conflicts, and disposition late results explicitly. Arrival order is not ancestry;
never merge or renumber event streams. Process completion does not close a route
or promote a claim.

## Report and persist

Commit events with their artifacts only under project Git authorization. Preserve
source-cache retention policy. Use one designated live view, preferably a generated
brief view when migration is authorized; do not create a parallel manual dashboard.
Report changed claims, active review conditions/conflicts, stale evidence,
dependents and route-only context. A clean check establishes bookkeeping integrity.
Use available `proof-audit`, `computation-audit` or `literature-check` skills
(`mathbox:<name>` in plugin installations) for correctness decisions, or perform
the relevant bounded check directly and disclose limits if unavailable.
