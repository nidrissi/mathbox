# Proof-audit obligation checklists

Use only the sections relevant to the claim.

## General logic and typing

- Every symbol, map, category, object class, and quantifier is defined.
- The conclusion follows from the stated—not intended—hypotheses.
- No implication is used in the reverse direction without proof.
- No induction, minimality, or compactness argument loses a boundary case.
- Definitions are stable across the proof; no hidden strengthening occurs.

## Graded, differential, and sign-sensitive arguments

- Differential and operation degrees are consistent.
- All Koszul crossings and suspensions are accounted for.
- Chain maps commute with differentials with the claimed sign.
- Homology-level statements are not inferred from chain-level data without the
  required quasi-isomorphism, convergence, or filtration argument.
- Test the smallest two-operation and three-operation orders.

## Category, variance, and duality

- Covariance/contravariance and left/right actions are correct.
- Opposites, duals, invariants, coinvariants, and completions are justified.
- Finite-type assumptions needed for dualization are present.
- Naturality squares and coherence data are checked, not inferred from matching
  object labels.

## Spectral sequences and filtrations

- Filtration is exhaustive, separated/complete as needed, and preserved.
- Page indexing and bidegrees are consistent.
- Convergence is strong enough for the claimed target.
- Extension problems are addressed.
- A collapse claim includes all possible differential sources and targets.

## Topology and homotopical algebra

- Model-category or infinity-categorical replacements are admissible.
- Point-set maps represent the claimed derived maps.
- Homotopy invariance and cofibrancy/fibrancy assumptions are sufficient.
- Local systems, basepoints, connectedness, orientations, and tangential data
  are not dropped.

## Representation and symmetry arguments

- Group actions and conventions are explicit.
- Stabilizers, orbit multiplicities, component permutations, and character
  signs are correct.
- Restriction/induction and invariant/coinvariant passages use the right side.
- Dimension checks and smallest nontrivial representations agree.

## Computation-dependent claims

- The code implements the stated mathematical object.
- Arithmetic domain and normalization are correct.
- Bounds cover the claimed range.
- Randomness, numerical tolerances, and rational reconstruction are controlled.
- Independent invariants or implementations catch correlated bugs.

## External sources

- Exact version, theorem, hypotheses, and notation translation are recorded.
- The source proves rather than merely states or suggests the result.
- No unstated functoriality, normalization, or completion is supplied by the
  citation.
