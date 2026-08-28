# Research Toolbox

Reusable agent skills for rigorous AI-assisted mathematical research, designed
to work with both OpenAI Codex and Claude Code.

Each top-level directory is an independently installable
[Agent Skill](https://agentskills.io/). The suite separates research,
verification, computation, literature work, manuscript integration, and
proofreading so that each workflow has a clear evidence standard and stopping
condition.

## Included skills

| Skill | Purpose | Invocation |
|---|---|---|
| [`research-init`](research-init/) | Initialize, retrofit, or refresh a mathematical research repository | explicit only |
| [`research-attempt`](research-attempt/) | Pursue one bounded proof, counterexample, reduction, source, or computation route | explicit only |
| [`proof-audit`](proof-audit/) | Adversarially audit an existing claim or proof and isolate the exact gap | explicit or automatic |
| [`literature-check`](literature-check/) | Verify an external result, citation, notation translation, or bounded novelty claim | explicit or automatic |
| [`computation-audit`](computation-audit/) | Design, run, or audit a claim-supporting mathematical computation | explicit or automatic |
| [`manuscript-integrate`](manuscript-integrate/) | Integrate an already validated result into an authoritative LaTeX manuscript | explicit only |
| [`proofread-math`](proofread-math/) | Conservatively proofread mathematical prose and LaTeX | explicit or automatic |
| [`research-retrospective`](research-retrospective/) | Reconcile project state and select the next bounded research routes | explicit only |

“Automatic” means that the host may select the skill when a request matches its
description. Every skill can still be invoked explicitly: use `$skill-name` in
Codex or `/skill-name` in Claude Code.

## Choosing a skill

| The task is primarily… | Use |
|---|---|
| setting up the research repository or revising its agent architecture | `research-init` |
| developing new mathematics along one controlled route | `research-attempt` |
| deciding whether an existing argument is correct as written | `proof-audit` |
| checking exactly what an external source proves | `literature-check` |
| obtaining or assessing finite computational evidence | `computation-audit` |
| transferring a validated result into the live paper | `manuscript-integrate` |
| correcting grammar, typography, LaTeX, references, or forced local typos | `proofread-math` |
| reviewing the project portfolio and deciding what to try next | `research-retrospective` |

Some important boundaries:

- A bounded computation is evidence only for its stated range, not a universal
  proof.
- Proofreading does not authorize changing an argument. Use `proof-audit` to
  diagnose an existing proof or `research-attempt` to develop a new one.
- `manuscript-integrate` transfers mathematics that has already been validated;
  it does not make conjectural work publication-ready.
- A failed literature search supports only a bounded search report, not a claim
  of global novelty.

## Installation

Clone the repository somewhere stable, then link the skills you want into the
personal skill directories used by Codex and Claude Code:

```bash
git clone https://github.com/nidrissi/research-toolbox.git \
  "$HOME/.local/share/research-toolbox"

toolbox_dir="$HOME/.local/share/research-toolbox"
mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"

for skill_file in "$toolbox_dir"/*/SKILL.md; do
  skill_dir=${skill_file%/SKILL.md}
  skill_name=${skill_dir##*/}
  ln -s "$skill_dir" "$HOME/.agents/skills/$skill_name"
  ln -s "$skill_dir" "$HOME/.claude/skills/$skill_name"
done
```

The commands deliberately do not overwrite an existing skill with the same
name. To install only one skill, run the corresponding two `ln -s` commands for
that directory. To update linked skills later, pull the repository:

```bash
git -C "$HOME/.local/share/research-toolbox" pull --ff-only
```

Codex can also install skills from a GitHub repository through its built-in
`$skill-installer` workflow.

## Repository structure

```text
research-toolbox/
├── AGENTS.md                 # shared contributor and agent instructions
├── CLAUDE.md                 # imports AGENTS.md for Claude Code
├── README.md
└── <skill-name>/
    ├── SKILL.md              # canonical workflow and trigger description
    ├── agents/openai.yaml    # Codex/OpenAI UI and invocation metadata
    ├── evals/
    │   ├── evals.json        # behavioral examples and assertions
    │   └── trigger-evals.json # positive and negative routing probes
    ├── references/           # supporting material loaded when needed
    ├── assets/               # optional templates or data files
    └── scripts/              # optional deterministic helpers
```

Not every skill needs every optional directory. References inside a skill are
relative to that skill directory, so packages remain portable when installed by
copying or symlinking.

The common `SKILL.md` format follows the open Agent Skills standard. Codex uses
`agents/openai.yaml` for host-specific presentation and invocation policy;
Claude Code ignores that file and uses compatible fields in `SKILL.md`.

## Development

Keep each skill focused on one job. Update its instructions, supporting files,
behavioral evals, and routing evals together when its contract changes. If a
skill is added, renamed, or removed, update the tables in this README in the
same change.

Repository-wide contribution and validation instructions are in
[`AGENTS.md`](AGENTS.md).

Useful upstream references:

- [Build skills for ChatGPT and Codex](https://developers.openai.com/codex/skills)
- [Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Agent Skills specification](https://agentskills.io/specification)
