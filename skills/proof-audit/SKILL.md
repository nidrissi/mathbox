---
name: proof-audit
description: >-
  Adversarially audit an existing mathematical claim, proof, derivation, diagram, or theorem dependency for correctness. Use to verify, check, stress-test, type-check or find gaps in a single claim, proof or dependency. Do not use for a whole-manuscript referee report, inventing a substantially new proof route, or merely copyediting prose.
---

# Mathematical proof audit

Audit the claim actually stated, under its stated hypotheses. Do not rescue it
by changing definitions, conventions, or scope.

For a referee-style assessment of an entire manuscript, use the available
`referee` skill (`mathbox:referee` in plugin installations). This skill remains
responsible for focused mathematical obligations delegated by that review.

## Establish the target

1. When auditing project files, read applicable instructions and resolve the
   authoritative statement, proof, status, conventions, literature record and
   verification commands, recording its locator or revision rather than a summary.
2. Restate the claim as a claim card:
   - quantified objects and exact conclusion;
   - hypotheses and exceptional cases;
   - source and target, coefficient domain, grading, variance, signs,
     finiteness/completion, equivariance, and range;
   - the project's recorded evidence label, dependencies, and cited computation or source.
3. If the statement cannot be typed unambiguously, return the ill-typed verdict;
   continue only under explicitly labelled readings.
4. Identify whether the primary target is the claim, a submitted argument or a
   specific evidence revision.

## Build the dependency graph

Inspect the raw argument even when a ledger, status file or claim card reports
`proved`. A recorded label locates evidence; it establishes neither the claim
nor its dependencies. Consult a project's `.mathbox/` ledger through the
available `research-state` skill only when an evidence revision bears on the
audit, including recorded evidence for a dependency the argument relies on, or
when the task calls for freshness, downstream impact or recording. For a ledger review, identify the
evidence ID, claim revision and pinned artifact. Inspect the raw artifact at
that revision. If the bytes have changed, distinguish an audit of the current
file from a review of the pinned version. If the pinned version is unavailable,
leave its argument ungraded and identify the missing artifact. If the exact
archived bytes are available, assess them against their hash and report any
remaining ledger freshness issue. Record an authorized review separately from
its evidence. Check that the exact evidence revision is current before appending
or proposing the review. If it is stale, report the assessment without a review
event. When an authorized review of current evidence can only be recorded
later, follow the `research-state` deferred packet contract and state that the
proposal is unapplied.

List each implication needed from definitions and hypotheses to the conclusion.
Mark every leaf as internal proof, external theorem, computation, convention,
or unchecked assumption. A dependency supported only by a recorded label, or by
stale evidence, is an unchecked assumption. Detect circular dependencies and claims whose evidence
ultimately points back to the claim itself.

## Audit adversarially

For every applicable obligation:

- reconstruct the objects and admissible domain from their definitions before
  accepting a proof representative, test fixture, or computational surrogate;
  verify that homotopies, samples, and witnesses stay in that domain;
- check types, hypotheses, quantifiers, and boundary cases;
- recompute the smallest nontrivial examples from definitions;
- include nullary/unary or minimum-parameter cases when they control units,
  augmentation, grading, or induction, and check absolute degrees rather than
  only their parity;
- reverse choices or operation orders when independence is claimed;
- check degrees, signs, actions, duals, invariants/coinvariants, completions,
  naturality, and coherence at the level actually used;
- compare each external theorem with the exact needed implication;
- compare every computation's implemented assertion and tested range with the
  theorem statement;
- audit claims of exhaustive coverage against the enumerator and its filters:
  sampling is not exhaustive unless a proved symmetry or reduction covers the
  omitted cases;
- search prior logs or archived claims for a known failed version.

Route unchecked external leaves through the available `literature-check` skill
(`mathbox:literature-check` in plugin installations), or check exact sources
directly if unavailable; mark the obligation conditional if unverifiable.
Route load-bearing computations through the available `computation-audit` skill
(`mathbox:computation-audit` in plugin installations), or apply the finite-assertion,
range and coverage checks above directly.

Load the relevant domain sections of
[obligation-checklists.md](references/obligation-checklists.md); do not apply
irrelevant checklists mechanically.

Mark each obligation **passed**, **failed**, **conditional**, **not addressed**,
or **out of scope**. Agreement on notation or small cases is not proof of a
universal statement.

## Verdict

Give one primary verdict for the requested audit target. For an argument or
evidence audit, lead with what that exact artifact establishes and identify
its decisive step or gap. Report independently established support for the
claim separately. When judging the claim under its stated hypotheses, choose:

- proved as written;
- correct only after a stated restriction;
- externally proved in the exact required form;
- conditional on a named input;
- computationally verified only in a stated range;
- incomplete, with the smallest missing implication;
- refuted, with a verified counterexample;
- ill-typed or internally inconsistent.

For a refutation, verify that the witness satisfies every hypothesis and show
where the conclusion fails. Call the witness minimal only if you justify the
ordering and rule out every smaller counterexample under it.

Default to no edits. Never close a gap with a new argument. Requested corrections
may only restrict the statement or fix a forced local step, after reviewing
downstream dependents. Label other repairs unaudited, retain the verdict and
route new arguments through the available `research-attempt` skill
(`mathbox:research-attempt` in plugin installations), or return the exact research
obligation if unavailable. Propagate into a manuscript only on explicit request
through the available `manuscript-integrate` skill (`mathbox:manuscript-integrate`
in plugin installations), or preserve its validation/edit boundaries directly.
Convention changes require the project's normal approval.

For a ledger review, grade what the reviewed evidence revision purports to
establish. Use `pass` when that evidence establishes its exact assertion,
`conditional` when it depends on a named unresolved input, and `fail` for a
defective argument or unsupported scope. A circular proof receives `fail` even
when separate source evidence proves the claim. A restriction or finite range
supports only evidence asserting that scope.

## Output

Before saving a durable record, proof, report or authored JSON, follow
[attribution.md](references/attribution.md).

Lead with the normalized claim and the verdict for the audit target. Include a
separate assessment when both the claim and its submitted argument are in scope.
Then give:

1. dependency graph;
2. obligation matrix;
3. decisive evidence or counterexample;
4. source/computation checks and commands;
5. exact remaining gap;
6. strongest safe statement and cheapest next check;
7. review provenance (self-review or independent) and exact revision audited.

## Independence

When the user or project requires an independent audit, use a fresh session or
isolated subagent when the
tool supports it and delegation is authorized. Give the exact claim and raw
proof/source artifacts, without the author's verdict or suspected gap. Ask for
a fresh derivation of the critical implication and of the object being tested.
Do not give it an implementation or geometric surrogate as though that were the
definition. Otherwise label the pass self-review. Neither agreement between
agents nor a different actor name proves independence or mathematical
correctness; successive reviews can share the same model error.
