# Mathematical computation checklist

## Representation of mathematical objects

- Indexing conventions and base cases match the definition.
- Basis order, orientations, signs, actions, and quotient relations are explicit.
- Canonicalization does not identify distinct objects or split equivalent ones.
- Sparse/dense and exact/approximate representations preserve semantics.

## Algebra and homological computation

- Check `d^2 = 0`, degree shifts, Leibniz signs, and filtration preservation.
- Matrix rank is computed over the intended field or ring.
- Modular computations justify reconstruction or characteristic transfer.
- Invariants/coinvariants and left/right actions use consistent conventions.
- Dimensions, Euler characteristics, traces, or characters match known cases.

## Numerical computation

- Precision and tolerance are justified by conditioning/error bounds.
- Results are stable under increased precision and altered algorithms.
- Interval, exact, or certified methods are used when the claim requires them.
- A visually plausible plot or residual alone is not certification.

## Reproducibility and systems

- Random seed and random generator are recorded.
- Parallel reductions are deterministic or their nondeterminism is bounded.
- Cache keys include all semantic inputs and convention versions.
- Environment and library versions are recorded.
- Output serialization is round-trip tested when reused as evidence.
- Timeouts and memory limits are reported as limits, not negative results.
