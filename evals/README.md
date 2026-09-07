# Evaluating Mathbox

There are three different validation surfaces:

1. `python3 scripts/check.py`: deterministic packaging, syntax and executable
   state/experiment/cache regressions. These verify software contracts, not
   mathematical performance.
2. `skills/*/evals/trigger-evals.json`: routing probes. A correct task answer does
   not establish that the right skill was selected.
3. `skills/*/evals/evals.json` and the raw fixtures below: behavioral mathematical
   tasks. Evaluate actual derivations, commands, persisted artifacts and scope.
   Do not score these by searching for reassuring phrases.

## Independent task protocol

Start a fresh agent/session with the named skill, the task and raw fixture only.
Keep expected answers, rubric and the author's diagnosis out of its context.
Use an isolated temporary project; do not let generated artifacts from one case
contaminate another. Run only authorized local operations. Give unavailable
source/software conditions honestly, not as invented test outcomes.

After execution, a separate reviewer checks the mathematical derivation and
observable effects against `cases.json`. Record skill revision, task, tool
availability, actual artifacts, reviewer and verdict. A self-review is not an
independent audit. Missing tools are a capability limitation, not a mathematical
failure. Success means satisfying the task contract, not following a fixed number
of tool calls or reproducing a preferred proof.

## Raw fixtures

| File | User task |
|---|---|
| `fixtures/modular-rank.md` | Audit the implication and determine the strongest justified conclusion. |
| `fixtures/equivariant-map.md` | Audit the equivariant comparison under the exact assumptions. |
| `fixtures/bounded-tower.md` | Pursue a decisive proof or counterexample route for the full target. |
| `fixtures/prime-binomial.md` | Execute three distinct approaches and settle the quantified claim. |

These cases test specific failure mechanisms. They are not a validated measure
of frontier research success. Keep held-out real project tasks before making
comparative performance claims. See `docs/validation-v3.md` for the actual
forward-testing scope of this redesign.
