---
name: research-init
description: >-
  Initialize, retrofit, or refresh an AI-assisted mathematical research repository. Use only when the user explicitly asks to set up or substantially revise AGENTS.md, CLAUDE.md, research workflow files, or the repository's agent architecture. Inspect first, interview adaptively, propose a reviewed file plan, and default to no repository-local skills because canonical workflows come from the mathbox plugin.
---

# Mathematical research repository initializer

Configure the repository as a durable research environment. Do not regenerate
skills supplied by the `mathbox` plugin inside it.

## Non-negotiable behavior

- Run only after an explicit request.
- Inspect before asking questions; do not ask for facts safely available in the
  repository.
- Ask at most five material questions at a time.
- Present a proposed file/migration plan before writing unless the user already
  authorized immediate execution.
- Never overwrite an existing instruction, proof, status, log, convention,
  configuration, or build file without explicit approval of the exact change.
- Do not invent commands, proof status, conventions, repository paths, or
  permissions.
- Preserve unrelated work. Do not commit, push, install dependencies, upload
  content, or contact third parties without authorization.
- Keep stable rules in instructions, recurring procedures in `mathbox` plugin
  skills, mutable facts in research records, and deterministic enforcement in
  code.

## Phase 1 — inspect read-only

1. Determine repository root and inspect `git status --short`.
2. Locate root/nested `AGENTS.md`, Claude memory/rules, current skill folders,
   and any unrecognized `skills/` folders.
3. Locate likely charter, status, claims, conventions, proof/manuscript,
   literature, log, computation, tests, CI, and build artifacts. Detect a
   `.research-cache/` convention without reading cached source content.
4. Detect duplicate `mathbox` plugin skill names and paths hard-coded relative
   to a skill installation.
5. Run the bundled read-only inspector when available:

```bash
python3 <mathbox-research-init-directory>/scripts/inspect_repo.py --root <repo>
```

Locate the installed `mathbox:research-init` plugin skill directory (or its
standalone installation); do not substitute a guessed relative path.

Produce a fact sheet with observed facts, tentative inferences, conflicts, and
missing information.

Initialization may inventory literature records and cache policy, but it does
not establish what cited mathematics proves. Do not perform substantive source
lookups during setup; record them as follow-up work for the available
`literature-check` skill (`mathbox:literature-check` in plugin installations).

## Phase 2 — interview adaptively

Use [interview.md](references/interview.md). Resolve only material ambiguity:
research goal, current deliverable, evidence thresholds, source authority,
fragile conventions, edit boundaries, verification, confidentiality/network,
Git policy, and definition of done.

Distinguish theorem goal from near-term output, proof from computation,
chain-level from derived/homology/topological claims, stable rules from mutable
status, and personal preferences from team-shared policy.

## Phase 3 — propose before writing

Present:

1. repository facts and unresolved questions;
2. proposed instruction hierarchy and source-of-truth order;
3. exact files to create, modify, move, archive, or leave untouched;
4. rules to retain, shorten, move, automate, or remove;
5. protected paths and approval boundaries;
6. verified fast, targeted, full, and manuscript checks;
7. migration risks and stale/conflicting instructions;
8. skill-layer decision from [skill-layer.md](references/skill-layer.md).
9. whether authorized literature retention needs a project-local cache and a
   tracked `/.research-cache/` ignore rule.

## Phase 4 — write the approved project layer

Use the assets selectively; delete unused sections and replace every
placeholder. A normal setup has:

- concise root `AGENTS.md`;
- `CLAUDE.md` importing `@AGENTS.md` plus genuine Claude-specific additions;
- at most one live dashboard;
- optional claims, conventions, literature, and append-only route records;
- when local source retention is authorized, a documented
  `.research-cache/literature/` convention and tracked Git ignore rule;
- nested instructions only for genuinely local invariants;
- documented verification commands and benchmark cases.

Do not duplicate mutable state in persistent instructions.

## Skill-layer rule

The default output is **no project skills**: use the installed `mathbox` plugin
for its canonical research workflows.

Never synthesize local copies of the `mathbox` plugin components
`research-attempt`, `proof-audit`, `literature-check`, `computation-audit`,
`manuscript-integrate`, `proofread-math`, `research-retrospective`, or
`research-init`.
Never write a skill to a root `skills/` directory.

A repository skill is allowed only after explicit approval and only if its
procedure is genuinely project-specific, recurring, distinct from the canonical
catalog, and given a project-qualified name. Project facts, file paths,
mathematical hazards, and benchmark examples belong in project files instead.
If remote/team portability requires common workflows, install and pin the
`mathbox` plugin. If that host cannot load plugins, vendor exact versioned
component skills rather than rewriting them.

## Phase 5 — validate

1. Remove every placeholder.
2. Confirm each referenced path exists or is explicitly planned.
3. Confirm every command was discovered or supplied.
4. Check authority, evidence labels, Git/network rules, and edit boundaries for
   contradictions.
5. Confirm that no `mathbox` plugin skill was duplicated locally and no skill
   was put under `skills/`.
6. Check instruction size and static links/paths.
7. Confirm that any literature cache is excluded from inspection and ignored
   by a tracked project rule rather than only by the cache's own internal
   rule; do not open its source content during repository initialization.
8. Run the cheapest verified project check when authorized.
9. Inspect `git diff --check` and the full diff.
10. Tell the user how to verify loaded instructions and skills in a fresh session.

Do not commit unless explicitly authorized.

## Final report

Report files changed, hierarchy rationale, rules moved and destinations,
validation, unresolved questions/commands, `mathbox` plugin availability, any
archived duplicate skills, and one recommended namespaced plugin invocation.

Use [output-contract.md](references/output-contract.md) as the acceptance
checklist.
