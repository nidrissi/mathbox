# Referee integration validation

Validation on 2026-09-30 covers the native `referee` skill, its deterministic
preparation helper, package integration, and synthetic manuscript trials.
The [migration map](referee-migration.md) records the architectural decisions
made before implementation. Math Scout's methodology is adapted; its runtime,
provider adapters and dependencies are excluded.

## Behavioral evidence

Fresh executors received the skill, task and raw manuscript, without the
expected answers in [`evals/cases.json`](../evals/cases.json). They used isolated
temporary projects and preserved raw passes separately from final reports.
All five dimensions were covered using sequential self-review. The core case
also used a fresh isolated `proof-audit` agent for three concrete obligations.
The source and enumeration specialist passes were explicitly self-review.
A separate grader independently checked the derivations, source quotations,
coverage, reconciliation, specialist provenance and actual computation records.

| Case | Observed result | Evidence |
|---|---|---|
| Correctness, edge cases and claims | Invalid cancellation confirmed by a counterexample; admitted $n=0$ case refutes the secondary theorem; all-fields headline exceeds characteristic-zero delivery. Valid triangular proofs remain valid. | [Core report](../evals/results/referee-v1/core/report.md), [focused proof audit](../evals/results/referee-v1/core/historical/specialists/proof-audit.md) |
| Cross-section false positive | Preserved the prior undefined-$\tau$ suspicion and dismissed it using the earlier definition. No unresolved notation question remains. | [Context report](../evals/results/referee-v1/context/report.md), [reconciliation](../evals/results/referee-v1/context/reconciliation.json) |
| Exposition | Verified the telescoping identities, algebra and $n=0$; retained a moderate signposting concern with a concrete remedy. | [Exposition report](../evals/results/referee-v1/exposition/report.md) |
| Unavailable external source | Focused literature/proof checks identify the rational-to-arbitrary-ring obligation while leaving authentication, definitions and applicability conditional. Correctness/adversarial coverage is partial. No source content or prior art is invented. | [Source report](../evals/results/referee-v1/source/report.md), [literature check](../evals/results/referee-v1/source/historical-specialists/literature-check.md) |
| Filtered enumeration | Executed supplied code: sixteen candidates, eight checked. A separate full-domain check finds eight failures; $(1,0,0,0)$ refutes the stated theorem. The passing filtered assertions do not establish it. | [Enumeration report](../evals/results/referee-v1/enumeration/report.md), [computation audit](../evals/results/referee-v1/enumeration/historical-specialists/computation-audit.md), [actual result](../evals/results/referee-v1/enumeration/computations/domain-audit/result.json) |

Eight [routing probes](../evals/results/referee-v1/routing/routing.json) selected
appropriate primary skills from descriptions and OpenAI metadata: focused proof,
proofreading, citation, computation, bounded new proof, sustained research, and
two whole-manuscript requests. This is selection evidence, not an end-to-end
measurement of either host's automatic router or explicit invocation controls.

The trials exposed a project-relative main-input bug in the helper. It was
fixed, given a direct regression, and the affected trials were rerun. A further
input-file EOF boundary regression now protects a caller's structural command
from a child file's trailing comment or control word. Preparation snapshots and
unchanged mathematics were rechecked after that change; prior evidence reuse
is recorded rather than relabeled as fresh execution.

The context trial exposed two artifact issues. One original raw quotation had
extra backslashes; the [original return](../evals/results/referee-v1/context/passes/05-current-claims.json)
and its [exact correction](../evals/results/referee-v1/context/passes/05-current-claims-quote-correction.json)
are both retained. Final reconciliation uses the correction. Informal historical
suspicions also lacked the fields of a new structured finding. The output
contract now explicitly preserves them as prior leads with unknown historical
fields, then reconciles them without inventing provenance.

The independent [grading record](../evals/results/referee-v1/grading.json) and
[grader's explanation](../evals/results/referee-v1/grading.md) distinguish final
case outcomes from the original quote-discipline deviation. All five final
cases and eight primary routing selections pass; original context quotation
discipline is partial with the correction recorded. These synthetic cases
establish only their observed behavior; they do not measure frontier research
performance or establish superiority over Math Scout's models. Most passes
are self-review, and independent grading can still share model errors.

PDF-only execution, absent-specialist fallback and a substantive changed-context
reuse scenario have behavioral contract cases but were not forward-tested here.
Unsafe/missing inputs are covered by helper regressions, not a live partial-review
trial. The executed reuse checks concern preparation changes on unchanged
mathematics; they do not demonstrate dependency-aware reuse after a definition
or theorem changes.

## Revisions and retained records

The latest executed preparation snapshots record contract SHA-256
`b9b52b576ec3c6fffe062a615fda3ba7865527f35d047ed91f31f3069b552bd7`.
The subsequent prior-lead clarification changes the current contract to
`5e41983f5185a3447e01e102947cc7d88421a090a44ea7c52105f1a5732bdc56`.
It changes neither the helper nor lane instructions. The grader checks current
contract compatibility separately; historical hashes are unchanged. Older
specialist returns carry their own actual revision and reuse records.

The [artifact inventory](../evals/results/referee-v1/artifact-inventory.json)
maps original temporary-project locators to retained byte-for-byte copies,
with sizes and SHA-256 hashes: 106 solver/routing records and eight grading
records. The grader checked the initial 91 retained records; fifteen additional
raw derivation notes it cites were retained afterwards without rewriting its
original grading output. Redundant prepared TeX copies and earlier complete
snapshots are omitted; the five public fixtures reproduce the exact manuscript
bytes in the retained manifests. Original absolute paths inside raw records
are historical execution provenance, not installation requirements. The
private reference archive and `.math-scout/` directory remain outside the
distribution.

## Preparation comparison

The [comparison record](../evals/results/referee-v1/preparation-comparison.json)
contains seventeen passing API-free comparisons against the user-supplied
Math Scout `0.3.0a1` archive. Six cases preserve behavior, eight implement
deliberate improvements, and three adopt stricter failure handling. Improvements
include inline literals, commented literal openers, deeply balanced titles,
input EOF boundaries, retained front matter, stable former-last-section identity,
and custom theorem context. Missing, cyclic and out-of-tree inputs fail
explicitly instead of silently yielding incomplete preparation.

The [repository-only comparison helper](../evals/compare_referee_preparation.py)
extracts selected API-free archived functions from an explicitly supplied
trusted source copy. It does not import Math Scout, install its dependencies or
invoke its CLI. Regenerate with paths to that reference copy and archive:

```bash
python3 evals/compare_referee_preparation.py \
  --reference TRUSTED_REFERENCE/src/math_scout/reviewer.py \
  --reference-version 0.3.0a1 \
  --archive ARCHIVE.zip \
  --output /tmp/referee-preparation-comparison.json
```

The migration map covers all seven substantive prompt contracts and the
preparation/resume boundaries. This is a methodology and algorithm comparison,
not a model-to-model benchmark.

## Software and package checks

The following checks passed:

- `python3 scripts/check.py`: eleven canonical skills and 157 executable
  regressions, including 26 manuscript-preparation tests. Package metadata,
  JSON, Python syntax and nested portable resource links also pass.
- The required `python3 -m json.tool` loop over plugin manifests, per-skill
  evals and asset JSON; the repository gate additionally parses retained JSON.
- `claude plugin validate .claude-plugin/plugin.json` and
  `claude plugin validate --strict .claude-plugin/marketplace.json`.
- `PYTHONPYCACHEPREFIX=/tmp/mathbox-pycache python3 -m py_compile
  skills/*/scripts/*.py evals/compare_referee_preparation.py`.
- Skill-creator frontmatter validation and OpenAI metadata generation parity
  for `referee`, including its explicit implicit-invocation policy.
- A standalone copy of only `skills/referee/`, run from another working
  directory, prepared a multi-file manuscript and passed all 26 regressions.
  Its contract hash agrees with the original installation.
- All seventeen archived-algorithm comparison assertions; retained artifact
  hash checks, five raw-fixture source hash checks, unchanged archive hash,
  Markdown math delimiter checks and `git diff --check`.

The runtime here is Python 3.14.7. New Python sources also parse under the
Python 3.10 grammar; actual 3.10/3.13 execution is left to the existing CI
matrix because those interpreters were not used locally.

Codex's available plugin CLI has no validation subcommand. Its discovery,
manifest, version/identity alignment and OpenAI skill metadata were checked
by the repository gate and skill-creator checks; no unavailable Codex validator
is reported as passing. No install, release or publication was requested.

No TeX compilation was run: the fixtures test source-based manuscript review
and the helper intentionally does not execute TeX. No live external-source
search was run for the stipulated unavailable synthetic citation. No paid API
benchmark, host-router execution or deep research-state integration was run:
these are outside this first integration's tested scope. Dependency-aware
incremental review through a thin ledger application remains the explicit
follow-up recorded in the migration map.

## Changed files

- New canonical skill: `skills/referee/SKILL.md`, `agents/openai.yaml`,
  `evals/evals.json`, `evals/trigger-evals.json`,
  `scripts/prepare_manuscript.py`, `scripts/test_prepare_manuscript.py`,
  `references/review-protocol.md`, `references/final-referee.md`,
  `references/output-contract.md`, `references/preparation.md`,
  `references/math-scout-license.txt`, and the five lane references
  `references/reviewers/{correctness,adversarial,exposition,notation,claims}.md`.
  All these paths are relative to `skills/referee/`.
- Existing skill routing: `skills/proof-audit/SKILL.md`,
  `skills/proof-audit/evals/evals.json`,
  `skills/proof-audit/evals/trigger-evals.json`, and
  `skills/proofread-math/evals/trigger-evals.json`.
- Packaging and public documentation: `.claude-plugin/plugin.json`,
  `.codex-plugin/plugin.json`, `README.md`, `docs/CHANGELOG.md`,
  `docs/referee-migration.md`, and this validation report. Existing release
  versions stay aligned at 3.2.0; changes are under Unreleased.
- Validation: `scripts/check.py`, `evals/README.md`, `evals/cases.json`,
  `evals/compare_referee_preparation.py`, and
  `evals/fixtures/referee-{core,context,exposition,source,enumeration}.tex`.
- Retained evidence: `evals/results/referee-v1/artifact-inventory.json`,
  `preparation-comparison.json`, `grading.json`, `grading.md`,
  `artifact-checks.json`, five `referee-*-artifact-inventory.json` grading
  inventories, and the individual raw artifacts listed in the inventory,
  all under `evals/results/referee-v1/`.
