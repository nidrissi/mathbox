---
name: referee
description: >-
  Referee a whole mathematical manuscript for correctness, edge cases, notation, exposition and claim calibration. Use for a referee report, whole-paper stress test, or section-by-section manuscript audit. Do not use for a focused claim or proof audit, proofreading alone, a standalone citation or computation check, answering referee comments on one's own paper, or developing new proofs.
---

# Mathematical manuscript referee

Assess the manuscript supplied using native reasoning and delegation; do not
install external review runtimes, provider SDKs or credentials.
Default to leaving the manuscript unchanged. A review request authorizes review
artifacts, not rewriting proofs, contacting authors or submitting a report.

## Establish scope and prepare

1. Read applicable project instructions and resolve the authoritative manuscript,
   its version, source/project boundary, and requested review scope. Ask before
   choosing between genuinely competing manuscripts or unclear boundaries.
2. Focused obligations use the available specialists below; whole-paper coverage
   and synthesis remain this skill's responsibility.
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
   errors without reading outside the authorized boundary; ask before widening
   `--root`. Do not claim complete coverage until resolved. If only a PDF, pasted text or a
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

When user/project instructions prescribe models or reasoning, read
[model-assignments.md](references/model-assignments.md); otherwise inherit host
defaults and record null requested fields. Use only exposed native controls;
disclose any fallback.

Follow the host's delegation authorization rules. Skill invocation authorizes
subagents only if those rules permit it; where explicit user delegation is
required, obtain it or use disclosed sequential self-review. Honor existing
authorization without asking again.

For each pass assign a unique `pass_id` and issue prefix, e.g. `corr-s3` and
`corr-s3-F`. A child writes only `passes/<pass_id>.json`. Give it resolved paths
for [review-protocol.md](references/review-protocol.md), its lane file and snapshot
unit files (paste text only if it cannot read files), exact source revision,
necessary dependencies and its disjoint scope. Withhold prior findings from
correctness/adversarial passes; whole-paper lanes may receive unverified leads.
Children return exact specialist obligations; the coordinator arranges fresh
confirmation. They do not launch specialists unless explicitly assigned.

Several compatible lanes may share a pass and coupled units may share an agent.
Bound concurrency by host capacity and mathematical usefulness; five-dimensional
coverage, rather than agent count, is the invariant. Apply model preferences
through native controls, with fresh context when required. Allow context requests.

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

Follow [final-referee.md](references/final-referee.md) and
[output-contract.md](references/output-contract.md) for dispositions, concerns
and the ordered report. Recheck raw findings against full source and specialist
evidence; reviewer agreement is not proof. Keep raw returns separate from final
conclusions, and disclose partial coverage. Absence of findings certifies neither
whole-paper correctness nor novelty.

For a revised manuscript, use the modest comparison/reuse rules in
[preparation.md](references/preparation.md). Unchanged unit text is only a
candidate for reuse: check context, dependencies, lane-contract revision and
actual prior artifacts. Rerun whole-paper passes and final synthesis on any
source change. Do not silently refresh old evidence or erase earlier findings.
