# Adopt the ledger without rewriting a project

1. Inspect instructions, current claims and exact supporting artifacts. Resolve
   which files currently carry authority. Do not initialize a ledger merely
   because a project contains mathematics.
2. State a concrete mapping from existing claim IDs to exact ledger contracts.
   Preserve IDs where valid. Separate differently quantified/restricted claims;
   leave ambiguous historical assertions unresolved.
3. Under the user's authorized setup/edit scope, initialize `.mathbox/`. Record
   leaves before consumers. Pin only evidence actually checked against the claim;
   an old “proved” label without an accessible argument stays conjectural.
4. Import source checks and finite runs with their original scope and provenance.
   Do not manufacture independent review metadata or upgrade historical evidence.
5. Run brief `check` and `status` first, then compare the relevant exact claim
   contracts through full or JSON detail with the old claims file. Explain disagreements
   using evidence strength, never timestamps alone. If replacing the old view,
   preserve its substantive material and designate the new authority explicitly.
6. Keep the compact research log and existing immutable route records. The ledger
   stores claim/evidence transitions; the records store reusable mathematics.

Existing schema-version-1 journals and minimal `{"schema_version": 1}` configs
remain readable without rewriting any event. Generated projection labels changed
from mathematical-sounding conclusions to `proof-recorded`, `source-recorded`,
`computation-recorded`, and `counterexample-recorded`; update consumers and
generated dashboards that matched the old strings. Do not translate those
states back to `proved` without applying the project's own audit and approval
policy.

Routes recorded before obligation targeting remain valid: an absent `resolves`
field means the route resolves its owning `claim`. Goal handoffs may add active
review objects and a separately typed `route_context` projection without
rewriting events or changing the claim dependency graph.

Do not infer that an old launched process is still running. If lifecycle history
is useful, register a program and route run against the exact historical base,
then add an `unknown` observation unless liveness was actually observed. Import
parallel proposals through the current ledger's single writer. Preserve each
run's base/result revision and record explicit conflicts; never infer precedence
from import order or merge two numbered event directories.

Migration is optional. A project can retain Markdown tables and use the same
evidence distinctions manually. There is deliberately no automatic prose parser
that turns confident historical summaries into proof events.

An installed standalone skill should not import code from a sibling skill.
Other workflows can invoke this skill when available or apply its evidence
principles to the existing project format; they must not copy its source into
every research repository.
