# Ledger format and commands

The journal is `.mathbox/events/000001.json`, etc., with schema version 1 in
`.mathbox/config.json`. New configurations also declare the
`recorded-evidence-v1` projection semantics. A pre-existing version-1 config
without that declaration remains readable and receives the same neutral
projection. Keep it in project version control. Events form a hash
chain, have UTC timestamps and actor attribution, and are written atomically
under an exclusive writer lock. Hash chaining detects accidental corruption; it
is not authentication against someone who can rewrite the whole journal. Git
history remains the provenance boundary. Concurrent branches must replay their
proposals sequentially, not merge two numbered journals by renaming files.

Requires Python 3.10+. The helper has no network, database or package dependency
and never executes a command found in a record. Project-relative artifact paths
cannot escape the root or traverse symlinks. Keep evidence outside `.mathbox/`.
Read-only commands never create directories. A stale writer lock is an explicit
error; inspect active work before manually removing it.

## Quick start

Here `TOOL` means the resolved path to this skill's `scripts/research_state.py`.

```bash
python3 "$TOOL" --root /path/to/project init
python3 "$TOOL" --root /path/to/project record claim.json
python3 "$TOOL" --root /path/to/project record evidence.json
python3 "$TOOL" --root /path/to/project check --summary
python3 "$TOOL" --root /path/to/project status
python3 "$TOOL" --root /path/to/project impact C_MAIN
python3 "$TOOL" --root /path/to/project next --goal C_MAIN
python3 "$TOOL" --root /path/to/project handoff --goal C_MAIN
python3 "$TOOL" --root /path/to/project pin-impact statements/parity.md
```

`record` prints a short receipt with its assigned `E000001` identifier, its
subject (claim, evidence, route, run, program or retraction target) and the
paths and hashes it pinned; `--json record` prints the complete event. Proposals
contain exactly `type`, `actor`, and `payload`. Generated timestamps, hashes and
revision snapshots belong to the helper. Exit codes: 0 success; 1 stale evidence
from `check`; 2 invalid input, unsupported version, integrity or I/O error.
Open conjectures are valid state and do not make `check` fail.
`check --summary` prints event and claim counts, counts by evidence/review status,
the total issue count and at most eight example issues. The omitted count is
explicit. `check --summary --full` prints every issue; `--json check` prints
the complete projection. Human `status` and `handoff` likewise default to brief
views; add `--full` after either subcommand for the complete Markdown report,
or put `--json` before the subcommand for the complete machine view. When
programs or runs exist, the brief view counts them by status and lists runs
needing attention: live, `stale-result`, or with a result not yet named by a
reconciliation. Open routes name those runs and their latest `continue` next
step and reason. Neither display mode changes
freshness checks or exit codes.

## Record several distinct events efficiently

`record-batch` accepts a JSON array of ordinary proposals in dependency order.
An optional `alias` on a proposal names its generated event ID for later
proposals in that same array. Use `{"$event":"alias"}` as a complete field value
to reference it, for example in a review's `evidence` field:

```json
[
  {"type":"evidence","actor":"author","alias":"proof_a","payload":{"claim":"A","kind":"proof","summary":"Checked argument","artifacts":[{"path":"proofs/a.md"}]}},
  {"type":"review","actor":"reviewer","payload":{"evidence":{"$event":"proof_a"},"outcome":"pass","independent":true,"summary":"Fresh check","artifact":{"path":"reviews/a.md"}}}
]
```

First run `record-batch proposals.json --dry-run`; then run the same command
without `--dry-run` after checking the event count, order and critical pinned
artifacts. Use `--json` with the dry-run when every proposed event must be inspected.
Dry-run IDs are provisional: another writer can append between the preview and
commit, so use batch aliases rather than copying preview IDs into later fields.
The helper takes one writer lock and replays the existing journal once. It
validates every proposal before appending any event, while still writing a
separate hash-chained file for each event. A filesystem interruption during
the append can leave a valid prefix of the batch. Inspect the current ledger
head before retrying; do not blindly replay the whole input. The default output
gives the event range, counts by type, and at most eight receipts with an
omitted count. Each receipt lists up to eight pinned paths and hashes, with a
`pins_omitted` count beyond that. `--json` prints every complete event; capture or inspect
that output selectively for a large batch.

For a host that can reason from the ledger but cannot execute or write, use the
[deferred handoff protocol](deferred-handoff.md). `ingest PACKET.json --dry-run`
validates staged text artifacts, one guarded index append, and the ordinary
batch proposals against an exact ledger head. Only locations that the optional
`deferred` section of `.mathbox/config.json` opens can receive files or an index
entry. `ingest PACKET.json` applies them;
`ingest -` reads the packet from standard input. This packet format is separate
from ledger schema version 1 and does not change event semantics.

`pin-impact PATH` reports current statement, evidence, and review pins of a
project-relative file, plus dependents of directly affected claims. It also
reports run-result pins: those runs become `stale-result` when the file
changes, although no claim does. Paths match after lexical normalization, so
`./proofs//a.md` and `proofs/a.md` name one file; new pins are stored in the
normalized spelling. The lookup reads recorded pins without hashing artifacts.
Its brief view shows counts and samples; `--json pin-impact PATH` gives every
ID. It is a diagnostic, not permission to treat byte changes as mathematically
harmless.

## Claim and evidence proposals

```json
{
  "type": "claim",
  "actor": "researcher",
  "payload": {
    "id": "C_MAIN",
    "statement": "For every integer n, n(n+1) is even.",
    "hypotheses": ["n is an integer"],
    "regime": "Exact integer arithmetic",
    "level": "Divisibility",
    "dependencies": [],
    "statement_artifact": {
      "path": "statements/parity.md",
      "locator": "Theorem A"
    }
  }
}
```

Repeating a claim ID creates a revision and requires a nonempty `reason`. Restate
the complete contract; old hypotheses are not implicitly inherited. Add separate
claim IDs for distinct restrictions, equivalent formulations requiring a bridge,
or unresolved proof obligations. Every dependency must already be registered.
Cycles are rejected, including cycles introduced by revisions.
`statement_artifact` is optional. Use it when a project file, rather than the
ledger text alone, controls the exact theorem statement. The helper pins the
whole file and retains the locator; a byte change conservatively stales evidence
for the claim and its consumers. Prefer a claim-scoped file when unrelated edits
to a large manuscript should not trigger that warning. A locator identifies the
intended statement but is not parsed or hashed independently.

```json
{
  "type": "evidence",
  "actor": "researcher",
  "payload": {
    "claim": "C_MAIN",
    "kind": "proof",
    "summary": "One of two consecutive integers is divisible by 2.",
    "artifacts": [{"path": "proofs/parity.md"}]
  }
}
```

Evidence kinds and additional required fields:

| Kind | Required payload fields | Interpretation |
|---|---|---|
| `proof` | Common fields above | Recorded argument under the exact claim contract |
| `source` | `identifier`, `version`, `locator`, `translation` | Exact theorem and checked project implication |
| `computation` | `assertion`, `bounds`, nonempty `non_claims` string array | Finite evidence; cannot discharge a dependency requiring proof |
| `counterexample` | `hypothesis_check` | Recorded witness satisfying every target hypothesis |

All require at least one durable artifact. Pin the complete argument, relevant
conventions, executable code/manifests and source translation reports as needed,
not just a summary saying “verified”. Undeclared dependencies or unpinned files
cannot be detected by this tool. A finite computation that exhausts a finite
theorem still needs a separate proof artifact establishing exhaustive coverage
and implementation correctness. The helper never infers such a bridge.

A computation can link a strict computation manifest instead of duplicating its
file closure in `artifacts`:

```json
{
  "type": "evidence",
  "actor": "researcher",
  "payload": {
    "claim": "C_FINITE",
    "kind": "computation",
    "summary": "Checked the declared finite instance.",
    "artifacts": [],
    "manifest": {"path": "runs/example/manifest.json"},
    "assertion": "The declared instance has rank 4.",
    "bounds": "One matrix over GF(5)",
    "non_claims": ["No assertion for other matrices"]
  }
}
```

The manifest must have the same `claim_id`, a completed zero-exit run, nonempty
`input_artifacts`, and nonempty `outputs`. Every declared path must be
project-relative, inputs must
retain equal before/after hashes, and input/output paths must be distinct. The
ledger copies and checks those pins whenever status is projected. It does not
validate the manifest's broader execution or mathematical schema; run the
computation-audit validator first. When `declared_results` is present, it must
exactly match the paths labeled as result outputs. Older or incomplete manifests can still be
pinned as ordinary artifacts, but do not gain automatic dependency closure.

## Reviews and corrections

```json
{
  "type": "review",
  "actor": "fresh-reviewer",
  "payload": {
    "evidence": "E000002",
    "outcome": "pass",
    "independent": true,
    "summary": "Re-derived the parity argument from the statement.",
    "artifact": {"path": "reviews/parity.md"}
  }
}
```

Allowed review outcomes: `pass`, `fail`, `conditional`. Keep a conditional audit's
missing input explicit. A pass applies only to its exact evidence. The helper
rejects reviewing already stale evidence and rejects self-declared independent
review by the evidence author. It cannot authenticate human/agent identities or
whether the reviewer actually worked independently. Active failed reviews block
their evidence; conflicting proof/counterexample evidence yields `disputed`.
A counterexample with an active conditional review leaves the claim
`conditional` unless another unqualified counterexample supports a negative
record. The same conditional rule applies to computation evidence. Coexisting
positive and counterexample evidence yields `disputed`.

Each projected claim contains its active `reviews`, keyed by review event ID,
with the evidence link, outcome, independence declaration, actor, summary,
report artifact, timestamp and current artifact issues. The compact `review`
field reports an independent pass, a conditional review, a failed review, or
conflicting pass/fail reviews. Inspect the full objects before resolving a
condition or conflict.

Retract an erroneous evidence or review event with:

```json
{"type":"retract","actor":"researcher","payload":{"target":"E000002","reason":"The witness does not satisfy the connectedness hypothesis."}}
```

A claim whose dependencies are not `proof-recorded` or `source-recorded` is
reported `conditional`, including when its own attached evidence is a finite computation.
Finite evidence never reads as verified while its inputs remain open.

Generated evidence states deliberately avoid project-level mathematical
promotion words:

| Generated state | Mechanical meaning |
|---|---|
| `proof-recorded` | A current proof artifact was recorded and declared claim dependencies have supporting proof/source records |
| `source-recorded` | A current source application was recorded under the same dependency condition |
| `computation-recorded` | Current bounded computation evidence was recorded; it does not discharge proof dependencies |
| `counterexample-recorded` | A current unqualified counterexample record was supplied |
| `conditional` | A declared dependency or review condition remains open |
| `disputed` | Current positive and counterexample evidence coexist |
| `stale`, `incomplete`, `conjectural` | Evidence changed, failed review blocks it, or no current evidence is recorded |

`independent-pass-recorded` likewise reports a current review event, not an
authenticated reviewer or theorem certification. Translate these mechanical
states through the repository's own approval policy; do not rename them to
`proved` automatically.

Changes in a claim's transitive revision snapshot or artifact bytes make evidence
stale. Dependency evidence being retracted or counterexample-supported instead makes downstream
arguments conditional. Re-record after mathematical revalidation, never just
to refresh bookkeeping. Generated labels describe recorded local proof, source,
finite evidence, counterexample, missing evidence, conflict or staleness.

New evidence can include `supersedes`, an array of prior evidence event IDs for
the same claim. Use this after actually revalidating a changed proof or contract.
It preserves the old evidence in history while removing it from the live view
and freshness gate. It does not declare the old statement false. Retraction of
the replacement does not automatically revive superseded evidence. Negative or
conditional reviews remain blockers even if their report later disappears;
their explicit retraction or new evidence is required to resolve the challenge.

## Routes

A `route` payload has `id`, owning `claim`, optional nonempty `resolves` (claim
IDs), `mechanism`, `question`, `discriminator`, `success`, `failure`,
`prerequisites` (claim IDs), and integer `gain`/`cost` in 1..5. When `resolves`
is omitted it defaults to the owning claim. Use it when a route organized under
a parent claim directly attacks a registered sub-obligation in that claim's
dependency closure. These estimates
support prioritization, not evidence promotion. Prerequisites mean results
needed *before* executing the route; do not list a resolved target as its own
prerequisite or turn route-only prerequisites into theorem dependencies. `next`
scores `(gain + number of selected downstream claims)
/ cost`, lists ready routes first and includes blockers for others. It does not
invent new routes, claim semantic diversity or assign success probabilities.

A `route-result` payload has `route`, `outcome` (`succeeded`, `failed`, `blocked`,
`inconclusive`), `reason`, and `next_question`. A route can close only once.
All four outcomes are terminal and remove the route from `next`. For an
unresolved route, first check its known continuations and record why none remains
executable within its stated scope. `inconclusive` does not mean the mechanism
is impossible. Do not use terminal `blocked` or `inconclusive` merely to park an
unfinished attempt for time, tools or priority; keep the route open and describe
the deferred action and resumption condition in its durable record and handoff.
Correction/reopening is a new route ID with `reopens` equal to the terminal
route-result or reconciliation event ID and a `changed_input` explanation. An exact repeated target/mechanism
without this explanation is rejected, whether the earlier route is open or
closed. Semantic duplicates still need human or agent judgment. Route success
does not itself create proof evidence.

For an established mathematical obstruction, `changed_input` must explain what
addresses that obstruction. Only when the prior result recorded no mathematical
obstruction, such as a premature or legacy `inconclusive` or `blocked` closure
for time, tools or priority, may it instead identify the closure error, the
overlooked unfinished continuation or restored resource, and the concrete next
action. Explicitly say when no mathematical premise changed. A `failed` result,
or any result whose reason records an obstruction, cannot be reopened by
relabelling its closure as premature. Preserve the old event; do not fabricate
new evidence or rename the mechanism to evade the reopening link. These are
semantic checks by the agent; the helper validates the event structure only.

`handoff` includes open candidates in `routes` and completed history in
`closed_routes`, filtered to the goal and its transitive dependencies when a
goal is supplied. A route is relevant when its owner or a claim in `resolves` is
selected. The handoff keeps route owners and prerequisite closures outside the
goal dependency closure in the separately typed `state.route_context` object.
Reported stale records are filtered to the claims and route context shown, so a goal
handoff never carries an unrelated claim's freshness problem. Use `check` or an
unfiltered `status` for the whole project. Each closed route includes its
payload and `event_id`, plus a nested `result` with the outcome,
reason/obstruction, next question and result `event_id` needed for `reopens`.
Markdown handoffs also show these continuation details. `next` continues to
list only open candidates. Each open candidate in `next` and `handoff` carries
`continuation`: `null`, or the `event_id`, `reason` and `next_question` of the
route's latest `continue` reconciliation. Both Markdown handoff views print it
under the route.

## Programs, executions and reconciliation

Use lifecycle events when work spans agents, branches, delayed responses, or
multiple sessions. Ordinary route/result records remain valid.

Start a program against a precise ledger head and external project revision:

```json
{
  "type": "program",
  "actor": "coordinator",
  "payload": {
    "id": "P_MAIN",
    "goal": "C_MAIN",
    "objective": "Resolve the registered goal through the live route portfolio.",
    "base_event": "E000012",
    "base_revision": "git:0123456789abcdef"
  }
}
```

The base event must already exist in the ledger. The revision is an external
immutable identifier or an explicit unversioned snapshot label; the helper
cannot verify a VCS revision. A `program-observation` records `program`, a state
(`active`, `waiting`, `blocked`, or `unknown`), `summary`, and
`observed_revision`. Use `unknown` when importing an old launch whose liveness
has not been observed; do not infer that it is active. A terminal
`program-result` records `program`, an outcome (`completed`, `blocked`, or
`abandoned`), `reason`, `next_action`, and `closed_revision`. Programs are
status containers and never promote claims. Close or explicitly abandon every
run before closing its program.

Start every execution separately, including parallel executions of one route:

```json
{
  "type": "route-run",
  "actor": "coordinator",
  "payload": {
    "id": "RUN_A",
    "program": "P_MAIN",
    "route": "R_LIFT",
    "base_event": "E000013",
    "base_revision": "git:0123456789abcdef",
    "executor": "worker-a",
    "work_scope": ["construct the lift", "do not edit the main ledger"]
  }
}
```

The route's owner or one of its resolved targets must belong to the program goal
or its dependency closure. A
`run-observation` records `run`, state (`active`, `waiting`, `blocked`, or
`unknown`), `summary`, and `observed_revision`. Its event becomes the generated
last observation. A `run-result` records `run`, outcome (`succeeded`, `failed`,
`blocked`, `inconclusive`, or `abandoned`), `reason`, `next_question`,
`result_revision`, and optional pinned `artifacts`. It closes only that
execution. Results may arrive after their route closed because their
base and result revisions, rather than event arrival order, carry chronology.

The ledger's single writer then records `route-reconcile` with `route`, one or
more run-result event IDs in `results`, their common `base_event` and
`base_revision`, `current_revision`, `reason`, `next_question`, and an explicit
`conflicts` string array. Runs based on different snapshots need separate
reconciliations. Differing run outcomes and `late-conflict` require a nonempty
conflict record. Decisions are:

- `continue`: retain an open route while waiting or adapting;
- `succeeded`, `failed`, `blocked`, or `inconclusive`: close an open route;
- `late-consistent`, `late-conflict`, `late-superseded`, or
  `late-not-applicable`: disposition a newly arrived result after closure.

For example, if a coefficient ansatz is inconclusive and a recurrence remains
untried, record the run's outcome as `inconclusive` and reconcile with `continue`.
Name the recurrence as the next action, or state why it is deferred and when to
resume it. The route stays in `next` and `handoff` with that next action and
reason as its `continuation`; a later run of that same route does not need
`reopens` or `changed_input`. These helpers do not schedule deferred work or
lower its score; read each candidate's `continuation` and apply the recorded
resource and priority conditions when choosing among candidates.

Each reconciliation must add at least one result not previously reconciled; a
later cumulative reconciliation may also cite earlier results. A terminal
reconciliation event is the event named by `reopens`. No outcome is inferred
from completion or arrival order. This serial proposal workflow records parallel
and delayed work without merging or renumbering journals. A run result or
reconciliation never creates mathematical evidence; record separate evidence
only after checking the result against the exact claim.

JSON status and handoff output include active review objects, `programs`, `runs`, and
`reconciliations`. Each program/run has a projected lifecycle status and a
generated `last_observed` event and timestamp. Changed terminal run artifacts
produce `stale-result` plus a ledger issue; they do not silently change the
recorded terminal outcome.
