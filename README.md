# Math Research Skills

A coherent, user-wide skill suite for AI-assisted mathematical research with
OpenAI Codex and Claude Code.

The suite uses one canonical installed copy and exposes it to both tools with
symlinks:

```text
~/.local/share/math-research-skills/current/skills/<name>/
        ├── ~/.agents/skills/<name>          # Codex
        └── ~/.claude/skills/<name>          # Claude Code
```

This prevents the two installations—and different repositories—from drifting.
Both tools can follow symlinked skill directories. Repository-local skills are
reserved for genuinely repository-specific procedures, not copies of these
common workflows.

## Included skills

| Skill | Purpose | Default invocation |
|---|---|---|
| `research-init` | Configure or refresh a mathematical research repository | explicit only |
| `research-attempt` | Run one bounded proof/counterexample/reduction route | explicit only |
| `proof-audit` | Adversarially audit a claim or proof | explicit or automatic |
| `literature-check` | Verify an external theorem, citation, or bounded novelty claim | explicit or automatic |
| `computation-audit` | Design or audit claim-supporting mathematical computation | explicit or automatic |
| `manuscript-integrate` | Move validated mathematics into a live manuscript | explicit only |
| `proofread-math` | Conservatively proofread mathematical LaTeX | explicit or automatic |
| `research-retrospective` | Reconcile project state and select the next bounded routes | explicit only |

## Routing cheatsheet

| The task is primarily… | Invoke |
|---|---|
| setting up or repairing the repository’s research operating system | `research-init` |
| discovering a new proof, counterexample, reduction, or route | `research-attempt` |
| deciding whether an existing proof is correct as written | `proof-audit` |
| checking exactly what an external source proves | `literature-check` |
| running a nontrivial claim-supporting calculation or search | `research-compute` |
| transferring an already validated result into the live paper | `manuscript-integrate` |
| reorganizing or clarifying already established mathematics | `revise-math` |
| grammar, typography, LaTeX, references, and forced local typos | `proofread-math` |

### Boundary questions

- **Does the argument itself change?** Use `research-attempt`, not proofreading or revision.
- **Is the task to judge rather than create?** Use `proof-audit`.
- **Does the conclusion depend on what a paper actually says?** Use `literature-check`.
- **Does a finite run support the claim?** Use `research-compute` and state the tested range.
- **Is the result still unresolved?** Do not use `manuscript-integrate` to make it look settled.
- **Is the mathematics complete but presentation poor?** Use `revise-math`, then `proofread-math`.

## Workflow examples and routing tests

### Example: attack a conjectural sign identity

1. Invoke `research-attempt` with the exact identity and convention version.
2. The route card identifies source/target, degree, action order, and smallest graph.
3. If a named theorem supplies a comparison map, use `literature-check`.
4. If a finite sweep is decisive evidence, use `research-compute` with exact arithmetic and a manifest.
5. Ask a fresh `proof-audit` pass to reverse operation orders and test sign-reversing automorphisms.
6. Only after the verdict is proved/externally proved should `manuscript-integrate` update the paper.

### Example: coauthor asks for “proofreading” but the proof changes

Request: “Shorten this proof by replacing the spectral sequence with a direct argument.”

Routing:

- not `proofread-math`;
- invoke `research-attempt` to develop and validate the new proof;
- then `revise-math` to fit it into the exposition;
- finally `proofread-math` for local QA.

### Example: source may not apply in characteristic 3

Use `literature-check`, not a general web summary. Record the exact version, coefficient hypotheses, notation translation, and every implication between the source theorem and the project claim. If the characteristic-3 step is absent, the result is conditional/unverified rather than “probably standard.”

### Example: computation finds no counterexample

`research-compute` reports the encoded model, exhaustive range, command, environment, assertions, and non-claims. “No counterexample in arity at most 8” is not a proof of the universal claim. The route may still be useful for selecting a proof strategy.

### Example: theorem proof already established, section is unreadable

Use `revise-math` for structural rewrite. It may move definitions, expose existing transitions, and remove redundancy, but it must isolate any step that would require new mathematics. Then invoke `proofread-math`.

### Negative trigger probes

The following should not invoke the indicated skill implicitly:

- `proofread-math`: “write a proof from scratch”; “replace this proof”; “assess novelty.”
- `proof-audit`: “fix the grammar”; “develop a new route after the proof fails.”
- `literature-check`: “explain this standard definition” when no source claim is at issue.
- `research-compute`: trivial arithmetic or a routine unchanged test rerun.
- `manuscript-integrate`: unresolved scratch notes or a conjectural calculation.
- `research-init`: ordinary work in an already configured repository.
