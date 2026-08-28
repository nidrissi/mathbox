---
name: proofread-math
description: >-
  Conservatively proofread mathematical prose and LaTeX for grammar, typography, syntax, notation consistency, cross-references, and uniquely forced local mathematical typos. Use for explicit math-proofreading requests and final self-review of theorem-, proof-, or equation-heavy edits. Do not invent, replace, shorten, or substantively repair proofs.
---

# Conservative mathematical proofreading

Proofread; do not re-author. Preserve the mathematics, notation, macros,
authorial voice, language variant, and project conventions.

## Select the mode

- **Edit mode:** the caller explicitly asks to correct a file or pasted text.
- **Review-only mode:** the caller asks for findings, comments, or a check
  without edits.
- **Self-review mode:** invoked after a broader edit; inspect only the changed
  hunks and enough context to resolve notation, references, and prose. Correct
  routine issues only in files already changed by the task.

Do not default from review-only to editing. For pasted LaTeX in edit mode,
return corrected LaTeX. For repository files, do not rewrite unrelated text.
If coverage is partial, state the exact scope reviewed.

## Workflow

1. Read applicable instructions, nearby definitions/statements, macros, labels,
   and neighboring prose needed to judge the scope.
2. Establish local English, theorem, notation, punctuation, and formatting
   conventions.
3. Review prose and display integration.
4. Review LaTeX structure, environments, delimiters, labels, references,
   citations, and custom commands.
5. Review local mathematical consistency without attempting a referee-level
   proof audit.
6. Apply only minimal, high-confidence edits; do not normalize equivalent LaTeX
   or replace correct wording by preference.
7. Re-read every changed sentence/display in context.
8. Run documented, proportionate validation when available; never invent a
   build or install dependencies.

The detailed checklist is in [checklist.md](references/checklist.md).

## Mathematical-token policy

A change to an operator, relation, sign, coefficient, variable, index, exponent,
subscript, superscript, quantifier, hypothesis, conclusion, domain, codomain, or
proof step is a **mathematical-token change**.

Make one only when the intended correction is uniquely forced by immediate
context, isolated and typographical, and does not require a new argument or
alter downstream reasoning. List every such change explicitly.

Otherwise leave the source unchanged and report the issue. A repeated pattern
alone does not justify changing a sign or index. An unbound symbol may signal a
missing definition. A proof gap is not a proofreading error; escalate it to
`proof-audit` when the caller wants investigation.

## Reviewer notes

Report unresolved issues outside the manuscript by default. Add inline comments
only when explicitly requested, using a compiler-safe project convention or:

```latex
% REVIEWER NOTE: [precise issue and what must be verified]
```

Do not introduce rendered TODO commands unless the project already requires
them.

## Output

For edited repository files, report:

```text
Proofread: [file or scope]
- Routine edits: [categories or none]
- Mathematical-token changes: [location and exact change or none]
- Unresolved issues: [location and issue or none]
- Validation: [command/result or not run with reason]
- Coverage: [only when partial]
```

For pasted text, return corrected source first, then the same categories. For
review-only mode, order findings by mathematical/meaning-changing risk, LaTeX
errors, then language/typography. If no objective issue remains, say so and make
no change.
