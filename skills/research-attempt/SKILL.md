---
name: research-attempt
description: >-
  Run one bounded, auditable mathematical research route: a proof attempt, reduction, counterexample search, source-dependent implication, or claim-supporting computation. Use when the user explicitly asks to attack a research question or invokes this skill. Do not use for routine editing, explanation, or an unchanged verification rerun.
---

# Bounded mathematical research attempt

Pursue exactly one route far enough to obtain a durable result, a precise
obstruction, or a well-identified next implication. Do not turn the research
log into a transcript.

## Resolve project context

Determine the repository root first. Read the applicable `AGENTS.md` and only
the current files relevant to the target. Resolve project roles from the paths
named there. When not explicit, look for the standard alternatives in
[project-context.md](references/project-context.md). Interpret every project
path relative to the repository root, never relative to this installed skill.

## Open the route

1. Inspect the worktree and preserve unrelated changes.
2. Normalize the target:
   - exact statement or decision;
   - quantified objects and source/target types;
   - hypotheses, coefficient domain, grading, variance, signs, finiteness,
     completion, equivariance, and range;
   - current evidence status and dependencies.
3. Find the nearest prior attempt and its first failed or unproved implication.
4. State a falsifiable success criterion, a failure/no-go criterion, and the
   cheapest decisive example, source check, or computation.
5. Choose one route. Do not silently broaden to a second work package.

Use the route card in [route-card.md](references/route-card.md) when a durable
entry will be needed.

## Execute

- Begin with the smallest typed case capable of changing the conclusion.
- Search actively for counterexamples, boundary cases, convention failures,
  circularity, and missing hypotheses.
- Do not repair a failed type, sign, variance, normalization, or completion
  check by silently changing the statement or convention.
- Verify every load-bearing external theorem in its exact needed form. Follow
  the `literature-check` protocol when available.
- For computation, separate the mathematical claim from the finite assertion
  implemented. Record domain, bounds, seed, versions, inputs, runtime, and
  non-claims; use the `computation-audit` protocol when appropriate.
- After any bounded success, pause before extending the arity, range, or case
  ladder. Identify the minimal structural features used, separate uniform
  features from case-specific coincidences, and formulate the candidate
  uniform lemma or obstruction. Run another finite case only if it
  discriminates between named alternatives or enters a genuinely new regime.
- A timeout, failed search, or bounded computation is not a universal negative
  result.
- A change to a registered convention requires explicit owner approval unless
  the project instructions already authorize that exact correction.

## Classify the outcome

Use one of:

- proved as written;
- proved after an explicit restriction;
- conditional on a named unverified input;
- computationally verified only in a stated range;
- heuristic or conjectural;
- refuted, with the smallest counterexample found;
- ill-typed or incomplete;
- inconclusive, with the first unresolved implication.

State the strongest surviving result. Never upgrade evidence because the route
was long or persuasive.

## Persist at a natural checkpoint

Exploration may remain scratch work. Create durable records when the route
produces reusable mathematics, a counterexample, a corrected dependency, a
material blocker, a convention decision, or a claim-supporting computation.

- Put reusable proof or obstruction details in the project's durable proof
  location.
- Append one route-level log entry; do not record every command or dead end.
- Update live status or claim obligations only when project state changed.
- Treat live status as current state, not chronology. Keep its latest full
  verification summary and link the route log or manifests for older runs.
- Keep historical entries immutable; append corrections.
- Do not integrate into a manuscript unless that is separately requested.

Evidence labels and promotion rules are summarized in
[evidence-model.md](references/evidence-model.md).

## Verify and report

Run the narrowest relevant documented check, then broader checks only when their
risk trigger applies. Report:

1. target and route;
2. outcome and evidence label;
3. decisive derivation, source, counterexample, or computation;
4. durable files changed;
5. commands run and exact scope;
6. unresolved assumptions and the next mathematical question; when evidence is
   bounded, include its uniform route or discriminating check.
