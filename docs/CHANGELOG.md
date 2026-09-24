# Changelog

All notable changes to Mathbox are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). The version is the
one declared in `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json` and
`.claude-plugin/marketplace.json`. The research-state ledger and computation
manifests have their own schema versions, independent of the plugin version.

## [Unreleased]

### Added

- `research-state`: deferred handoff ingestion for hosts that can inspect a
  project but cannot run the helper or write files. Such a host returns one
  `mathbox-deferred-v1` packet; `ingest PACKET.json --dry-run` validates it and
  `ingest PACKET.json` applies it locally. The packet is pinned to the exact
  ledger head it was written against. It may create new text artifacts and add
  one guarded index entry, but only at locations that the optional `deferred`
  section of `.mathbox/config.json` allows. Artifacts are hashed during staging,
  and proposals go through ordinary batch validation. The local command
  generates event IDs, hashes and timestamps; the packet never supplies them.
  See the [deferred handoff contract](../skills/research-state/references/deferred-handoff.md).
  ([#12])
- `research-program`, `research-attempt`, `proof-audit` and `literature-check`
  emit a deferred packet when persistence is authorized but the host cannot
  execute or write. They say that the packet has not yet been applied. ([#12])
- Regression tests for ingestion and a behavioral evaluation for a web host.
  ([#12])

## [3.1.0] — 2026-09-23 — Compact workflows and route continuation

### Added

- `research-state`: `record-batch` prevalidates a batch of distinct events and
  appends them in one pass. Aliases let events in the batch refer to each
  other, and `--dry-run` previews the batch. ([#9])
- `research-state`: a read-only `pin-impact PATH` query that lists the claims
  and evidence that pin a project file. ([#9])
- `research-program`: program closeout. It writes one checked synthesis of the
  decisive outcomes and a compact view of current decisions, and links the
  exact route artifacts. A new
  [closeout template](../skills/research-program/assets/program-closeout.template.md)
  supports it. A retrospective closeout separates the historical cutoff from
  the assessment made at migration time. Routes not assigned to the program
  stay linked but are left out of program verdicts. ([#9])
- `research-program`: a short program- or phase-level entry point above the
  route-level indexes for long programs. Small projects can keep a flat index.
  ([#9])
- `research-init`: a reviewed
  [migration workflow for existing repositories](../skills/research-init/references/existing-repo-migration.md)
  that respects ledger pins. It adds a bounded planning pass, a content
  crosswalk, preservation of history, and validation before and after the
  migration. It never rewrites ledger events, and it never turns historical
  prose into proof. ([#9])
- Reopening guidance: a premature route closure, or a legacy closure for
  resource reasons only, can be corrected by an append-only reopening that
  states whether any mathematical premise changed. ([#11])
- The evaluation fixture `evals/fixtures/inconclusive-continuation.md` and
  behavioral and routing cases for unfinished work, budget limits, reopening,
  and valid obstructions. ([#11])

### Changed

- `research-state` and the repository inspector print a brief report by
  default: counts, actionable IDs, and how many items were omitted. Use
  `--full` for the complete Markdown report, or `--json` (ledger) or
  `--format json` (inspector) for JSON. ([#9])
- The `research-init` templates keep mutable progress out of `AGENTS.md`, and
  the skills now favor current summaries, looking up only the history they
  need, and checkpointing only material route changes. ([#9])
- `research-attempt` writes route outcomes only to the designated route index.
  ([#9])
- `research-program`, `research-attempt` and `research-state` separate the
  outcome of an attempt from the disposition of its route. An inconclusive
  attempt no longer closes a route while a proposed continuation is still
  untried. Before closing an unresolved route, agents account for known
  continuations and for the scope of any obstruction. Deferred work keeps a
  concrete next action and a condition for resuming it. The ledger event
  schema is unchanged. ([#11])
- `research-init` treats a `CLAUDE.md` bridge as optional, because Claude Code
  v2.1.277 and later loads `AGENTS.md` directly. It still checks that an
  existing `CLAUDE.md` imports `@AGENTS.md`. ([#10])

### Removed

- The repository-root `CLAUDE.md` shim. Claude Code now reads `AGENTS.md`
  directly. ([#10])

## [3.0.1] — 2026-09-16 — Review- and obligation-aware handoffs

### Added

- `research-state`: `check --summary` for compact integrity checks. ([#8])
- Routes accept optional `resolves` metadata. It lets route discovery find a
  route aimed at a registered sub-obligation, including a route owned by a
  parent claim, and it scopes runs to that obligation. ([#8])
- Handoffs expose active review events and review conflicts in both JSON and
  Markdown, instead of reducing them to a single summary flag. ([#8])
- A separate `state.route_context` closure lists prerequisites that only a
  route uses. The theorem dependency graph stays unchanged. ([#8])

### Fixed

- Conditional and failed reviews now apply the same way to every kind of
  evidence. Previously, a conditional review could leave bounded computation
  evidence labeled `computation-recorded`. ([#8])

## [3.0.0] — 2026-09-08 — Research programs and versioned evidence

A redesign around sustained research programs and versioned evidence. See the
[design rationale](design-v3.md) and the [validation report](validation-v3.md).
([#7])

### Added

- The skill `research-program` pursues a substantial goal across distinct
  proof, counterexample, source and computation routes. It starts each route
  from an explicit checkpoint, keeps partial results, reconciles parallel or
  delayed returns from a common base, and continues after failed attempts.
- The skill `research-state` keeps an optional, append-only, versioned ledger
  in the research project's `.mathbox/` directory. It records exact claim
  revisions, optional bindings to statement files, transitive dependencies,
  hashed evidence, review provenance kept separate from the evidence, and the
  lifecycle of programs and runs. From these it generates dependency-impact,
  stale-evidence and handoff views. Generated labels such as `proof-recorded`
  and `source-recorded` describe recorded evidence, not certified proofs. See
  the [ledger command contract](../skills/research-state/references/ledger.md).
- `computation-audit`: a bounded
  [experiment runner](../skills/computation-audit/references/runner.md). It
  records the actual argv, hashes of the inputs and the scientific results,
  bounded logs and the finite scope, and it can apply POSIX memory, CPU-time
  and CPU-affinity limits. It emits version 2 computation manifests.
- `research-attempt`: structural moves, each with an exact mathematical
  obligation. They cover coefficient changes, naturality, homotopy versus
  homology, spectral-sequence obstructions, gluing, mechanisms uniform in a
  parameter, and counterexample design.
- `research-init`: the repository inspector detects research roles under other
  file names, ambiguous live files, computation manifests, path and cache
  conventions, and migration material that needs review or quarantine. It
  does not follow symlinked files.
- `scripts/check.py`, a standard-library regression gate for package
  contracts, the inventory of synthetic fixtures, and the behavior of the
  ledger, experiment runner, inspector and literature cache. A GitHub Actions
  workflow runs it on Python 3.10 and 3.13.
- Synthetic evaluation fixtures under `evals/fixtures/`, the
  [evaluation protocol](../evals/README.md), and recorded task-trial evidence
  under `evals/results/v3/`.

### Changed

- `proof-audit` independently reconstructs the claimed object, its domain and
  its absolute degrees. A computation done on a convenient substitute does not
  count as evidence for the original claim. A coverage claim must match the
  iterator that was actually run, not a sample or a parity check.
- `literature-check` separates finding a source from verifying it. It searches
  equivalent and historical terminology and follows citation chains to primary
  sources.
- `manuscript-integrate` propagates accepted changes through a project map of
  semantic dependents instead of relying on filename proximity.
- `validate_manifest.py` rejects an unfilled template as evidence unless
  `--template` is passed. Complete version 1 records remain valid; the report
  lists the provenance they cannot establish and does not upgrade them to
  version 2.
- The Python helpers require Python 3.10 or later.

## [2.2.0] — 2026-09-04 — Literature cache and research records

### Added

- `literature-check`: a persistent literature cache inside the project, in
  `.research-cache/literature/`, ignored by Git. It stores PDFs and extracted
  text addressed by content, looks up exact source identifiers before fetching
  a source again, and keeps arXiv versions distinct. The helper uses
  `pdftotext` when it is available. It never fetches sources or handles
  credentials, and it refuses to write any file that Git would track. See
  [source-cache.md](../skills/literature-check/references/source-cache.md).
  ([#5])
- Other research-facing skills send questions about external mathematical
  sources to `literature-check`. `research-init` records the project's policy
  on retaining cached sources. ([#5])
- Research attempts, findings, corrections and decisions are stored as
  immutable standalone records under `research/records/`. `RESEARCH_LOG.md`
  becomes a compact, append-only index of links to them, with normalized
  dated filenames. ([#6])
- A lossless migration workflow, gated on approval, for long-form legacy logs.
  ([#6])

### Changed

- The Codex short description is under 30 characters. ([#4])

## [2.1.0] — 2026-09-02 — Generalization gates and plugin namespacing

### Added

- A mandatory generalization probe after bounded cases succeed. Another finite
  case is allowed only if it distinguishes named alternatives, audits a
  different code path, or enters a new regime. ([#1])
- Behavioral regression evals for `research-attempt`, `computation-audit` and
  `research-retrospective`. ([#1])

### Changed

- A next-step field states a mathematical question and a uniform route or
  discriminator, not a command to run. Live status holds only the current
  state; past verification narratives belong in logs or manifests. ([#1])
- The `mathbox:` namespace is used consistently for plugin invocations in
  Codex and Claude Code, and plugin installs are distinguished from standalone
  fallbacks throughout the manifests, OpenAI metadata, cross-skill references
  and evals. ([#2])

## [2.0.0] — 2026-08-28 — Initial public release

First public release. It is packaged as the `mathbox` plugin for Claude Code
and Codex, with eight skills that can each be installed on their own:
`research-init`, `research-attempt`, `proof-audit`, `literature-check`,
`computation-audit`, `manuscript-integrate`, `proofread-math` and
`research-retrospective`.

### Added

- The Claude plugin manifest and the marketplace catalog. The repository root
  is also the plugin root.
- Codex packaging and presentation metadata, and the icon
  `assets/mathbox.svg`.
- One canonical copy of each skill under `skills/`, with portable `SKILL.md`
  frontmatter (`name` and `description` only) and OpenAI invocation policy in
  `agents/openai.yaml`.
- Shared contributor instructions in `AGENTS.md`, and the MIT license.

## Pre-release development (2026-04 to 2026-08)

This history predates versioned releases; the project was first called
"Research Toolbox".

- April–June 2026: early skills for math proofreading, LaTeX typesetting and
  translating notes.
- July 2026: `proofread-math` rewritten with evals, and the typesetting skill
  reworked. `research-init` was added, followed by the research suite:
  `research-attempt`, `proof-audit`, `literature-check`, `computation-audit`,
  `manuscript-integrate` and `research-retrospective`. The typesetting and
  translation skills were removed.
- August 2026: packaged as a plugin, renamed `mathbox`, and prepared for
  release as 2.0.0.

[Unreleased]: https://github.com/nidrissi/mathbox/compare/v3.1.0...HEAD
[3.1.0]: https://github.com/nidrissi/mathbox/compare/v3.0.1...v3.1.0
[3.0.1]: https://github.com/nidrissi/mathbox/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/nidrissi/mathbox/compare/v2.2.0...v3.0.0
[2.2.0]: https://github.com/nidrissi/mathbox/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/nidrissi/mathbox/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/nidrissi/mathbox/releases/tag/v2.0.0
[#1]: https://github.com/nidrissi/mathbox/pull/1
[#2]: https://github.com/nidrissi/mathbox/pull/2
[#4]: https://github.com/nidrissi/mathbox/pull/4
[#5]: https://github.com/nidrissi/mathbox/pull/5
[#6]: https://github.com/nidrissi/mathbox/pull/6
[#7]: https://github.com/nidrissi/mathbox/pull/7
[#8]: https://github.com/nidrissi/mathbox/pull/8
[#9]: https://github.com/nidrissi/mathbox/pull/9
[#10]: https://github.com/nidrissi/mathbox/pull/10
[#11]: https://github.com/nidrissi/mathbox/pull/11
[#12]: https://github.com/nidrissi/mathbox/pull/12
