# Evidence model

Recommended labels:

- **proved** — a complete durable argument under exact stated hypotheses;
- **externally proved** — exact external theorem verified and correctly
  translated;
- **computationally verified** — exact finite assertion checked in a recorded
  range;
- **conditional** — depends on a named unverified implication;
- **heuristic** — motivated but not established;
- **conjectural** — intentionally open claim;
- **refuted** — a valid counterexample is recorded;
- **superseded** — historical statement replaced by an explicit correction.

A claim is promoted only when its durable evidence, dependencies, and review
status are linked. Computation never becomes proof without an argument that the
finite assertion decides the mathematical claim.

Keep three axes distinct:

| Axis | Examples | Meaning |
|---|---|---|
| Mathematical evidence | proof, exact external theorem, finite computation, counterexample | What supports the exact statement |
| Review | unreviewed, self-reviewed, independently audited, disputed | Who checked which argument and how |
| Freshness | current, stale, retracted | Whether the checked statement, dependencies and artifact bytes still match |

“Independently audited” is review provenance, not a stronger theorem. A fresh
review must inspect the raw proof under the current contract; different actor
names alone are insufficient. A changed dependency invalidates downstream
applications until rechecked. A dependency with only computational or conditional
support does not establish a universal downstream theorem.

An optional `.mathbox/` ledger implements these distinctions through the
available `research-state` skill. Its status is a projection of declared evidence,
not a formal proof certificate. Existing Markdown projects can use the same
distinctions without adopting the helper.
