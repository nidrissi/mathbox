---
name: proof-audit
description: >-
  Adversarially audit an existing mathematical claim, proof, derivation, diagram, or theorem dependency for correctness. Use for requests to verify, referee, stress-test, type-check, find gaps, or isolate the exact remaining implication. Default to read-only. Do not use to invent a substantially new proof route or merely copyedit prose.
---

# Mathematical proof audit

Audit the claim actually stated, under its stated hypotheses. Do not rescue it
by changing definitions, conventions, or scope.

## Establish the target

1. Determine the repository root and read applicable instructions.
2. Resolve current proof, status, claims, conventions, literature, and
   verification roles from project instructions or standard filenames.
3. Restate the claim as a claim card:
   - quantified objects and exact conclusion;
   - hypotheses and exceptional cases;
   - source and target, coefficient domain, grading, variance, signs,
     finiteness/completion, equivariance, and range;
   - evidence label, dependencies, and cited computation or source.
4. If the statement cannot be typed unambiguously, report that before auditing
   the argument.

## Build the dependency graph

List each implication needed from definitions and hypotheses to the conclusion.
Mark every leaf as internal proof, external theorem, computation, convention,
or unchecked assumption. Detect circular dependencies and claims whose evidence
ultimately points back to the claim itself.

## Audit adversarially

For every applicable obligation:

- check types, hypotheses, quantifiers, and boundary cases;
- recompute the smallest nontrivial examples from definitions;
- reverse choices or operation orders when independence is claimed;
- check degrees, signs, actions, duals, invariants/coinvariants, completions,
  naturality, and coherence at the level actually used;
- compare each external theorem with the exact needed implication;
- compare every computation's implemented assertion and tested range with the
  theorem statement;
- search prior logs or archived claims for a known failed version.

When an external-source leaf is not already verified in the project's durable
literature record, route the source question through the available
`literature-check` skill (`mathbox:literature-check` in plugin installations).
That workflow checks an authorized project-local cache before fetching. If the
skill is unavailable or the exact source cannot be checked, mark the leaf
**conditional**; do not fill it from a snippet, secondary citation, or memory.

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

Default to no edits. When the user also requests correction, change the durable
proof and dependent status only after identifying the failed implication and
reviewing the blast radius. A convention change still requires the project's
normal approval.

## Output

Lead with the normalized claim and verdict. Then give:

1. dependency graph;
2. obligation matrix;
3. decisive evidence or counterexample;
4. source/computation checks and commands;
5. exact remaining gap;
6. strongest safe statement and cheapest next check.

For an independent audit, use a fresh session or isolated subagent when the
tool supports it; do not let the author's route summary substitute for reading
the proof.
