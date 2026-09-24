# Mathbox

`mathbox` is a plugin for Claude Code and Codex with ten Agent Skills for
sustained, auditable mathematical research, plus optional standard-library
Python tools.

Each skill handles one job: research, verification, computation, literature
work, manuscript integration, or proofreading. Each job has its own evidence
standard and stopping condition. The canonical distribution is the plugin, but
every skill can also be installed on its own as a standalone Agent Skill.

These are research workflows and safeguards, not a computer algebra system or
a replacement for mathematical review.

[Changelog](docs/CHANGELOG.md) · [v3 design](docs/design-v3.md) ·
[v3 validation](docs/validation-v3.md) · [Evaluation protocol](evals/README.md)

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

Install `mathbox` from Codex's plugin directory, start a new session, and try:

```text
$mathbox:proof-audit Audit the proof of Lemma 3.2 and isolate the first unproved implication.
```

If the plugin directory listing is not available yet, the built-in skill
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

Update the plugin through the host's plugin manager. To update a standalone
checkout, run `git -C "$HOME/.local/share/mathbox" pull --ff-only`. For a
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
| [`proof-audit`](skills/proof-audit/) | decide whether an existing claim or proof is correct and isolate the exact gap | automatic |
| [`literature-check`](skills/literature-check/) | verify what an external source proves, check a bounded novelty claim, or cache a source locally | automatic |
| [`computation-audit`](skills/computation-audit/) | design, run, or audit a computation that supports a claim | automatic |
| [`manuscript-integrate`](skills/manuscript-integrate/) | transfer an already validated result into the authoritative LaTeX manuscript | explicit |
| [`proofread-math`](skills/proofread-math/) | fix grammar, typography, LaTeX, references, or local typos whose correction is forced | automatic |

A host may pick an **automatic** skill for any task that matches its
description. An **explicit** skill runs only when you ask for it. This boundary
is set in the skill's description and body, not in host-specific frontmatter.
Any skill can be invoked by name. With the plugin, use `/mathbox:<skill>` in
Claude Code or `$mathbox:<skill>` in Codex. With standalone installs, use
`/<skill>` or `$<skill>`.

### Safeguards

- A bounded computation is evidence only for its stated range, never a
  universal proof.
- A proof audit reconstructs the claimed object independently. A computation
  on a convenient substitute proves nothing about the original object. A
  coverage claim must match the iterator that actually ran and the absolute
  grading, not only samples or parity checks.
- Proofreading never changes an argument. Use `proof-audit` to diagnose a
  proof and `research-attempt` to develop a new one.
- `manuscript-integrate` transfers mathematics that has already been
  validated. It does not make conjectural work ready for publication.
- A failed literature search supports only a bounded search report, never a
  claim of global novelty. A novelty check searches equivalent and historical
  terminology and follows citation chains to primary sources where it can.
- Any new question about what an external source proves goes through
  `literature-check`, so every skill applies the same rules for exact versions,
  cache use and evidence.

### Example prompts

Each line below is a separate Codex prompt. In Claude Code, write
`/mathbox:` instead of `$mathbox:`.

```text
$mathbox:research-program Pursue this conjecture through distinct proof and counterexample routes. Preserve the original goal and continue after failed attempts.
$mathbox:research-state Check which claims depend on Lemma K, which evidence is stale, and what to attack next.
$mathbox:research-init Plan a migration of this repository's AGENTS.md and live status; preserve history and inspect ledger pins before editing.
```

## Optional local tools

These tools are Python helpers bundled with the skills and use only the
standard library. Projects that keep plain Markdown status files work without
them.

- **Research ledger** (`research-state`). This is an append-only, versioned
  record in the project's `.mathbox/` directory. It records claim revisions,
  dependencies, hashed evidence, review provenance, and the runs of programs
  and routes. From these it generates brief handoff, impact and stale-evidence
  reports. A label such as `proof-recorded` describes recorded evidence. It
  does not certify a proof or replace the project's own promotion policy. A
  host that cannot execute commands can return a deferred packet that is
  ingested locally later. See the
  [ledger contract](skills/research-state/references/ledger.md) and the
  [deferred handoff](skills/research-state/references/deferred-handoff.md).
- **Experiment runner** (`computation-audit`). It runs a bounded computation and
  records the actual argv, the hashes of its inputs and results, bounded logs,
  its finite scope, and optional POSIX resource limits. The result is a
  version 2 computation manifest. See the
  [runner contract](skills/computation-audit/references/runner.md).
- **Literature cache** (`literature-check`). When a project authorizes keeping
  source material, the helper stores PDFs and extracted text in
  `.research-cache/literature/`, addressed by content. Keep a
  `/.research-cache/` rule in the project's `.gitignore`. The helper refuses
  to write anything Git would track, never fetches sources or handles
  credentials, and never modifies the cache during lookups. See the
  [cache contract](skills/literature-check/references/source-cache.md).
- **Repository inspector** (`research-init`). It builds a read-only inventory
  of research roles, live files, computation manifests and cache conventions
  before setup or migration. See the
  [existing-repository migration guide](skills/research-init/references/existing-repo-migration.md).

## Repository layout

```text
mathbox/
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
[Submitting a Claude plugin to OpenAI](https://developers.openai.com/plugins/guides/submit-claude-plugin)

## License

[MIT](LICENSE) © 2026 Najib Idrissi-Kaïtouni.
