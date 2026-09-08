# Repository initialization acceptance checklist

## Root instructions

- Exact live filename is `AGENTS.md`.
- Mission, current deliverable, success/fallback, and exclusions are explicit.
- Source-of-truth order is unambiguous.
- Mutable status is referenced, not duplicated.
- Evidence labels and claim-promotion standards are defined.
- Protected, read-only, and routine paths are explicit.
- Commands are verified and concrete.
- Git, network, confidentiality, and handoff policies are explicit.
- Any authorized local literature cache has an explicit retention policy and a
  verified `/.research-cache/` Git ignore rule.
- No unexplained residue from another repository remains.
- Root instructions are concise; detailed procedures are not copied into them.

## Claude bridge

- `CLAUDE.md` imports `@AGENTS.md` rather than duplicating it.
- Additions are genuinely Claude-specific.
- The user verifies it in a fresh/current session.

## Research records

- Exactly one live dashboard is designated.
- Claims have exact hypotheses and durable evidence links.
- Evidence, independent review and freshness are separate fields. If an optional
  `.mathbox/` ledger is adopted, its authoritative role and single live view are
  explicit; old confident prose is not automatically imported as proof.
- Computations state exact range and provenance.
- Blockers name the missing implication.
- Logging threshold is route-level, not command-level.
- `RESEARCH_LOG.md` is a compact index whose entries link to standalone records.
- Standalone records have a title, date, normalized filename, outcome/evidence
  label, decisive evidence, and next unresolved question.
- Indexed records and historical entries are append-only; corrections are new
  linked records.
- Source-derived theorem/fact inventory entries remain labeled as candidate or
  unchecked until an exact source record is verified; dependent proof and
  manuscript work does not silently treat them as established inputs.
- Any detected long-form legacy log has an approved, lossless migration mapping
  or is explicitly reported as pending.
- A legacy mapping classifies each source span as mission-relevant, foreign or
  ambiguous against the repository's stated mission.
- Foreign, ambiguous and unmatched material is preserved in quarantine and is
  not indexed as live project history without a reviewed reclassification.
- Source boundaries, dates, destinations, carried evidence labels and unresolved
  provenance are reviewed before the compact index replaces the legacy log.

## Manuscript constraints, when applicable

- Venue, call/template and submission category are confirmed, not inferred.
- Document language and intended mathematical audience are confirmed.
- Deadline includes date, time, timezone and hard/soft/internal status.
- The page/count convention explicitly states treatment of front matter,
  bibliography, figures/tables, appendices and supplemental material.
- The page budget separately allocates front matter, main exposition,
  figures/tables, bibliography, appendices/supplement and contingency.
- Unknown constraints or allocations remain labeled unknown; an old template,
  current page count or generic venue norm is not substituted for owner input.

## Verification

- Fast, targeted, full, and manuscript commands are distinguished.
- Full-suite triggers are risk-based.
- Deterministic rules have a script/test/CI/hook plan where appropriate.
- Canonical mathematical benchmarks are named.
- Final report lists checks not run.
- Inspector output distinguishes clean Git from unavailable metadata, inventories
  computation manifests separately, reports semantic role aliases and potential
  duplicate dashboards/handoffs, and conservatively identifies broken relative
  links/path-shaped code spans.

## Skills

- The `mathbox` plugin was detected or its absence reported.
- No `mathbox` plugin workflow was recreated locally.
- No skill exists under root `skills/`.
- Any project skill has a distinct name, justification, correct tool path, and
  evals.
- Duplicate or stale project skills are archived only with approval.
