# Program closeout and compact current state

Use at a material program or phase boundary, or for an explicit compaction
request. A closeout may leave the mathematical goal open. Do not create one
merely because a session ended, and do not start new research on a closeout-only
request. The result is a checked synthesis and a smaller default handoff, not
a replacement for proofs, audits, computations, route records, or ledger events.

## Establish the exact base

Read the project authority and edit rules, current goal contract, and current
summary. Search the designated history entry point for the program, then open
its route index and only the records needed for decisive or conflicting
outcomes. With a ledger, use a brief goal handoff and freshness check; inspect
full contracts, active review reports, and artifacts for every status used in
the synthesis. Record the base Git revision or ledger head and the relevant
pre-existing issue IDs. Do not infer proof from a generated label.

## Write one durable closeout

Place the closeout in the project-designated records area. Give it a stable
program/phase identifier and link the exact authoritative artifacts. Use the
[small closeout template](../assets/program-closeout.template.md) when it helps;
remove empty fields rather than filling them with speculation. State:

- original target and whether it was reached, partially advanced, refuted, or
  remains open, with exact hypotheses, range and evidence/review conditions;
- the strongest surviving results and claim IDs, each linked to its proof,
  source check, or bounded computation rather than reprinting them;
- decisive closed mechanisms and their first failed implication, plus the new
  mathematical input required to reopen any of them;
- unresolved dependencies, active route, cheapest discriminating next action,
  and any conflicting review or stale evidence;
- base revision/ledger head, relevant verification scope, and links to the
  route index or records that support the synthesis.

Do not add a claim/evidence/review ledger event solely for a closeout. Record
one only when the mathematical state actually changed, under `research-state`
rules. A closeout can be a checkpoint rather than a terminal verdict.

## Keep navigation and current state small

Keep exactly one designated live dashboard. Replace superseded checkpoint
narratives with a concise current result, exact blocker, active route, review
conditions, and next decision; link the closeout for prior work. A program
summary is historical synthesis, not a second live claims dashboard. Do not
copy a route table, full ledger projection, or verification transcript into
the live file.

For sustained programs, the default history entry point should list programs
or phases, not every route. Each entry links a closeout and a route-level
index; the latter links immutable route records with one-line outcomes. A
program still in progress may have an "opened" entry linking its route index;
append a separate closeout entry when a phase ends rather than rewriting that
historical entry. The live dashboard, not the history index, says which route
is currently active. A small project may retain a flat index. If a program
index itself becomes long, partition it by phase or interval and keep a short
navigational entry point.
Index entries are append-only within their designated file; corrections link
new records. Do not silently relocate old entries during ordinary closeout.
For an existing flat index, use the reviewed `research-init` migration rather
than pretending its history disappeared. If that skill is unavailable, keep the
flat index intact and report the migration as pending.

Set an advisory project-specific size or repeated-checkpoint trigger for the
live view and top-level index. Exceeding it prompts review, not automatic
truncation or deletion. Agents should load the current summary and targeted
index entries, never every historical program by default.

## Validate the contraction

Before replacing old live prose, map each substantive span to the current
view, a linked closeout/route record, or an explicitly retained unresolved
archive. Reconcile exact claim wording, evidence and review conditions,
unresolved questions, and affected pins. Check links and compare relevant
ledger issue IDs with the base; do not repair staleness by refreshing hashes.
Run the project's risk-appropriate checks and inspect the full diff. Report
what remains open and any history that is only archived pending classification.
If a contradiction or protected file cannot be resolved under current
authorization, leave that part unchanged and report the decision needed.
