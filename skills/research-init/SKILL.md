---
name: research-init
description: >-
  Set up, plan a retrofit of, substantially revise, or migrate an AI-assisted mathematical research repository's agent architecture: AGENTS.md, CLAUDE.md, live status/history, workflow files and their authority structure, including moving a flat research log into program indexes. Use only on an explicit request. Do not use for an ordinary research attempt, closing out one named program or phase, or a read-only project retrospective.
---

# Mathematical research repository initializer

Configure a durable project layer; use installed Mathbox workflows rather than
regenerating them locally. Keep stable rules in instructions, recurring procedures
in skills, mutable facts in records and deterministic enforcement in code.

## Non-negotiable behavior

- Run only on explicit request. A migration plan is read-only.
- Inspect before asking for safely discoverable facts; ask at most five material
  questions together.
- Present a reviewable file plan before writing unless immediate execution is
  already authorized. Do not re-request authority for routine work in scope.
- Even when authorized, obtain review of a legacy-history mapping and any
  authority-ambiguous replacement before applying it. Preserve substantive
  existing material and unrelated work; expose conflicts and a reviewable diff.
- Never invent commands, status, conventions, paths or permissions. Do not
  commit, push, install dependencies, upload or contact others without authority.

## Phase 1 — inspect read-only

Determine root and inspect Git state; unavailable metadata is different from a
clean worktree. Run the installed [inspect_repo.py](scripts/inspect_repo.py) first:

```bash
python3 <skill-directory>/scripts/inspect_repo.py --root PROJECT
```

Resolve this skill's actual location rather than guessing a project path.
Use `--full` for full Markdown inventory or `--format json` for complete data.
Inspect omitted current-path findings before authority/edit decisions; historical
link overflow alone need not be loaded. Do not read cached source content.

The inspector finds instructions, role aliases, declared paths, cache conventions,
manifest/log classifications, skills, broken references and dashboard/handoff
candidates. Supply judgments it cannot make:

- designate actual authority among candidates and verify entry-point links to
  relevant closeouts, route indexes and records;
- distinguish stable rules from mutable status and source-derived candidate
  assertions from checked facts;
- resolve certain broken links versus tentative path-shaped references;
- identify whether flat linked history needs sharding or legacy/mixed prose
  needs lossless extraction;
- check root `CLAUDE.md` imports `@AGENTS.md` when both exist.

Sizes, filenames and dated-marker counts are review prompts, not verdicts about
mathematical status or permission to remove history. Produce a fact sheet of
observations, tentative inferences, conflicts and missing information.

Inventory source policies only; substantive checks belong to the available
`literature-check` skill (`mathbox:literature-check` in plugin installations),
or exact-source checking if unavailable. If also requested, execute those checks
as subsequent work packages; setup does not leave authorized verification undone.

## Phase 2 — interview adaptively

Read [interview.md](references/interview.md), including manuscript constraints
when applicable. Resolve material goal/deliverable, evidence thresholds, authority,
conventions, edit boundaries, checks, confidentiality, Git and definition of done.
Distinguish theorem goal from near-term output, proof from finite evidence,
chain-level from derived claims, and personal preferences from shared policy.
Never infer submission constraints or page budgets from filenames or venue norms.

## Phase 3 — propose before writing

Present facts/conflicts and exact files to create, modify, move, archive or retain;
source-of-truth hierarchy; rules retained/moved/automated; protected paths and
approval boundaries; verified fast/targeted/full/manuscript checks; migration
risks; and the [skill-layer decision](references/skill-layer.md).

Include cache retention/ignore policy, retaining a safely identified alternate
cache rather than creating a duplicate. Identify unverified source-derived
inventories and the verification package required before promotion. For a
manuscript deliverable give confirmed constraints and a complete page budget
with unknowns explicit. Existing live-file migrations need a source/destination
crosswalk, pin baseline and unresolved authority conflicts before replacement.

## Existing-file and history migration

Follow [existing-repo-migration.md](references/existing-repo-migration.md) for all
baseline, crosswalk, pin-aware editing and history migration mechanics. Route by
inspector class: `long-form-legacy`/`mixed` needs reviewed extraction;
`compact-linked-index` may need reviewed sharding if the flat index is too large;
`unstructured` needs manual inventory before classification. Detection alone
never authorizes rewriting. A plan-only request ends at the reviewable plan.
A plugin upgrade alone does not authorize a project migration or hash refresh.

Use available `research-state` (`mathbox:research-state` in plugin installations)
for optional ledger adoption or evidence revisions; if unavailable preserve
prose records and report the limitation. Never import confident prose as proof.

## Phase 4 — write the authorized project layer

Read [output-contract.md](references/output-contract.md) **before writing**.
Use assets selectively, delete unused sections and replace scaffolding values:

| Asset | Default destination |
|---|---|
| [AGENTS.template.md](assets/AGENTS.template.md) | `AGENTS.md` |
| [CLAUDE.template.md](assets/CLAUDE.template.md) | optional `CLAUDE.md` |
| [PROJECT_CHARTER.template.md](assets/PROJECT_CHARTER.template.md) | `PROJECT_CHARTER.md` |
| [RESEARCH_STATUS.template.md](assets/RESEARCH_STATUS.template.md) | one of `RESEARCH_STATUS.md` / `HANDOFF.md` |
| [PROOF_OBLIGATIONS.template.md](assets/PROOF_OBLIGATIONS.template.md) | `PROOF_OBLIGATIONS.md` / `CLAIMS.md` |
| [CONVENTIONS.template.md](assets/CONVENTIONS.template.md) | `CONVENTION_REGISTRY.md` / `CONVENTIONS.md` |
| [LITERATURE.template.md](assets/LITERATURE.template.md) | `LITERATURE_LEDGER.md` / `LITERATURE.md` |
| [RESEARCH_LOG.template.md](assets/RESEARCH_LOG.template.md) | `RESEARCH_LOG.md` |
| [VERIFICATION.template.md](assets/VERIFICATION.template.md) | `VERIFICATION.md` |

Explicit project-designated paths override these defaults. Exactly one designated
live dashboard states current evidence, blocker and next action. Record mission,
deliverable, success, fallback and exclusions in the charter, or an `AGENTS.md`
*Mission* section when there is no charter. Other root instructions contain
stable local rules, authority/edit boundaries, checks and pointers rather than
mutable facts. `CLAUDE.md` is optional when sessions load `AGENTS.md` directly;
otherwise it imports that file and holds only genuine host additions.

Use optional claims, conventions and literature records as needed. Define
**history entry point**, **route index** and **route record** as navigation,
compact outcome links and immutable standalone route detail respectively. A
small project can combine entry point/index; sustained programs link through
program/phase indexes. Keep exactly one live view and search growing history
instead of imposing full loads. Preserve checkpoint material and active pins
before replacing live narratives; migration reference gives these rules.

Authorized retention needs a documented cache convention and tracked ignore
rule. Nested instructions serve only genuinely local invariants. Verification
commands and mathematical benchmarks must be concrete and discovered/supplied.

For frequently changing dependencies consider optional ledger adoption, with
one generated live view and only checked artifacts. It does not certify proofs.
For sustained work make `research-program` discoverable without copying its
workflow into root instructions.

## Skill-layer rule

Default to **no project skills**. Never synthesize local copies of canonical
Mathbox skills or write skills under root `skills/`. The inspector's `CANONICAL`
set defines the catalog; read the skill-layer reference for approved project
skills and exact versioned vendoring when the host cannot load plugins.

## Phase 5 — validate and report

Remove placeholders outside intentional fenced format examples; verify paths
exist or are explicitly planned and commands were discovered/supplied. Check
authority, evidence/review/freshness, Git/network and edit boundaries for conflicts.
Review all live-view candidates and broken paths without silently choosing
an authority. Keep instructions limited to stable rules and pointers; detailed
procedures and repeated mutable facts signal excess load.

Confirm no duplicated canonical or root skills, and caches are excluded from
inspection and ignored by a tracked project rule. Run the cheapest verified
project check when authorized, then inspect the full diff and `git diff --check`.
For migrations compare the complete crosswalk, pins, issues, claims, protected
rules and links with baseline; distinguish old issues from introduced ones.

Report files/hierarchy, moved rules and destinations, checks and skipped reasons,
remaining conflicts/commands, plugin availability and archived skills. Give one
recommended invocation and how to verify instruction/skill loading in a fresh
session. Migration reports also identify preserved history and freshness issues.
