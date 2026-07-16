---
name: proofread-math
description: Proofreads mathematical writing and LaTeX conservatively for grammar, typography, syntax, notation consistency, cross-references, and locally verifiable mathematical typos. Use as final quality assurance after drafting or materially editing theorem-, proof-, or equation-heavy LaTeX—including self-review of changed .tex files or diffs—and for explicit math-proofreading requests. It does not invent proofs or make substantive mathematical revisions.
---

# Mathematical LaTeX proofreading

Proofread; do not re-author. Make the smallest high-confidence corrections that preserve the mathematics, notation, authorial voice, and repository conventions.

## Scope and mode

1. Follow any explicit scope or output mode from the caller.
2. When invoked inside a broader writing or editing task, complete the requested draft first, then apply this workflow to the draft. Do not use the skill to invent the mathematics.
3. For repository files, edit the source in place. When self-reviewing recent work, review the changed hunks and enough surrounding context to resolve notation, references, and prose; do not rewrite unrelated text.
4. For pasted LaTeX, return corrected LaTeX unless the caller requests review only.
5. For review-only requests, report findings without changing the source.
6. If the material is too large for a complete pass, finish the requested or changed scope first and state exactly what was reviewed. Do not claim full-document coverage.

Before editing, inspect relevant project instructions, nearby definitions and theorem statements, macro definitions, labels, and neighboring prose when they are needed to judge the text.

## Workflow

1. **Establish local conventions.** Identify the language variant, notation, custom macros, theorem style, equation punctuation, and formatting conventions already in use.
2. **Review prose.** Check grammar, spelling, punctuation, agreement, articles, referents, sentence structure, and transitions between prose and displays.
3. **Review LaTeX.** Check structural syntax, environments, delimiters, math mode, alignment, labels, references, citations, and locally defined commands.
4. **Review mathematical consistency.** Check notation and locally verifiable typographical consistency without attempting a referee-level proof verification.
5. **Apply minimal edits.** Do not replace correct wording merely with a stylistic preference, normalize unrelated formatting, or rename notation.
6. **Verify the result.** Re-read every changed sentence or display with its immediate context. Undo any change that introduces ambiguity or changes mathematical meaning.
7. **Validate when practical.** Use an existing repository compile, lint, or test command when it is documented, available, relevant, and proportionate. Do not install packages, change dependencies, or invent a build procedure. Distinguish new failures from pre-existing ones.
8. If validation finds a problem caused by the edits, fix it and rerun the relevant check. Report anything that remains unresolved.
9. Stop after a clean verification pass; avoid repeated stylistic churn.

## What to check

### Prose and typography

- spelling, grammar, punctuation, capitalization, hyphenation, and duplicated or omitted words;
- subject–verb agreement, articles, prepositions, pronoun antecedents, and parallel structure;
- equation punctuation and grammatical integration of displayed mathematics;
- consistent terminology and formal mathematical tone;
- awkward phrasing only when a local, meaning-preserving improvement is clear.

Preserve the author's English variant and established terminology. Do not flatten an individual style into generic prose.

### LaTeX and document consistency

- balanced braces and delimiters;
- matching `\begin{...}` and `\end{...}` pairs;
- valid use of math mode, alignment markers, line breaks, and delimiter sizing;
- resolvable `\label`, `\ref`, `\eqref`, and `\cite` keys when the surrounding project makes them available;
- duplicate labels, incorrect equation references, and inconsistent theorem or equation names;
- custom commands and package-specific syntax in light of the preamble or local definitions.

Preserve custom macros, labels, citation keys, environment choices, and line layout unless a definite error requires a change. Do not convert between equivalent LaTeX forms merely for preference. If unfamiliar syntax cannot be resolved from the project, leave it unchanged and report the uncertainty only when it appears problematic.

### Local mathematical consistency

Check, within the available context:

- symbols, indices, primes, decorations, subscripts, and superscripts;
- operators, relations, signs, constants, coefficients, and parentheses;
- quantified variables, index ranges, hypotheses, domains and codomains;
- dimensions, degrees, arities, and other type-like constraints;
- consistency between theorem statements, proofs, definitions, and cited equations;
- whether prose accurately describes the adjacent formula.

## Mathematical edit policy

Treat any change to an operator, relation, sign, coefficient, variable, index, exponent, subscript, superscript, quantifier, hypothesis, conclusion, domain, codomain, or proof step as a **mathematical-token change**.

Make a mathematical-token change only when all of the following hold:

1. the intended correction is uniquely forced by the immediate context;
2. the error is isolated and typographical rather than logical;
3. the correction does not require a new argument or alter downstream reasoning.

List every mathematical-token change explicitly in the final report. Never silently repair one.

When any condition fails, leave the source unchanged and report an unresolved issue with a precise location and explanation. In particular:

- a repeated pattern alone does not justify adding a missing subscript or superscript;
- a plausible alternative identity does not justify changing a sign or operator;
- an unbound or inconsistent symbol may indicate a missing definition rather than a typo;
- a gap in a proof is not a copyediting problem.

Do not add hypotheses, alter theorem statements, fill proof gaps, rewrite arguments, strengthen or weaken claims, or resolve mathematical ambiguity by guessing.

## Reviewer notes

Report unresolved mathematical issues outside the manuscript by default. Do not insert Markdown blockquotes, bold reviewer notes, or package-dependent commands into LaTeX source.

If the caller explicitly requests inline annotations, add a compiler-safe comment immediately above the relevant line:

```latex
% REVIEWER NOTE: [precise issue and what must be verified]
```

Do not use `\todo`, `\textbf`, or another rendered annotation unless the project already defines and requests it.

## Output

### Repository or file-edit mode

Edit the requested source, then report:

```text
Proofread: [file or scope]
- Routine edits: [brief categories, or "none"]
- Mathematical-token changes: [location and exact change, or "none"]
- Unresolved issues: [location and issue, or "none"]
- Validation: [command and result, or "not run" with reason]
- Coverage: [include only when less than the full requested scope was reviewed]
```

Do not paste the entire edited file unless requested. Do not enumerate every comma or spelling correction; summarize routine edits by category.

### Pasted-text mode

Return the corrected source first in one fenced `latex` block. Follow it with:

- a brief summary of routine edits;
- every mathematical-token change, with the original and replacement;
- unresolved issues, each tied to a quoted fragment, equation label, or supplied line number;
- validation performed, if any.

### Review-only mode

List findings in this order:

1. likely mathematical or meaning-changing issues;
2. LaTeX errors;
3. language and typography issues.

For each finding, give a precise location, the problem, and a minimally invasive suggested correction. Do not rewrite the full source unless requested.

If no objective issue remains, say so and make no changes.
