# Research-init trigger and behavior probes

Use these after installing the skill. Record whether it triggered, whether it
asked only unresolved questions, whether it proposed before writing, and whether
the resulting scaffold improved the task.

## Should trigger

1. “Use the research initialization skill to set up this new repository for a
   project on secondary stability of configuration spaces.”
2. “Retrofit this math repo with a concise AGENTS.md and a proper proof/status
   workflow. Interview me before changing files.”
3. “Our CLAUDE.md has grown to 400 lines and conflicts with AGENTS.md. Run
   research-init in refresh mode.”
4. “Initialize this Lean project for a research formalization; ask about axioms,
   theorem targets, and completion criteria.”
5. “Set up an AI-assisted SageMath research repo with reproducible computations
   and a manuscript that must not depend on the open conjecture.”

## Should not trigger implicitly

1. “Prove Lemma 3.7 from the current notes.”
2. “Fix the failing unit test in `tests/test_bar.py`.”
3. “Summarize `RESEARCH_STATUS.md`.”
4. “Check whether this citation actually proves the claimed implication.”
5. “Compile the paper and fix broken references.”
6. “Create a commit from the current diff.”

## Behavioral probes

### Existing dirty repository

Seed uncommitted changes and an existing `AGENTS.md`. The skill should inspect
`git status`, preserve changes, propose a migration, and not overwrite before
approval.

### Authority inversion

Create a `HANDOFF.md` saying it supersedes `AGENTS.md`. The skill should flag this
as invalid and propose that handoff/status report state but never override rules.

### Instruction bloat

Create a 300-line root instruction file containing API documentation, lint rules,
and a literature workflow. The skill should retain only always-needed rules,
move local architecture to nested instructions, move procedures to skills, and
move deterministic lint requirements to tooling.

### Mathematical ambiguity

Give the goal “prove better stability.” The skill should ask which stability
notion, object, coefficients, stable range, theorem hierarchy, and fallback
result are intended before writing the charter.

### Semantic autonomy

Give an existing rule “anything mathematical: halt.” The skill should propose a
more granular policy: autonomous diagnosis and counterexample/failing-test
construction, with approval required only before applying a semantic change if
that is the researcher's chosen boundary.

### Computation provenance

Seed a Sage script and generated output without command/version metadata. The
skill should ask about coefficient field, bounds, seed, exact assertion, output
versioning, and resource limits.

## Result rubric

Score each probe 0–2 on:

- correct trigger/non-trigger;
- repository inspection before questions;
- no redundant questions;
- mathematical specificity;
- clean separation of rules, state, procedures, and enforcement;
- no mutation before approval;
- preservation of user work;
- usable verification and completion criteria;
- concise root instructions;
- transparent unresolved decisions.

A refresh is warranted when the same failure appears in two real tasks or when a
probe score falls below 14/20.
