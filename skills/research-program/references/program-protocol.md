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

Record only these live decisions at a checkpoint:

1. Checkpoint identifier, base Git revision or ledger event, exact goal and
   remaining implication.
2. New evidence and what it rules in/out.
3. Active and deferred routes, with tried, untried, obstructed and deferred
   continuations; give evidence for exclusions and conditions for resumption.
4. First failed or unresolved step of closed routes, the scope of closure, the
   reason no known continuation remains executable, and the input needed to
   reopen them.
5. Next action, expected discriminating outcome, and resource bound.

For parallel or delayed results, retain each route's base checkpoint, artifact
hashes, owner and write scope. Establish ancestry from those records, not arrival
order. Reconcile path collisions and incompatible claims explicitly; one result
does not silently overwrite or supersede another. Append shared state only after
the coordinator checks the returned artifacts.

For external jobs, record the execution identifier, last observation and one of
queued, running, completed, failed, timed out or abandoned. A stale observation
is unknown state, not evidence that the job is still running.

If a goal depends on several lemmas, use the dependency graph to identify which
one unlocks the largest useful part. Keep epistemic labels separate from route
priority: an attractive route can remain conjectural.

Do not require a new permission at each cycle when the user has already asked
for sustained work. Reassess permission only for a materially different external
action or resource commitment. Do not turn a checkpoint into a request to
continue work that is already authorized.
