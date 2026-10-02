# Route card

Write each durable route as a standalone Markdown file:

```markdown
# <Short title>

- **Date:** <YYYY-MM-DD>
- **Kind:** <attempt, finding, counterexample, decision, correction, or project kind>
- **Corrects:** <relative link, only for a correction>
- **Program/route/claim IDs:** <existing IDs, or not registered>
- **Base checkpoint:** <Git revision or ledger event; actual inputs>
- **Target:**
- **Hypotheses and types:**
- **Active conventions:**
- **Current dependency/evidence status:**
- **Nearest prior attempt and first failure:**
- **Route:**
- **Mechanism and distinctness from prior routes:**
- **Changed input, if reopening a failed route:**
- **Success criterion:**
- **Failure/no-go criterion:**
- **Cheapest decisive check:**
- **Attempt outcome:**
- **Route disposition and scope:** <open (continuations may be deferred) or closed as succeeded/failed/blocked/inconclusive; scope and reason>
- **Continuations:** <tried, untried, obstructed with evidence, or deferred with resumption condition>
- **Evidence label:**
- **Review and freshness status:**
- **First unresolved or failed implication:**
- **Strongest surviving statement:**
- **Artifacts and commands:**
- **Next unresolved question:**
- **Uniform route or obstruction, when evidence is bounded:**
- **What another bounded case would discriminate, if applicable:**
```

Route dispositions: `succeeded` meets its criterion; `failed` has an established
obstruction; terminal `blocked` has a scoped reason no continuation remains
executable; terminal `inconclusive` exhausts known scoped continuations without
settling the mechanism. Resource/access waits keep the route open with a deferred
continuation. Attempt outcome is separate from all these dispositions.

Unless project instructions specify another convention, store the record under
`research/records/` as `YYYY-MM-DD-normalized-title.md`. Normalize the title to
Unicode NFKD, remove non-ASCII combining marks, lowercase it, replace each run
outside `[a-z0-9]` with one hyphen, and trim leading or trailing hyphens. On a
collision, append `-2`, then `-3`, and so on. Use the checkpoint date; for
migrated legacy entries, add a `Date provenance:` field when the date was
inferred or unavailable.

Append one line to the designated route index, with a link relative to that
index. A sustained program may use a program/phase route index linked from the
short top-level history entry point; do not duplicate the route line there.
The path below illustrates a root-level `RESEARCH_LOG.md`; adjust its relative
path for a nested index:

```markdown
- YYYY-MM-DD — [Short title](research/records/YYYY-MM-DD-normalized-title.md) — **evidence label** — One-sentence strongest result or blocker.
```

Do not copy a detailed proof, computation manifest, or literature record into
the route record. Link the authoritative artifact under `Artifacts and
commands` and state only what it establishes.
