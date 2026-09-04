# Route card

Write each durable route as a standalone Markdown file:

```markdown
# <Short title>

- **Date:** <YYYY-MM-DD>
- **Kind:** <attempt, finding, counterexample, decision, correction, or project kind>
- **Corrects:** <relative link, only for a correction>
- **Target:**
- **Hypotheses and types:**
- **Active conventions:**
- **Current dependency/evidence status:**
- **Nearest prior attempt and first failure:**
- **Route:**
- **Success criterion:**
- **Failure/no-go criterion:**
- **Cheapest decisive check:**
- **Outcome:**
- **Evidence label:**
- **First unresolved or failed implication:**
- **Strongest surviving statement:**
- **Artifacts and commands:**
- **Next unresolved question:**
- **Uniform route or obstruction, when evidence is bounded:**
- **What another bounded case would discriminate, if applicable:**
```

Unless project instructions specify another convention, store the record under
`research/records/` as `YYYY-MM-DD-normalized-title.md`. Normalize the title to
Unicode NFKD, remove non-ASCII combining marks, lowercase it, replace each run
outside `[a-z0-9]` with one hyphen, and trim leading or trailing hyphens. On a
collision, append `-2`, then `-3`, and so on. Use the checkpoint date; for
migrated legacy entries, add a `Date provenance:` field when the date was
inferred or unavailable.

Append one line to the history index, with a link relative to that index:

```markdown
- YYYY-MM-DD — [Short title](research/records/YYYY-MM-DD-normalized-title.md) — **evidence label** — One-sentence strongest result or blocker.
```

Do not copy a detailed proof, computation manifest, or literature record into
the route record. Link the authoritative artifact under `Artifacts and
commands` and state only what it establishes.
