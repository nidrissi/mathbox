# Scaffold selection policy

Use the smallest architecture that preserves mathematical truth, reproducibility,
and safe autonomy.

## Always consider

### `AGENTS.md`

Use for stable, operational, repository-specific facts needed on most tasks:
mission, authority order, semantic-change policy, canonical checks, protected
paths, and completion contract.

Do not use for evolving theorem status, long tutorials, complete API references,
linter rules, or multi-stage procedures.

### `CLAUDE.md`

Normally import `@AGENTS.md` and add only Claude-specific behavior. Avoid a second
copy of the same instructions.

### `PROJECT_CHARTER.md`

Use when the mathematical scope, theorem hierarchy, hypotheses, conventions, or
decision gates are nontrivial and expected to remain stable over multiple tasks.

### `RESEARCH_STATUS.md`

Use for the concise current dashboard. It must never be an authority over agent
rules or proofs.

## Add when justified

### `RESEARCH_LOG.md`

Add for open-ended research with meaningful failed routes or corrections. Log at
route-level checkpoints, not after every command.

### `VERIFICATION.md`

Add when checks have risk tiers, computations support claims, or mathematical
acceptance tests differ from ordinary CI.

### `LITERATURE_LEDGER.md`

Add when exact external theorems, notation translation, or novelty assessment is
central. Do not create it merely to store a bibliography.

### `PROOF_OBLIGATIONS.md`

Add when a theorem has enough dependencies that status prose hides the actual
weakest arrows. Keep stable claim IDs and evidence pointers; do not duplicate the
proof.

### `CONVENTION_REGISTRY.md`

Add for sign-, grading-, orientation-, variance-, or canonicalization-heavy
projects where a convention change invalidates several proofs or computations.
Use a readable versioned source, not only a hash.

### Experiment manifest schema

Add for computation-heavy projects whose outputs support claims or must be
reproduced across machines. Store a JSON manifest beside each significant run;
do not require it for disposable exploratory commands.

### Nested `AGENTS.md`

Add only when a subtree has local invariants, environment, or protected files
that do not apply elsewhere. A nested file should mostly contain differences from
the root, not restate it.

### Skill

Add for a repeatable multi-step procedure with a recognizable trigger, explicit
inputs/outputs, and more detail than should be loaded on every task. Examples:
proof audit, literature theorem check, computation provenance run, manuscript
integration, release/publish workflow.

### Hook/CI/wrapper

Add for deterministic enforcement: formatting, file generation, protected paths,
forbidden secrets, schema checks, or test commands. Keep policy in prose only
when it genuinely requires judgment.

## Avoid

- `HANDOFF.md` or status prose that can override instructions;
- several overlapping “source of truth” files;
- hard-coded ephemeral paths without a portability explanation;
- tool-specific environment branches keyed by agent brand rather than runtime;
- automatic dependency installation or network access;
- invented commit trailers, citation metadata, or publication status;
- duplicated style/lint rules already encoded in configuration;
- blanket “stop and ask” policies for every semantic suspicion;
- mandatory logging of every micro-attempt;
- archival rewrites that erase failed reasoning.
