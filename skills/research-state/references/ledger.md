# Ledger format and commands

The journal is `.mathbox/events/000001.json`, etc., with schema version 1 in
`.mathbox/config.json`. Keep it in project version control. Events form a hash
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
python3 "$TOOL" --root /path/to/project --json status
python3 "$TOOL" --root /path/to/project impact C_MAIN
python3 "$TOOL" --root /path/to/project next --goal C_MAIN
python3 "$TOOL" --root /path/to/project handoff --goal C_MAIN
python3 "$TOOL" --root /path/to/project check
```

`record` prints the event including its assigned `E000001` identifier. Proposals
contain exactly `type`, `actor`, and `payload`. Generated timestamps, hashes and
revision snapshots belong to the helper. Exit codes: 0 success; 1 stale evidence
from `check`; 2 invalid input, unsupported version, integrity or I/O error.
Open conjectures are valid state and do not make `check` fail.

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
    "dependencies": []
  }
}
```

Repeating a claim ID creates a revision and requires a nonempty `reason`. Restate
the complete contract; old hypotheses are not implicitly inherited. Add separate
claim IDs for distinct restrictions, equivalent formulations requiring a bridge,
or unresolved proof obligations. Every dependency must already be registered.
Cycles are rejected, including cycles introduced by revisions.

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
`conditional` unless another unqualified counterexample supports refutation.
Conflicting proof evidence still yields `disputed`.

Retract an erroneous evidence or review event with:

```json
{"type":"retract","actor":"researcher","payload":{"target":"E000002","reason":"The witness does not satisfy the connectedness hypothesis."}}
```

Changes in a claim's transitive revision snapshot or artifact bytes make evidence
stale. Dependency evidence being retracted or refuted instead makes downstream
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

A `route` payload has `id`, `claim`, `mechanism`, `question`, `discriminator`,
`success`, `failure`, `prerequisites` (claim IDs), and integer `gain`/`cost` in
1..5. These estimates support prioritization, not evidence promotion. Prerequisites
mean results needed *before* executing the route; do not list the target as its
own prerequisite. `next` scores `(gain + number of selected downstream claims)
/ cost`, lists ready routes first and includes blockers for others. It does not
invent new routes, claim semantic diversity or assign success probabilities.

A `route-result` payload has `route`, `outcome` (`succeeded`, `failed`, `blocked`,
`inconclusive`), `reason`, and `next_question`. A route can close only once.
Correction/reopening is a new route ID with `reopens` equal to the result's
event ID and a `changed_input` explanation. An exact repeated target/mechanism
without this explanation is rejected. Semantic duplicates still need human or
agent judgment. Route success does not itself create proof evidence.

`handoff` includes open candidates in `routes` and completed history in
`closed_routes`, filtered to the goal and its transitive dependencies when a
goal is supplied. Each closed route includes its payload and `event_id`, plus
a nested `result` with the outcome, reason/obstruction, next question and result
`event_id` needed for `reopens`. Markdown handoffs also show these continuation
details. `next` continues to list only open candidates.
