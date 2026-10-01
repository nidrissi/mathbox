# Math Scout migration map

This map was recorded before implementing `referee`. The reference is the
user-supplied archive of `nidrissi/math-scout`, version `0.3.0a1`, inspected on
2026-09-30. The private repository and supplied archive remain unchanged.
The temporary `.math-scout/` directory is not part of the distribution.
Archive SHA-256:
`7919f326105d863502a9427bedf0794088e48d6eaf9d5c8e104ea373ccd75723`.

**Port Math Scout's mathematical review methodology into Mathbox; do not embed
Math Scout's LLM runtime inside Mathbox.**

## Audit of the two repositories

Mathbox has ten canonical skills, portable frontmatter, per-skill behavioral
and routing evals, a root inventory of raw behavioral fixtures, and a
standard-library package/regression gate. Claude lists skill directories;
Codex discovers `./skills/`. There are no root `evals/evals.json` or
`evals/trigger-evals.json`: those contracts live in each skill's `evals/`.

Math Scout puts preparation, issue models, scope selection, resume and synthesis
in `src/math_scout/reviewer.py`. Its seven prompt files hold the epistemic
contract. Three reviewers read sections; two read the whole paper. The final
referee receives every finding, including quotes and confidence, and rechecks
them against the source. The CLI and four provider modules handle API requests,
credentials, model selection, costs and retries. `tests/test_reviewer.py`
includes API-free preparation and resume tests as well as stubbed orchestration
tests; CLI/provider tests exercise the runtime that will not migrate.

## Component decisions

| Math Scout component | Decision | Mathbox destination or replacement |
|---|---|---|
| `prompts/review_protocol.md` | PORT | `referee/references/review-protocol.md`: shared severity, confidence, exact location, searchable quotations, limited-context discipline, empty findings allowed |
| `prompts/formal_verifier.md` | PORT | Internal correctness lane; focused mathematical confirmation uses `proof-audit` |
| `prompts/adversarial_skeptic.md` | PORT | Internal adversarial lane: concrete degeneracies, quantifiers, uniformity, brittle reductions |
| `prompts/exposition_referee.md` | PORT | Internal exposition lane, expert audience, actionable remedies, severity capped at major |
| `prompts/notation_auditor.md` | PORT | Whole-paper notation lane; compare both occurrences and search before alleging absence |
| `prompts/claim_auditor.md` | PORT | Whole-paper claims lane; quote promise and theorem, distinguish material overclaiming from normal compression |
| `prompts/final_referee.md`, `format_all_issues`, `format_coverage_note` | ADAPT | Independent source reconciliation, duplicate merging, explicit coverage gaps and eight-part report; no journal prestige assumption or automatic publication verdict |
| `ReviewerSpec`, `ReviewerScope`, `REVIEWER_SPECS`, `run_pipeline` | ADAPT | Five dimensions with native, bounded delegation; mathematical dependencies choose units, rather than one call per lane per section |
| `Issue`, `IssueWithReviewer`, `Review` | ADAPT | Portable JSON contract in a reference: preserve original fields, add lane, finding ID and review provenance; no Pydantic dependency |
| `strip_comment`, `mask_non_content` | PORT | Offset-preserving lexical mask, extended to inline literals and escaped commands; comments must not open fake literal environments |
| `_resolve_reference`, `_is_within`, `resolve_inputs`, `load_tex` | PORT | Standard-library helper, project boundary including symlinks, lookup from the main file's directory then the including file's, nested inputs; mask literal inputs too |
| `SECTION_RE`, `chunk_by_section`, `_front_matter`, `_safe_filename`, `chunk_stem` | ADAPT | Balanced titles, retained front matter and unsectioned bodies, explicit skipped-unit metadata, safe filenames; keep source intact for whole-paper review |
| `extract_global_context` and its regexes | ADAPT | Preamble/title/abstract plus labeled theorem-like environments and source map; mechanical context is an index, not a substitute for reading dependencies |
| `chunk_key`, `prompts_digest`, `run_settings` | ADAPT | Full SHA-256 prepared-unit, whole-source and skill-contract hashes; position-independent identity and conservative comparison metadata |
| `ResumeState`, `load_resume_state`, `retarget_reviews`, `sweep`, `issues.jsonl` | ADAPT | Immutable preparation snapshots and optional prior-manifest comparison; no automatic file moves, deletion, completed-review database or reuse verdict |
| `_validate_managed_output_tree`, `_validate_completed_state` | ADAPT | Refuse output symlinks and occupied snapshots; validate comparison metadata without opening paths supplied by it |
| Concrete proof verification | REPLACE WITH MATHBOX | `proof-audit`: exact obligation, raw argument and hypotheses, honest independence |
| External theorem / prior-art verification | REPLACE WITH MATHBOX | `literature-check`: bounded source question, authorized cache first, conditional when unavailable |
| Load-bearing code, tables and enumeration | REPLACE WITH MATHBOX | `computation-audit`: claimed population versus actual coverage, finite evidence kept separate from proof |
| Requested mechanical proofreading | REPLACE WITH MATHBOX | `proofread-math`; exposition review remains a distinct lane |
| Durable freshness / claim provenance | REPLACE WITH MATHBOX | Optional existing `research-state` ledger; never initialize one just to referee |
| Preparation and resume regression fixtures | ADAPT | Direct `unittest` cases and synthetic raw behavioral manuscripts; test real invariants, not prompt keywords |
| `providers/anthropic.py`, `providers/openai.py` | DO NOT PORT | SDK adapters, credentials, capability/pricing tables, streaming and caching |
| `providers/base.py`, `providers/registry.py`, provider exports | DO NOT PORT | API request/usage classes, provider registry, token counting and error normalization |
| `_call_with_retry`, `call_reviewer`, `_generation_request`, `run_dry_run`, `_confirm`, CLI model presets | DO NOT PORT | API retries, effort ladders, paid-run confirmations, token estimates and cross-provider selection |
| `pyproject.toml`, `uv.lock`, runtime dependency and CI configuration | DO NOT PORT | No Math Scout installation, executable or third-party Python dependencies |

## Deliberate first-version adaptations

- Preserve all five dimensions, not five public skills or a fixed agent count.
  Native isolated agents review disjoint work; the coordinator performs final
  reconciliation. When unavailable, use separate sequential passes and disclose
  self-review.
- Preparation fails before producing a snapshot on missing, cyclic, excessive
  or out-of-bound inputs. Math Scout warns and may leave input commands or drop
  cycles; a native reviewer must not silently call such a source complete.
- A lexical helper does not execute TeX, expand arbitrary macros, resolve
  conditionals, or authenticate bibliography contents. State these limits and
  inspect original sources when they affect coverage.
- Input-file boundaries receive a synthetic newline when the included file
  lacks one, preventing a trailing comment/control word from swallowing the
  caller's next structural command. Original source locators remain separate.
- Retain every prepared unit, including front matter and bibliography, in the
  manifest. Skip obvious non-mathematical units only for local proof passes;
  whole-paper review still sees them.
- Hash comparison identifies unchanged text only. Changed definitions,
  hypotheses, dependencies, context, lane contract or reviewer method can stale
  a prior local review. Any whole-source change invalidates whole-paper passes
  and final synthesis. Reuse requires inspecting actual previous review
  artifacts and their context, not a matching filename or hash alone.
- Follow-up: evaluate a thin `research-state` application for dependency-aware
  incremental reviews after realistic use. Do not build a parallel ledger in v1.

## Validation scope

Compare preprocessing directly with the archived algorithms on synthetic
fixtures, and compare every retained prompt obligation against this map.
The repository-only comparison helper is
[`evals/compare_referee_preparation.py`](../evals/compare_referee_preparation.py);
it extracts and executes selected API-free functions from an explicitly supplied
trusted reference copy, without importing Math Scout or its dependencies.
Forward-test real manuscript errors, false-positive suppression, specialist
handoffs and routing using the repository's independent-task protocol. Package
checks and preprocessing tests are software evidence, not mathematical
performance scores. A methodology/preparation comparison does not establish
superiority over Math Scout's API models.
