# Suite review: findings and remediation plan

**Status:** all 152 finding changes implemented. Acceptance verification is partial; see the [validation record](../evals/results/suite-review-2026-10-02/README.md).
**Base:** `main` at `9717972`. All line numbers refer to that commit.
**Date:** 2026-10-02.

This document records a read-only review of all 11 skills and their supporting
artifacts, and orders the findings into a remediation plan. It is the handoff
for whoever implements the fixes, human or agent.

The implementation is complete across all seven batches. The checkboxes below
track implementation, not a claim that all mathematical behavioral evals passed.
Package/helper checks, bounded forward trials and one explicit live Codex program
trial were run. The full 135-case behavioral suite and automatic routing on both
hosts were not run. Keep this document until those acceptance checks are closed;
then remove it as originally planned.

## How to use this plan

- Work one batch at a time. Each batch can be reviewed on its own and lists
  its acceptance checks. Batches 1–3 fix behavior and should land first;
  batches 4–6 are routing, cost, and consistency work.
- Before fixing a finding, re-read the cited text at the current revision.
  Line numbers drift as batches land, and every finding is a reviewer's
  report, not a proof.
- Follow `AGENTS.md` for every change:
  - read the complete `SKILL.md` first;
  - update the behavioral and trigger evals whenever a contract changes;
  - record user-visible changes under `## [Unreleased]` in
    `docs/CHANGELOG.md`;
  - run the listed checks.
- Cite finding IDs in commit messages. Tick a finding's box here when it lands,
  or move it to [Findings not adopted](#findings-not-adopted) with a reason.
  Delete this document once every batch is closed.
- Settle the [decisions](#decisions-needed) that block a batch before starting
  it.

### Finding IDs

Each ID has a prefix, a number, a severity and a verification mark.

**Prefixes:**

| Prefix | Skill or scope |
|---|---|
| `CA` | computation-audit |
| `LC` | literature-check |
| `PA` | proof-audit |
| `PM` | proofread-math |
| `MI` | manuscript-integrate |
| `RF` | referee |
| `RA` | research-attempt |
| `RP` | research-program |
| `RI` | research-init |
| `RR` | research-retrospective |
| `RS` | research-state |
| `X` | cross-cutting suite issues |

**Numbers** follow each reviewer's original ranking. Some skills were reviewed
together and share one number sequence:

- PA, PM and MI;
- RA and RP;
- RI and RR.

A gap in a sequence means that finding was merged into another item, usually an
`X` item or the trigger-eval list.

**Severity:**

- **High:** following the text literally can record a wrong mathematical
  status, lose research state, or produce output the next step cannot use.
- **Medium:** likely misbehavior, or documentation that has drifted from the
  code or schema.
- **Low:** clarity, cost, or polish.

**✔** marks a finding that the coordinating reviewer re-checked against the
files, in addition to the original reviewer's check.

## Method and baseline

Eight read-only reviewers covered the suite:

- computation-audit;
- literature-check;
- proof-audit, proofread-math and manuscript-integrate;
- referee;
- research-attempt and research-program;
- research-init and research-retrospective;
- research-state;
- a cross-cutting pass over routing, packaging, vocabulary and the README.

They all used the same rubric:

- **Clarity:** explicit inputs, outputs, labels and stopping conditions.
- **Alignment:** `SKILL.md`, references, assets, scripts, `agents/openai.yaml`
  and evals agree with each other.
- **Token efficiency:** how much text loads, and how often.
- **Agent Skills practice:** description quality and progressive disclosure.
- **Mathematical safeguards.**

Reviewers read the scripts' argparse definitions and code paths. Several
findings were reproduced with throwaway probes in a scratch directory.

At the base commit, all of these pass:

- `python3 scripts/check.py`;
- JSON lint of every manifest and eval file;
- `claude plugin validate .claude-plugin/plugin.json`;
- `claude plugin validate --strict .claude-plugin/marketplace.json`.

`git diff --check` is clean.

**Overall verdict:** no mathematical safeguard is weakened, and the helper
scripts are well tested. The main risks are:

- documentation that disagrees with the helper scripts or schemas;
- safeguards that exist only in a description or an eval assertion, with no
  rule in the skill body;
- the interface between research-attempt, research-program and the closeout;
- trigger evals that test boundaries in one direction only;
- the size of the research-init and research-state bodies.

## High-severity summary

| ID | Skill | Problem | Batch |
|---|---|---|---|
| CA-1 ✔ | computation-audit | The only manifest template is version 1. research-state links only version-2 manifests. | 1 |
| RS-1 ✔ | research-state | The required `decision` key of `route-reconcile` is never documented. | 1 |
| RS-2 | research-state | Unknown payload keys are stored permanently in the append-only ledger. | 1 |
| RF-1 | referee | Child reviewers never receive the issue schema, and lane files point to an unlinked protocol. | 1 |
| RF-2 ✔ | referee | Parallel children all emit `F001`, yet IDs must be unique within the run. | 1 |
| CA-2 | computation-audit | No step checks that the loop actually covers the claimed population. | 2 |
| LC-1 | literature-check | `source` evidence is recorded with no condition on what was verified. | 2 |
| PA-2 | proof-audit | A requested correction can close a gap with a new, unaudited argument. | 2 |
| MI-1 | manuscript-integrate | There is no stop rule for unvalidated or stale input. | 2 |
| RF-4 | referee | Reviewer lanes run specialist skills themselves, which undermines fresh review. | 2 |
| RR-1 | research-retrospective | Edit mode replaces narratives with links without checking for a durable home. | 2 |
| RP-1 ✔ | research-program | The closeout has no place for open routes with deferred continuations. | 3 |
| RA-2 | research-attempt | A delegated attempt has no write scope and writes shared live state directly. | 3 |
| RA-3 | research-attempt | Ledger persistence omits the `continue` reconciliation, so continuations are lost. | 3 |
| X-1 | research-state | The trigger fires whenever a ledger exists, not when the user asks for one. | 4 |
| RI-2 | research-init | The body is 2,327 words, about twice what it needs. | 5 |

## Batch 1: Make the documentation match the scripts and schemas

Goal: an agent that follows the documentation produces records the helpers
accept, and the helpers reject malformed records.

### research-state

- [x] **RS-1** · high · ✔ ·
  `skills/research-state/references/ledger.md:387-397`
  - **Problem:** the `route-reconcile` field list ends with "…an explicit
    `conflicts` string array… Decisions are:" and never names the required
    `decision` key (`research_state.py:462-463`).
    - An agent that guesses `outcome` has it silently ignored.
    - The event then fails with "invalid reconciliation decision".
  - **Fix:** "…`conflicts` string array, and `decision`, one of:". Add one
    JSON example of a `continue` reconciliation.
- [x] **RS-2** · high · `skills/research-state/scripts/research_state.py:249`
  (`apply`)
  - **Problem:** unknown payload keys are accepted and stored permanently.
    The reviewer reproduced this:
    - a misspelled `statment_artifact` leaves the claim unbound;
    - a misspelled `resolve` leaves the route scoped to its owner;
    - both runs exit 0, and `check` reports nothing.
  - **Why it is permanent:** routes are immutable, and a repeated owner plus
    mechanism is rejected (RS-3). The route can only be corrected by renaming
    the mechanism, which `ledger.md:307-308` forbids.
  - **Fix:** define the allowed payload fields for each event type. Reject
    unknown keys when an event is recorded, and name the allowed keys in the
    error. Add a regression test. See [D2](#decisions-needed).
- [x] **RS-3** · medium · `skills/research-state/references/ledger.md:295-297`
  - **Problem:** the text says "An exact repeated target/mechanism without this
    explanation is rejected". The code instead:
    - keys duplicates on the owning `claim` plus `mechanism`
      (`research_state.py:360-363`);
    - requires a reopened route to keep its owner, `resolves` and mechanism
      (`:356`). Eval 12 relies on this, but no document states it.
  - **Fix:** "A new route repeating an earlier route's owning `claim` and
    `mechanism` is rejected unless it `reopens` that route's terminal event
    with identical owner, `resolves`, and mechanism. To apply one mechanism to
    another obligation, make that obligation the owner."
- [x] **RS-4** · medium · `skills/research-state/SKILL.md:105-106,116-118`
  - **Problem:** `supersedes` is never mentioned. After revalidation, an agent
    either retracts evidence that is valid but outdated, or leaves the stale
    evidence active.
    - In the second case, `check` exits 1 indefinitely.
    - The review label stays `failed-review-recorded`.
  - **Fix:** "After real revalidation, record new evidence with
    `supersedes: [old IDs]`; retract only erroneous records."
- [x] **RS-5** · medium · `skills/research-state/SKILL.md:24-27`
  - **Problem:** the text says the default reports list runs that are live,
    `stale-result`, or awaiting reconciliation. In fact `check --summary`
    returns only counts and issues (`research_state.py:1530-1542`). Only the
    brief `status` and `handoff` views list runs that need attention.
  - **Fix:** correct the sentence and add `status` to the command map. Say
    what to use when no goal is registered.
- [x] **RS-13** · low-medium ·
  `skills/research-state/references/deferred-handoff.md:49-53`
  - **Problem:** "the actual `sha256` of the inspected head event" suggests
    hashing the file. The stored field is a digest of canonical JSON, so a host
    that hashes the file bytes gets a mismatch.
  - **Fix:** "Copy the `event_id` and `sha256` fields from the highest-numbered
    `.mathbox/events/NNNNNN.json`; never compute them."
- [x] **RS-16** · low · `ledger.md:40-41`
  - **Problem:** says exit 1 means stale evidence. The code (`:1552`) returns 1
    for any freshness or integrity issue.
- [x] **RS-17** · low · `ledger.md:235`
  - **Problem:** "reported `conditional`" applies only to a claim that has
    current proof, source or computation evidence. A claim with no evidence
    reads `conjectural`, and one with a counterexample reads
    `counterexample-recorded`.
- [x] **RS-18** · low · `ledger.md:165,185`
  - **Fix:** change "strict computation manifest" to "version-2 manifest (v1
    manifests pin only as ordinary artifacts)". Pair this with CA-1.
- [x] **RS-19** · low · `skills/research-state/references/migration.md:34-36`
  - **Problem:** asks for a run against "the exact historical base", but
    `base_event` must be an existing event.
  - **Fix:** say which event to use, and put the historical commit in
    `base_revision`.
- [x] **RS-20** · low · `research_state.py:411`
  - **Problem:** starting a run on a closed route or program is rejected, but
    this is undocumented. Eval 5 depends on the ordering.
  - **Fix:** add one sentence near `ledger.md:384`.
- [x] **RS-21** · low · `research_state.py:1436-1462` (`--help`)
  - **Problem:**
    - `--root`, `--json`, `--summary`, `--full`, `--goal` and `--dry-run` have
      no help text;
    - `next` and `handoff` share one help line;
    - the `pin-impact` help omits reviews and run results;
    - `check --full` and `pin-impact --full` are undocumented.

### computation-audit

- [x] **CA-1** · high · ✔ ·
  `skills/computation-audit/assets/computation-manifest.json:2`
  - **Problem:** the only template is `"schema_version": 1`.
    - `SKILL.md:56-57,65,76,112` and `references/runner.md:108` call version 1
      historical.
    - The validator reports a filled template as "valid legacy version 1".
    - research-state refuses to link it: "linked computation evidence requires
      a version 2 manifest" (`research_state.py:572-574`).
    - `SKILL.md:56` (claim-supporting runs use the template) overlaps `:67`
      (new authorized runs use the runner).
  - **Fix:** send new runs to the runner, which emits version 2. Keep the
    template only for runs made outside the runner, and say that it yields a
    version-1 record that cannot be linked in the ledger. The alternative is to
    ship a version-2 template. See [D1](#decisions-needed).
- [x] **CA-3** · medium ·
  `skills/computation-audit/scripts/validate_manifest.py:384`
  - **Problem:** prints "valid evidence record…" for a timed-out run without
    showing `run.status`.
  - **Fix:** include the status in the message, e.g. "valid evidence record
    (run status: timeout)". Add to SKILL.md: "A valid record may document a
    failed, timed-out, or changed-input run; read `run.status` before
    interpreting."
- [x] **CA-10** · medium ·
  `skills/computation-audit/references/runner.md:17,22`
  - **Problem:**
    - The example puts the code file in `mathematics.inputs`, which
      contradicts `runner.md:33-35` and eval 5.
    - `"version": "record actual version"` passes validation if copied
      verbatim.
  - **Fix:** use `"inputs": ["integers n with -100 <= n <= 100"]`, and
    `"version": ""` or a real version string.
- [x] **CA-13** · low · `scripts/run_experiment.py:418-425`
  - **Problem:** the arguments have no help text, and the defaults (60 s
    timeout, 4 MiB of output) are documented nowhere. A long Sage run is
    therefore silently recorded as a timeout.
  - **Fix:** add help strings with `%(default)s`, and state the defaults in
    `runner.md`.

### literature-check

- [x] **LC-5** · medium ·
  `skills/literature-check/scripts/literature_cache.py:551-552`
  - **Problem:** `SKILL.md:31` says an unversioned arXiv copy is only a
    discovery candidate. Yet a record stored as an unversioned arXiv ID and
    queried with the same ID returns `exact-identifier` (reproduced).
  - **Fix:** label such a match as a candidate, or document the behavior in
    `references/source-cache.md:40-42`. See [D6](#decisions-needed).
- [x] **LC-10** · low · `literature_cache.py:403,425,431`
  - **Problem:** `add`:
    - accepts zero `--id`, which leaves the record unfindable by `find --id`;
    - accepts `--id arxiv:…v2 --version v5` without a consistency check;
    - accepts a non-ISO `--date-checked`;
    - overwrites `date_checked` on every re-ingest.
  - **Fix:** require at least one ID, validate dates and reject conflicting
    versions. Document `date_checked` as the ingest date.
- [x] **LC-9** · low · `literature_cache.py:513,563-577`
  - **Problem:** `find --query` is a literal, case-folded substring match over
    raw `pdftotext -layout` output. A phrase broken across lines or hyphenated
    is missed.
  - **Fix:** normalize whitespace, and add to `source-cache.md:42-44`: "A miss
    is not evidence the source lacks the statement."

### referee

- [x] **RF-1** · high · `skills/referee/SKILL.md:79-81`,
  `references/model-assignments.md:57-58`
  - **Problem:** child reviewers never get the issue schema.
    - The list of what each child receives leaves out the schema.
    - `references/review-protocol.md:70` sends children to `output-contract.md`
      for fields. That file is 957 words and mostly coordinator-only.
    - Every lane file opens with "Read the shared protocol." and gives no link
      (`references/reviewers/*.md:3`).
  - **Fix:**
    - Move the issue JSON block and its field rules (`output-contract.md:49-78`)
      into a "Return format" section of `review-protocol.md`.
    - Link each lane file to `../review-protocol.md`.
    - In SKILL.md write: "Give each child the resolved paths of
      review-protocol.md, its lane file and its snapshot unit files (paste the
      text only if it cannot read files)."
    - This saves about 800 words per child.
- [x] **RF-2** · high · ✔ · `skills/referee/references/output-contract.md:53,71`
  - **Problem:** IDs must be unique within the run, but the sample uses `F001`,
    and the "disjoint output scope" in `SKILL.md:81` is undefined. Parallel
    children therefore all emit `F001`.
  - **Fix:** give each pass a `pass_id` and an ID prefix (e.g. `corr-s3-F001`).
    A child writes only `passes/<pass_id>.json`.
- [x] **RF-5** · medium-high · ✔ (first point) · `output-contract.md`
  - **Problem:** the schema has gaps.
    - `:9-11`: `manuscript_sha256` is not a manifest key. The manifest has
      `source_sha256` and `source_files_sha256` (`prepare_manuscript.py:584-587`).
    - `:12-14`: coverage-entry keys are not named, and no pass ID links an
      issue's `reviewer` to its coverage entry and model provenance.
    - `:91`: the reconciliation hash keys are not named.
    - `:98-100`: final concerns have no container.
    - `:102`: "top-level" could mean either JSON file.
  - **Fix:**
    - Give a coverage example:
      `{pass_id, lanes, scope, unit_ids, context, executor, method, status, model_assignment}`.
    - Set `manuscript_sha256` to the manifest's `source_sha256`, and also carry
      `source_files_sha256`.
    - Add a `concerns` array to `reconciliation.json`.
    - Make `reviewer` equal to `pass_id`.
- [x] **RF-8** · medium · `SKILL.md:147-148`, `references/preparation.md:141`
  - **Problem:** both require checking the "lane-contract revision", but the
    manifest holds only one global `contract_sha256`
    (`prepare_manuscript.py:513-521`, `preparation.md:81`).
  - **Fix:** add a `contract_files` map `{relpath: sha256}`, which is additive
    to schema 1. The alternative is to state that any `contract_changed`
    reruns all local passes. See [D8](#decisions-needed).
- [x] **RF-11** · medium · `SKILL.md:34-38`, `output-contract.md:3,77-78,83`
  - **Problem:**
    - The snapshot directory doubles as the run directory, while
      `preparation.md:144` says snapshots are immutable.
    - Filenames for raw returns and prior leads are not specified.
  - **Fix:** define `referee/<run>/` as the snapshot files (never edited) plus
    `passes/`, `prior-leads.md`, `findings.json`, `reconciliation.json` and
    `report.md`.
- [x] **RF-21** · low · `scripts/prepare_manuscript.py:625-628`
  - **Problem:**
    - The positional `manuscript` argument has no help text.
    - The `--root` help does not say that a relative manuscript path is rebased
      onto `--root`, while `--output` and `--previous` stay relative to the
      current directory.
    - The sentence at `preparation.md:13` is garbled.

### research-init

- [x] **RI-7** · medium · `skills/research-init/assets/AGENTS.template.md:5-6,13,20`
  vs `scripts/inspect_repo.py:40-50`
  - **Problem:** on a filled template, `declared_paths()` finds the
    conventions, literature, research log and records, but misses the charter,
    status, claims and verification paths (reproduced). The cause is "See `…`"
    lines and labels such as "Claims/obligations".
  - **Fix:** use labels like `- **Charter:** \`…\``, and add `verification` and
    `route index` to `DECLARED_PATH_LABELS`.
- [x] **RI-8** · medium · `skills/research-init/SKILL.md:74-75`
  - **Problem:** the text says "Use `--full` for the complete Markdown report",
    but `markdown()` (`inspect_repo.py:625-640`) omits:
    - semantic roles;
    - the computation-manifest classification;
    - `declared_paths`.

    The brief view also omits declared paths and alternate caches, which
    Phase 3 item 9 needs.
  - **Fix:** print these fields, or state that only `--format json` is
    complete.
- [x] **RI-21** · low · `inspect_repo.py:786-790`
  - **Problem:** the parser has no description, and `--root` and `--max-depth`
    have no help. `--root` silently resolves to the Git top level.
  - **Fix:** `ArgumentParser(description=__doc__)` plus help strings that state
    this behavior.
- [x] **RI-25** · low · `assets/RESEARCH_LOG.template.md:14-24`
  - **Problem:** the fenced examples keep their placeholders, which conflicts
    with Phase 5's "Remove every placeholder". `classify_research_log` counts
    fenced lines, so the template itself classifies as `compact-linked-index`.
  - **Fix:** skip fenced lines in the classifier, or state that the block is
    intentional.

**Acceptance:**

- `python3 scripts/check.py`;
- `py_compile` of every changed script;
- `validate_manifest.py … --template` when CA-1 changes the manifest;
- the `inspect_repo.py` smoke test when the inspector changes;
- regression tests for RS-2, CA-3, LC-10, and RF-8 if it changes the script;
- a referee trial on a host requiring explicit user delegation: a referee
  request alone causes no subagent launch and uses disclosed sequential
  self-review; existing delegation authorization is honored without re-asking;
- changelog entries for each helper or schema change.

## Batch 2: Put the missing safeguards into the skill bodies

Goal: every safeguard that a description, README line or eval assertion
promises is backed by an explicit rule in the skill body, and each one has a
behavioral eval.

### manuscript-integrate

- [x] **MI-1** · high · `skills/manuscript-integrate/SKILL.md:18-23`
  - **Problem:** there is no stop rule for unvalidated, stale, heuristic or
    gappy input, and "validated" is never defined. Step 3 says a generated
    `proved` label does not validate a proof, but not what to do next.
    `README.md:147-148` promises the skill "does not make conjectural work
    ready for publication".
  - **Fix:** "To integrate a result as established, require current durable
    evidence supporting its exact statement and scope (proved, externally
    proved, or computationally verified within the stated range), with no
    active failed review against it. Otherwise block that promotion; route
    correctness questions to `proof-audit` and new arguments to
    `research-attempt`; do not repair the proof here. On explicit request, a
    conditional statement may be integrated under MI-3 with its unresolved
    dependency and evidence status intact. Validated citation changes and
    corrections or removals need support for the change, not positive proof
    evidence for a claim no longer asserted."
  - **Evals:** a lemma marked proved in the ledger whose proof skips a boundary
    case; an explicitly requested conditional statement with an unverified
    source; an authorized scope removal or validated citation correction that
    asserts no new mathematical result.
- [x] **MI-3** · medium · `SKILL.md:29-31`
  - **Problem:** "keep that result conditional rather than supplying validation
    here" can be read as "integrate it as a conditional statement". Eval 2
    (`evals/evals.json:24`) expects integration to be blocked.
  - **Fix:** "Do not integrate that result unless the user explicitly asks for
    a conditional statement. In that case, carry the missing hypothesis or
    unverified dependency and conditional status into the text; do not promote
    its evidence status. Otherwise report integration as blocked with its
    status unchanged." This is MI-1's explicit conditional-integration exception.
- [x] **MI-16** · low · `SKILL.md:84-85,95-97`
  - **Problem:** the verifier and build steps lack "when documented; otherwise
    report not run". The Report section never says that a clean build or
    proofread pass is not validation, which eval 4 asserts.
  - **Fix:** add both clauses.

### proof-audit and proofread-math

- [x] **PA-2** · high · `skills/proof-audit/SKILL.md:100-103`
  - **Problem:** a requested correction may change the durable proof after the
    failed implication is found, with no limit on the repair. The ban on new
    proofs lives only in the description, and there is no handoff when the
    durable proof is the manuscript itself.
  - **Fix:** "Never close a gap with a new argument. A requested correction may
    only restrict the statement or fix a forced, local step. Label any other
    repair as unaudited, do not upgrade the verdict on its strength, and route
    it to `research-attempt`. Propagate into a manuscript only through
    `manuscript-integrate`, on explicit request."
  - **Eval:** an "audit and fix" request.
- [x] **PA-10** · medium · `SKILL.md:89-98` vs `evals/evals.json:80`
  - **Problem:** there are eight verdicts, but ledger reviews accept only
    `pass`, `fail` or `conditional`, and no mapping is given. A restricted
    verdict could be recorded as `pass`.
  - **Fix:** "`pass` only if the verdict supports the evidence's exact claim,
    `conditional` for a conditional verdict, `fail` otherwise."
- [x] **PM-12** · medium · `skills/proofread-math/evals/evals.json`
  - **Problem:** no case tests "A proof gap is not a proofreading error"
    (`SKILL.md:62-64`), or a uniquely forced token change being made and
    listed (`:56-58,85`).
  - **Fix:** add both cases.

### computation-audit

- [x] **CA-2** · high · `skills/computation-audit/SKILL.md:35-44`,
  `references/checklist.md`
  - **Problem:** nothing checks that the loop enumerates the claimed
    population; only resource truncation is mentioned (`:44`).
    - This is the repository's own sampled-enumeration case
      (`evals/cases.json:61`).
    - referee delegates "claimed population versus actual coverage" to this
      skill.
    - `research-attempt/SKILL.md:87-89` already states the rule.
  - **Fix:** add the bullet "whether the loop enumerates the claimed
    population: compare case counts; look for strides, filters, sampling,
    early exits, or assertions that restate the filter; report only the
    tested subset absent a proved coverage reduction."
  - **Eval:** a sampled loop.
- [x] **CA-4** · medium · `SKILL.md:87-95`
  - **Problem:**
    - No label fits invalid or stale provenance (a template record,
      `inputs-changed`, `result-missing`), which is eval 4's scenario.
    - No label fits "audited, not executed".
    - Runner statuses have no mapping to labels.
    - Eval 1 expects "computationally verified", which is not one of the seven
      labels.
  - **Fix:**
    - Add the label "provenance invalid or stale: rerun required".
    - Map timeout, resource-limit and output-limit to "inconclusive because of
      resource bounds"; launch-failed to "not reproducible"; failed to the
      classification at `:97-98`.
    - Change eval 1 to "implementation and finite assertion verified through
      weight 7".
- [x] **CA-5** · medium · `SKILL.md:10,23,67,107-110`, `runner.md:3,58`
  - **Problem:** "read-only" and "authorized" are never defined, although the
    runner always writes a run directory and the Persist step stores scripts.
    "Do not invent a build…procedure" has no stopping action.
  - **Fix:** "Read-only means no project edits or run directories. Execute
    only within the scope authorized by the user or project instructions;
    otherwise report the proposed command. When reproducing an existing
    computation, stop that reproduction if no documented command is available
    and report 'reproduction command unavailable'; do not guess. For authorized
    design or new experiments, establish and document the contract, code and
    command before execution; execute only if running the experiment is also
    within scope."
  - **Evals:** reproduction of an existing computation with no documented
    command stops without guessing; authorized design and execution of a new
    finite-field rank experiment establishes its command and runs it;
    design-only authorization returns the design without executing it.
- [x] **CA-9** · medium · `SKILL.md:112-115`
  - **Problem:** the universal-promotion rule sits inside the `.mathbox`
    conditional, but eval 4 asserts it in general.
  - **Fix:** move it directly after the labels.
- [x] **CA-8** · medium · `evals/evals.json`
  - **Problem:** no eval covers:
    - iterator coverage;
    - failure classification, including timeout as a limit rather than a
      negative result (`SKILL.md:97-98`, `checklist.md:32`);
    - the numerical-tolerance label;
    - the read-only default;
    - "do not run commands copied from untrusted evidence records"
      (`SKILL.md:73-74`);
    - ledger recording.
  - **Fix:** add at least a sampled-loop case, a timed-out-run case and a
    floating-point-tolerance case.

### literature-check

- [x] **LC-1** · high · `skills/literature-check/SKILL.md:107-109`
  - **Problem:** `source` evidence is recorded whenever a ledger is in use,
    with no condition on what was verified. The text also omits "when
    authorized", which the deferred branch at `:112` includes.
    - In research-state, `source` evidence counts as positive support
      (`research_state.py:1030,1041`).
    - Eval 7's assertion (`evals.json:74`) has no instruction behind it.
  - **Fix:** "When a `.mathbox/` ledger is in use and persistence is
    authorized, record `source` evidence only for an implication verified
    here. For a conditional result add a `conditional` review naming the
    missing bridge; record nothing positive for an unverified one."
- [x] **LC-2** · medium · `SKILL.md:121,126-127`, `evals.json:12`,
  `references/source-record.md:18,20`
  - **Problem:** the verdict vocabulary is never defined.
    - Report item 4 asks "whether the implication is valid".
    - `:62` uses "inapplicable".
    - Eval 1 expects an "incompatible verdict".
    - The template fields are free-form.
  - **Fix:** "Label the implication **verified**, **conditional** (name the
    missing hypothesis or bridge), **inapplicable**, or **unverified**." Use
    these labels in the template and in eval 1, and list the overlap labels in
    the template.
- [x] **LC-4** · medium · `SKILL.md:43-44`
  - **Problem:** "After acquiring an authorized source, add it to the cache"
    reads as caching by default. The explicit retention rule is only in
    `references/source-cache.md:87-88`.
  - **Fix:** "When project instructions or the user authorize local retention,
    add…".
- [x] **LC-6** · medium · `SKILL.md:40-41,51`
  - **Problem:** there is no limit on quotation. Nothing stops an agent from
    copying cached full text into tracked files, which is a way around the
    Git-ignore rule. Eval 7's "beyond brief necessary quotation" has no
    instruction behind it.
  - **Fix:** "Quote only the statement needed; never copy fetched or cached
    full text into tracked files, reports, or handoff packets."

### referee

- [x] **RF-4** · high · `skills/referee/references/reviewers/correctness.md:13-14,26-27,31-32`,
  `adversarial.md:26`, `claims.md:31`
  - **Problem:** lane files tell child reviewers to run specialist skills,
    while `SKILL.md:105-108` has the coordinator supply raw arguments for a
    fresh derivation. A child that confirms its own suspicion is not fresh,
    and nested delegation may not exist on the host.
  - **Fix (lane files):** "State the exact obligation for
    `proof-audit`/`literature-check`/`computation-audit`; do not run
    specialists unless the coordinator asks."
- [x] **RF-6** · medium · `output-contract.md:98`
  - **Problem:** final concerns carry an "evidence status" with no defined
    values. `references/final-referee.md:26-27` distinguishes a gap, a false
    statement, a local explanation and an unverified external input.
  - **Fix:** define the values `refuted`, `gap`, `conditional`, `question` and
    `presentation`. Positive "checked" or "valid" statements in the report
    must name the method: proof-audit, an independent recheck, or self-review.
- [x] **RF-14** · low-medium · `review-protocol.md:77-79` vs `SKILL.md:82-83`
  - **Problem:** "Prior findings can help avoid duplication" conflicts with
    not giving a fresh correctness auditor the suspected answer.
  - **Fix:** "Withhold prior findings from correctness and adversarial passes;
    whole-paper lanes may receive them labelled as unverified leads."
- [x] **RF-15** · low-medium · `SKILL.md:42-43`
  - **Problem:** "Resolve preparation errors" does not forbid manually opening
    a file the script refused. Eval 8 asserts that out-of-bound input is not
    read.
  - **Fix:** add "without reading outside the authorized boundary; ask before
    widening `--root`."

### Research workflow skills

- [x] **RR-1** · high · `skills/research-retrospective/SKILL.md:99-103`
  - **Problem:** edit mode replaces older narratives with links without
    checking that the narrative has a durable home, and without running
    `pin-impact`. research-attempt has that guard (`SKILL.md:146-149`). The
    mode also overlaps research-init's migration trigger (compare retro
    eval 2).
  - **Fix:** "Replace an older narrative with a link only when it already has
    a durable home (indexed record, manifest, or closeout), the edit policy
    permits it, and `pin-impact` shows no pin conflict. Otherwise leave it and
    report that compaction needs a `research-program` closeout or a
    `research-init` migration." See [D5](#decisions-needed).
- [x] **RR-19** · low · `research-retrospective/SKILL.md:106-107`
  - **Problem:** the skill never says that manuscript inclusion, bounded
    computation or a failed search cannot upgrade a label. "Completed
    deliverables still described as unresolved" could be misread that way.
  - **Fix:** add one line to "Build the portfolio".
- [x] **RA-7** · medium · `skills/research-attempt/SKILL.md:108`
  - **Problem:** "refuted, with the smallest counterexample found". The caveat
    about minimality is only in `references/structural-moves.md:21-22`, which
    is loaded only for obstructed structural routes.
  - **Fix:** "…with the counterexample found (call it smallest only relative
    to a stated search order unless every smaller case is excluded)."
- [x] **RP-21** · low · `skills/research-program/SKILL.md:156`
  - **Problem:** no manuscript or novelty guard.
  - **Fix:** add "Integrate into a manuscript only on explicit request and
    after audit; integration is not validation. Route novelty questions to
    literature-check; a failed search is not novelty."
- [x] **RI-9** · medium · `skills/research-init/assets/LITERATURE.template.md:3,5`
  - **Problem:** invites load-bearing novelty checks but has no source-status
    or search-scope columns.
  - **Fix:** add those columns, plus "A failed search supports only
    'apparently new within the stated scope'."

**Acceptance:**

- one behavioral eval per high item;
- trial runs on realistic tasks following `evals/README.md`;
- `scripts/check.py`;
- changelog entries describing each new rule.

## Batch 3: Research workflow interfaces

Goal: research-attempt, research-program, the closeout, the research-init
templates and research-retrospective exchange the same fields, under the same
names, and never drop an open continuation.

### Closeout and delegated attempts

- [x] **RP-1** · high · ✔ ·
  `skills/research-program/references/program-closeout.md:35-46`,
  `assets/program-closeout.template.md:15-25`
  - **Problem:** there is nowhere to record an open route with an untried or
    deferred continuation. Neither file mentions "deferred", "untried" or
    "continuation"; #11 updated SKILL.md, the protocol and the handoff, but
    not these. The template allows only:
    - "Routes closed by cutoff … reopen only with <new mathematical input>";
    - one "Active route".

    A closeout can therefore drop continuations, and it demands new
    mathematics to reopen an inconclusive route that was never obstructed.
  - **Fix:**
    - Add the section `## Open routes and continuations` with entries of the
      form `<Route ID> — <untried/deferred step, next action, resumption condition>`.
    - Change the closed-route line to "<obstruction, or scoped reason no
      continuation remained> — reopen with <changed input addressing it>".
    - Add "deferred continuations" to the reconciliation list at `:99-100`.
- [x] **RA-2** · high · `skills/research-attempt/SKILL.md:130-155`
  - **Problem:** an attempt has no notion of write scope, owner, base
    checkpoint or coordinator. research-program requires all of them
    (`research-program/SKILL.md:70-74`, `references/handoff.md:31-35`).
    - A delegated attempt appends to the shared index and live status.
    - In a deferred host, each attempt emits its own packet, which contradicts
      program eval 14 ("Returns one packet").
  - **Fix (attempt):** "When run as a delegated or parallel work package,
    write only within the assigned scope; return the route record and
    proposed index, status, and ledger entries, with base checkpoint and
    artifact hashes, to the coordinator."
  - **Fix (program):** "Collect work-package updates and append them, or one
    deferred packet, yourself."
- [x] **RA-3** · high · `research-attempt/SKILL.md:150-151`
  - **Problem:** "record only changed contracts, evidence, reviews, and route
    outcomes" leaves out the run result plus `continue` reconciliation that
    research-state requires when an open route's continuation must outlive the
    session.
  - **Fix:** append "; for an open route whose unfinished continuation must
    outlive this session, a run result with a `continue` reconciliation."

### Report, route card and vocabulary

- [x] **RA-4** · medium · `research-attempt/SKILL.md:172-178`,
  `references/route-card.md:5-33`
  - **Problem:** the report omits the route disposition, the continuations and
    the base checkpoint. The route card has no route, claim or program IDs and
    no base, yet the closeout template uses `<Route ID>` and `<Claim ID>`, and
    `handoff.md:4` requires IDs.
  - **Fix:**
    - Change report item 2 to "attempt outcome, evidence label, route
      disposition, and continuations".
    - Add "base checkpoint and actual inputs when part of a program".
    - Add `**Program/route/claim IDs:**` and `**Base checkpoint:**` to the
      card.
- [x] **RA-5** · medium · `route-card.md:23`
  - **Problem:** "<open, deferred, or closed as succeeded, failed, blocked or
    inconclusive…>" conflicts with `research-program/SKILL.md:118-119,179`,
    where blocked routes stay open.
    - "Deferred" is a state of a continuation, not of a route.
    - The ledger has no deferred route state.
    - Terminal `blocked` is never defined.
  - **Fix:** "<open (continuations may be deferred) or closed as
    succeeded/failed/blocked/inconclusive>", with a one-line definition of
    each. In research-program, change `:179` to "leave those routes open with
    their deferred next steps".
- [x] **RA-6** · medium · `research-attempt/SKILL.md:101-110`,
  `references/evidence-model.md:5-14`
  - **Problem:** there are eight outcomes and eight labels, with no mapping.
    The index line requires an "evidence label", so an inconclusive attempt
    gets "inconclusive" written as a label. The pointer at `:164-165` is
    passive and sits in Persist.
  - **Fix:** move the pointer into Classify: "Read evidence-model.md before
    assigning a label or promoting a claim. The outcome describes this
    attempt; the label describes the strongest surviving statement. Leave the
    target's label unchanged only when the unsuccessful attempt adds no evidence
    against the target or its existing support, such as an ill-typed attempted
    construction. If the target itself is ill-typed or its support is
    invalidated, report the exact defect and affected evidence and dependents,
    route the correctness question through `proof-audit`, and correct durable
    status under the project's authorized edit rules. Do not continue to present
    the old label as reliable or infer refutation merely from a failed
    construction."
  - **Evals:** an ill-typed attempted construction leaves an independently
    supported target's label intact; discovering that a target labelled proved
    is itself ill-typed reports the defect and affected support, and updates
    authorized status without treating the old label as reliable.
- [x] **X-7** · medium · `research-attempt/SKILL.md:101-110` vs
  `proof-audit/SKILL.md:92,96,98`
  - **Problem:**
    - The outcome list lacks "externally proved", which
      `evidence-model.md:6` defines.
    - It merges "ill-typed or incomplete" (`:109`), which proof-audit keeps
      apart; "incomplete" also overlaps "inconclusive" (`:110`).
    - "Proved after an explicit restriction" (`:104`) and proof-audit's
      "correct only after a stated restriction" say the same thing in
      different words.
  - **Fix:** align the two lists.
- [x] **RP-8** · medium · `research-program/references/program-protocol.md:47`
  - **Problem:** research-program defines no evidence vocabulary or
    route-record format, only "epistemic labels". It depends on
    research-attempt for both, but research-attempt is explicit-only on Codex
    (`allow_implicit_invocation: false`).
  - **Fix:** add a short fallback vocabulary and the minimal route-record
    fields. See [D7](#decisions-needed).

### Evals and smaller interface fixes

- [x] **RA-9** · medium · `research-attempt/evals/evals.json:62` (eval 6)
  - **Problem:** the eval expects "Closes this route with its first
    obstruction … without asking permission again". After #11 this contradicts
    `SKILL.md:115-122`. The rule against re-asking exists only in
    `research-program/references/program-protocol.md:50-53`.
  - **Fix the eval:** "Records the first failed implication; closes the route
    only if it obstructs the whole mechanism and no continuation remains;
    otherwise returns continuations."
  - **Fix the skill:** add "Do not re-request authority already granted." to
    the attempt intro.
- [x] **RP-22** · low · `research-program/SKILL.md:151,168-170`
  - **Problem:** "one guarded index entry" vs research-state's "at most one".
    The run states queued, running, completed and timed out do not match the
    ledger's.
  - **Fix:** use "at most one", and add a one-line mapping to ledger states.
- [x] **RP-24** · low · `research-program/evals/evals.json:62` (eval 6)
  - **Problem:** "proposes or uses a program/route index hierarchy" is
    ambiguous against `SKILL.md:15-18`, which gives flat-log restructuring to
    research-init.
  - **Fix:** "reports the flat-index migration as a pending research-init step
    without restructuring it."
- [x] **RP-23** · low · `program-closeout.md:91`, `:17-18`
  - **Problem:** "Set an advisory project-specific size … trigger" implies
    editing project instructions, which is research-init's job. Lines 17-18
    hard-code the helper's "eight issues".
  - **Fix:** "If project instructions lack one, propose…", and drop the
    number.
- [x] **RP-15** · low · `research-program/SKILL.md:46`
  - **Problem:** "it" in "Initialize it only when useful and authorized" is
    ambiguous.
  - **Fix:** "Initialize a `.mathbox/` ledger only when…".
- [x] **RA-17** · low · `research-attempt/SKILL.md:78-80`
  - **Problem:** the unavailable-skill fallback covers only literature-check.
  - **Fix:** reuse research-program's sentence (`research-program/SKILL.md:84-88`)
    for computation-audit and research-state.

### Retrospective and research-init templates

- [x] **RR-5** · medium · `research-retrospective/SKILL.md:15-23`
  - **Problem:** reads only the history index. It never follows program or
    phase entries to the closeouts and route indexes that research-init
    scaffolds (`RESEARCH_LOG.template.md:5-8`) and research-attempt resolves
    (`project-context.md:10-11`).
  - **Fix:** "follow the history entry point's program/phase links to the
    relevant closeout and route index."
- [x] **RI-6** · medium · `research-init/assets/AGENTS.template.md:13-20`
  - **Problem:** the project map has no slot for route indexes, so
    research-attempt resolves the location ad hoc (`research-attempt/SKILL.md:140`).
  - **Fix:** add `- **Route indexes:** {{ROUTE_INDEX_LOCATION}}`.
- [x] **RI-3** · medium · `research-init/SKILL.md:142-152,154-198`,
  `references/existing-repo-migration.md:55-56,70-71`
  - **Problem:** history migration is split across three places, and the
    reference points back to SKILL.md. A long but compact flat index
    (inspector class `compact-linked-index`) never reaches the sharding
    procedure, even though sharding is a named trigger.
  - **Fix:** put all history-migration steps in one reference, and route by
    inspector class in SKILL.md.
- [x] **RI-4** · medium · `research-init/SKILL.md:20-21` vs `:157-161`
  - **Problem:** "unless the user already authorized immediate execution"
    conflicts with "Broad retrofit authorization… does not substitute for
    review".
  - **Fix:** add to the non-negotiables: "Even when authorized, obtain review
    of a legacy-history mapping and of any authority-ambiguous replacement
    before applying it."
- [x] **RI-10** · medium · `research-init/SKILL.md:202,293-294`
  - **Problem:** "Use the assets selectively" names no asset or destination
    file. `references/output-contract.md` holds writing requirements, but is
    read only after the writing is done.
  - **Fix:** add a nine-row map from asset to destination that matches
    `research-attempt/references/project-context.md`, and read
    `output-contract.md` before Phase 4.
- [x] **RI-11** · medium · `research-init/SKILL.md:206-208` vs `:219-221`
  - **Problem:** a small project may state its mission in root AGENTS.md, but
    new setup puts the deliverable in the charter. The AGENTS template has no
    inline option (eval 13).
  - **Fix:** "…in the charter, or in an AGENTS.md *Mission* section when there
    is no charter", and add that optional section to the template.
- [x] **RI-14** · low-medium · `research-init/SKILL.md:211`
  - **Problem:** "at most one live dashboard" vs `output-contract.md:34` and
    research-program, which both say "exactly one".
  - **Fix:** "exactly one designated live dashboard".
- [x] **RI-15** · low-medium · `research-init/assets/AGENTS.template.md:32-35`
  - **Problem:** lists "superseded" as a freshness value and omits the review
    value "disputed". `evidence-model.md:14,25` treats "superseded" as an
    evidence label.
  - **Fix:** align the template with the evidence model, and qualify
    `:22-23` to "checked computation (for its exact finite assertion)".
- [x] **RI-16** · low-medium · `research-init/assets/RESEARCH_STATUS.template.md:3`
  - **Problem:** "Last reconciled: {{DATE}}" can't support the revision
    comparison the retrospective makes (`research-retrospective/SKILL.md:25-27`).
  - **Fix:** "Last reconciled: {{DATE}} at {{GIT_REVISION_OR_LEDGER_HEAD}}".

**Acceptance:**

- a two-attempt program trial, run with authorized delegation and then in
  deferred mode, with each attempt's continuation surviving a closeout;
- a continuation trial reuses an open program registered at an earlier
  checkpoint, with the execution and reconciliation based on a later checkpoint;
  its `continue` reconciliation remains visible in `next` and `handoff`, without
  duplicating the program or inventing base fields on the run result (RA-3,
  RS-9);
- the updated research-attempt eval 6 and research-program evals 6 and 14
  pass;
- `scripts/check.py`;
- the `inspect_repo.py` smoke test, if RI-7 has landed.

## Batch 4: Routing, descriptions and trigger evals

Goal: every risky pair of skills has explicit exclusions on both sides and a
disambiguating eval case in each direction, and `check.py` enforces the
mechanical rules in `AGENTS.md`.

### Findings

- [x] **X-1** · high · `skills/research-state/SKILL.md:4` (same as RS-6)
  - **Problem:** "Use when a project has a .mathbox ledger" triggers on
    repository state rather than on the request. The skill is implicitly
    invocable, and eight other skills already delegate to it.
  - **Fix:** rewrite the description (below) and add "Do not use merely
    because a ledger exists."
- [x] **X-2** · medium · `skills/research-attempt/SKILL.md:4`
  - **Problem:** the route types "source-dependent implication" and
    "claim-supporting computation" repeat triggers from literature-check and
    computation-audit. The description doesn't exclude auditing existing
    work, while proof-audit does exclude new routes.
  - **Fix:** "…counterexample search, or a computational or source-based
    attack. Do not use to audit an existing proof, computation, or source
    alone."
- [x] **X-14** · medium · computation-audit, literature-check and
  proofread-math descriptions (`SKILL.md:4`)
  - **Problem:** their only "Do not" clauses are behavior rules, not routing
    exclusions, which `AGENTS.md` requires (from CA-6, LC-7 and PM-7).
  - **Fix:** add these exclusions:
    - computation-audit: "Do not use to verify a cited theorem, audit a proof
      with no load-bearing computation, pursue a whole research route, or for
      general programming."
    - literature-check: "Do not use to audit a proof's internal logic, attack
      an implication, format bibliographies, or insert citations into a
      manuscript."
    - proofread-math: "Not for correctness audits, referee reports, or source
      verification."

    Move behavior-only clauses such as "Default to read-only" into the bodies
    where length is tight.
- [x] **PA-6** · medium · `skills/proof-audit/SKILL.md:4`
  - **Problem:** the triggers "verify, referee, stress-test" collide with
    referee's "referee report, whole-paper stress test".
  - **Fix:** "…verify, check, stress-test, type-check… a single claim, proof,
    or dependency".
- [x] **X-13** · low · `skills/manuscript-integrate/SKILL.md:4`
  - **Problem:** "referee response" shares a word with the referee skill.
  - **Fix:** reword to "a response to referee comments", and add "answering
    referee comments on one's own paper" to referee's exclusions.
- [x] **X-5** · medium · `README.md:121-123`, `evals/README.md:8-9`
  - **Problem:** an explicit skill is enforced differently on each host.
    - On Codex, `allow_implicit_invocation: false` enforces explicit-only
      skills. On Claude Code only the wording does.
    - research-attempt, research-init, research-retrospective and
      manuscript-integrate are explicit-only. On Codex, a request to attack a
      single bounded lemma therefore reaches no skill, because
      research-program excludes it.
    - The evals README doesn't say whether trigger evals assume the full suite
      is installed, or how explicit-only positives are scored.
  - **Fix:** document per-host semantics in the README, and add a routing
    protocol to `evals/README.md`.
- [x] **RF-12** · medium · `skills/referee/evals/trigger-evals.json:3,9,10`
  - **Problem:** these positives test implementation details (`alltt`, model
    controls) rather than routing.
  - **Fix:** replace them with routing-relevant phrasings.
- [x] **X-11** · medium · `scripts/check.py:41-43,77-79`
  - **Problem:** trigger evals are only parsed as JSON.
  - **Fix:** enforce:
    - the `{query: str, should_trigger: bool}` shape;
    - a description of at most 1,024 characters;
    - frontmatter containing only `name` and `description`;
    - README inventory and invocation column match the skill directories and
      `allow_implicit_invocation`;
    - the hand-kept canonical skill lists match `skills/`
      (`research-init/SKILL.md:249-251`, and `CANONICAL` in
      `research-init/scripts/inspect_repo.py:20-24`);
    - the marketplace description matches the plugin manifest;
    - changelog release headings match the manifest version.
- [x] **X-22** · low · `agents/openai.yaml` files
  - **Problem:**
    - `research-program/agents/openai.yaml:3`: the short description omits
      closeout.
    - `research-state/agents/openai.yaml:4`: the default prompt's "next
      research routes" overlaps research-retrospective.

### Description lengths and draft rewrites

All 11 descriptions are always in context, 5,057 characters in total. The goal
here is precision, not length: the added exclusions roughly offset the trims.

| Skill | Characters | Note |
|---|---|---|
| research-program | 619 | "Coordinate successive attempts…" does not help routing |
| research-init | 573 | the process sentence does not help routing |
| research-state | 537 | trigger too broad (X-1) |
| literature-check | 528 | safeguards instead of exclusions |
| referee | 491 | lists lanes and process |
| research-retrospective | 491 | |
| research-attempt | 415 | overlaps other skills (X-2) |
| proof-audit | 387 | |
| proofread-math | 349 | |
| manuscript-integrate | 337 | |
| computation-audit | 330 | no routing exclusion |

The drafts below keep every trigger and exclusion. Check each one against the
current text, merge in the X-14 exclusions, and rerun the trigger evals before
adopting it. Keep the suite's imperative voice
([not adopted](#findings-not-adopted)).

- **research-program (~520):** "Pursue a substantial mathematical goal across
  multiple proof, counterexample, literature, and computational routes, or
  close out one named program or phase by compacting its live status and
  history. Use for sustained investigation, several approaches, continuing
  after failed routes until a goal is reached, or an authorized program/phase
  closeout. Do not use for a single bounded attempt, explanation, proofreading,
  a read-only project retrospective, or migrating instructions or a flat
  research log into program indexes."
- **research-init (~430):** "Set up, plan a retrofit of, substantially revise,
  or migrate an AI-assisted mathematical research repository's agent
  architecture: AGENTS.md, CLAUDE.md, live status/history, workflow files and
  their authority structure, including moving a flat research log into program
  indexes. Use only on an explicit request. Do not use for an ordinary research
  attempt, closing out one named program or phase, or a read-only project
  retrospective."
- **research-state (~460):** "Read or update a local append-only .mathbox
  ledger of exact claims, evidence revisions, dependency impact, review
  provenance, routes and parallel or delayed runs. Use when the user asks to
  set up, check, record in or reconcile such a ledger, detect stale evidence,
  or generate its dependency-aware handoff. Do not use merely because a ledger
  exists, for a casual math question, as a substitute for proof auditing, or
  for a prose retrospective from status files."
- **literature-check (~430):** "Verify what an external mathematical source
  proves: exact theorem, hypotheses and version, citation, notation
  translation, source-dependent implication, or a bounded novelty claim; cache
  authenticated sources for reuse. Use when a proof relies on a named result,
  when the user asks whether a claim is known, or to cache a source. Do not use
  for citation formatting; never treat snippets or failed searches as proof or
  global novelty."
- **referee (~390):** "Referee a whole mathematical manuscript for correctness,
  edge cases, notation, exposition and claim calibration. Use for a referee
  report, whole-paper stress test, or section-by-section manuscript audit. Do
  not use for a focused claim or proof audit, proofreading alone, a standalone
  citation or computation check, answering referee comments on one's own paper,
  or developing new proofs."

### Proposed trigger-eval cases

These cases are merged and deduplicated from all reviewers. Sources: X-3, X-4,
CA-7, LC-7, MI-13, PA-6, RA-11, RP-10, RI-13, RS-7 and RF-12. Two of them are
new phrasings written here, for attribution and notation translation.

Each line is a `should_trigger` value and a query.

**computation-audit**

- `true` — "Audit the enumeration supporting Proposition 2."
- `true` — "Design a finite-field rank computation for Conjecture 2 up to n=12 and
  say what each outcome implies."
- `true` — "Is this floating-point eigenvalue check enough for Lemma 4?"
- `false` — "Find gaps in Theorem 2's proof."
- `false` — "Show stale evidence in the .mathbox ledger."
- `false` — "Referee this whole paper, including its computational appendix."
- `false` — "Attack the conjecture by searching for a counterexample up to
  n = 20 and record the route."

**literature-check**

- `true` — "Does citation [17] prove this?"
- `true` — "Check whether Theorem 3.2 of the cited paper, in our sign
  conventions, gives the statement we use in Lemma 5."
- `true` — "Who first proved this result, and is our attribution in the
  introduction accurate?"
- `false` — "Attack Lemma 5 by applying Theorem 2.1 of the cited paper after
  translating its notation, and record the route."
- `false` — "Check that every \cite key in paper.tex resolves."
- `false` — "Referee this paper."
- `false` — "Audit the proof of Lemma 4 for gaps."

**manuscript-integrate**

- `true` — "Incorporate our responses to the referee's comments into paper.tex."
- `false` — "Lemma 3 is now proved."
- `false` — "Check whether Theorem 2 in paper.tex is correct."
- `false` — "Referee this manuscript."
- `false` — "Check whether the corrected lemma is right before we add it to the
  paper."

**proof-audit**

- `true` — "Referee only the proof of Proposition 3.1."
- `false` — "Stress-test this whole paper."
- `false` — "Review this manuscript for mathematical correctness."
- `false` — "Proofread this paper."
- `false` — "Audit the Sage enumeration supporting Claim C7."

**proofread-math**

- `false` — "Integrate the validated Lemma 4.1 into paper.tex and update its
  cross-references."

**referee**

- `false` — "Referee the proof of Lemma 3.2 only."
- `false` — "Check this paper's notation consistency and cross-references."
- `false` — "Incorporate our responses to the referee's comments into paper.tex."
- `false` — "Do a final pass over the whole paper for typos, LaTeX errors and
  broken references."

**research-attempt**

- `true` — "Try to prove the comparison map is injective in degree 0 using the
  transfer."
- `true` — "Attack Lemma 5 by applying Theorem 2.1 of the cited paper after
  translating its notation, and record the route."
- `true` — "Attack the conjecture by searching for a counterexample up to
  n = 20 and record the route."
- `false` — "Check whether the proof of Lemma 2 has a gap."
- `false` — "Audit the Sage script supporting Claim C7 and record its
  provenance."
- `false` — "Rerun the existing verification script unchanged."
- `false` — "Record this route result in the .mathbox ledger."
- `false` — "Close out phase B."

**research-program**

- `false` — "Make one bounded attempt at Lemma 3 via Mayer–Vietoris, then stop."
- `false` — "Explain why this spectral sequence degenerates."

**research-retrospective**

- `true` — "What should I work on next in this project?"
- `true` — "This project uses .mathbox. Review the whole project and recommend
  the next three routes."
- `false` — "Review this manuscript and write a referee report."
- `false` — "Compact the live dashboard and move dated checkpoints into
  records." Depends on [D5](#decisions-needed).

**research-init**

- `true` — "Compact the live dashboard and move dated checkpoints into records."
  Depends on [D5](#decisions-needed).
- `false` — "Initialize a .mathbox ledger for this project and register Claims A
  and B."
- `false` — "What should I work on next in this project?"

**research-state**

- `false` — "This project has a .mathbox ledger; proofread the edited paragraph
  in Section 2."
- `false` — "This project uses .mathbox. Review the whole project and recommend
  the next three routes."
- `false` — "Set up AGENTS.md, a charter and a live status file for this
  research repository."
- `false` — "Attack lemma L in this .mathbox project."
- `false` — "Close out program P and compact its status."
- `false` — "Migrate our flat research log into program indexes."
- `false` — "Validate this computation manifest."

**Acceptance:**

- the trigger-eval JSON validates;
- `check.py` gains the X-11 checks and passes;
- a routing trial over the full suite, recorded under `evals/results/`, with
  explicit-only positives scored as `evals/README.md` defines;
- README updated if any invocation policy changes;
- changelog entries for the trigger-boundary changes.

## Batch 5: Token efficiency

Goal: smaller mandatory loads, with no rule lost. Each item names what stays.

### Targets

| File or load | Now | Target |
|---|---|---|
| `research-init/SKILL.md` | 2,327 words | ~1,200 |
| `research-state/SKILL.md` | ~1,490 | ~1,140 |
| `research-program/SKILL.md` | ~1,590 | ~1,370 |
| `research-attempt/SKILL.md` | ~1,410 | ~1,290 |
| `computation-audit/SKILL.md` | ~780 | ~680 |
| `literature-check/SKILL.md` | ~906 | ~800 |
| referee, per run | `model-assignments.md` (809) and `preparation.md` (1,218) always read; issue schema reached through `output-contract.md` | model file read only when models are specified; `preparation.md` ~450; ~800 fewer words per child |

### research-init

- [x] **RI-2** · high · `skills/research-init/SKILL.md`
  - **Phase 1 (~525 → ~220 words):** run the inspector first and keep only the
    judgments it cannot make. Drop `:70-83`, which describe the report format
    the report already prints. Lines `:36-63` repeat what the inspector does.
  - **Legacy log migration, `:154-198` (~410 words → a ~60-word router):** move
    it into `references/existing-repo-migration.md`, together with RI-3.
  - **Skill-layer rule, `:243-260` (~116 → ~40 words):** keep the rule, and
    point to `references/skill-layer.md` and the inspector's `CANONICAL`.
  - **Manuscript paragraph, `:104-108`:** replace with one line pointing to
    `references/interview.md`.
  - **Phase 4 (~342 → ~200 words):** move `:223-231` (pins, checkpoint
    preservation, size budgets) to the migration reference.
  - **Remove repeats:**
    - plugin upgrade: `:15-16`, `:148-149`;
    - inspector counts are not verdicts: `:78-80`, `:227-228`;
    - literature-derived inventory: `:51-53`, `:89-95`, `:131-132`;
    - no commit: `:28`, `:283`.
  - **Phase 5 item 6,** "Check instruction size": give a criterion or delete
    it.
- [x] **RI-24** · low · `research-init/references/output-contract.md:104-111`
  - **Problem:** about 90 words describe inspector behavior that the tests
    already cover.
  - **Fix:** delete.

### research-state

- [x] **RS-8** · medium · `skills/research-state/SKILL.md:121-158` (376 words)
  - **Problem:** the closure rule is stated at `:79-81` and again at
    `:129-133`. The reopening rules (`:134-136,150-154`) and continuation
    mechanics (`:142-149`) restate `ledger.md:286-309,399-406`.
  - **Keep:**
    - an inconclusive result, resource limit or priority change never
      justifies closure;
    - continuation is recorded through a run;
    - a pointer to `ledger.md` for the rest.

    This saves about 180 words.
- [x] **RS-9** · medium · `SKILL.md:144-147`
  - **Problem:** continuation through a run leaves its prerequisites and
    checkpoint relationships implicit: an open program covering the route,
    a registered execution, its result and a `continue` reconciliation.
  - **Fix:** "Use an existing open program whose goal covers the route, or
    register one if absent. Record the missing `route-run`, `run-result` and
    `route-reconcile` events, using `decision: continue`; reuse applicable
    existing records. The cited runs and their reconciliation must share a
    `base_event` and `base_revision`. A run result inherits its base through its
    run and has no base fields. The program retains its own starting checkpoint,
    which may differ from a later execution's base."
  - **Eval:** the continuation trial in Batch 3 uses different program and
    execution checkpoints without re-registering the program.
- [x] **RS-10** · medium · `SKILL.md:53-70`
  - **Problem:** `:53-65` (~130 words) restate
    `references/deferred-handoff.md`. Lines `:67-70` apply to every session
    but sit under "When state is writable only later".
  - **Fix:** cut the deferred section to its trigger, the pointer, and "never
    invent IDs or hashes; say the packet is unapplied" (saves ~80 words). Move
    `:67-70` to "Read before changing state".
- [x] **RS-11** · low-medium · `SKILL.md:15`
  - **Problem:** says to read `ledger.md` "before recording events", but its
    label table (`ledger.md:239-255`) is needed to interpret read-only
    reports. The review-label values are not listed.
  - **Fix:** "Read ledger.md before interpreting labels or recording events",
    and list the five review values at `ledger.md:224`.
- [x] **RS-12** · low-medium · `ledger.md:327-421`
  - **Problem:** "Programs, executions and reconciliation" (~590 of ~2,960
    words) is needed only for multi-session work.
  - **Fix:** move it to `references/executions.md`. See
    [D3](#decisions-needed).
- [x] **RS-15** · low · `SKILL.md:16-18,26-34,47`
  - **Problem:** the `--json` placement, "read-only" and "resolve TOOL" are
    each stated twice, and `ledger.md` is linked four times (`:15,49,151,157`).
  - **Fix:** state each once (~50 words).
- [x] **RS-23** · low · `migration.md:21-32,45-48`, `ledger.md:3-6`
  - **Problem:** these are version history, and they duplicate each other.
    `migration.md:45-48` is packaging guidance, not migration.
  - **Fix:** move both to the changelog (~120 words).
- [x] **RS-25** · low · `ledger.md:216,219-220,260-261`
  - **Problem:** the "disputed" rule is stated twice, and `:260-261` restates
    the label table.
  - **Fix:** keep one copy of each.

### research-program and research-attempt

- [x] **RP-12** · medium · `research-program/SKILL.md:40-45,70-76,168-172`
  - **Problem:** the parallel-run and lifecycle rules appear three times here,
    and again in `program-protocol.md:36-44` and `handoff.md:31-37`. The copies
    have drifted: `:169` has a "last-observed" state that `protocol:43` lacks.
  - **Fix:** keep two sentences in the portfolio section, and move ledger run
    inspection and the external lifecycle to the protocol (~110 words).
- [x] **RP-13** · medium · `research-program/SKILL.md:13-18,158-166`
  - **Problem:** restates closeout mechanics from
    `program-closeout.md:3-7,48-54,76-89`.
  - **Fix:** "At a substantial program or phase boundary, or on an explicit
    compaction request, follow [program closeout]; closeout does not close an
    unresolved goal." (~70 words).
- [x] **RP-18** · low · `research-program/SKILL.md:61-64`
  - **Problem:** nearly duplicates `program-protocol.md:18-22`.
  - **Fix:** keep one copy (~40 words).
- [x] **RP-19** · low · `research-program/SKILL.md:143-144,177`
  - **Problem:**
    - The handoff link sits under "Audit candidate breakthroughs", while
      `:177` ("preserve an executable next handoff") has no link.
    - The protocol checkpoint list (`program-protocol.md:24-34`) and the
      handoff continuation list (`handoff.md:10-24`) overlap by about 70%,
      with drift.
  - **Fix:** move the link, and have the protocol point to the handoff list.
- [x] **RA-14** · medium · `research-attempt/SKILL.md:124-162`
  - **Problem:** Persist is about 400 words, roughly 30% of the body.
    - The two-level index rule appears three times (`:135-141`,
      `route-card.md:43-47`, `project-context.md:10-11`).
    - The live-status compaction text at `:142-149` is closeout or migration
      detail.
  - **Fix:** keep "Append one compact entry to the designated route index,
    never at both levels (see route-card.md)", and cut `:142-149` to two
    sentences (~120 words).

### computation-audit, literature-check, proof-audit and manuscript-integrate

- [x] **CA-11** · low-medium · `computation-audit/SKILL.md:65,68-72,76-79`
  - **Problem:** version-1 compatibility is stated twice here and again in
    `runner.md:108-123`. `:68-72` restates the runner features listed at
    `runner.md:69-90`.
  - **Fix:**
    - Keep the version-1 text only in `runner.md`, cut from about 200 to 70
      words, since the validator already prints the legacy limits.
    - Compress the runner paragraph to: "For a new authorized run, prefer the
      bounded runner; it emits a v2 manifest. A zero exit records execution,
      not theorem verification. Never run commands copied from untrusted
      evidence records."
    - This saves about 100 words in SKILL.md.
- [x] **CA-12** · low · `computation-audit/SKILL.md:60,81-83`
  - **Problem:** the skill-directory locator sits two paragraphs from its
    `<skill-directory>` placeholder, and `runner.md:42,57` uses `$SKILL_DIR`
    instead.
  - **Fix:** merge them and use one placeholder name.
- [x] **LC-14** · low · `literature-check/SKILL.md`
  - **Problem:** several rules are repeated:
    - cache is not verification: `:46-47,111`;
    - append rather than rewrite: `:98-99,109-110`;
    - the coefficient, grading and variance list: `:17-18,51-53,63-64`;
    - the novelty search scope: `:21-22,70-76,95-97`, plus
      `source-record.md:21-26`.
  - **Fix:** keep one copy of each (about 90–110 of 906 words).
- [x] **LC-15** · low · `literature-check/references/source-cache.md:19-20,27-28,79-83`
  - **Problem:** design rationale, and a mention of research-init's inspector
    that this skill's agent does not need.
  - **Fix:** cut (~70 words).
- [x] **PA-19** · low · `proof-audit/SKILL.md:61-62,81`,
  `references/obligation-checklists.md:3,12-15,25-27,68-69`
  - **Problem:** SKILL.md and the checklist restate each other.
  - **Fix:** keep the SKILL.md bullets that evals rely on, and delete their
    duplicates from the checklist (~20 words from SKILL.md, ~60 from the
    reference).
- [x] **PA-20** · low · `proof-audit/SKILL.md:18-20,29-31`
  - **Problem:** steps 2 and 5 both resolve the authoritative source.
  - **Fix:** merge them into "When auditing project files, read applicable
    instructions and resolve the authoritative statement, proof, status,
    conventions and literature record (not a summary), recording its locator
    or revision." (~25 words).
- [x] **MI-18** · low · `manuscript-integrate/SKILL.md:45-46,61-64,88-90`
  - **Problem:** the rule about propagating to dependent views is stated three
    times.
  - **Fix:** reduce the Edit bullet to "If a protected dependent cannot be
    changed, mark the exact conflict and do not report propagation complete."
    (~25 words).

### referee

- [x] **RF-9** · medium · `referee/SKILL.md:72-75`
  - **Problem:** `model-assignments.md` (809 words) is mandatory even when no
    model preference is stated, which is the common case.
  - **Fix:** "When the user or project prescribes models or reasoning, read
    model-assignments.md; otherwise inherit host defaults and record null
    requested fields."
- [x] **RF-10** · medium · `referee/references/preparation.md`
  - **Problem:** 1,218 words, always loaded. `:12-58` describe lexer
    internals: CR handling, `alltt` flow, segment caching, macOS `/var`.
  - **Fix:**
    - Move those internals to the script docstring.
    - Keep the invocation, run layout, exit code 2 with the fresh-directory
      retry rule, the limits that need manual inspection, and comparison
      semantics (~450 words).
    - Replace the prose at `:72-90` with the actual unit keys: `id`, `sha256`,
      `identity_sha256`, `file`, `reviewable`, `skip_reason`, `location`.
- [x] **RF-16** · low · `referee/SKILL.md:20-25,130-143`
  - **Problem:** restates `final-referee.md` steps 1-6,
    `output-contract.md:148-149` and the description's exclusions.
  - **Fix:** keep the two invariants (agreement is not proof; absence of
    findings certifies nothing) and point to the references (~120 words).
- [x] **RF-17** · low · `referee/SKILL.md:9-11`, `preparation.md:4,149-150`
  - **Problem:** author-facing or time-sensitive text.
  - **Fix:**
    - Replace "Port mathematical review methodology, not an LLM runtime…" with
      "Use the host's native reasoning and delegation; do not install external
      review runtimes, provider SDKs, or credentials."
    - Drop "installs Math Scout" and the roadmap note.

### Suite and README

- [x] **X-18** · low · suite boilerplate
  - **Problem:**
    - The literature-check routing paragraph (60–80 words) appears seven
      times: computation-audit `:25-31`, manuscript-integrate `:24-31`,
      proof-audit `:71-77`, research-attempt `:75-81`,
      research-retrospective `:38-43`, research-init `:89-95` and
      proofread-math `:42-46`.
    - The `.mathbox` paragraph that routes to research-state appears eight
      times, the deferred-packet sentence four times, and the
      independent-review paragraph three times.
    - Together that is about 1,250 of 12,500 SKILL.md words. Each run loads
      only one copy, so the real cost is that the copies drift apart.
  - **Fix:** shrink each copy to one line and keep its fallback, which
    preserves independent installation. Drop "That workflow checks an
    authorized project-local cache before fetching" from the five callers.
- [x] **X-21** · low · `README.md:128-154,189-206`
  - **Problem:** the Safeguards section (including the referee
    model-assignment detail at `:143-146`) and the tool descriptions restate
    skill contracts.
  - **Fix:** reduce them to one-liners with links.

**Acceptance:**

- the measured word counts meet the targets;
- every behavioral eval for a trimmed skill still passes in a trial run;
- `scripts/check.py`, which verifies the links to moved reference text;
- changelog entries only where behavior or load order changes.

## Batch 6: Vocabulary, cross-references and packaging

### Vocabulary and skill references

- [x] **X-8** · medium · "handoff" has five meanings
  - **The five:**
    - a prose project handoff (`research-retrospective/SKILL.md:4`);
    - the generated `handoff --goal` (`research-state/SKILL.md:4,23`);
    - a continuation handoff (`research-program/SKILL.md:143,177`,
      `references/handoff.md`);
    - an "executable handoff" (`research-attempt/SKILL.md:121`);
    - the deferred write packet (`research-state/SKILL.md:55`,
      `proof-audit/SKILL.md:40`, `literature-check/SKILL.md:113`,
      `research-attempt/SKILL.md:154`, `research-program/SKILL.md:151`).
  - **Fix:** call the last one a "deferred packet" (`mathbox-deferred-v1`) in
    prose. Consider renaming `deferred-handoff.md` and updating its links.
- [x] **X-9** · medium · skill-name references
  - **Problem:** the standard form is "the available `X` skill (`mathbox:X` in
    plugin installations)" with a fallback (e.g. `proof-audit/SKILL.md:72-75`;
    `referee/SKILL.md:99-103` gives the general rule). These places
    hard-code the plugin name or have no fallback:
    - `manuscript-integrate/SKILL.md:82`;
    - `research-attempt/SKILL.md:25,84-85,149,161`;
    - `research-retrospective/SKILL.md:47,119`;
    - `computation-audit/SKILL.md:113`;
    - `literature-check/SKILL.md:108,112-113`.
  - **Fix:** use the standard form everywhere.
    - literature-check's fallback should say: "If research-state is
      unavailable, report the proposed source evidence fields and say nothing
      was recorded."
    - research-retrospective `:119` should also allow research-program when
      the top route spans several approaches.
- [x] **X-6** · medium · ✔ · `research-retrospective/SKILL.md:95-96`
  - **Problem:** "the `mathbox` feedback ledger" is not defined anywhere in the
    repository.
  - **Fix:** "report general plugin-skill bugs to the user (or the Mathbox
    issue tracker)".
- [x] **X-15** · low · `research-state/SKILL.md:172`
  - **Problem:** "the mathematical specialist workflow" is undefined.
  - **Fix:** name proof-audit, computation-audit or literature-check.
- [x] **X-16** · low · "ledger" used for literature
  - **Problem:** "literature ledger" (`literature-check/SKILL.md:24,103`,
    `manuscript-integrate/SKILL.md:17`, `research-retrospective/SKILL.md:15`)
    vs "literature record" (`proof-audit/SKILL.md:72`,
    `research-init/SKILL.md:89`).
  - **Fix:**
    - Use "literature record", so that "ledger" means only `.mathbox`.
    - In literature-check, use "source record" for the "durable
      extraction/translation report".
    - Replace "verified-source event" with "`source` evidence" (from LC-13).
- [x] **X-17** · low · `research-program/SKILL.md:165`,
  `research-init/SKILL.md:196`
  - **Problem:** "retrospective closeout" collides with the
    research-retrospective skill name.
  - **Fix:** "historical closeout".
- [x] **X-24** · low · history vocabulary
  - **Problem:** many names for the same things: "history entry point",
    "compact history index", "research-history index", "flat index",
    "top-level history", "the log" and "journal"
    (`research-attempt/SKILL.md:13,21,42`, `research-program/references/handoff.md:33`,
    research-init). This merges RA-20 and RI-23.
  - **Fix:** define "entry point", "route index" and "route record" once in
    `research-attempt/references/project-context.md`, and mirror them in
    research-init. Add "history entry point" to the inspector's aliases.
- [x] **PA-22** · low · `proof-audit/SKILL.md:26,76,102`
  - **Fix:**
    - "mark that obligation conditional", not "leaf";
    - "after reviewing downstream dependents", not "blast radius";
    - "the project's recorded evidence label".
- [x] **PM-23** · low · `proofread-math/SKILL.md:34-35`
  - **Problem:** "referee-level proof audit" collides with the referee skill.
  - **Fix:** "without auditing correctness (that belongs to `proof-audit`)".
- [x] **MI-11** · medium · `manuscript-integrate/SKILL.md:53-54`
  - **Problem:** the support categories differ from proof-audit's leaf types
    and from the suite's labels.
  - **Fix:** use the project's evidence labels: proved, externally proved,
    computationally verified in a stated range, conditional, heuristic,
    conjectural.
- [x] **CA-15** · low · `computation-audit/SKILL.md:9,17`
  - **Problem:** "finite assertion", "exact computational surrogate" and
    `assertion_tested` name the same concept, and "surrogate" is undefined.
  - **Fix:** "finite assertion actually computed (recorded as
    `assertion_tested`)".

### Packaging and repository documents

- [x] **X-10** · medium · `docs/CHANGELOG.md:42-47,57-71`
  - **Problem:** the "Fixed" entries describe bugs in the referee preparation
    helper, which has never been released. The first "Changed" entry
    describes a new referee feature.
  - **Fix:** fold both into the referee "Added" entries, as `AGENTS.md`
    requires.
- [x] **X-12** · low · `.claude-plugin/marketplace.json:12`
  - **Problem:** the description differs from `.claude-plugin/plugin.json:3`
    and `.codex-plugin/plugin.json:4`, and no keyword mentions refereeing.
  - **Fix:** align them.
- [x] **X-20** · low · `README.md:54`
  - **Problem:** "not available yet" is time-sensitive.
- [x] **X-23** · low · `AGENTS.md:25`
  - **Problem:** "`evals/evals.json`" reads as a root path, but the root
    `evals/` directory holds `cases.json`.
  - **Fix:** write `skills/<name>/evals/…`.
- [x] **RI-22** · low · `research-init/assets/CLAUDE.md`
  - **Problem:** breaks the `.template.md` naming. The inspector lists it as
    an instruction file, and a vendored copy may load as nested memory.
  - **Fix:** rename it to `CLAUDE.template.md`.

**Acceptance:**

- `grep` finds no remaining old terms;
- `scripts/check.py` link checks pass;
- `claude plugin validate`, both manifests;
- changelog entries for any user-visible renames.

## Batch 7: Remaining clarity and eval-coverage items

These items can ride along with whichever batch touches the same file.

### computation-audit

- [x] **CA-14** · low · `SKILL.md:87,117-120`
  - **Problem:** there are two output specifications, and the report omits the
    outcome label.
  - **Fix:** use one numbered template:
    1. contract and non-claims;
    2. code paths and command;
    3. provenance (manifest path, `run.status`);
    4. checks performed;
    5. outcome label and exact result;
    6. residual risks;
    7. structural features, and either a uniform argument or the next
       discriminating check.
- [x] **CA-16** · low · `evals/evals.json:33`
  - **Problem:** eval 3 asserts "Checks the authorized local cache before
    fetching", which is literature-check's internal behavior. The fallback at
    `SKILL.md:28-29` has no cache step.
  - **Fix:** make the assertion conditional on literature-check being
    available.

### literature-check

- [x] **LC-3** · medium · `SKILL.md:60-62`
  - **Problem:** "Record which of these was actually checked" has no slot in
    the report (`:116-124`) or in `source-record.md`.
  - **Fix:** add "**Checks performed:** source authenticated / theorem
    extracted / project application".
- [x] **LC-8** · medium · `SKILL.md:29-31,45-46`
  - **Problem:** step 1 queries the cache, but the `find` syntax lives only in
    `source-cache.md`, and the pointer covers only initializing or modifying
    the cache.
  - **Fix:** link `source-cache.md` from step 1, and change the later pointer
    to "before any cache command".
- [x] **LC-11** · low · `source-cache.md:73-75`
  - **Problem:** doesn't say whether the agent may edit `.gitignore`.
  - **Fix:** "If the helper warns, report it; add the rule only when
    authorized."
- [x] **LC-12** · low · `source-cache.md:84-85`
  - **Fix:** "From the cache, record only its SHA-256 and extraction status…".
- [x] **LC-17** · low · `evals/evals.json`
  - **Problem:** no cases for:
    - notation translation and attribution;
    - an "apparently new" report with the full scope fields;
    - the helper's `.gitignore` warning or a metadata conflict;
    - finding where the retention policy lives.

### proof-audit and proofread-math

- [x] **PA-5** · medium · `proof-audit/SKILL.md:64-68`
  - **Problem:** computation leaves are audited inline, with no route to
    computation-audit.
  - **Fix:** "Route a load-bearing computation leaf through the available
    `computation-audit` skill; otherwise apply these checks directly."
- [x] **PA-9** · medium · `proof-audit/SKILL.md:107-123`
  - **Problem:** the independence protocol sits under Output, and its trigger
    is vague. The output list lacks review provenance and freshness, which
    evals 3 and 7 assert.
  - **Fix:**
    - Move the protocol to an "Independence" section that starts "When the
      user or project requires an independent audit…".
    - Add output item 7: "review provenance (self-review or independent) and
      the exact revision audited".
    - This saves about 35 words.
- [x] **PA-14** · low · `proof-audit/SKILL.md:27-28`
  - **Fix:** "…return the ill-typed verdict; continue only under explicitly
    labelled readings."
- [x] **PM-8** · medium · `proofread-math/SKILL.md:21`
  - **Problem:** no default mode is given for a plain "Proofread this paper."
  - **Fix:** "When the caller does not explicitly ask for corrections, use
    review-only mode."
- [x] **PM-21** · low · `proofread-math/SKILL.md:17-19`
  - **Problem:** self-review says to inspect only the changed hunks, but
    allows edits anywhere in the changed files.
  - **Fix:** "Correct routine issues only inside the changed hunks; report
    others."

### manuscript-integrate

- [x] **MI-15** · low · `SKILL.md:73-76`
  - **Problem:** "When the mathematical state changes" is undefined, and the
    default record paths would be created even in projects that keep no
    research records.
  - **Fix:** "When integration changes a claim's statement, scope, or status
    (not its prose), and the project keeps research records, update…".
- [x] **MI-17** · low · `references/integration-checklist.md:3`
  - **Problem:** "word for word in scope" contradicts the notation translation
    required at `SKILL.md:41`.
  - **Fix:** "exactly in scope and hypotheses, modulo the recorded notation
    translation".

### referee

- [x] **RF-7** · medium · `model-assignments.md:80-82`
  - **Problem:** a delegated final referee does not receive `final-referee.md`
    or `output-contract.md`.
  - **Fix:** add both.
- [x] **RF-13** · medium · `evals/evals.json`
  - **Problem:** no cases for:
    - the no-edit default when the user does not mention it;
    - the order of the eight report sections;
    - the child handoff and ID uniqueness;
    - no unrequested accept/reject recommendation (`final-referee.md:45-47`).
- [x] **RF-18** · low · `review-protocol.md:43-46`, `exposition.md:22`
  - **Fix:** "Exposition: at most major. Notation/presentation: at most major
    unless a statement has no single evaluable meaning; then treat it as a
    mathematical finding."
- [x] **RF-19** · low · `final-referee.md:31-32`
  - **Fix:** "Confirmed mathematical concerns from any lane".
- [x] **RF-20** · low · `output-contract.md:71-73`
  - **Fix:** "`lane` is one of `correctness`, `adversarial`, `exposition`,
    `notation`, `claims`, or `final-referee`."

### Research workflow skills

- [x] **RR-12** · medium · `research-retrospective/evals/evals.json`
  - **Problem:** three assertions have no instruction behind them:
    - eval 1, "States the strongest safe current claim";
    - eval 7, "Does not hide the presence or count of omitted stale issues";
    - eval 2, "rephrases the next action", which is only partly backed.
  - **Fix:** add a "strongest currently supported statement" portfolio field,
    and "report omitted-issue counts from brief checks".
- [x] **RI-17** · low · `research-init/evals/evals.json` (eval 6)
  - **Problem:** asserts "Reports misplaced root skills…", but the prompt has
    no root `skills/` directory.
  - **Fix:** add one to the prompt, or drop the clause.
- [x] **RS-22** · low · `research-state/evals/evals.json`
  - **Problem:** no cases for:
    - revalidation with `supersedes`;
    - a manifest-linked computation;
    - `impact`;
    - declining `init` for an unauthorized or casual request.
- [x] **RS-24** · low · `research-state/SKILL.md:28-29,68,165-166`
  - **Fix:**
    - "retracted dependency evidence", not "A retracted dependency";
    - "a generated brief view", to reconcile the two dashboard sentences.

## Decisions needed

| ID | Question | Blocks | Recommendation |
|---|---|---|---|
| D1 | Ship a version-2 hand-fillable manifest template, or limit the template to version-1 records of runs made outside the runner? | CA-1, RS-18 | First check whether a hand-filled version-2 record can pass `validate_manifest.py` without fields only the runner produces. If it can, ship it; otherwise limit the template's scope. |
| D2 | When research-state rejects unknown payload keys, must existing ledgers still replay? | RS-2 | Validate only when recording new events. Leave replay of existing events unchanged, with no ledger schema bump. |
| D3 | Split the executions section of `ledger.md` into its own reference? | RS-12 | Yes, if RS-8 and RS-10 do not already bring the research-state load within budget. |
| D4 | How should referee invocation respect the host's delegation authorization rules (RF-3)? | RF-1, RF-2, RF-4 | Follow the actual host rules. A skill invocation authorizes delegation only if those rules permit it. Where explicit user delegation is required, obtain it before spawning or use disclosed sequential self-review. Do not ask again when applicable delegation authorization already exists. |
| D5 | Should research-retrospective keep an edit mode for compaction, or always hand off to a research-program closeout or a research-init migration? | RR-1, trigger cases | Keep a narrow reconcile-only edit mode with the RR-1 guard, and route compaction elsewhere. |
| D6 | For an unversioned arXiv match, change the helper's output or only the documentation? | LC-5 | Change the output label. The ledger safeguard depends on it. |
| D7 | Can research-program invoke the explicit-only research-attempt on Codex? | RP-8, X-5 | Needs a check on a real host. Add RP-8's fallback either way. |
| D8 | Per-file contract hashes in the referee manifest, or rerun everything on any contract change? | RF-8 | Use the additive `contract_files` map; incremental reuse is the point of the snapshot. |
| D9 | Land all batches in this PR, or split them into follow-up PRs? | all | Batches 1–3 as separate commits here. Split batches 4–6 into follow-up PRs if the diff becomes hard to review. |

## Findings not adopted

- **Third-person descriptions** (raised under LC-7, RF-22, RA/RP-25 and
  RS-25). The whole suite uses imperative voice consistently, and both hosts
  route on content, not voice. Revisit only as a suite-wide change.
- **Removing per-skill copies of shared routing text.** Every skill must remain
  installable on its own, so X-18 shrinks the copies instead of removing them.

## Not covered by this review

- live routing or behavioral eval trials with fresh agents, on either host;
- conversion to OpenAI/Codex format (no Codex CLI was available);
- `openai.yaml` field-length limits;
- GitHub release titles against the changelog;
- non-POSIX runner behavior;
- the Windows `O_BINARY`, CRLF and locale branches beyond the existing tests.
