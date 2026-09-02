---
name: manuscript-integrate
description: >-
  Integrate an already validated mathematical result, correction, citation, or referee response into an authoritative LaTeX manuscript while preserving hypotheses, evidence status, notation, and dependencies. Use only when the user explicitly requests manuscript integration. Do not use to invent a proof or to perform routine copyediting.
---

# Manuscript integration

Transfer validated mathematics into the live manuscript. Integration does not
supply mathematical validation or human review.

## Preconditions

1. Determine repository root, inspect the worktree, and read applicable
   instructions.
2. Resolve the authoritative manuscript, proof source, current status/claims,
   conventions, literature ledger, bibliography, and verification commands.
3. Identify the exact validated result and its evidence/review status.
4. Stop if the source proof conflicts with current status, the required external
   theorem has not been checked, or the target manuscript is ambiguous.

## Build the integration map

State:

- source theorem/lemma/correction and durable location;
- target section and theorem hierarchy;
- exact hypotheses, coefficient regime, grading, signs, variance, range, and
  exceptions;
- notation translation;
- external dependencies and citations;
- downstream statements, introduction claims, examples, and cross-references
  affected;
- validation plan and human-review obligation.

## Edit

- Change the smallest coherent manuscript region.
- Keep hypotheses adjacent to the claim and preserve every limitation.
- Distinguish internal proof, external input, computation, heuristic, and open
  question.
- Do not make a publishable theorem depend accidentally on an optional stronger
  conjecture or unfinished route.
- Preserve historical source files; correct the live manuscript and record the
  correction rather than rewriting chronology.
- Update notation, theorem names/numbers, references, citations, introduction,
  comparison, and outlook only where the result requires it.
- Do not edit generated output or bibliography entries without checking the
  project's source convention.

Use [integration-checklist.md](references/integration-checklist.md) for
load-bearing theorem changes.

## Synchronize durable state

When the mathematical state changes, update the durable proof, claims/status,
and one substantive research-log entry together. Do not log routine prose or
formatting. Keep any specialist or human-review obligation open until it has
actually occurred.

## Verify

1. Perform a conservative pass with the `mathbox:proofread-math` plugin skill
   over the changed TeX and needed context.
2. Run the documented targeted mathematical verifier.
3. Run the appropriate out-of-tree or canonical manuscript build.
4. Inspect undefined references/citations, warnings in the changed region,
   theorem numbering, bibliography changes, and `git diff --check`.
5. Review the final diff for unintended semantic or generated-file changes.

## Report

Report the integrated result, files changed, source evidence, claim/status
changes, commands and warnings, unresolved mathematical or manuscript risk, and
remaining human review.
