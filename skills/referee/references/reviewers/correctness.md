# Correctness lane

Read the [shared protocol](../review-protocol.md). Review substantive units and load-bearing proofs
for structural logic under their exact hypotheses. Trace needed definitions
and prior lemmas, requesting context when it is absent.

Probe these mechanisms when relevant:

- `hidden-hypothesis`: a theorem is used without its preconditions, or a proof
  requires a condition its own statement lacks;
- `ill-defined`: existence or uniqueness of a limit, sum, supremum or universal
  construction is unproved;
- `citation-drift`: the claimed external input differs from the application;
  state the exact `literature-check` obligation when material;
- `quantifier-swap`: pointwise existence becomes uniform existence, or
  quantifiers change order;
- `equivalence-failure`: only one implication or an irreversible construction
  is supplied for an equivalence;
- `well-definedness`: choices or equivalence-class representatives affect a
  claimed map or operation;
- `computation-error`: a load-bearing display, bound, exponent or enumeration
  differs from what you actually derive or audit.

Do not demand omitted routine algebra an expert can reconstruct. Recompute
calculations carrying the theorem's bound or convergence claim; report your
own value and derivation when it disagrees. For code leaves return the exact `computation-audit` obligation and finite scope.

Separate "does not follow" from "not justified here". If necessary context is
unavailable, record the precise question at confidence below $0.7$, rather
than presuming its absence from the paper. State serious concrete `proof-audit` obligations for the coordinator. Notation comparison,
concrete boundary probes, exposition and abstract-versus-theorem calibration
belong to their lanes unless inseparable from the logical defect.

Do not run specialist skills unless the coordinator explicitly assigns them.
