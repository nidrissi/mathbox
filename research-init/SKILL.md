---
name: research-init
description: Initialize, retrofit, or refresh an AI-assisted mathematical research repository. Use only when the user explicitly asks to set up or redesign repository instructions, research records, verification workflows, or agent skills. Inspect the repository read-only, interview the researcher about mathematical and operational choices that cannot be inferred, propose a minimal scaffold, and obtain approval before writing files.
disable-model-invocation: true
argument-hint: "[new|retrofit|refresh] [optional project goal]"
---

# Research repository initialization

Build a small, auditable operating system for AI-assisted mathematical research.
Do not generate a generic wall of instructions. Infer what the repository already
knows, interview for decisions that require mathematical judgment, and keep
always-loaded guidance short.

## Invocation and operating modes

- Claude Code: `/research-init`
- Codex: mention `$research-init` explicitly or choose it from `/skills`.
- `$ARGUMENTS` may name a mode (`new`, `retrofit`, or `refresh`) and a preliminary
  research goal. Treat it as a hint, not as permission to overwrite files.

Modes:

1. **new** — an empty or nearly empty research repository;
2. **retrofit** — a repository with mathematical material but no coherent agent
   architecture;
3. **refresh** — an existing `AGENTS.md`/`CLAUDE.md` setup that has drifted,
   bloated, or become contradictory.

Research profiles:

- **proof-first** — theorem development, counterexamples, sign/convention work;
- **manuscript** — a paper or monograph is the near-term deliverable;
- **computation** — Sage/Python/Julia/Magma/Mathematica or other experimental work;
- **formalization** — Lean/Coq/Agda/Isabelle or proof-assistant development;
- **mixed** — several profiles with an explicit primary one.

## Non-negotiable principles

1. **Inspect before asking.** Do not ask for information already available in the
   repository, its Git history, current instructions, or standard configuration.
2. **Interview before writing.** Mathematical scope, theorem hierarchy,
   conventions, evidence thresholds, and autonomy boundaries require the
   researcher's judgment.
3. **Propose before mutating.** Present the proposed files, authority order, and
   important policy choices. Obtain approval before creating or editing them.
4. **Never overwrite silently.** Preserve existing material, show a diff or
   migration map, and archive superseded instructions only with approval.
5. **Separate stable rules from evolving state.** A status or handoff file reports
   progress; it never overrides agent instructions, the project charter,
   protected paths, or durable proofs.
6. **Put procedures in skills.** Multi-step literature reviews, proof audits,
   computation runs, and manuscript integration are loaded on demand rather than
   copied into every `AGENTS.md`.
7. **Use deterministic enforcement for deterministic rules.** Formatting,
   generated-file checks, protected paths, and forbidden commands belong in
   tests, hooks, CI, permissions, or wrapper scripts when practical.
8. **Do not equate computation with proof.** Record provenance and the exact
   assertion tested.
9. **Do not install dependencies, enable network access, commit, push, publish,
   or contact anyone without explicit authorization.**
10. **Do not make the current deliverable depend on an optional open theorem.**
    Record a theorem hierarchy and acceptable fallback outputs.

## Phase 0 — read-only repository probe

Before the interview:

1. Locate the Git root and read all applicable agent instructions.
2. Run `git status --short` when Git is available.
3. Inspect top-level files, relevant subdirectories, lockfiles, CI, build tools,
   tests, manuscript sources, proof files, computational scripts, and existing
   status/log/handoff documents.
4. Inspect recent Git history only when it clarifies conventions or active work.
5. Detect current instruction mechanisms:
   - `AGENTS.md`, `AGENTS.override.md`, or fallback names;
   - `CLAUDE.md`, `CLAUDE.local.md`, and `.claude/rules/`;
   - `.agents/skills/`, `.claude/skills/`, hooks, permissions, and CI gates;
   - other agent files whose useful content may need consolidation.
6. Run `scripts/repo_probe.py` from this skill when Python 3.9+ is available:

   ```bash
   python /path/to/research-init/scripts/repo_probe.py --root . --format markdown
   ```

7. Classify every discovered instruction as one of:
   - durable repository rule;
   - mathematical charter/convention;
   - evolving status;
   - repeatable procedure;
   - deterministic check;
   - historical note;
   - stale, contradictory, or unverifiable claim.

Do not edit anything in this phase.

## Phase 1 — infer facts and prepare the interview

Create an internal fact table with three columns:

- **observed** — directly supported by repository evidence;
- **inferred** — plausible, with the evidence and uncertainty stated;
- **unknown/decision required** — cannot be settled without the researcher.

Read `references/project-profiles.md` and choose the likely primary profile. Use
`references/interview.md` to ask only unresolved questions. Ask in coherent
batches, not as a long questionnaire. Usually two to four batches are enough.

Challenge vague answers constructively. In particular, turn:

- “solve the problem” into a theorem hierarchy and decision gates;
- “check the literature” into source classes, date/version requirements, and a
  novelty-claim policy;
- “verify computations” into commands, resource caps, and mathematical
  acceptance tests;
- “ask before changing math” into an explicit autonomy matrix;
- “keep a log” into a route-level definition of a substantive attempt.

## Phase 2 — minimum interview coverage

Do not scaffold until the following are known or explicitly marked undecided:

1. precise research question and intended contribution;
2. near-term reviewable deliverable and time horizon;
3. strong target, intermediate target, and acceptable fallback;
4. hypotheses, coefficients, grading, signs, variance, naming, and other stable
   conventions that can invalidate a proof or computation;
5. established results, open gaps, failed routes, and authoritative evidence;
6. in-scope and out-of-scope work;
7. canonical proof/manuscript/code paths and protected or historical material;
8. environment, setup, fast/targeted/full/document checks, and resource limits;
9. claim-status and literature-verification standards;
10. agent autonomy for semantic edits, dependencies, network, Git actions,
    external communication, and destructive commands;
11. logging cadence, generated-output policy, and definition of done;
12. whether parallel agents or worktrees will be used.

Profile-specific questions are in `references/interview.md`.

## Phase 3 — propose the scaffold

Present a concise proposal before writing. Include:

- selected mode and profile;
- proposed authority order;
- files to create, retain, split, move, or retire;
- content that will remain always loaded;
- procedures that will become skills;
- deterministic rules that should become scripts/hooks/CI;
- unresolved choices and the defaults you propose;
- a migration table mapping old sections to new destinations;
- expected `AGENTS.md` line and byte count.

Default architecture:

```text
AGENTS.md                         short, stable repository-wide core
CLAUDE.md                         imports @AGENTS.md; Claude-only additions
PROJECT_CHARTER.md                stable mathematical scope and conventions
RESEARCH_STATUS.md                concise current dashboard
RESEARCH_LOG.md                   append-only route-level history
VERIFICATION.md                   commands and mathematical acceptance tests
LITERATURE_LEDGER.md              only when external results are central
.agents/skills/<procedure>/       on-demand procedures for Codex
.claude/skills/<procedure>/       symlink/copy when needed for Claude Code
<subtree>/AGENTS.md               only for genuinely local rules
hooks / CI / wrapper commands     deterministic enforcement
```

Create fewer files when the project does not need all of these. A small theorem
note may need only `AGENTS.md`, `PROJECT_CHARTER.md`, and `RESEARCH_STATUS.md`.

Default size targets:

- root `AGENTS.md`: about 60–140 lines; investigate anything over 180;
- `CLAUDE.md`: normally the import plus a few Claude-specific lines;
- each skill: one procedure with explicit inputs, outputs, stop conditions, and
  verification;
- no duplicated lint/style rule already enforced by tooling.

Wait for approval before Phase 4. Approval of the scaffold is not authorization
to commit or push it.

## Phase 4 — implement conservatively

After approval:

1. Copy and fill only the useful templates from `assets/`.
2. Preserve existing prose that carries real project knowledge; relocate it with
   attribution rather than paraphrasing away mathematical nuance.
3. Create `CLAUDE.md` with `@AGENTS.md` unless an existing Claude-specific design
   has a clear reason not to.
4. Put path-specific architecture or invariants in the nearest applicable nested
   `AGENTS.md`, not the root file.
5. Put task procedures in project skills. Prefer a shared skill source with a
   symlink where the local platform supports it; otherwise document the copy and
   synchronization policy.
6. For sign-heavy projects, offer `CONVENTION_REGISTRY.md`. For claim-supporting
   computations, offer the experiment-manifest schema and example. Do not create
   either for projects that will not maintain them.
7. Replace long command lists with a checked-in wrapper, Make target, or task
   runner only when the repository already supports such a tool or the user
   approves adding one.
8. Add hooks or CI only after confirming the repository's trust, portability,
   and contributor requirements. Never add an auto-download or networked hook.
9. Do not invent successful test commands, publication status, literature
   coverage, licenses, or Git trailers.
10. Leave placeholders visible if the user intentionally deferred a decision;
   mark them `UNRESOLVED`, not with plausible fabricated content.

## Phase 5 — validate and report

Run:

```bash
python /path/to/research-init/scripts/validate_scaffold.py --root .
```

Then perform these checks manually:

- applicable instruction chain is unambiguous;
- `CLAUDE.md` imports the intended core;
- no mutable status document can override operational rules;
- no contradictory stop/continue rules remain;
- every referenced file and command exists or is explicitly marked unresolved;
- proof, computation, and literature statuses are not conflated;
- protected paths and Git/network policies are explicit;
- the root file contains project-specific knowledge, not generic coding advice;
- procedures and lint details have not leaked back into always-loaded context;
- existing user changes remain intact.

Report:

1. repository observations and profile;
2. files created/changed and files deliberately left alone;
3. old-to-new migration map;
4. validation commands and results;
5. unresolved choices and risks;
6. exact invocation/install instructions for both Codex and Claude Code;
7. recommendation for a small set of realistic probe tasks to test the guidance.

Do not claim the setup is finished until the user has reviewed the mathematical
charter and the semantic-change/autonomy policy.

## Refresh cycle

A repository instruction system is an empirical artifact, not a constitution.
After several real tasks:

1. collect repeated corrections, ignored rules, false triggers, and unnecessary
   context;
2. run three to eight representative probe tasks, including at least one task
   that should *not* activate each skill;
3. move deterministic failures into tooling;
4. remove generic, obsolete, duplicated, or never-used text;
5. add only repository-specific facts whose absence caused an observed error;
6. repeat after major architectural or research-goal changes.

Never optimize solely for shorter files. Optimize for correct task selection,
correct mathematics, reproducible evidence, and low maintenance burden.
