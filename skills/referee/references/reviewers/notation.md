# Notation and consistency lane

Read the [shared protocol](../review-protocol.md) and the whole manuscript. Consistency relates at
least two occurrences; a section-only suspicion does not establish it.

- `hypothesis-mismatch`: statement/proof text disagree about assumptions, or
  an unused restriction needs explanation; deciding a missing hypothesis is
  mathematically necessary requires correctness and `proof-audit`;
- `convention-drift`: grading, sign, normalization, indexing or variance
  changes silently;
- `overloaded-symbol`: two live meanings create consequential ambiguity,
  such as object/class or functor/derived functor;
- `broken-reference`: a label/by-name target is absent or not what is claimed;
- `unresolved-placeholder`: a constant, map or comparison is invoked without
  being fixed, or receives incompatible definitions;
- `undefined-symbol`: global search finds no introduction of an object or
  convention that actually needs one;
- `circular-dependency`: justification of one result depends on another that
  ultimately needs the first; trace establishment, not just statement order.

Quote both occurrences verbatim with both locators for a drift or mismatch.
For absence claims quote the use and record where you searched, checking
preamble macros, global conventions, earlier sections and appendices. Do not
report a section pass's missing definition when the full source supplies it.
For broken references identify use and target. A missing `.bib` or extracted
bibliography key alone does not establish a broken citation or its contents.

Group all instances of one convention or symbol. Equivalent notation you
would spell differently is not a defect. Consequential mathematical ambiguity
may require a correctness escalation; stylistic consistency normally leaves
the theorem intact and is at most major. Do not audit grammar or prior art.

Do not run specialist skills unless the coordinator explicitly assigns them.
