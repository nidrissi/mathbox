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
- Apply the user's existing authorization to coherent setup/retrofit changes;
  do not ask again for routine edits already in scope. Preserve substantive
  existing material and show a reviewable diff. Resolve genuine ambiguity before
  replacing an authoritative proof, convention, or historical record.
- Do not invent commands, proof status, conventions, repository paths, or
  permissions.
- Preserve unrelated work. Do not commit, push, install dependencies, upload
  content, or contact third parties without authorization.
- Keep stable rules in instructions, recurring procedures in `mathbox` plugin
  skills, mutable facts in research records, and deterministic enforcement in
  code.

## Phase 1 — inspect read-only

1. Determine repository root and inspect `git status --short`. Distinguish a
   clean Git worktree from unavailable Git metadata; do not report both as an
   empty status.
2. Locate root/nested `AGENTS.md`, Claude memory/rules, current skill folders,
   and any unrecognized `skills/` folders. If root `CLAUDE.md` exists alongside
   `AGENTS.md`, check whether it imports `@AGENTS.md`. A missing `CLAUDE.md` is
   expected when Claude Code loads `AGENTS.md` directly.
3. Locate likely charter, status, claims, conventions, proof/manuscript,
   literature, log, computation, tests, CI, and build artifacts. Recognize
   semantic aliases and variants, including `PLAN`, `STATUS`, `OUTLINE`,
   `MANIFEST`, theorem/fact inventories and dated or qualified `HANDOFF` files;
   names are candidates, not authority decisions. Inventory computation
   manifests separately from build manifests. Detect project-declared path maps
   and source-cache locations, and recognizable alternate cache conventions,
   without reading cached source content or proposing a second cache by default.
   Treat theorem/fact inventory entries derived from literature as candidate
   assertions until their exact source records are checked; schedule that
   verification before dependent proof or manuscript work treats them as facts.
4. Classify `RESEARCH_LOG.md`, when present, as a compact linked index,
   long-form legacy history, or a mixture. Locate any separate research-record
   directory and check whether the log links to it.
   Detect `.mathbox/config.json` without replaying all history during inventory.
5. Detect duplicate `mathbox` plugin skill names and paths hard-coded relative
   to a skill installation. Report multiple dashboard or handoff candidates for
   authority review. Conservatively check relative Markdown links and
   path-shaped backtick references; distinguish certain broken links from
   tentative path candidates and ignore code fences, URLs and shell examples.
6. Run the bundled read-only inspector when available:

```bash
python3 <mathbox-research-init-directory>/scripts/inspect_repo.py --root <repo>
```

Locate the installed `mathbox:research-init` plugin skill directory (or its
standalone installation); do not substitute a guessed relative path.

Produce a fact sheet with observed facts, tentative inferences, conflicts, and
missing information. Preserve confidence distinctions: a filename, directory
name or path-shaped code span is not proof of its semantic role.

Initialization may inventory literature records and cache policy, but it does
not establish what cited mathematics proves. Do not perform substantive source
lookups during setup; record them as follow-up work for the available
`literature-check` skill (`mathbox:literature-check` in plugin installations).
If the user also requested those source checks, execute them as a subsequent
work package within the same assignment. The setup boundary does not authorize
leaving an explicitly requested verification task unfinished.

## Phase 2 — interview adaptively

Use [interview.md](references/interview.md). Resolve only material ambiguity:
research goal, current deliverable, evidence thresholds, source authority,
fragile conventions, edit boundaries, verification, confidentiality/network,
Git policy, and definition of done.

If a manuscript or submission is the current deliverable, also resolve its
venue/template, language, audience, deadline and timezone, page-count rule and
page budget. The budget must account explicitly for front matter, bibliography,
figures/tables and contingency. Never infer these constraints from a filename,
an old draft, a generic venue norm or an approximate current page count.

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
   tracked ignore rule, or should retain a safely identified project-declared
   alternate cache rather than creating a duplicate.
10. for a manuscript deliverable, the confirmed submission constraints and a
   complete page budget, with every unresolved item left explicitly unknown.
11. source-dependent inventory entries that remain unverified, and a literature-
    check work package ordered before any dependent claim is promoted or used.

When this explicitly requested setup, retrofit, or refresh finds route-level
prose in `RESEARCH_LOG.md`, the proposed plan must include the legacy migration
below. Trigger on the log's structure, not its line count. Detection does not
authorize the rewrite.

## Legacy research-log migration

Make the mapping and file plan reviewable. An ordinary research attempt or
retrospective does not trigger migration. Before creating the compact index,
present a source-span-to-destination mapping to the user or designated project
owner and obtain its review. Broad retrofit authorization permits preparation
of the mapping and files, but it does not substitute for review of route
relevance or ambiguous provenance.

1. Compare each prospective entry with the repository's explicit mission,
   current target and scope. Classify it as mission-relevant, foreign, or
   ambiguous, citing the text that supports the classification. Do not infer
   relevance from a filename, topic keyword or apparent mathematical quality.
2. Map every recognizable mission-relevant route-level entry to a standalone
   record under the project-designated directory, or `research/records/` by
   default. Preserve its substantive text and chronological order; do not
   strengthen its evidence label or status.
3. Preserve foreign and ambiguous material under a project-designated
   quarantine, or `research/quarantine/legacy/` by default, with its original
   provenance and the reason it was not classified as live project history.
   Quarantine is preservation, not a mathematical verdict. Do not link this
   material from the live research index unless a reviewed mapping later
   classifies it as mission-relevant.
4. Use an entry's recorded date when available. Otherwise infer the earliest
   date from Git history that contains the entry and mark `Date provenance:
   inferred from Git history`. If Git cannot supply a date, use the migration
   date and mark that the original date was unavailable.
5. Put unmatched preamble or unstructured historical material in quarantine as
   a dated `legacy-context` record rather than discarding it. Classify it as
   mission-relevant only after review.
6. For mapping review, show source boundaries, original/inferred date, proposed
   filename, relevance class, evidence label carried forward, and any unresolved
   provenance or authority question. Revise the mapping in response to review.
7. Only after that mapping is reviewed, build a compact `RESEARCH_LOG.md` index
   with one chronological linked line per approved mission-relevant record.
   Verify that every substantive part of the old log is represented either in
   an indexed record or in quarantine before replacing its body.
8. After migration, treat records and index entries as immutable. Append a new
   correction record and index entry instead of rewriting history.

## Phase 4 — write the approved project layer

Use the assets selectively; delete unused sections and replace every
placeholder. A normal setup has:

- concise root `AGENTS.md`;
- optional `CLAUDE.md` importing `@AGENTS.md` for sessions that cannot load
  `AGENTS.md` directly or need genuine Claude-specific additions;
- at most one live dashboard;
- optional claims, conventions, literature, a compact append-only research
  index, and immutable standalone route records;
- when local source retention is authorized, a documented
  `.research-cache/literature/` convention and tracked Git ignore rule;
- nested instructions only for genuinely local invariants;
- documented verification commands and benchmark cases.

Do not duplicate mutable state in persistent instructions.

For a project whose claim dependencies and evidence frequently change, consider
the available `research-state` skill and its optional `.mathbox/` ledger. Use its
conservative migration workflow: import exact claims and checked artifacts,
preserve existing IDs and records, and designate a single live generated view.
Do not initialize it for a small project that does not benefit. The ledger
checks bookkeeping; it neither certifies mathematics nor replaces proof files.

For sustained multi-route work, make `research-program` discoverable as the
coordinator of successive attempts, without copying its workflow into AGENTS.

## Skill-layer rule

The default output is **no project skills**: use the installed `mathbox` plugin
for its canonical research workflows.

Never synthesize local copies of the `mathbox` plugin components
`research-attempt`, `proof-audit`, `literature-check`, `computation-audit`,
`manuscript-integrate`, `proofread-math`, `research-retrospective`, or
`research-init`, `research-program`, or `research-state`.
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
7. Review every reported dashboard/handoff candidate and broken relative path;
   do not silently choose authority or rewrite a tentative backtick candidate.
8. Confirm that any literature cache is excluded from inspection and ignored
   by a tracked project rule rather than only by the cache's own internal
   rule; do not open its source content during repository initialization.
9. Run the cheapest verified project check when authorized.
10. Inspect `git diff --check` and the full diff.
11. Tell the user how to verify loaded instructions and skills in a fresh session.

Do not commit unless explicitly authorized.

## Final report

Report files changed, hierarchy rationale, rules moved and destinations,
validation, unresolved questions/commands, `mathbox` plugin availability, any
archived duplicate skills, and one recommended namespaced plugin invocation.

Use [output-contract.md](references/output-contract.md) as the acceptance
checklist.
