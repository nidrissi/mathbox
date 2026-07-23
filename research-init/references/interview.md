# Research-init interview guide

Ask only questions not already answered by repository evidence. Use short batches
and summarize the answers after each batch. The researcher may defer a choice;
record it as unresolved rather than guessing.

## Batch A — mathematical target

1. State the research question as a falsifiable mathematical claim or decision.
2. What is the next artifact another mathematician can review: lemma note,
   counterexample, computation, preprint section, software result, or formal proof?
3. What is the strongest target, the intermediate theorem, and an acceptable
   obstruction/counterexample/reduction if the strong target fails?
4. Which hypotheses are fixed for this phase, and which are intended to be relaxed?
5. Which distinctions must never be conflated (for example chain vs homology,
   ordered vs unordered, connected vs disconnected, strict vs homotopy coherent)?
6. What would conclusively show that the active route is unproductive?

## Batch B — conventions and evidence

1. Coefficient ring/field, characteristic, completion, finiteness, connectivity,
   or model-category assumptions?
2. Grading, suspension, Koszul sign, variance, symmetric-group action, duality,
   orientation, and naming conventions?
3. Which results are currently proved, externally proved, computationally
   verified, heuristic, conjectural, conditional, or failed?
4. Which files contain durable proofs, and which merely report status?
5. What qualifies as a substantive attempt worth logging?
6. Which minimal examples, edge cases, or counterexample families are mandatory?

## Batch C — literature and novelty

1. Which sources or researchers are indispensable, and which databases should be
   searched?
2. Must exact theorem versions, coefficients, and notation translations be logged?
3. What novelty language is acceptable before expert review?
4. Are local PDFs licensed or private, and may their contents be quoted or only
   cited/summarized?
5. Is network access allowed for literature searches and package metadata?

## Batch D — repository operations

1. Canonical code, proof, manuscript, data, archive, and generated-output paths?
2. Protected paths and files requiring explicit approval?
3. Setup command and fast, targeted, full, and document checks?
4. Resource caps: time, RAM, core count, arity/weight/degree, disk, or API budget?
5. Are dependencies pinned? May agents install or upgrade them?
6. May agents create branches/worktrees, commit, push, open pull requests, publish,
   email, or use external services?
7. For a suspected semantic bug, should the agent diagnose and propose only, or
   may it apply a fix after producing a failing test/counterexample?
8. Which generated artifacts are versioned, ignored, or immutable?

## Batch E — completion and collaboration

1. What exact evidence must appear in the final report?
2. Which checks are mandatory for which risk classes?
3. Should an independent agent/reviewer try to refute important results?
4. Will multiple agents work concurrently? Which tasks are read-heavy versus
   write-heavy, and how will worktrees/ownership prevent collisions?
5. How often should status and logs be updated: per route checkpoint, daily,
   milestone, or before handoff?

## Profile-specific follow-ups

### Proof-first

- Is a computer-assisted proof admissible, and what certificate or replay is
  required?
- What is the theorem dependency graph?
- Which local sign/convention failure should trigger a global review?
- Which proof obligations need independent checking?

### Manuscript

- Which source is the assembled live paper?
- Which sections/results are submission-ready, provisional, or excluded?
- Citation/style/build commands and journal constraints?
- May the agent rewrite mathematical prose, or only propose edits?
- Must the current paper remain independent of an open flagship theorem?

### Computation/software

- Exact arithmetic versus numerical approximation?
- Canonicalization, cache, serialization, and parallelism invariants?
- Expected output schemas and filename contracts?
- Which small cases have trusted answers?
- When is the full test suite required despite its cost?

### Formalization

- Target prover and pinned toolchain?
- Trusted axioms, classical principles, quotient constructions, and library style?
- Is the objective executable formalization, theorem statement design, or porting?
- What counts as proof completion: no `sorry`, no new axioms, linter clean, or CI?

### Mixed

- Which profile controls conflicts and final completion?
- Which artifacts are primary evidence and which are explanatory mirrors?
