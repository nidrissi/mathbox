---
name: referee
description: >-
  Conduct a referee-style assessment of a mathematical manuscript as a whole, covering correctness, adversarial edge cases, notation and consistency, exposition, and claim calibration. Use for a referee report, whole-paper stress test, or section-by-section manuscript audit with final reconciliation against the full source. Do not use for a focused claim or proof audit, mechanical proofreading alone, a standalone citation or computation check, or developing new proofs and research routes.
---

# Mathematical manuscript referee

Assess the manuscript actually supplied. Port mathematical review methodology,
not an LLM runtime: use the host's native reasoning and delegation, never the
Math Scout executable, provider SDKs, credentials, pricing or model tables.
Default to leaving the manuscript unchanged. A review request authorizes review
artifacts, not rewriting proofs, contacting authors or submitting a report.

## Establish scope and prepare

1. Read applicable project instructions and resolve the authoritative manuscript,
   its version, source/project boundary, and requested review scope. Ask before
   choosing between genuinely competing manuscripts or unclear boundaries.
2. Use `proof-audit` for one lemma, theorem dependency or proof. Use
   `proofread-math` for mechanical proofreading alone, `literature-check` for a
   standalone source question, and `computation-audit` for a standalone
   computation. Developing a new argument belongs to `research-attempt` or
   `research-program`. A whole-paper report remains this skill's responsibility
   when it delegates particular obligations.
3. Read [review-protocol.md](references/review-protocol.md) before reviewing.
   Its severity, confidence, evidence and limited-context rules apply to every
   pass, including synthesis.
4. For LaTeX sources, use the optional standard-library helper following
   [preparation.md](references/preparation.md). Resolve its installed directory;
   manuscript paths are relative to the project, not this skill. For example:

   ```bash
   python3 <skill-directory>/scripts/prepare_manuscript.py paper.tex --root PROJECT --output RUN
   ```

   Use a new review directory in the project's designated review area, or
   `referee/<run>/` at the project root if none is designated. Never write
   review artifacts under `.mathbox/`: that directory belongs to a
   research-state ledger, which pins evidence only from outside it. Creating a
   review directory never initializes a ledger.
5. Read the manifest, preparation limits and full source. Resolve preparation
   errors before claiming complete coverage. If only a PDF, pasted text or a
   host without execution is available, build the same scope/coverage inventory
   manually, use real page/result locators, and disclose extraction limits.

## Survey the full manuscript

Identify central claims, hypotheses, conventions, internal dependencies,
external-source leaves, and computational leaves. Map each main theorem to
its load-bearing proofs and sections. Read abstract/introduction together with
actual theorem statements. Extracted context is an index, not proof evidence;
read referenced definitions and arguments in full.

Choose review units by dependency structure: one section, a theorem and proof,
several tightly coupled sections, or one whole-paper question. Include
substantive front matter and appendices. Check units marked non-mathematical
before skipping them; bibliography remains available to whole-paper passes.

## Cover five dimensions

Read each lane contract when assigning or performing that lane:

| Lane | Scope and contract |
|---|---|
| Correctness | Every substantive unit and load-bearing proof; [correctness.md](references/reviewers/correctness.md) |
| Adversarial | Concrete boundary cases, degeneracies, quantifiers, uniformity and reductions in those units; [adversarial.md](references/reviewers/adversarial.md) |
| Exposition | Proof architecture, motivation and signposting for an expert; [exposition.md](references/reviewers/exposition.md) |
| Notation | Whole manuscript, including definitions, conventions and cross-references; [notation.md](references/reviewers/notation.md) |
| Claims | Whole manuscript, comparing headline promises with delivery and evidenced framing; [claims.md](references/reviewers/claims.md) |

Read [model-assignments.md](references/model-assignments.md) before assigning
passes, including final reconciliation. Resolve user/project model and reasoning
preferences against the host's available native controls. Prefer the prescribed
settings; continue with a disclosed fallback when they cannot be applied.

Use isolated native subagents where supported and authorized. Apply resolved
settings through the native delegation controls, not merely in the child
prompt. Give each a specific unit/question, lane contract, shared protocol,
exact source revision, raw source, necessary dependency context, and disjoint
output scope. Let agents
request more context; do not give a fresh correctness auditor the suspected
answer. Bound concurrency by the host's capacity and mathematical usefulness.
Several lanes may share a pass, and coupled sections may share an agent; do
not spawn one agent per section per lane mechanically. Coverage of all five
dimensions is the invariant, not the number of agents. Split passes when their
model assignments differ, unless a disclosed fallback makes them compatible.

Without delegation, perform separate sequential passes and label their
provenance as self-review. Preserve raw returns and disclose failed, partial,
unreviewed or reused scopes. Do not count a launch as completed coverage.
Record requested settings, observed execution settings and fallback reasons
alongside coverage and structured findings using
[output-contract.md](references/output-contract.md). An empty issue list is
valid. Keep low-confidence leads distinct from demonstrated defects.

## Confirm focused obligations with Mathbox

Resolve available skills by name (`mathbox:<name>` in plugin installations,
bare names when standalone). Read and follow the selected specialist contract.
Keep this package independently installable: if a specialist is absent, perform
the bounded check directly with available tools, report that fallback, and
leave anything not settled conditional.

- **`proof-audit`:** use for serious mathematical findings that become concrete
  obligations, such as whether Lemma 5.3 implies Proposition 5.7 under the
  actual hypotheses. Supply the exact statements, dependency context and raw
  argument for a fresh derivation. A lane flag alone is not confirmation.
- **`literature-check`:** use when a conclusion depends on what an external
  theorem establishes or on a material prior-art claim. State the bounded
  source question, exact version/generalities needed and existing source
  record. Follow its authorized cache-first workflow. Do not search every
  citation. If the source is unavailable, retain a conditional obligation,
  never a fabricated prior-art verdict.
- **`computation-audit`:** use for load-bearing scripts, tables, enumerations
  or numerical evidence. Compare claimed objects/population with actual
  implementation and bounds. Run only justified authorized commands; bounded
  success and sampled coverage do not prove a universal theorem.
- **`proofread-math`:** use only for a requested mechanical proofreading
  component. Keep it separate from exposition assessment and preserve the
  review-only default unless manuscript edits were requested.
- **`research-state`:** optional when an initialized ledger already exists
  and provenance recording is useful and authorized. Pin actual statements,
  evidence and reports from the review directory; ledger integrity does not
  validate mathematics. Do not initialize it or create a parallel state
  database merely for refereeing.

## Reconcile and report

Read [final-referee.md](references/final-referee.md). Inspect every important
raw finding independently against the full manuscript and specialist evidence.
Verify its searchable quote, exact claim, hypotheses and dependency impact;
search globally before alleging undefined notation or absent results. Reject
false positives, merge duplicate defects, preserve distinct consequences, and
recalibrate severity and confidence. Agreement between reviewers is not proof.

Retain raw findings separately from final conclusions, with the disposition
and reason for each in the reconciliation record. Write a synthesized report
in the stable structure from [output-contract.md](references/output-contract.md),
including exact coverage, unresolved leaves, and actual checks. Do not
concatenate reviewer returns or turn exposition concerns into mathematical
invalidity. A partial review can deliver a report but must say it is partial;
absence of findings never certifies the whole paper or its novelty.

For a revised manuscript, use the modest comparison/reuse rules in
[preparation.md](references/preparation.md). Unchanged unit text is only a
candidate for reuse: check context, dependencies, lane-contract revision and
actual prior artifacts. Rerun whole-paper passes and final synthesis on any
source change. Do not silently refresh old evidence or erase earlier findings.
