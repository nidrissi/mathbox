# Route selection and continuation

Use a small live portfolio, not a fixed ceremony before every calculation.

| Route family | Useful discriminator | What failure means |
|---|---|---|
| Structural proof | Construct the comparison or homotopy at the level claimed | Failure of that comparison, not necessarily the conjecture |
| Counterexample | Compute an invariant capable of separating the claimed equivalence classes | Negative search only within its tested class |
| Literature transfer | Translate an exact theorem including functoriality and hypotheses | Missing transfer step remains an internal proof obligation |
| Obstruction/reduction | Isolate a necessary obstruction or sufficient uniform lemma | A conditional reduction, unless its remaining leaf is established |
| Exact experiment | Distinguish two named structural predictions | Bounded evidence about the implemented object |

Prefer a route whose outcome changes the next decision. Do not count a renamed
spectral-sequence calculation as independent of another route depending on the
same collapse. An exotic technique is not a route until its first executable
mathematical step is stated.

The claim dependency graph records jointly required mathematical obligations.
Routes are alternative mechanisms. If a route is organized under a parent claim
but attacks a narrower registered obligation, record that obligation as the
route's resolved target; keep prerequisites needed only to execute that route as
route context rather than adding false theorem dependencies.

At checkpoints use the continuation field list in [handoff.md](handoff.md);
record only changed decisions rather than another full research narrative.

For parallel or delayed results, retain each route's base checkpoint, artifact
hashes, owner and write scope. Establish ancestry from those records, not arrival
order. Reconcile path collisions and incompatible claims explicitly; one result
does not silently overwrite or supersede another. Append shared state only after
the coordinator checks the returned artifacts.

Before launching, inspect live, stale and unreconciled runs of the same route.
Recheck relevant stale artifacts and reconcile returns before relying on them;
compare work scopes to avoid duplication. Distinct runs can share a base with
noncolliding write scopes while existing runs remain live.

For external jobs record execution ID, last observation and queued, running,
completed, failed, timed out or abandoned state. Map queued to ledger `waiting`,
observed running to `active`, timeout to a `blocked`/`inconclusive` run result
with explicit resource reason; completion needs its actual attempt outcome,
not assumed `succeeded`. Preserve `last_observed` metadata separately. A stale observation
is unknown state, not evidence that the job is still running.

If a goal depends on several lemmas, use the dependency graph to identify which
one unlocks the largest useful part. Keep epistemic labels separate from route
priority: an attractive route can remain conjectural.

If research-attempt cannot be invoked under host rules, execute the bounded
route directly. Use evidence labels proved, externally proved, computationally
verified in a stated range, conditional, heuristic, conjectural, refuted and
superseded; separate review provenance and freshness. A minimal route record
has target and IDs, base checkpoint/inputs, hypotheses/conventions, mechanism,
criteria and discriminator, derivation/artifacts/commands, attempt outcome,
evidence label, route disposition/scope, continuations and next action.
A resource limit or inconclusive attempt cannot alone close its route.

Do not require a new permission at each cycle when the user has already asked
for sustained work. Reassess permission only for a materially different external
action or resource commitment. Do not turn a checkpoint into a request to
continue work that is already authorized.
