# Project-context resolution

Terminology: the **history entry point** is the navigational file reaching program
or phase histories; a **route index** contains compact linked outcomes; a
**route record** is the immutable standalone account of one material attempt.
In a small flat project, entry point and route index may be the same file.

Use explicit paths in the applicable `AGENTS.md` first. Otherwise prefer:

- charter: `PROJECT_CHARTER.md`;
- live state: exactly one of `RESEARCH_STATUS.md` or `HANDOFF.md`;
- claims: `PROOF_OBLIGATIONS.md`, then `CLAIMS.md`;
- conventions: `CONVENTION_REGISTRY.md`, then `CONVENTIONS.md`;
- literature: `LITERATURE_LEDGER.md`, then `LITERATURE.md`;
- history entry point: `RESEARCH_LOG.md`; follow its program/phase links to the
  designated route index when the project uses a hierarchical history;
- detailed history: `research/records/`;
- verification: `VERIFICATION.md`;
- repository map: `README.md` or `CODE_MAP.md`.

Do not read every candidate wholesale. If two candidates make conflicting
claims and `AGENTS.md` does not resolve authority, expose the conflict rather
than choosing the stronger or newer-looking statement.
