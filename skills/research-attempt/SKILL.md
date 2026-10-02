---
name: research-attempt
description: >-
  Run one bounded, auditable mathematical research route: a proof attempt, reduction, counterexample search, or a computational or source-based attack. Use when the user explicitly asks to attack a research question or invokes this skill. Do not use to audit an existing proof, computation or source alone, or for a sustained multi-route investigation that continues after failed approaches, routine editing, explanation, or an unchanged verification rerun.
---

# Bounded mathematical research attempt

Pursue one route to a durable result, precise obstruction or next implication.
A bounded package does not end a broader authorized investigation. Continue with
available `research-program` (`mathbox:research-program` in plugin installations),
or directly if unavailable. Honor existing authority; do not turn the log into
a transcript.

## Resolve project context

Read applicable instructions and current summary; search large files for the
target rather than loading them wholesale. Resolve designated paths, or use
[project-context.md](references/project-context.md); paths are project-relative,
never skill-relative. Follow history entry points to relevant route indexes.
Use available `research-state` (`mathbox:research-state` in plugin installations)
for brief checks and registered-goal handoffs, inspecting relevant contracts,
reviews and dependency closure before trusting labels. If unavailable, inspect
prose evidence directly. Clean bookkeeping is not mathematical verification.

## Open the route

1. Inspect the worktree and preserve unrelated changes.
2. Normalize the target:
   - exact statement or decision;
   - quantified objects and source/target types;
   - hypotheses, coefficient domain, grading, variance, signs, finiteness,
     completion, equivariance, and range;
   - current evidence status and dependencies.
3. Search the history entry point for the target and nearby mechanisms,
   then open only the nearest relevant records needed to find the first failed
   or unproved implication.
4. State falsifiable success and failure/no-go criteria, and the cheapest decisive
   example, source check or computation.
5. Choose one program route and compare mechanisms with prior failures.
   Retrying a mechanism with an established
   obstruction requires a new input, invariant, construction or hypothesis that
   addresses its first failed step. An unresolved step is not an obstruction;
   resuming an untried or deferred continuation needs a concrete next action,
   not a new mathematical premise. State what changes when resuming a stalled
   step: sub-step, method, tool or resource; do not rerun unchanged.

Use the route card in [route-card.md](references/route-card.md) when a durable
entry will be needed.

For an obstructed structural route, consult the relevant moves in
[structural-moves.md](references/structural-moves.md). Turn a proposed analogy
into a specific comparison, obstruction or discriminating invariant.

## Execute

- Begin with the smallest typed case capable of changing the conclusion.
- Verify that the chosen example, representative and every intermediate
  construction belong to the claimed domain; a convenient surrogate needs an
  explicit comparison theorem before it can decide the route.
- Search actively for counterexamples, boundary cases, convention failures,
  circularity, and missing hypotheses.
- Check nullary/unary or minimum-parameter cases and absolute degrees whenever
  a unit, augmentation, suspension or induction boundary is involved.
- Do not repair a failed type, sign, variance, normalization, or completion
  check by silently changing the statement or convention.
- Use the available `literature-check` skill (`mathbox:literature-check` in plugin
  installations) for external theorem questions and `computation-audit`
  (`mathbox:computation-audit`) for finite evidence. If unavailable, perform the
  exact-source or finite-evidence checks directly and disclose limits. Record
  computational domain, bounds, seed, versions, inputs, runtime and non-claims;
  leave unverified sources conditional.
- Before calling a finite sweep exhaustive, compare the claimed population with
  the actual iterator, filters and skipped cases. Sampling requires a proved
  coverage reduction.
- After bounded success, identify uniform structural features versus case-specific
  coincidences and formulate a uniform lemma or obstruction before extending
  the case ladder. Another finite case must discriminate named alternatives or
  reach a new regime.
- A timeout, failed search, or bounded computation is not a universal negative
  result.
- A change to a registered convention requires explicit owner approval unless
  the project instructions already authorize that exact correction.

## Classify the outcome

Use one of:

- proved as written;
- correct only after a stated restriction;
- externally proved in the exact required form;
- conditional on a named unverified input;
- computationally verified only in a stated range;
- heuristic or conjectural;
- refuted, with a valid counterexample (smallest only in a stated search order
  unless every smaller case is excluded);
- incomplete, with the smallest missing implication;
- ill-typed or internally inconsistent;
- inconclusive, with the first unresolved implication.

Read [evidence-model.md](references/evidence-model.md) before assigning labels or
promoting claims. Outcome describes this attempt; evidence label describes the
strongest surviving statement. An unsuccessful construction adding no evidence
against an independently supported target leaves its label intact. If the target
itself is ill-typed or its support invalidated, report the defect, affected evidence
and dependents; use available `proof-audit` (`mathbox:proof-audit` in plugin
installations), or audit directly if unavailable, and correct authorized durable
status. Do not treat the old label as reliable or infer refutation from a failed
construction. Never upgrade evidence for effort or persuasive prose.

Classify this attempt separately from the route's disposition. If a construction
is unresolved, say what you could not establish; do not infer that it is
impossible. Preserve other proposed continuations as untried, obstructed with
evidence, or deferred with a reason and resumption condition. An inconclusive
attempt or a resource limit alone does not close the route. Return unfinished
work to the program, or retain a continuation handoff when only this bounded
attempt was authorized. Closing an unresolved route needs an account of why no
known continuation remains executable within its stated scope.

## Persist at natural checkpoints

Exploration may remain scratch work. Create durable records when the route
produces reusable mathematics, a counterexample, a corrected dependency, a
material blocker, a convention decision, or a claim-supporting computation.

- Put reusable proof or obstruction details in the project's durable proof
  location.
- Write one self-contained route record in the project-designated research
  records directory, or `research/records/` when none is designated. Use the
  format and filename rules in [route-card.md](references/route-card.md).
- Append one compact entry to the designated route index, never at both history
  levels; see the route card. Update status only for material changes.
- Replace an old live narrative with a link only once it has a durable home,
  edit policy permits it and `pin-impact` finds no conflict. Otherwise report
  pending program closeout or repository migration.
- In a ledger, record changed contracts, evidence, reviews and route outcomes;
  for an open continuation that must outlive the session, also record a run result
  with a `continue` reconciliation through available `research-state`
  (`mathbox:research-state` in plugin installations). If unavailable, preserve
  equivalent prose fields and disclose that no events were recorded.
- When delegated or parallel, write only in assigned scope. Return the route
  record and proposed index/status/ledger updates, base checkpoint, actual inputs
  and artifact hashes to the coordinator; do not edit shared live state or emit
  a separate deferred packet.
- For authorized standalone persistence on a non-writing host, use research-state's
  deferred packet contract and say ingest is pending.
- Once indexed, keep the record and index entry immutable. Record a correction
  in a new file with a `Corrects:` link and append it to the same designated
  route index. Do not create a program closeout for each attempt.
- Preserve legacy long-form entries; use the new format prospectively. Route
  migration to available `research-init` (`mathbox:research-init` in plugin
  installations), or report it pending if unavailable.
- Do not integrate into a manuscript unless that is separately requested.

## Verify and report

Run the narrowest relevant documented check, then broader checks only when their
risk trigger applies. Report:

1. target and route;
2. attempt outcome, evidence label, route disposition and continuations;
   base checkpoint and actual inputs when part of a program;
3. decisive derivation, source, counterexample, or computation;
4. durable files changed;
5. commands run and exact scope;
6. unresolved assumptions and the next mathematical question; when evidence is
   bounded, include its uniform route or discriminating check.
