# Project profile heuristics

Choose one primary profile. A mixed repository may use several, but the primary
profile determines completion and conflict resolution.

## Proof-first

Signals: `.tex`/Markdown theorem notes, conjecture and lemma ledgers, graph/sign
computations, few software releases, an open theorem as the main objective.

Emphasize: theorem hierarchy, hypotheses and conventions, minimal counterexamples,
claim labels, durable proof paths, literature theorem checks, adversarial review.

## Manuscript

Signals: assembled paper, bibliography, referee reports, journal formatting,
separate draft/rebuilt/archive directories.

Emphasize: live manuscript authority, integration criteria, citation verification,
build commands, distinction between publishable current paper and open flagship.

## Computation/software

Signals: package metadata, tests, CI, Sage/Python/Julia code, benchmark scripts,
generated datasets, serialization formats.

Emphasize: exact environment detection, canonical wrappers, mathematical
invariants, risk-tiered testing, provenance, resource limits, output schemas,
backward compatibility, deterministic gates.

## Formalization

Signals: Lean/Coq/Agda/Isabelle project files, theorem-prover CI, imported library
versions, `sorry`/axiom policies.

Emphasize: pinned toolchain, trusted base, statement-design authority, proof
completion criteria, namespace/style conventions, small compilable increments.

## Mixed

Use only when no single profile controls the deliverable. State which profile is
primary. Keep software architecture local to code subtrees and mathematical scope
in the charter; do not force every task to load both manuals.
