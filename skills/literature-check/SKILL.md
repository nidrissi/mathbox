---
name: literature-check
description: >-
  Verify what an external mathematical source proves: exact theorem, hypotheses and version, citation, notation translation, source-dependent implication, attribution, or a bounded novelty claim; cache authenticated sources for reuse. Use when a proof relies on a named result, the user asks whether a claim is known, or to cache a source. Do not use to audit internal proof logic, attack an implication, format bibliographies, or insert citations into a manuscript.
---

# Mathematical literature check

Verify the exact implication, not merely related terminology. Prefer primary
sources; snippets and failed searches establish neither proof nor global novelty.

## Define the source question

For a cache-only request, go directly to acquisition and stop after reporting
cache provenance. A theorem or project claim is optional for this task.

State the project claim or arrow, likely result, acceptable source class, exact
version and required hypotheses: coefficients, grading, variance, finiteness,
actions, normalization, completion and range. Identify theorem verification,
attribution, notation translation, overlap classification or bounded novelty
as the task. Read existing literature records and dependent arguments first.

## Acquire and authenticate

1. Query an authorized project-local cache by stable identifier before fetching;
   read [source-cache.md](references/source-cache.md) before **any cache command**.
   A different or unversioned arXiv copy is only a discovery candidate.
2. Prefer the published paper, official preprint, author manuscript or other
   primary source. Abstracts, reviews, snippets and citation chains are discovery
   aids unless they themselves are the cited result.
3. Record title, authors, identifier, exact version/revision, stable locator and
   date checked. For a theorem check, verify numbering and hypotheses in the
   project's version.
4. Respect confidentiality and copyright. Quote only the needed statement;
   never copy fetched or cached full text into tracked files, reports or deferred
   packets, or upload licensed/private material without authorization.

When the user or project authorizes local retention, add acquired sources at a
natural checkpoint for reuse. Cache hits save acquisition work; they do not
verify mathematical content or authenticate metadata. Retain an established
alternate cache rather than creating a duplicate.

For cache-only work, report the operation and its outcome, identifier/version,
source locator, retention basis, cache location, retained SHA-256, extraction
status and any warnings or conflicts, as available. Distinguish cache metadata
from observed files and check actual bytes before claiming verified retention.
Mark missing or mismatched artifacts explicitly. Say which identity and
integrity checks were performed. Mark theorem verification as unperformed and
stop before assigning an application verdict, assessing novelty or recording
source evidence.

## Extract and translate

Extract the exact theorem, definition or formula and its hypotheses and exceptions.
State whether the source proves, sketches, states, conjectures or motivates it.
Write a notation dictionary to project conventions and check the application
one arrow at a time. A citation supplies no unstated functor, equivalence,
coherence datum or limiting argument. Objectwise, natural, equivariant, filtered,
integral and completed statements are different contracts until a bridge is proved.

Separate **source authentication**, **theorem extraction** and **project
application**; record which checks actually occurred. Label the implication:

- **verified**: the exact source result and translation establish the arrow;
- **conditional**: state the assumed premise or bridge and check the deduction
  from it to the project claim;
- **inapplicable**: a checked mismatch prevents the proposed application;
- **unverified**: available evidence does not settle it.

When the exact passage is unavailable, mark attribution of the claimed result
to the source **unverified**, even if the paper's identity is authenticated.
A supplied paraphrase may serve as an explicit assumption for a separately
checked conditional deduction. If that deduction also lacks a step, leave it
unverified and identify the gap.
Use [source-record.md](references/source-record.md) for the durable source record.

## Novelty and overlap

Separate discovery from verification. Search the exact statement, synonyms,
older vocabulary, equivalent formulations, object/invariant names and neighboring
fields. Follow backward references and available forward citations, relevant
authors' earlier work and adjacent bibliographies. Use multiple suitable indices
when feasible and disclose unavailable coverage.

Read strongest candidates in primary versions and compare exact hypotheses and
conclusions. For a material “apparently new” claim, use a second strategy or
fresh reviewer when available; disclose a same-searcher second pass.

If a strong candidate's exact hypotheses or conclusion cannot be compared,
report **overlap undetermined** for the unresolved comparison. Identify the
candidate, the missing passage or translation and what would settle it.
Retain any overlap established from other sources. Withhold an apparently-new
verdict while a material candidate remains unresolved.

For a completed comparison or bounded search, use only these overlap labels:

- known verbatim;
- known after translation of notation;
- formal corollary not stated;
- new proof of a known statement;
- partial or adjacent result only;
- apparently new within the stated search scope;
- conjectural or explicitly open in a checked source.

For “apparently new,” report databases, exact/synonym queries, date horizon,
languages/fields, citation chains, second-pass method and blind spots. A failed
search is never a global novelty theorem. Append later-discovered overlap as a
correction and propagate it; preserve the earlier scoped search.

For priority questions, specify what qualifies as a proof of the exact result.
Give the locator, version and date of the earliest qualifying proof located
within the reported search scope, or say none was verified. Distinguish
announcement, public preprint and publication dates. Report first publication
or historical priority only to the extent independently supported by the
chronology and coverage.
Identify earlier unresolved leads that limit either conclusion.

## Record and report

Before saving a durable record, proof, report or authored JSON, follow
[attribution.md](references/attribution.md).

Update literature records only when authorized and the check changes a dependency
or attribution; update status/history only for changed live research state.
Preserve old checks when versions or interpretations change and inspect dependents.

When persistence is authorized in a `.mathbox/` project, use the available
`research-state` skill.
Record or propose `source` evidence only for the claim the inspected text
establishes under its checked hypotheses and translation. Pin the source
record. Put a checked conditional deduction and its outstanding premise in
the assessment. When reviewing existing application evidence, attach any
`conditional` review to that exact evidence revision.
If no inspected text establishes a relevant claim, omit `source` evidence
entirely, including from deferred proposals. On a non-writing host, use the
deferred packet contract when its prerequisites are met and there is a valid
ledger proposal. Otherwise return the assessment with any justified proposal
and state what remains unsaved.

Report exact source/version, retained hash and extraction status, result used,
notation/hypothesis translation, **checks performed** (authentication, extraction,
application), implication verdict, overlap/search scope and unresolved ambiguity.
