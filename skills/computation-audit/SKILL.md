---
name: computation-audit
description: >-
  Design, run, or audit a mathematical computation that supports a research claim, including symbolic, exact, finite-field, representation-theoretic, homological, or numerical experiments. Use when correctness, provenance, tested range, reproducibility, or interpretation matters. Do not present bounded output as a universal proof.
---

# Mathematical computation audit

Separate the mathematical claim from the finite assertion implemented by code.
Default to read-only audit when the user asks to review an existing computation.

## Specify the contract

1. Determine repository root and applicable instructions.
2. State:
   - mathematical claim or research decision;
   - exact computational surrogate;
   - coefficient/arithmetic domain and conventions;
   - input family, bounds, exclusions, and resource caps;
   - what a pass, failure, timeout, or inconsistent result would imply;
   - what the computation cannot establish.
3. Locate the authoritative code, data, prior outputs, and documented command.
   Do not invent a build or execution procedure.

## Audit the implementation

Check the relevant items in [checklist.md](references/checklist.md), especially:

- object construction, indexing, basis, normalization, and group actions;
- exact arithmetic versus floating approximation;
- chain condition, symmetry, dimension, conservation, or other invariants;
- smallest hand-computable and known benchmark cases;
- deterministic seeds and stable input ordering;
- independent implementation or orthogonal invariant for load-bearing results;
- parser, serialization, cache, parallelism, and stale-output risks;
- whether resource truncation silently changes the claimed range.

A passing test of the code is evidence about the code path, not automatically
about the theorem.

## Run proportionately

Use the narrowest command capable of deciding the current question. Record
commit, dirty state, command, environment/software versions, runtime, hardware
when relevant, coefficient domain, convention version, inputs, seed, bounds,
outputs, and checksums.

For reusable or claim-supporting runs, create a manifest from
[computation-manifest.json](assets/computation-manifest.json). Validate it with:

```bash
python3 <skill-directory>/scripts/validate_manifest.py <manifest.json>
```

The exact skill-directory syntax is tool-specific; locate this installed skill
rather than guessing a repository-relative path.

## Interpret conservatively

Return one of:

- implementation and finite assertion verified in the stated range;
- result reproduced but implementation not independently validated;
- conditional on numerical tolerance, random sampling, or an external library;
- inconsistent with a benchmark or invariant;
- not reproducible in the available environment;
- inconclusive because of resource bounds;
- counterexample found to the mathematical claim.

If a failure occurs, distinguish mathematical counterexample, implementation
bug, environment/configuration failure, and insufficient resources.

After a successful bounded run, identify which observed features are structural
and which may be case-specific. Recommend a larger bound only when it tests a
named alternative, audits the implementation, or enters a genuinely new
regime; accumulating another success is not by itself a research decision.

## Persist and report

Store reusable scripts in the project's designated checks/computation area, not
inside a prose log. Preserve raw outputs only when justified; otherwise record
checksums and a regeneration command. Update claims/status only when the result
changes research state.

Report the contract, code paths, command, provenance, checks performed, exact
result, non-claims, residual risks, structural features implicated, and either
a candidate uniform argument or the cheapest check that discriminates named
alternatives.
