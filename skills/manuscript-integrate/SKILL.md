---
name: manuscript-integrate
description: >-
  Integrate an already validated mathematical result, correction, citation, or response to referee comments into an authoritative LaTeX manuscript while preserving hypotheses, evidence status, notation, and dependencies. Use only when the user explicitly requests manuscript integration. Do not use to invent a proof or to perform routine copyediting.
---

# Manuscript integration

Transfer validated mathematics into the live manuscript. Integration does not
supply mathematical validation or human review.

## Preconditions

1. Determine repository root, inspect the worktree, and read applicable
   instructions.
2. Resolve the authoritative manuscript, proof source, current status/claims,
   conventions, literature record, bibliography, and verification commands.
3. Identify the exact validated result and its evidence/review status.
   If `.mathbox/` is present, use the available `research-state` workflow to
   check the current claim revision, artifact freshness and dependency closure.
   Read the proof itself; a generated `proved` label does not validate it.
4. To integrate a result as established, require current durable evidence for
   its exact statement and scope: proved, externally proved, or computationally
   verified within the stated range, with no active failed review. A label alone
   is insufficient. Block promotion of stale, heuristic, unvalidated or gappy
   input. Route correctness questions through the available `proof-audit` skill
   and new arguments through the available `research-attempt` skill. If the
   relevant skill is unavailable, return the exact obligation. Do not repair
   proofs here. Block an item when conflicting sources leave its validated
   statement or revision unresolved. When the validated revision is clear,
   correct authorized downstream records that disagree with it. Stop if the
   authoritative manuscript is ambiguous.
5. Route unchecked external inputs through the available `literature-check` skill,
   or check the exact source directly if unavailable. When a premise remains
   unverified, integrate a conditional statement only on explicit request and
   only if current durable evidence establishes the exact conclusion assuming
   that premise. Read and link that evidence, state the premise explicitly and
   mark the result conditional. For any blocked item, report the missing
   obligation, preserve the existing status of the item and its dependents,
   and continue authorized edits with independent support.
6. Validated citation changes, corrections and removals need support for the
   change, not positive proof evidence for a claim no longer asserted.

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
- project maps, theorem inventories, source guides, status files and verification
  benchmarks whose meaning depends on the changed scope;
- validation plan and human-review obligation.

## Edit

- Change the smallest coherent manuscript region.
- Keep hypotheses adjacent to the claim and preserve every limitation.
- Preserve project evidence labels: proved, externally proved, computationally
  verified in a stated range, conditional, heuristic and conjectural.
- Do not make a publishable theorem depend accidentally on an optional stronger
  conjecture or unfinished route.
- Preserve historical source files; correct the live manuscript and record the
  correction rather than rewriting chronology.
- Update notation, theorem names/numbers, references, citations, introduction,
  comparison, and outlook only where the result requires it.
- If a protected dependent cannot be changed, mark the exact conflict and do
  not report propagation complete.
- Do not edit generated output or bibliography entries without checking the
  project's source convention.

Use [integration-checklist.md](references/integration-checklist.md) for
load-bearing theorem changes.

## Synchronize durable state

Before saving a durable record, proof, report or authored JSON, follow
[attribution.md](references/attribution.md).

When integration changes a claim's statement, scope or status and the project
keeps research records, update only the durable artifacts made stale by the
change. Link the existing validated proof revision when its content still
supports the integrated statement. Bring affected claims/status entries up to
date and record the change once in a standalone record with a compact linked
route-index entry. Reuse current records and index entries that already capture
the change. Use designated paths, or `research/records/` and `RESEARCH_LOG.md`
when records already exist. Do not put route details in the index, rewrite
indexed history, or log routine prose or formatting. Keep any specialist or
human-review obligation open until it has actually occurred.

## Verify

1. Use the available `proofread-math` skill over changed TeX and context,
   or apply conservative proofreading directly if unavailable.
2. Run the targeted mathematical verifier when documented; otherwise report not run.
3. Run the documented manuscript build; otherwise report not run.
4. Inspect undefined references/citations, warnings in the changed region,
   theorem numbering, bibliography changes, and `git diff --check`.
5. Search for the superseded statement, scope and terminology across declared
   dependents; classify each remaining occurrence as current, historical or
   stale.
6. Review the final diff for unintended semantic or generated-file changes.

## Report

Report the integrated result, files changed, source evidence, claim/status
changes, commands and warnings, unresolved mathematical or manuscript risk, and
remaining human review. A clean build or proofreading pass does not validate
mathematical correctness.
