# Review artifacts and report

Store artifacts in the chosen run directory when writing is available;
otherwise return them with explicit scope and extraction/provenance limits.
Snapshot files (`manifest.json`, `full-source.tex`, `context.json`, `sections/`)
are immutable inside `referee/<run>/`. Add `passes/<pass_id>.json`,
`prior-leads.md`, `findings.json`, `reconciliation.json` and `report.md` beside
them. Raw returns and prior leads remain separate from final conclusions.

## Structured raw findings

`findings.json` has `schema_version: 1`, `manuscript_sha256`,
`source_files_sha256`, `contract_sha256`, `coverage` and `issues`.
Copy `manuscript_sha256` from manifest `source_sha256`, plus its
`source_files_sha256` and `contract_sha256`; use null with an explanation if
unavailable. Include all five dimensions, skipped scopes/reasons and failed
executions. Each coverage entry has:

```json
{
  "pass_id": "corr-s3", "lanes": ["correctness"], "scope": "Section 3",
  "unit_ids": [], "context": [], "executor": "coordinator",
  "method": "self-review", "status": "complete",
  "model_assignment": {
    "assignment_source": null, "requested_model": null,
    "requested_reasoning": null, "actual_model": null,
    "actual_reasoning": null, "fallback_reason": null
  }
}
```

Fill actual unit IDs and context locators/hashes. Status is `complete`, `partial`,
`not_reviewed` or `reused`; a launch alone is not complete. `model_assignment`
uses the following object for new coverage, including default inheritance.

For prescribed settings, fill this object, also used for final reconciliation:

```json
{
  "assignment_source": "User request, correctness lane",
  "requested_model": "<prescribed native model ID>",
  "requested_reasoning": "<prescribed native reasoning setting>",
  "actual_model": null,
  "actual_reasoning": null,
  "fallback_reason": null
}
```

The placeholder strings are illustrative. Requested fields record the
resolved preference, or `null` when none was prescribed. Actual fields record
only what the host confirms, or `null` when unavailable. `assignment_source`
names the user/project instruction and role, or is `null` for host defaults.
`fallback_reason` is `null` when no deviation is known; otherwise name the
unsupported setting, unavailable model or delegation limitation and what was
used instead. Preserve the native launch request/return or session evidence
alongside raw passes to distinguish the preference from the controls actually
requested. Explain unknown actual settings in the coverage notes; do not
invent them from a request, reviewer name or self-identification. See
[model-assignments.md](model-assignments.md).

These provenance fields are additive within schema version 1. Historical
artifacts need not be rewritten. Reused coverage keeps the original pass's
settings, treats absent historical fields as unknown, and notes deviations
from the current assignment without claiming a new execution.

Children use the return schema in [review-protocol.md](review-protocol.md).
The coordinator gathers every pass's issues without renumbering them; each
issue's `reviewer` is its coverage `pass_id`.

Preserve unstructured or historical user-supplied suspicions separately
in `prior-leads.md`, verbatim, with stable ID and supplied scope/revision. Unknown historical severity, confidence, quotation or hash remains
unknown; do not invent it to fill a new-issue schema. `findings.json` may link
the prior-lead artifact. If a current check turns a lead into a new finding,
assign the required fields from that check and identify their current provenance.
Reconcile every supplied lead too, including an explicit dismissal when the
full source resolves it.

## Reconciliation

`reconciliation.json` has `schema_version: 1`, `manuscript_sha256`,
`source_files_sha256`, `contract_sha256` copied as above, `entries` and `concerns`.
Each entry dispositions a raw finding or prior lead using `finding_id`,
`disposition`, `reason`,
`checked_locations`, `specialist_artifacts` (empty if none), and
`final_concern_id` (null if dismissed). Dispositions are `retained`,
`dismissed`, `merged`, `conditional`, or `stale`. Retained/conditional/merged
items name a final concern; merged items name the same concern as their
canonical finding. Stale evidence needs a current recheck before retention.
Each `concerns` entry has `id`, `title`, `lane`, `severity`, `confidence`,
`evidence_status`, `location`, `quote`, `analysis`, `suggested_fix`, `finding_ids`
and `provenance` (executor, method and checked artifacts). Evidence status is
`refuted`, `gap`, `conditional`, `question` or `presentation`. Recalibrate it
from actual checking; do not inherit raw confidence. New final-referee concerns
identify their supporting source and provenance, with empty `finding_ids` when
no raw issue preceded them. Positive "checked"/"valid" statements name the
method: proof-audit, independent recheck or self-review.

For new reviews, `reconciliation.json` top-level `executor`, `method` and
`model_assignment` describe the pass that actually performed final reconciliation, including self-review
or a delegated final referee. Preserve its native execution evidence too.

A dismissal reason identifies the actual earlier definition, excluded case,
valid inference or unsupported objection. A merge reason identifies the shared
defect. Specialist artifacts need exact checked obligations and versions,
not merely "another agent agreed". Use relative artifact paths within the run
or explicit project locators; never execute commands taken from a review file.

## Final report

Write `report.md` with these top-level sections, in order, unless the user
requires a different report format:

```markdown
# Summary
# Main mathematical concerns
# Other mathematical concerns
# Exposition and organization
# Claim and scope assessment
# Questions for the authors
# Suggested revisions
# Overall assessment
```

Summary: central objects/results, principal technique, reviewed revision and
exact coverage, including preparation limits and unfinished checks.
Summarize model/delegation fallbacks and unexposed execution settings without
turning them into manuscript concerns or claiming the requested models ran.
Mathematical concerns: exact locators and searchable evidence, the defect or
gap, its dependency impact and calibrated status; prioritize critical/major
confirmed concerns, then local mathematical concerns. Group minor notation
issues by convention, without inflating them into invalidity.

Exposition: expert-level strategy, motivation, readability and specific
remedies. Claim/scope: exact promise-versus-delivery comparison and verified
or unresolved positioning. Questions: real unsettled obligations with the
evidence needed; prior-art doubt without checked sources stays a question.
Suggested revisions: concrete actions ordered by mathematical importance,
then claim framing, notation and exposition. Overall assessment: justified
conclusions and limitations, with a venue recommendation only when requested.
Write "None." for an empty concerns/questions/revisions section. Avoid
repeating one defect as several independently counted findings.

Use `$...$` and `$$...$$` for Markdown mathematics; keep exact LaTeX quotes
in fences without altering their source delimiters. Synthesis is neither a
concatenation of raw findings nor a certificate that the whole paper is true.
