# Verification matrix

## Command tiers

| Tier | Purpose | Command | Expected cost | Required when |
|---|---|---|---|---|
| Smoke | Syntax/import/basic build | `{{COMMAND}}` | {{COST}} | {{TRIGGER}} |
| Targeted | Changed component or claim | `{{COMMAND}}` | {{COST}} | {{TRIGGER}} |
| Full | Cross-cutting regression | `{{COMMAND}}` | {{COST}} | {{TRIGGER}} |
| Document | TeX/docs/reference integrity | `{{COMMAND}}` | {{COST}} | {{TRIGGER}} |

## Mathematical acceptance tests

- Minimal examples: {{EXAMPLES}}
- Invariants: {{INVARIANTS}}
- Counterexample atlas: {{ATLAS}}
- Independent/adversarial check: {{SECOND_CHECK}}

## Computation provenance

Record for every claim-supporting run:

- Git revision and dirty status
- Exact command and working directory
- Software/runtime versions and lockfile state
- Coefficient ring/field and precision
- Input object, bounds, seed, and conventions
- Output path and checksum where useful
- Exact assertion tested and result

## Stop conditions

- Stop or narrow a computation when {{RESOURCE_LIMIT}}.
- Do not interpret timeout, out-of-memory, or missing cases as a mathematical
  negative result.
