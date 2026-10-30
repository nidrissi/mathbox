# Model attribution

Attribute immutable authored artifacts: route records, proofs, source records,
audit and referee reports, closeouts, saved handoffs, and agent-authored JSON
such as assessments, contracts and hand-filled manifests. Put
`**Model ID:** <exact ID>` near the top of Markdown or
`"model_id": "<exact ID>"` in JSON; use `unknown` or `null`, respectively, when
the ID is unavailable. Where a skill's output contract names an existing field
for this, use it instead of adding `model_id`. For `.tex`, `.bib`, `.txt` and
other formats, put attribution in an accompanying Markdown or JSON record.

Copy the ID only from execution metadata the host exposes in the producing
agent's own context, such as an environment line naming the exact model. A
requested model, display nickname, presumed default or the agent's unsupported
belief about itself is not execution evidence. Do not add a collector, hook or
dependency to discover identity.

Live files that are rewritten or appended to carry no Model ID: status
dashboards, claim, literature, convention and verification registries,
charters, history and route indexes, and agent instruction files. The immutable
records they link to carry the attribution.

`**Model ID:**` always names the author of the content it heads. Each delegated
contributor attributes what it wrote; a synthesis records its own author. A
section added to an existing proof or record is headed by its own author's
Model ID, and existing attribution stays as it is.
Verbatim reused or extracted text keeps its original ID, or `unknown` when it
had none. An agent that only extracts or collects such text records itself as
`**Extracted by:** <exact ID>`, never as that content's Model ID. Never backfill
or relabel historical artifacts or imported source material.

Ordinary manuscript edits and chat replies need no field. Deterministic helper
output (runner manifests and logs, inspector, cache and snapshot output, ledger
check and handoff output) keeps its software provenance; attribute the
accompanying assessment instead. Ledger events, proposals and fixed transport
envelopes keep their existing schemas; put attribution inside the authored
artifact content they carry.
