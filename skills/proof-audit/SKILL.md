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

## Build the dependency graph

When the project has a `.mathbox/` ledger, use the available `research-state`
skill to detect changed artifacts, stale claim revisions and downstream impact.
Inspect the raw current proof even when the ledger reports `proved`. Record an
audit separately from the evidence it reviews when updates are authorized.
If those updates are authorized but this host cannot execute or write, use the
`research-state` deferred packet contract for the audit report and review
proposal; state that it has not been recorded.

List each implication needed from definitions and hypotheses to the conclusion.
Mark every leaf as internal proof, external theorem, computation, convention,
or unchecked assumption. Detect circular dependencies and claims whose evidence
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

Return exactly one primary verdict:

- proved as written;
- correct only after a stated restriction;
- externally proved in the exact required form;
- conditional on a named input;
- computationally verified only in a stated range;
- incomplete, with the smallest missing implication;
- refuted, with the smallest valid counterexample;
- ill-typed or internally inconsistent.

Default to no edits. Never close a gap with a new argument. Requested corrections
may only restrict the statement or fix a forced local step, after reviewing
downstream dependents. Label other repairs unaudited, retain the verdict and
route new arguments through the available `research-attempt` skill
(`mathbox:research-attempt` in plugin installations), or return the exact research
obligation if unavailable. Propagate into a manuscript only on explicit request
through the available `manuscript-integrate` skill (`mathbox:manuscript-integrate`
in plugin installations), or preserve its validation/edit boundaries directly.
Convention changes require the project's normal approval.

For ledger reviews, use `pass` only when the verdict supports the evidence's
exact claim, `conditional` for a conditional verdict, and `fail` otherwise.
A restriction or finite range does not pass evidence asserting the full claim.

## Output

Lead with the normalized claim and verdict. Then give:

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
