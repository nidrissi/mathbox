---
name: literature-check
description: >-
  Verify an external mathematical theorem, citation, notation translation, source-dependent implication, or bounded novelty claim, reusing authorized project-local source copies when available. Use when a proof relies on a named paper/result, when exact hypotheses or versions matter, when the user asks whether a claim is known, or when an authenticated mathematical source should be cached for later checks. Prefer primary sources and record the search scope. Do not treat snippets or failed searches as proof or global novelty.
---

# Mathematical literature check

Verify the exact implication, not merely the presence of related terminology.

## Define the source question

State:

- the project claim or arrow requiring support;
- likely source/result and acceptable source class;
- required coefficients, grading, variance, finiteness, equivariance,
  normalization, version, and range;
- whether the task is theorem verification, attribution, notation translation,
  overlap classification, or bounded novelty search.

Read an existing literature-ledger entry and the dependent proof before
searching when they exist.

## Acquire and authenticate

1. When the project permits local source retention, query its literature cache
   by exact DOI, arXiv version, ISBN, or other stable identifier before fetching.
   A different or unversioned arXiv copy is only a discovery candidate.
2. Prefer the published paper, official preprint, author manuscript, formal
   documentation, or another primary source.
3. Record title, authors, publication/preprint identifier, exact version or
   revision date, stable locator, and date checked.
4. Use abstracts, reviews, search snippets, lecture notes, and citation chains
   only as discovery aids unless they are themselves the result being cited.
5. For a changing preprint, verify that theorem numbering and hypotheses belong
   to the version actually used by the project.
6. Respect confidentiality and copyright; do not upload or reproduce licensed
   or private material without authorization.

After acquiring an authorized source, add it to the cache at a natural
checkpoint so later agents can reuse both the PDF and any extracted text. Read
[source-cache.md](references/source-cache.md) before initializing or modifying
the cache. Cache hits save acquisition work; they do not authenticate the
source or verify its mathematical content.

## Extract and translate

Record the exact theorem, definition, or formula used, including all hypotheses,
exceptions, coefficient restrictions, source/target categories, variance,
actions, grading, and completion assumptions. Note whether the source proves,
sketches, states, conjectures, or only motivates it.

Write an explicit notation dictionary to the project conventions. Verify the
project implication one arrow at a time. A citation supplies no unstated
functor, equivalence, coherence datum, normalization, or limiting argument.

Use [source-record.md](references/source-record.md) for durable entries.

## Novelty and overlap

Classify only as:

- known verbatim;
- known after translation of notation;
- formal corollary not stated;
- new proof of a known statement;
- partial or adjacent result only;
- apparently new within the stated search scope;
- conjectural or explicitly open in a checked source.

For “apparently new,” report databases, queries, date range, languages or fields
searched, citation chains followed, and important blind spots. A failed search
is never a global novelty theorem.

## Record and report

Update the project's literature ledger only when authorized and when the check
changes a dependency or attribution. Update status/log only if live research
state changes.

Report:

1. exact source and version, plus the cache content hash and extraction
   status when the source was retained locally;
2. exact result used;
3. notation/hypothesis translation;
4. whether the implication is valid;
5. overlap/novelty classification and search boundary;
6. unresolved source ambiguity or missing implication.

Return **unverified** or **conditional** when the exact source is unavailable,
the translation fails, or the needed implication is neither stated nor formal.
