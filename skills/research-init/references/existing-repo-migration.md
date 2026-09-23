# Migrate existing instructions and live research state

Use this workflow only for an explicitly requested repository retrofit or its
plan. It concerns project files, not installation of a newer `mathbox` plugin.
Existing schema-v1 `.mathbox/` journals remain readable without rewriting
events; a repository without a ledger need not acquire one. Do not create a
second manually maintained claims dashboard.

## Establish a reviewable baseline

- Inspect Git state and the applicable instructions. Identify the charter,
  claims, conventions, live dashboard/handoff, history index, durable records,
  proof artifacts, and exact edit/approval boundaries. Use the brief inspector
  first; open only the full sections needed to resolve current-path findings.
  File size and dated headings suggest review, not obsolescence.
- Name the current authority for each role. Resolve competing live files and
  stale or contradictory instructions from evidence, not filename or timestamp.
  If authority is ambiguous, leave the affected text in place and request the
  specific decision before replacing it.
- Where `.mathbox/` exists, use the available `research-state` skill to capture
  `check --summary`, relevant goal handoffs, and `pin-impact PATH` for each file
  proposed for editing. Record issue counts and representative IDs, including
  pre-existing stale evidence. Inspect exact artifacts for material conflicts;
  a clean ledger check is not a proof audit. Querying active pins does not prove
  that an unpinned document is semantically safe to change. If that skill is
  unavailable, report the limit and inspect existing records without copying
  its code into the repository.

## Map before compressing

For a plan-only request, inventory headings and representative sections; mark
uninspected ranges rather than loading a huge file into context. Before
replacing old content, complete a source-to-destination crosswalk for each
substantive status/handoff section and instruction rule. Work in bounded
sections. Repetitive sections may be grouped when their source boundaries
stay traceable. A useful row identifies source span, current
claim or purpose, authority/evidence label, destination or preserved archive,
action, pin impact, and unresolved question. Keep it in the reviewable plan or
PR; do not create a permanent duplicate inventory unless the project needs it.

- Keep the live view to current result, exact evidence and review status,
  principal blocker, active route, and bounded next action. Move chronology to
  linked program closeouts, immutable route records, and their indexes. If a
  historical passage has no durable home, preserve it with provenance in a
  linked record or archived snapshot before replacing the live body. Git
  history alone is not a discoverable research index. Do not copy the same
  narrative into both the dashboard and a new record.
- Retain every unique mathematical convention, protected-path rule,
  authorization boundary, confidentiality rule, and verified check when
  shortening `AGENTS.md`. Point to the authoritative charter and live view;
  remove duplicated mutable facts only after their destination is verified.
  Replace blanket instructions to load whole growing files with a current
  summary plus targeted lookup, not with permission to skip relevant evidence.
- Treat route-level prose in `RESEARCH_LOG.md` under the separate reviewed
  legacy-log mapping in `SKILL.md`. Do not silently turn foreign or ambiguous
  history into live project records.
- Keep contradictory mathematical statuses visible as unresolved until the
  exact proof, source, or computation has been checked. Never choose the newest
  confident sentence merely because it is newer.

## Migrate a long flat history index

If a flat `RESEARCH_LOG.md` has itself become large, do not merely rename it or
summarize its lines into one confident program verdict. Inventory its entries
in bounded sections. Map each relevant route to a program or phase by the
actual target and mechanism; preserve uncertain or foreign entries under the
reviewed legacy-log classification in `SKILL.md`. Write one linked closeout
per material program/phase, carrying exact evidence and review limits. A short
top-level entry point then links closeouts and route indexes; each route index
retains one-line links to its immutable records. Do not duplicate every route
line at the top level.

Prefer keeping the old flat file intact as a frozen legacy route index and
designating a new compact entry point in project instructions, with a link to
that legacy index. Future routes go to program/phase indexes. If the project
instead needs the old filename for the new entry point, preserve a lossless
snapshot of the old index, rebase moved relative links mechanically, verify
every destination, and obtain the required mapping review before replacement.
Old entry text and evidence labels remain historical; program summaries do
not upgrade them. A small project may keep its flat index without sharding.

## Handle ledger and artifact pins conservatively

Compacting an unpinned dashboard needs no ledger event if no mathematical
contract changed. A session or migration itself needs no event. Do not refresh
any hash just to silence staleness. A whole-file pin stales on any byte change;
before editing such a file, either preserve it, move the intended edit to an
appropriate unpinned current-state file, or arrange the required mathematical
recheck and claim/evidence revision through `research-state`. Do not move
mutable facts into a heavily pinned charter merely to match a template. A
`pin-impact` result covers active declared pins, not every semantic reader or
historical reference.

If ledger adoption is separately useful and authorized, follow the
`research-state` migration contract: map exact claims and checked artifacts,
preserve valid IDs, and leave unsupported old “proved” labels unpromoted. Do
not parse prose automatically into proof events or rewrite numbered events.

## Verify and stop appropriately

Before replacing a live file, verify that every substantive old span has a
durable destination or is explicitly retained as unresolved. Compare exact
claim wording, evidence and review conditions, current blockers, active route,
protected rules, and all edited links against the baseline. Rerun the targeted
project checks and ledger `check --summary` when present; compare issue IDs and
counts instead of demanding that pre-existing problems disappear. Use full
ledger detail only for affected claims or issues. Inspect the full diff and
`git diff --check`; use risk-based full checks for semantic-core or broad
changes. Report skipped checks and remaining conflicts.
Use project-specific advisory size or repeated-checkpoint triggers for the
live view and top-level index; exceeding one calls for review, not deletion.

Stop the affected migration step when authority, historical provenance, or a
pinned mathematical claim cannot be resolved under current authorization.
Leave the original material intact and report the smallest decision or audit
needed. Do not delete or rewrite numbered ledger events, immutable indexed
records, or protected proofs as a cleanup shortcut.
