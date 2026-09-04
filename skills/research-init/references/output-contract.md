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
- No unexplained residue from another repository remains.
- Root instructions are concise; detailed procedures are not copied into them.

## Claude bridge

- `CLAUDE.md` imports `@AGENTS.md` rather than duplicating it.
- Additions are genuinely Claude-specific.
- The user verifies it in a fresh/current session.

## Research records

- Exactly one live dashboard is designated.
- Claims have exact hypotheses and durable evidence links.
- Computations state exact range and provenance.
- Blockers name the missing implication.
- Logging threshold is route-level, not command-level.
- `RESEARCH_LOG.md` is a compact index whose entries link to standalone records.
- Standalone records have a title, date, normalized filename, outcome/evidence
  label, decisive evidence, and next unresolved question.
- Indexed records and historical entries are append-only; corrections are new
  linked records.
- Any detected long-form legacy log has an approved, lossless migration mapping
  or is explicitly reported as pending.

## Verification

- Fast, targeted, full, and manuscript commands are distinguished.
- Full-suite triggers are risk-based.
- Deterministic rules have a script/test/CI/hook plan where appropriate.
- Canonical mathematical benchmarks are named.
- Final report lists checks not run.

## Skills

- The `mathbox` plugin was detected or its absence reported.
- No `mathbox` plugin workflow was recreated locally.
- No skill exists under root `skills/`.
- Any project skill has a distinct name, justification, correct tool path, and
  evals.
- Duplicate or stale project skills are archived only with approval.
