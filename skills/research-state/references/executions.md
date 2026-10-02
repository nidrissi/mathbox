# Programs, executions and reconciliation

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
or its dependency closure. Runs cannot start on closed routes or programs. A
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
`conflicts` string array, and required `decision`, one of the values below. Runs based on different snapshots need separate
reconciliations. Differing run outcomes and `late-conflict` require a nonempty
conflict record. Decisions are:

- `continue`: retain an open route while waiting or adapting;
- `succeeded`, `failed`, `blocked`, or `inconclusive`: close an open route;
- `late-consistent`, `late-conflict`, `late-superseded`, or
  `late-not-applicable`: disposition a newly arrived result after closure.

A continuation reconciliation proposal is:

```json
{
  "type": "route-reconcile",
  "actor": "coordinator",
  "payload": {
    "route": "R_LIFT", "results": ["E000015"],
    "base_event": "E000013", "base_revision": "git:0123456789abcdef",
    "current_revision": "git:fedcba9876543210", "decision": "continue",
    "reason": "The coefficient ansatz is unresolved; the recurrence remains untried.",
    "next_question": "Derive the recurrence once computation access is restored.",
    "conflicts": []
  }
}
```

Copy actual existing IDs/revisions. The program's original base can differ from
a later execution's base; only the cited runs and reconciliation must match.
A run result has no base fields and inherits them through its `run`.

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
