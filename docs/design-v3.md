# Mathbox v3: research programs with versioned evidence

## Diagnosis

Version 2.2 had useful, focused mathematical workflows and an unusually careful
local literature cache. Three structural gaps limited long investigations:

- The research executor was explicitly restricted to one route, with no
  coordinator for a user asking to continue through several failed approaches.
- Proof, computation and review labels were prose conventions. No executable
  dependency graph noticed that a theorem's input statement or proof had changed.
- The computation validator accepted a blank template. It checked field names,
  not whether the record contained an actual assertion, range, run or valid hash.

The redesign retains the specialist boundaries and adds the missing coordination
and state layer. It does not require every mathematical conversation to become
a managed project.

## Architecture

| Layer | Responsibility | Authority boundary |
|---|---|---|
| Research program | Own the original goal; execute distinct routes and allocate effort by information gained | Cannot turn partial success into the requested theorem |
| Specialist skills | Develop one route, audit a proof, check a source, run an experiment or edit a manuscript | A workflow cannot substitute for a missing mathematical implication |
| Project artifacts | Exact statements, full derivations, checked source translations, code and review reports | Durable arguments carry the mathematical content |
| Optional ledger | Record revisions, dependencies, artifact hashes, review attribution and route outcomes | Validates declared provenance and freshness, not the argument's truth |
| Evaluation | Test packaging, execution and actual mathematical task behavior separately | Software tests are not evidence of frontier research success |

Every skill is still independently installable. No helper imports a sibling
skill, no server or database is required, and there are no model/provider API
dependencies. The existing literature cache is preserved.

## Research policy changes

The new `research-program` interprets one route as one work package within a
sustained assignment. It preserves the exact goal, distinguishes routes by
their failure mechanisms, executes discriminating checks and continues with new
inputs after failure. It supports proof and counterexample searches together.
It requires actual mathematical progress rather than an indefinitely growing
list of plans. Resource/tool limits and exhausted available ideas remain honest
stopping conditions, never a reason to fabricate a breakthrough.

The individual research skill now includes structural moves for coefficient
changes, naturality, homotopy versus homology, spectral-sequence obstructions,
gluing, parameter-uniform mechanisms and counterexample design. Each move has
an exact mathematical obligation.

Fresh audit work receives the claim and raw artifacts without the author's
desired verdict. Review provenance is independent of mathematical evidence and
artifact freshness. Source work distinguishes authenticating a document,
extracting its theorem and proving its applicability. Unavailable companion
skills can be replaced by direct checks with available tools; unverifiable
mathematical inputs remain conditional.

Setup applies existing user authorization to coherent edits. It no longer asks
for approval of each routine modification within an already authorized retrofit.
Ambiguous authority changes and destructive historical rewrites still require
resolution before execution.

## State invariants

- Claims have explicit hypotheses, regime, conclusion level and dependencies.
- Evidence is attached to the claim and all transitive dependency revisions.
- Proof/source/computation/counterexample evidence remain different types.
- Computation cannot discharge a universal proof dependency without a separate
  recorded argument establishing why the finite assertion decides the claim.
- Changed artifacts or contracts make evidence stale. Refuted/retracted inputs
  make downstream arguments conditional. Conflicting proof and counterexample
  evidence is displayed as disputed.
- Audits address exact evidence events. Author self-review cannot be marked
  independent. Losing a negative audit report cannot silently clear its challenge.
- Corrections append events. Revalidated evidence can explicitly supersede old
  evidence while preserving history. No automatic migration promotes old prose.
- Read-only commands never initialize or mutate the project. Writes serialize
  under a lock and publish complete event files atomically.

The ledger cannot discover undeclared dependencies, prove an alleged argument,
authenticate an actor's identity or measure real reviewer independence. These
are explicit semantic responsibilities of the research and audit workflows.
Its hash chain detects accidental corruption, not a malicious complete rewrite.

## Migration and compatibility

Install v3 through the existing distribution path. Use `research-program` for
sustained requests; existing single-purpose invocations continue to work. The
ledger is opt-in for a project and has its own schema version, separate from the
plugin version. Keep existing Markdown status and proof files until their
mapping and authoritative replacement are clear. Adopt only the active claim
subgraph that benefits from tracking.

Complete computation manifests in version 1 remain readable. Blank templates
now require `--template`; this intentional validation change prevents treating
scaffolds as evidence. New runs optionally use the version 2 provenance runner.
Python helpers require Python 3.10+. POSIX process-group termination is tested;
other platforms only receive direct-process termination from this runner.

## Next work that needs real project evidence

The next improvement should be measured on held-out research tasks from actual
projects: time to identify a false implication, repeated failed mechanisms,
stale evidence detected, reproducible runs, and useful mathematical results per
research session. The elementary fixtures here test failure mechanisms, not
research creativity at the frontier.

Formal-verifier adapters should record exact propositions, toolchain and kernel
results once a project supplies a Lean/Coq/other formal target. A fabricated
formalization layer would add no assurance. Literature acquisition can be
extended through authorized source providers without putting credentials in the
ledger. Parallel research should use explicit write ownership and coordinator
reconciliation; the journal deliberately has a single writer and no distributed
merge protocol.
