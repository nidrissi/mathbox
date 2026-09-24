# Mathbox v3: research programs with versioned evidence

> **Scope:** This document explains the design of 3.0 and was last revised for
> 3.0.1. It covers neither the compact reports, ledger batches and program
> closeout added in 3.1.0 nor the deferred handoff ingestion added since then;
> see the [changelog](CHANGELOG.md) for those.

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
and state layer. Additional adversarial hardening also exposed failure classes that a
nominally valid workflow could miss: audits reusing the claimant's surrogate
object, sparse iterators presented as exhaustive, parity checks masking absolute
degree errors, parallel returns without a common-base reconciliation, narrow
novelty searches, and repository migrations that inferred authority from
filenames. The fixes and regression examples are entirely synthetic. The redesign does not require
every mathematical conversation to become a managed project.

## Architecture

| Layer | Responsibility | Authority boundary |
|---|---|---|
| Research program | Own the original goal; execute distinct routes and allocate effort by information gained | Cannot turn partial success into the requested theorem |
| Specialist skills | Develop one route, audit a proof, check a source, run an experiment or edit a manuscript | A workflow cannot substitute for a missing mathematical implication |
| Project artifacts | Exact statements, full derivations, checked source translations, code and review reports | Durable arguments carry the mathematical content |
| Optional ledger | Record revisions, statement bindings, dependencies, artifact hashes, review attribution, route outcomes and execution lifecycle | Validates declared provenance and freshness, not the argument's truth |
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
artifact freshness. The reviewer reconstructs the claimed object, domain and
absolute degrees independently, checks minimum cases and iterator coverage, and
does not let a regularized substitute or sampled sweep inherit the original
claim. Source work separates discovery from verification, searches equivalent
and historical terminology, follows citation chains, and distinguishes
authenticating a document, extracting its theorem and proving its applicability.
Unavailable companion skills can be replaced by direct checks with available
tools; unverifiable mathematical inputs remain conditional.

Setup applies existing user authorization to coherent edits. Its inspector
recognizes semantic filename aliases, distinguishes unavailable Git metadata
from a clean worktree, inventories computation manifests and declared path/cache
conventions, and reports competing dashboard or handoff candidates without
choosing authority from names. It does not follow symlinked files. Legacy log
migration maps source spans against the stated mission, quarantines foreign or
ambiguous material, and requires review before replacing the live index.
Manuscript setup leaves venue, language, audience, deadline, counting convention
and complete page budget unknown until confirmed. Source-derived inventory
entries remain pending until checked. Ambiguous authority changes and destructive
historical rewrites still require resolution before execution.

Parallel research uses explicit base checkpoints, owners and write scopes.
Arrival order is not ancestry, shared files are written only after coordinator
reconciliation, and a restricted theorem or conditional lemma remains a partial
result rather than silently completing the original goal. Manuscript integration
propagates accepted changes through a project map of semantic dependents instead
of relying on filename proximity.

## State invariants

- Claims have explicit hypotheses, regime, conclusion level and dependencies;
  an optional hashed statement artifact binds ledger text to the controlling file.
- Evidence is attached to the claim and all transitive dependency revisions.
- Proof/source/computation/counterexample evidence remain different types, with
  neutral generated labels such as `proof-recorded` and `source-recorded`.
- Computation cannot discharge a universal proof dependency without a separate
  recorded argument establishing why the finite assertion decides the claim.
- A linked v2 computation record pins its manifest plus the complete declared
  input/output closure; equal before/after input hashes and a completed zero-exit
  run are required before the ledger grants closure semantics.
- Changed artifacts or contracts make evidence stale. Counterexample-supported
  or retracted inputs make downstream arguments conditional. Conflicting proof
  and counterexample evidence is displayed as disputed.
- Audits address exact evidence events. Author self-review cannot be marked
  independent. Conditional computation reviews affect claim state, active review
  objects remain visible in handoffs, and pass/fail conflicts cannot display as
  an unqualified independent pass. Losing a negative audit report cannot silently
  clear its challenge.
- Claim dependencies represent jointly required obligations. Routes may name
  narrower obligations they resolve, while route-only prerequisites remain
  separately typed handoff context rather than synthetic theorem dependencies.
- Corrections append events. Revalidated evidence can explicitly supersede old
  evidence while preserving history. No automatic migration promotes old prose.
- Read-only commands never initialize or mutate the project. Writes serialize
  under a lock and publish complete event files atomically.
- Programs and route runs record common bases, observations (including explicit
  `unknown`), terminal revisions, conflicts and late-result dispositions. Run or
  route success never promotes a mathematical claim by itself.

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

Historical computation manifests in version 1 remain readable with their
original nonempty software strings, absent/null repository revisions, and
unambiguous project- or manifest-relative output paths. The validator reports
the provenance those records cannot establish; it does not upgrade them to v2.
Blank templates require `--template`. New v2 runs can declare and hash scientific
result files, cross-check execution artifacts, and request POSIX address-space,
CPU-time and affinity caps plus cooperative numerical-library thread caps.
Python helpers require Python 3.10+. POSIX process-group termination is tested;
other platforms only receive direct-process termination from this runner.

Existing research-state schema-version-1 journals and minimal configs remain
readable without event rewriting. Generated status strings intentionally use
the neutral `*-recorded` vocabulary, so dashboards or scripts matching the old
mathematical-sounding strings must be updated. New lifecycle events require the
v3 helper.

## Evaluation boundary and future work

Real-project evaluation should remain held out and confidential. Only aggregate
measures—time to identify a false implication, repeated failed mechanisms, stale
evidence detected, reproducible runs, and useful mathematical results per
research session—belong in public reports. The elementary fixtures in this
repository test transferable failure mechanisms, not research creativity at the
frontier.

Formal-verifier adapters should record exact propositions, toolchain and kernel
results once a project supplies a Lean/Coq/other formal target. A fabricated
formalization layer would add no assurance. Literature acquisition can be
extended through authorized source providers without putting credentials in the
ledger. Parallel research should use explicit write ownership and coordinator
reconciliation; the journal deliberately has a single writer and no distributed
merge protocol.
