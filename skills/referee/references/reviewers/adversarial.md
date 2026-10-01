# Adversarial lane

Read the shared protocol. Stress-test admissible cases and reductions, using
the actual definitions and global hypotheses. Skepticism is rigor, not an
instruction to invent objections.

- `degenerate-case`: empty objects, dimension/arity zero, the trivial group or
  module, singular elements, equality cases, induction's initial index;
- `non-uniformity`: a constant or construction depends on a parameter after
  the argument treats it as uniform; inspect its quantifier scope;
- `finiteness-trap`: finite/finitely generated/finite-dimensional properties
  migrate to an infinite setting, or an infinite-case argument misses a finite
  degeneracy;
- `brittle-reduction`: a WLOG or symmetry move omits an asymmetric admissible
  case or fails to preserve the hypotheses;
- `implicit-assumption`: characteristic, commutativity, separability,
  tameness, local finiteness or a topological property is assumed without grant.

Name the precise object or parameter regime. Check that the manuscript does
not exclude it and that any witness/intermediate construction lies in the
claimed domain. Work the candidate through; "may fail in general" is not a
finding. State whether the conclusion fails or only the proposed proof lacks
justification. A fragile step needing a local explanation is usually moderate;
a valid counterexample affecting the headline result may be critical.

Use `proof-audit` to confirm consequential obligations. A theorem failing on a
case its statement admits belongs here; an abstract omitting the theorem's
restriction belongs to claims. Keep notation and exposition in their lanes.
