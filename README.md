# Mathbox

`mathbox` is a plugin for Claude Code and Codex with eleven Agent Skills for
sustained, auditable mathematical research, plus optional standard-library
Python tools.

Each skill handles one job: research, verification, computation, literature
work, manuscript refereeing and integration, or proofreading. Each job has
its own evidence standard and stopping condition. The canonical distribution
is the plugin, but every skill can also be installed on its own as a standalone
Agent Skill.

These are research workflows and safeguards, not a computer algebra system or
a replacement for mathematical review.

[Changelog](docs/CHANGELOG.md) · [v3 design](docs/design-v3.md) ·
[v3 validation](docs/validation-v3.md) ·
[Referee validation](docs/referee-validation.md) ·
[Evaluation protocol](evals/README.md)

[Support](https://github.com/nidrissi/mathbox/issues) ·
[Privacy policy](PRIVACY.md) · [Terms of use (MIT License)](LICENSE)

## Installation

### Claude Code

Add this repository as a marketplace and install the plugin:

```text
/plugin marketplace add nidrissi/mathbox
/plugin install mathbox@mathbox
```

Start a new session, run `/skills`, and try:

```text
/mathbox:proof-audit Audit the proof of Lemma 3.2 and isolate the first unproved implication.
```

The repository root is also the plugin root, so you can test a checkout
without installing it:

```bash
git clone https://github.com/nidrissi/mathbox.git
claude --plugin-dir ./mathbox
```

### Codex

Add this repository as a marketplace and install the plugin with a current
Codex CLI:

```bash
codex plugin marketplace add nidrissi/mathbox
codex plugin add mathbox@mathbox
```

This works before Mathbox is published in the public plugin directory. The
catalog at [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json)
points to the repository root, which contains the Codex manifest and all eleven
skills. No separate plugin copy is needed.

For a local checkout, run `codex plugin marketplace add ./mathbox` from its
parent directory instead. To install through the ChatGPT desktop app, restart
the app after adding the marketplace, open the Plugins Directory, select
**Mathbox** as the source, and install **Mathbox**.

Start a new session and try:

```text
$mathbox:proof-audit Audit the proof of Lemma 3.2 and isolate the first unproved implication.
```

When installing standalone skills, the built-in skill
installer can install the skills directly:

```text
$skill-installer Install every skill under skills/ from https://github.com/nidrissi/mathbox.
```

This installs standalone skills rather than the plugin, so you invoke them by
bare names such as `$proof-audit`.

### Standalone skills

You need Git and a host that supports Agent Skills. Python 3.10+ is needed
only for the optional helper scripts. Clone the repository somewhere stable:

```bash
git clone https://github.com/nidrissi/mathbox.git "$HOME/.local/share/mathbox"
skills_dir="$HOME/.local/share/mathbox/skills"
```

Then link one skill, or all of them, into each host you use:

```bash
mkdir -p "$HOME/.agents/skills" "$HOME/.claude/skills"

# One skill
ln -s "$skills_dir/proof-audit" "$HOME/.agents/skills/proof-audit"   # Codex
ln -s "$skills_dir/proof-audit" "$HOME/.claude/skills/proof-audit"   # Claude Code

# All skills, both hosts
for skill_file in "$skills_dir"/*/SKILL.md; do
  skill_dir=${skill_file%/SKILL.md}
  skill_name=${skill_dir##*/}
  ln -s "$skill_dir" "$HOME/.agents/skills/$skill_name"
  ln -s "$skill_dir" "$HOME/.claude/skills/$skill_name"
done
```

These commands never overwrite an existing skill with the same name. On
native Windows, use WSL or copy the directories instead of linking them.

### Updating and pinning

Update the plugin through the host's plugin manager. To refresh the Codex Git
marketplace, run `codex plugin marketplace upgrade mathbox`, then install the
updated entry with `codex plugin add mathbox@mathbox`. You can inspect the
marketplace with `codex plugin marketplace list`. To pin its Git source, use
`codex plugin marketplace add nidrissi/mathbox --ref <ref>` with a branch,
release tag, or commit containing the Codex catalog; older releases without
`.agents/plugins/marketplace.json` do not expose this catalog.

To update a standalone checkout, run
`git -C "$HOME/.local/share/mathbox" pull --ff-only`. For a
reproducible setup, check out a [release tag](docs/CHANGELOG.md) before
linking.

The skills use the mathematical software your project already has. Installing
Mathbox does not install SageMath, LaTeX, or other project dependencies.

## Skills

| Skill | Use it to… | Invocation |
|---|---|---|
| [`research-program`](skills/research-program/) | pursue a substantial goal across distinct routes, continue after failed attempts, or close out a program or phase | automatic |
| [`research-attempt`](skills/research-attempt/) | pursue one bounded proof, counterexample, reduction, source, or computation route | explicit |
| [`research-state`](skills/research-state/) | track claim revisions, evidence freshness, dependency impact and ledger handoffs | automatic |
| [`research-init`](skills/research-init/) | set up or migrate a research repository's agent architecture | explicit |
| [`research-retrospective`](skills/research-retrospective/) | review a project read-only and choose the next bounded routes | explicit |
| [`referee`](skills/referee/) | assess an entire manuscript across five review dimensions and reconcile a calibrated referee report | automatic |
| [`proof-audit`](skills/proof-audit/) | decide whether an existing claim or proof is correct and isolate the exact gap | automatic |
| [`literature-check`](skills/literature-check/) | verify what an external source proves, check a bounded novelty claim, or cache a source locally | automatic |
| [`computation-audit`](skills/computation-audit/) | design, run, or audit a computation that supports a claim | automatic |
| [`manuscript-integrate`](skills/manuscript-integrate/) | transfer an already validated result into the authoritative LaTeX manuscript | explicit |
| [`proofread-math`](skills/proofread-math/) | fix grammar, typography, LaTeX, references, or local typos whose correction is forced | automatic |

A host may select an **automatic** skill for a matching task. Codex enforces
**explicit** skills through `allow_implicit_invocation: false` in
`agents/openai.yaml`; request `$mathbox:<skill>` (or its standalone name) to
load one. Claude Code uses the description/body's explicit-request boundary.
A plain task matching an explicit-only skill may therefore have no directly
loaded skill in Codex. Other workflows can use their documented direct fallback
when host invocation rules do not permit loading a specialist.

Use `/mathbox:<skill>` in Claude Code or `$mathbox:<skill>` in Codex; standalone
names omit `mathbox:`. Invocation policy does not override host tool or delegation
authorization. See the [routing evaluation protocol](evals/README.md#routing-protocol).

### Safeguards

- [Computation](skills/computation-audit/SKILL.md) supports only its audited assertion and range.
- [Proof audits](skills/proof-audit/SKILL.md) inspect raw evidence and preserve unresolved gaps.
- [Proofreading](skills/proofread-math/SKILL.md) changes only conservative local errors.
- [Refereeing](skills/referee/SKILL.md) reconciles whole-paper findings; reviewer agreement is not proof.
- [Integration](skills/manuscript-integrate/SKILL.md) requires current support for established claims.
- [Literature checks](skills/literature-check/SKILL.md) verify exact implications and bound novelty reports.

### Example prompts

Each line below is a separate Codex prompt. In Claude Code, write
`/mathbox:` instead of `$mathbox:`.

```text
$mathbox:research-program Pursue this conjecture through distinct proof and counterexample routes. Preserve the original goal and continue after failed attempts.
$mathbox:research-state Check which claims depend on Lemma K, which evidence is stale, and what to attack next.
$mathbox:research-init Plan a migration of this repository's AGENTS.md and live status; preserve history and inspect ledger pins before editing.
$mathbox:referee Referee this entire manuscript and reconcile mathematical, notation, claim and exposition findings against the full source.
```

## Optional local tools

These tools are Python helpers bundled with the skills and use only the
standard library. Projects that keep plain Markdown status files work without
them.

- [Research ledger](skills/research-state/references/ledger.md): append-only claim/evidence tracking, brief views and [deferred packets](skills/research-state/references/deferred-packet.md).
- [Experiment runner](skills/computation-audit/references/runner.md): bounded execution and v2 provenance records, including observed status.
- [Literature cache](skills/literature-check/references/source-cache.md): authorized, ignored local PDFs/text with metadata and hash checks.
- [Repository inspector](skills/research-init/SKILL.md): read-only inventory before setup or migration.
- [Manuscript preparation](skills/referee/references/preparation.md): immutable lexical snapshots and conservative reuse candidates.

## Repository layout

```text
mathbox/
├── .agents/plugins/marketplace.json  # Codex marketplace (repository-root plugin)
├── .claude-plugin/       # Claude plugin manifest (explicit skill list) and marketplace
├── .codex-plugin/        # Codex package and presentation metadata
├── .github/workflows/    # CI: scripts/check.py on Python 3.10 and 3.13
├── assets/mathbox.svg    # plugin icon
├── docs/                 # changelog, design notes and validation reports
├── evals/                # evaluation protocol, synthetic fixtures and recorded trials
├── scripts/check.py      # package and regression gate
├── skills/<skill-name>/
│   ├── SKILL.md          # canonical workflow contract
│   ├── agents/openai.yaml  # OpenAI presentation and invocation policy
│   ├── evals/            # behavioral and routing probes
│   ├── references/       # supporting material
│   ├── assets/           # optional templates or data
│   └── scripts/          # optional deterministic helpers
├── AGENTS.md             # contributor instructions
└── LICENSE
```

The repository keeps exactly one copy of each skill. The Codex manifest points
to `skills/`, and the Claude manifest lists each skill directory. Relative
links therefore keep working whether a skill is copied, linked, loaded as a
plugin, or converted by OpenAI. Skill directory names are bare (for example,
`proof-audit`); the plugin adds the `mathbox:` namespace. `SKILL.md`
frontmatter uses only the portable `name` and `description` fields.

## Development

```bash
python3 scripts/check.py            # static package checks and regression suites
python3 scripts/check.py --static   # static checks only
```

The check verifies software contracts, not mathematical behavior. For
behavioral and routing evaluation, follow the
[evaluation protocol](evals/README.md).

When a skill's contract changes, update its instructions, supporting files,
behavioral evals and routing evals together. When a skill is added, renamed or
removed, update this README in the same change. Record user-visible changes
under **Unreleased** in the [changelog](docs/CHANGELOG.md). The full
contributor and validation rules are in [`AGENTS.md`](AGENTS.md).

Upstream references:
[Agent Skills specification](https://agentskills.io/specification) ·
[Claude Code plugins](https://code.claude.com/docs/en/plugins) ·
[ChatGPT and Codex plugins](https://learn.chatgpt.com/docs/build-plugins) ·
[Plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins#package-and-distribute-plugins) ·
[Submitting a Claude plugin to OpenAI](https://developers.openai.com/plugins/guides/submit-claude-plugin)

## License

[MIT](LICENSE) © 2026 Najib Idrissi-Kaïtouni.
