---
name: literature-check
description: >-
  Verify what an external mathematical source proves: exact theorem, hypotheses and version, citation, notation translation, source-dependent implication, attribution, or a bounded novelty claim; cache authenticated sources for reuse. Use when a proof relies on a named result, the user asks whether a claim is known, or to cache a source. Do not use to audit internal proof logic, attack an implication, format bibliographies, or insert citations into a manuscript.
---

# Mathematical literature check

Verify the exact implication, not merely related terminology. Prefer primary
sources; snippets and failed searches establish neither proof nor global novelty.

## Define the source question

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
   date checked. Verify theorem numbering and hypotheses in the project's version.
4. Respect confidentiality and copyright. Quote only the needed statement;
   never copy fetched or cached full text into tracked files, reports or deferred
   packets, or upload licensed/private material without authorization.

When the user or project authorizes local retention, add acquired sources at a
natural checkpoint for reuse. Cache hits save acquisition work; they do not
verify mathematical content or authenticate metadata. Retain an established
alternate cache rather than creating a duplicate.

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
- **conditional**: name the missing hypothesis or bridge;
- **inapplicable**: a checked mismatch prevents the proposed application;
- **unverified**: available evidence does not settle it.

An authenticated paper may be inapplicable. Unavailable exact text is unverified,
or conditional when the required assumption can be named, rather than confirmed.
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

Use only these overlap labels:

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

## Record and report

Update literature records only when authorized and the check changes a dependency
or attribution; update status/history only for changed live research state.
Preserve old checks when versions or interpretations change and inspect dependents.

When persistence is authorized in a `.mathbox/` project, record `source` evidence
only for an implication verified here through the available `research-state`
skill (`mathbox:research-state` in plugin installations), pinning the source
record. For a conditional application, record the checked conditional implication
and a `conditional` review naming its missing bridge; never record positive
support for an unverified application. The cache hash alone supplies no such
verification. If research-state is unavailable, report proposed source evidence
fields and say nothing was recorded. On an authorized non-writing host, use its
deferred packet contract and say it is unapplied.

Report exact source/version, retained hash and extraction status, result used,
notation/hypothesis translation, **checks performed** (authentication, extraction,
application), implication verdict, overlap/search scope and unresolved ambiguity.
