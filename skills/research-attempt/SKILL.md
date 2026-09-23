---
name: research-attempt
description: >-
  Run one bounded, auditable mathematical research route: a proof attempt, reduction, counterexample search, source-dependent implication, or claim-supporting computation. Use when the user explicitly asks to attack a research question or invokes this skill. Do not use for a sustained multi-route investigation that continues after failed approaches, routine editing, explanation, or an unchanged verification rerun.
---

# Bounded mathematical research attempt

Pursue one route far enough to obtain a durable result, a precise obstruction,
or a well-identified next implication. This is a work-package boundary, not a
reason to stop a broader user-authorized investigation. For sustained or
multi-route requests, use the available `research-program` workflow, or continue
successive attempts directly if it is unavailable. Do not turn the log into a
transcript.

## Resolve project context

Determine the repository root first. Read the applicable `AGENTS.md`, the
current status summary when present, and only the files relevant to the target.
Search a large status, claims file, or history index for relevant sections
rather than loading it wholesale. Resolve project roles from the paths
named there. When not explicit, look for the standard alternatives in
[project-context.md](references/project-context.md). Interpret every project
path relative to the repository root, never relative to this installed
`mathbox:research-attempt` plugin skill (or its standalone installation).

If the project uses `.mathbox/`, use the available `research-state` skill's
brief check and goal handoff, opening full details only for the relevant
contracts and evidence. Check freshness and the target's dependency closure
before trusting a status label. Otherwise use the existing prose evidence records. A clean ledger
is bookkeeping evidence, not mathematical verification.

## Open the route

1. Inspect the worktree and preserve unrelated changes.
2. Normalize the target:
   - exact statement or decision;
   - quantified objects and source/target types;
   - hypotheses, coefficient domain, grading, variance, signs, finiteness,
     completion, equivariance, and range;
   - current evidence status and dependencies.
3. Search the research-history index for the target and nearby mechanisms,
   then open only the nearest relevant records needed to find the first failed
   or unproved implication.
4. State a falsifiable success criterion, a failure/no-go criterion, and the
   cheapest decisive example, source check, or computation.
5. Choose one route within the current program. Match it against prior failed
   mechanisms, not merely prior titles. Reopening one requires a new input,
   invariant, construction or hypothesis that addresses its first failed step.

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
- Route every load-bearing question about what an external mathematical source
  proves through the available `literature-check` skill
  (`mathbox:literature-check` in plugin installations). That workflow checks an
  authorized project-local cache before fetching. If the skill is unavailable,
  perform the exact-source check directly with available tools. If the source
  cannot be verified, leave the input conditional; snippets and memory do not
  discharge it.
- For computation, separate the mathematical claim from the finite assertion
  implemented. Record domain, bounds, seed, versions, inputs, runtime, and
  non-claims; use the `mathbox:computation-audit` plugin skill when
  appropriate.
- Before calling a finite sweep exhaustive, compare the claimed population with
  the actual iterator, filters and skipped cases. Sampling requires a proved
  coverage reduction.
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
- Write one self-contained route record in the project-designated research
  records directory, or `research/records/` when none is designated. Use the
  format and filename rules in [route-card.md](references/route-card.md).
- Append one compact linked entry to the project-designated route index. In a
  small flat history this is normally `RESEARCH_LOG.md`; in a sustained
  program it may be a program/phase index reached from the short top-level
  history entry point. Do not add the same route to both levels or put route
  details, commands, or dead ends in an index. If a hierarchical project has
  no designated route index, resolve that location under its edit rules before
  appending; do not turn the top-level program entry into a flat route log.
- Update live status or claim obligations only when project state changed.
- Treat live status as current state, not chronology. Keep its latest full
  verification summary and link the route record or manifests for older runs.
  Do not add another full checkpoint story. Replace a stacked dated narrative
  with current facts and a link only when that narrative already has a durable
  home (an indexed record, manifest, or closeout) and the project's edit policy
  permits it. Otherwise leave it in place and report that compaction needs a
  `research-program` closeout or `mathbox:research-init` migration.
- In an executable ledger, record only changed contracts, evidence, reviews,
  and route outcomes. A session alone needs no event. Use a prevalidated batch
  for several necessary events while preserving their distinct types.
- Once indexed, keep the record and index entry immutable. Record a correction
  in a new file with a `Corrects:` link and append it to the same designated
  route index. Do not create a program closeout for each attempt.
- If the index still contains legacy long-form entries, do not rewrite them as
  a side effect of this attempt. Use the new format prospectively and report
  that a `mathbox:research-init` migration remains pending.
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
