# Suite review implementation validation

All 152 finding changes in the suite review plan are implemented. This record
separates code/package checks, bounded behavioral observations and remaining
acceptance coverage. [implementation.json](implementation.json) lists finding
IDs, decisions, measured loads and every changed file. The original plan remains
until its full behavioral acceptance checks are closed.

The coordinator reviewed raw derivations, executed code, returned artifacts and
filesystem effects separately from the three trial executors. This is a bounded
contract evaluation, not a research-performance benchmark or independent
certification of a universal mathematical theorem.

| Trial | Observed behavior | Raw evidence |
|---|---|---|
| Suite applicability routing | 158 frozen query decisions agree with all 174 supplied per-skill binary labels; 27 explicit-only positives are scored as task applicability. | [decisions](routing/raw-routing-decisions.json), [comparison](routing/routing-comparison.json), [catalog](routing/suite-descriptions-and-policies.json) |
| Read-only enumeration audit | A stride visits 16 of 64 inputs. The report flags omitted cases, missing run evidence and unavailable reproduction command; the project remains unchanged. | [response](safeguards/01-sampled-enumeration.md), [task, fixture and effects](safeguards/01-sampled-enumeration.json) |
| New exact computation | All 625 matrices in $\mathrm{GF}(5)^{2\times2}$ are visited. Elimination and determinant classification agree, with rank counts $1,144,480$. The completed v2 manifest and bounded ledger evidence validate. | [response](safeguards/02-gf5-rank.md), [code, manifest, results and receipts](safeguards/02-gf5-rank.json) |
| Correction and integration gates | The quotient claim at zero is ill-typed. The authorized audit only restricts the supplied cancellation argument; established integration is blocked. An explicitly conditional theorem application retains its unavailable source and exact premise. | [audit](safeguards/03-proof-audit.md), [blocked integration](safeguards/04-established-integration.md), [conditional integration](safeguards/05-conditional-integration.md), corresponding `.json` artifact bundles |
| Proofreading | A substantive false claim is reported and left unchanged in default review-only mode. | [response](safeguards/06-proofread.md), [fixture and effects](safeguards/06-proofread.json) |
| Source application | A synthetic rational objectwise theorem supplies no integral natural equivalence. Positive source evidence is recorded only for the separate rational claim. | [response](safeguards/07-source-application.md), [source, translation and journal](safeguards/07-source-application.json) |
| Referee fallback and reconciliation | Sequential self-review covers the manuscript without edits. A prior undefined-notation suspicion is dismissed against its earlier definition. Simulated child returns use distinct pass IDs. | [whole-paper report](referee/no-delegation.md), [prior-lead report](referee/prior-lead.md), [child-format report](referee/child-format.md), corresponding `.json` bundles |
| Later execution base and closeout | A program registered earlier accepts runs/reconciliation from a later checkpoint. Generated views and a two-route closeout preserve open continuations. | [trial notes](continuation/trial-notes.md), [ledger](continuation/case1-ledger.json), [closeout project](continuation/case2-closeout.json), [raw observations](continuation/raw.json) |
| Actual delegated packages | Two agents write only their assigned sum/square-sum records for $n=0,1,2,3$. Coordinator normal persistence and a single deferred packet preserve both universal continuations without theorem evidence or route closure. | [sum](native-program/sum.md), [squares](native-program/squares.md), [closeout](native-program/closeout.md), [commands/effects/packet](native-program/coordinator.json), [normal](native-program/normal-project.json), [deferred](native-program/deferred-project.json) |
| Inspect-only packet generation | Sequential role simulation emits one complete coordinator packet with zero response-phase tools/writes. Local dry-run and ingest validate actual files, the guarded index append and continuation lifecycle. | [task, packet, receipts and effects](continuation/raw.json), [resulting project](continuation/case3-deferred.json) |
| History and pin preservation | A plan-only 2,000-entry linked-index migration and a retrospective with a pinned dashboard preserve all project bytes. | [sharding plan](continuation/sharding-plan.md), [retrospective](continuation/retrospective.md), [snapshots/effects](continuation/raw.json) |
| Explicit live Codex program | Codex CLI 0.160.0 loads updated research-program, uses its direct route fallback without loading research-attempt, performs the exact four-case check and preserves both open routes without writes or subagents. | [task](live-codex/task.txt), [response](live-codex/extended-response.md), [native events](live-codex/extended-stdout.jsonl), [arithmetic](live-codex/arithmetic.json), [preservation](live-codex/preservation.json) |

Final read-only contract review covered all 11 skills and cross-cutting changes.
It found a default-inspector inventory overflow and a description-scalar/length
checker bypass; both were fixed with executable regressions before final checks.
See [checks.json](checks.json) for commands, exit codes and coverage limits.

The frozen routing decisions have SHA-256
`db39cb7cbb723d47a9d158447092048bc6f5a3ee3ab6a6c629a1ad0f2670e9dd`.
Descriptions and invocation policies did not change during that routing trial.
Some bodies/references changed concurrently; recorded initial hashes are retained
without silently replacing them with final hashes. Early continuation reads were
not hashed at read time; later exact captures are explicitly distinguished in
their provenance records. Initial safeguard reads also share evaluator context.

The full 135-case behavioral suite was not executed: many case definitions are
scenario specifications without complete mathematical/project fixtures. These
bounded trials exercise the changed safeguards but do not establish a pass for
every scenario. Automatic full-suite skill selection on Codex and Claude was not
tested. The live Codex task explicitly named research-program, and does not
establish that another explicit-only skill can load implicitly. The referee host
authorization and child-format cases are simulations; their empty issue arrays
leave populated-field calibration, duplicate merging and serious specialist
confirmation untested. Builds and external source authentication were outside
the synthetic fixtures. Windows/non-POSIX execution remains untested.

The first sandboxed live Codex launch could not initialize its app server because
of the outer read-only filesystem. An authorized run outside that outer sandbox
reached the skills but timed out after 45 seconds; a 180-second-bound rerun
completed in about 124 seconds. The inner Codex session remained read-only.
Original failure/timeout logs are retained. A runner import refreshed an ignored
repository bytecode file during the GF(5) trial; its prior bytes were unavailable,
and no tracked source changed. That effect is disclosed in safeguard provenance.

Artifact bundles use `raw-text-artifacts-v1`: each `files` entry contains the
original relative path, SHA-256 and complete UTF-8 text. Hashes are verified from
the decoded text. Original temporary paths in command logs identify where trials
ran; they are observations, not installation instructions. Standalone skill-source
captures, bytecode, the large generated sharding index/crosswalk and redundant
orchestration files are omitted. The sharding report and full before/after hashes
retain its tested scope; the export is a selected evidence set, not a complete
temporary-directory backup.

The standalone sum record is a display copy with one terminal blank line removed.
Its original bytes and SHA-256 remain in `native-program/normal-project.json`
and the coordinator packet; recorded evidence pins refer to those original bytes.
