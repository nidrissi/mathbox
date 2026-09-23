# Repository initialization acceptance checklist

## Root instructions

- Exact live filename is `AGENTS.md`.
- Root instructions point to the charter for the mission, current deliverable,
  success/fallback, and exclusions; mutable values are not copied into AGENTS.md.
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
- A long status or history file is searchable by relevant section; instructions
  do not require loading it wholesale for every research task.

## Claude instructions

- `CLAUDE.md` is optional when Claude Code loads `AGENTS.md` directly.
- If present alongside `AGENTS.md`, `CLAUDE.md` imports `@AGENTS.md` rather
  than duplicating it; additions are genuinely Claude-specific.
- The user verifies instruction loading in a fresh/current session.

## Research records

- Exactly one live dashboard is designated.
- The dashboard states current evidence, blocker, and next action. Older
  checkpoint narratives are linked from the compact history index and durable
  records rather than stacked in the live file.
- Claims have exact hypotheses and durable evidence links.
- Evidence, independent review and freshness are separate fields. If an optional
  `.mathbox/` ledger is adopted, its authoritative role and single live view are
  explicit; old confident prose is not automatically imported as proof.
- Computations state exact range and provenance.
- Blockers name the missing implication.
- Logging threshold is route-level, not command-level.
- The designated history entry point is compact. A flat route index is valid
  for small projects; sustained programs use program/phase entries leading to
  closeouts and route indexes, without repeating all route lines at the top.
- Program closeouts preserve the original target, strongest surviving result,
  first failed steps, evidence/review conditions, and next decision with links.
- Retrospective closeouts distinguish a provenance-labeled historical cutoff
  from the later assessment checkpoint; later evidence is not backdated.
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

## Existing-repository migration, when requested

- The plan identifies existing authority, protected rules, baseline ledger
  issues, and active file pins; a plugin upgrade alone does not trigger edits.
- A source-to-destination crosswalk accounts for substantive live-status and
  instruction material before replacing it, without duplicating chronology.
- Pinned charter, proof, or evidence files are not rewritten or rehashed just
  to conform to a template; unresolved claim conflicts remain explicit.
- Existing numbered ledger events and immutable indexed records stay intact.
  A prose-only project is not forced to adopt a ledger.
- If a flat index is sharded, its old entries and working links remain
  reachable. Mission-relevant routes of uncertain program membership stay in
  a linked unclassified inventory; foreign or mission-ambiguous text follows
  the reviewed quarantine policy. Neither is silently promoted to a verdict.
- Before/after checks compare exact claim, review, issue, link, and instruction
  state; pre-existing stale issues are distinguished from introduced ones.

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
  links/path-shaped code spans. Its brief report counts omitted candidates,
  keeps log and manifest classifications and skill-location findings, and
  separates historical-path examples from current-path examples; route
  records count as current. Dated
  checkpoint-marker counts remain tentative and never decide claim status.
- Project-specific size or repeated-checkpoint triggers prompt compaction review
  but never license automatic truncation of current mathematical conditions.

## Skills

- The `mathbox` plugin was detected or its absence reported.
- No `mathbox` plugin workflow was recreated locally.
- No skill exists under root `skills/`.
- Any project skill has a distinct name, justification, correct tool path, and
  evals.
- Duplicate or stale project skills are archived only with approval.
