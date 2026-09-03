# Mathbox

`mathbox` is a plugin for Codex and Claude Code containing eight reusable Agent
Skills for rigorous AI-assisted mathematical research.

The toolbox separates research, verification, computation, literature work,
manuscript integration, and proofreading so that each workflow has a clear
evidence standard and stopping condition. The canonical distribution is the
`mathbox` plugin; each bundled skill remains independently installable for
hosts or environments that need a standalone Agent Skill.

These are research workflows and safeguards, not a computer algebra system or
a replacement for mathematical review.

## Quick start

### Claude Code: install the plugin

From a Claude Code session, add this repository as a marketplace and install
the bundle:

```text
/plugin marketplace add nidrissi/mathbox
/plugin install mathbox@mathbox
```

Start a new session, run `/skills`, and try:

```text
/mathbox:proof-audit Audit the proof of Lemma 3.2 and isolate the first unproved implication.
```

Claude namespaces plugin skills with the plugin name. The repository root is
also the plugin root, so a source checkout can be tested without installation:

```bash
git clone https://github.com/nidrissi/mathbox.git
claude --plugin-dir ./mathbox
```

### Codex: install the plugin

Install `mathbox` from Codex's plugin directory. The repository is a native
Codex plugin through `.codex-plugin/plugin.json`; the Claude manifest also
provides the explicit skill inventory used by OpenAI's skills-only conversion
path. Both hosts therefore load the same canonical directories under `skills/`
without duplicated packages.

Start a new session, run `/skills`, and try the namespaced plugin skill:

```text
$mathbox:proof-audit Audit the proof of Lemma 3.2 and isolate the first unproved implication.
```

If the plugin directory listing is not yet available, Codex's built-in skill
installer can install the component skills directly from the repository:

```text
$skill-installer Install every skill under skills/ from https://github.com/nidrissi/mathbox.
```

That fallback is a standalone skill installation, not a `mathbox` plugin
installation, so its explicit invocations use bare names such as
`$proof-audit`.

### Standalone or single-skill installation

Requirements are Git, a host with Agent Skills support, and Python 3 only for
the optional bundled helper scripts. This compatibility path installs bare
skills rather than the `mathbox` plugin. The helpers use the standard library.

Clone the repository somewhere stable:

```bash
git clone https://github.com/nidrissi/mathbox.git \
  "$HOME/.local/share/mathbox"
toolbox_dir="$HOME/.local/share/mathbox"
skills_dir="$toolbox_dir/skills"
```

To install only `proof-audit`, link it into the host you use:

```bash
# Codex
mkdir -p "$HOME/.agents/skills"
ln -s "$skills_dir/proof-audit" "$HOME/.agents/skills/proof-audit"

# Claude Code
mkdir -p "$HOME/.claude/skills"
ln -s "$skills_dir/proof-audit" "$HOME/.claude/skills/proof-audit"
```

To link all eight skills for both hosts:

```bash
mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"

for skill_file in "$skills_dir"/*/SKILL.md; do
  skill_dir=${skill_file%/SKILL.md}
  skill_name=${skill_dir##*/}
  ln -s "$skill_dir" "$HOME/.agents/skills/$skill_name"
  ln -s "$skill_dir" "$HOME/.claude/skills/$skill_name"
done
```

These commands do not overwrite an existing skill with the same name. On
native Windows, use WSL or copy the selected directories instead of creating
symlinks. Standalone invocations use `$proof-audit` in Codex and `/proof-audit`
in Claude Code; plugin-installed invocations use `$mathbox:proof-audit` in
Codex and `/mathbox:proof-audit` in Claude Code.

The `mathbox` plugin skills use the mathematical software already available in
your project. Installing the plugin or its standalone component skills does not
install SageMath, LaTeX, or other project dependencies.

## Included plugin skills

| Plugin skill | Purpose | Selection |
|---|---|---|
| [`mathbox:research-init`](skills/research-init/) | Initialize, retrofit, or refresh a mathematical research repository | explicit request |
| [`mathbox:research-attempt`](skills/research-attempt/) | Pursue one bounded proof, counterexample, reduction, source, or computation route | explicit request |
| [`mathbox:proof-audit`](skills/proof-audit/) | Adversarially audit an existing claim or proof and isolate the exact gap | automatic |
| [`mathbox:literature-check`](skills/literature-check/) | Verify or locally cache an external result, citation, notation translation, or bounded novelty claim | automatic |
| [`mathbox:computation-audit`](skills/computation-audit/) | Design, run, or audit a claim-supporting mathematical computation | automatic |
| [`mathbox:manuscript-integrate`](skills/manuscript-integrate/) | Integrate an already validated result into an authoritative LaTeX manuscript | explicit request |
| [`mathbox:proofread-math`](skills/proofread-math/) | Conservatively proofread mathematical prose and LaTeX | automatic |
| [`mathbox:research-retrospective`](skills/research-retrospective/) | Reconcile project state and select the next bounded research routes | explicit request |

“Explicit request” is a portable routing boundary expressed in the skill's
description and body, not a host-specific frontmatter switch. “Automatic” means
that a matching task may select the skill without naming it. Every plugin skill
can still be invoked by name: use `$mathbox:skill-name` in Codex or
`/mathbox:skill-name` in Claude Code. Bare `$skill-name` and `/skill-name`
forms refer only to standalone installations.

## Choosing a skill

| The task is primarily… | Use |
|---|---|
| setting up the research repository or revising its agent architecture | `mathbox:research-init` |
| developing new mathematics along one controlled route | `mathbox:research-attempt` |
| deciding whether an existing argument is correct as written | `mathbox:proof-audit` |
| checking exactly what an external source proves | `mathbox:literature-check` |
| obtaining or assessing finite computational evidence | `mathbox:computation-audit` |
| transferring a validated result into the live paper | `mathbox:manuscript-integrate` |
| correcting grammar, typography, LaTeX, references, or forced local typos | `mathbox:proofread-math` |
| reviewing the project portfolio and deciding what to try next | `mathbox:research-retrospective` |

Important boundaries:

- A bounded computation is evidence only for its stated range, not a universal
  proof.
- Proofreading does not authorize changing an argument. Use the
  `mathbox:proof-audit` plugin skill to diagnose an existing proof or
  `mathbox:research-attempt` to develop a new one.
- The `mathbox:manuscript-integrate` plugin skill transfers mathematics that
  has already been validated; it does not make conjectural work
  publication-ready.
- A failed literature search supports only a bounded search report, not a claim
  of global novelty.

## Local literature cache

When a research repository authorizes retaining source material,
`literature-check` can reuse PDFs and extracted text from the project's ignored
`.research-cache/literature/` directory. Records are content-addressed by the
PDF's SHA-256 and searchable without a database; tracked literature ledgers keep
only bibliographic metadata, hashes, and extraction status. The bundled helper
uses `pdftotext` opportunistically when it is installed, and never fetches
sources or handles credentials itself.

Keep a tracked `/.research-cache/` rule in the project's own `.gitignore`. The
helper also writes an internal ignore rule as a fallback, refuses to write any
artifact Git would track — including one already in the index — and reports
whether coverage comes from a project rule or only from its own, so a missing
project rule stays visible rather than silently satisfied. Lookups
(`find`, `show`, `verify`) never create or modify the cache.

Other research-facing skills route any new question about what an external
mathematical source proves through `literature-check`; this ensures they share
the same exact-version, cache-first, and evidence rules. Proofreading checks
citation syntax only, and repository initialization inventories literature
policy without performing substantive source verification.

## Updating and pinning

The `mathbox` plugin can be updated through the host's plugin manager. For a
manual standalone installation, pull the checkout:

```bash
git -C "$HOME/.local/share/mathbox" pull --ff-only
```

For a reproducible setup, check out a release tag or commit before linking the
skills.

## Repository structure

```text
mathbox/
├── .codex-plugin/
│   └── plugin.json                       # Codex package and presentation metadata
├── .claude-plugin/
│   ├── marketplace.json                  # Claude marketplace catalog
│   └── plugin.json                       # root plugin metadata and skill list
├── assets/
│   └── mathbox.svg                       # Codex square icon and logo
├── AGENTS.md                             # shared contributor instructions
├── CLAUDE.md                             # imports AGENTS.md for Claude Code
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md                       # canonical workflow contract
        ├── agents/openai.yaml             # OpenAI presentation metadata
        ├── evals/                         # behavior and routing probes
        ├── references/                    # supporting material
        ├── assets/                        # optional templates or data
        └── scripts/                       # optional deterministic helpers
```

There is only one copy of each skill. The Codex manifest points to `skills/`,
the Claude manifest lists each directory beneath it explicitly, and every skill
remains independently installable. Relative resource links therefore continue
to work when a skill is copied, linked, loaded by Claude, or converted by
OpenAI.

Canonical skill folders and `SKILL.md` names are intentionally bare (for
example, `proof-audit`) so they remain portable Agent Skills. Installing the
bundle as a plugin exposes them under the `mathbox:` namespace.

The `SKILL.md` frontmatter uses only the portable required Agent Skills fields
`name` and `description`. OpenAI uses `agents/openai.yaml` for host-specific
presentation and invocation policy; other hosts ignore it.

## Contributing

Keep each skill focused on one job. Update its instructions, supporting files,
behavioral evals, and routing evals together when its contract changes. If a
skill is added, renamed, or removed, update the tables in this README in the
same change.

Repository-wide contribution and validation instructions are in
[`AGENTS.md`](AGENTS.md).

Useful upstream references:

- [Build plugins for ChatGPT and Codex](https://learn.chatgpt.com/docs/build-plugins)
- [Submit a Claude Code plugin to OpenAI](https://developers.openai.com/plugins/guides/submit-claude-plugin)
- [Create plugins for Claude Code](https://code.claude.com/docs/en/plugins)
- [Agent Skills specification](https://agentskills.io/specification)

## License

[MIT](LICENSE) © 2026 Najib Idrissi-Kaïtouni.
