# Research log

This is the compact history entry point. Put route details in immutable
standalone records under `{{RESEARCH_RECORDS}}`. A small project may append one
route link per material checkpoint here. For sustained programs, keep this
file to program/phase closeouts and link each closeout to a separate route
index. An "opened" entry may link the active program's route index before its
first closeout; the live dashboard names the active route. Do not duplicate
every route here. Do not rewrite indexed history; append a linked correction
instead.

## Program/phase entry format

```markdown
- YYYY-MM-DD — [Program closeout]({{RESEARCH_RECORDS}}/program-closeout.md) — **goal status** — Strongest result or blocker; [route index]({{RESEARCH_RECORDS}}/program-routes.md).
```

A program route index contains one linked outcome line per durable route. For
a small flat history, use that same route-line format directly here. Adjust
relative links when the route index lives in a subdirectory:

```markdown
- YYYY-MM-DD — [Route title]({{RESEARCH_RECORDS}}/YYYY-MM-DD-normalized-title.md) — **evidence label** — One-sentence strongest result or blocker.
```
