# Repository instructions

## Purpose

This repository publishes reusable Agent Skills for rigorous mathematical
research. Each directory directly under `skills/` containing `SKILL.md` is an
independently installable package. The repository root also packages the
complete suite for Claude Code and as a skills-only archive that OpenAI can
convert during submission. Keep the skills portable across both hosts.

## Sources of truth

- `SKILL.md` is the canonical behavioral contract for a skill.
- Files under `references/`, `assets/`, and `scripts/` support that contract and
  must be referenced with paths relative to the skill directory.
- `agents/openai.yaml` contains OpenAI-specific presentation and invocation
  metadata; do not duplicate the workflow there.
- `.codex-plugin/plugin.json` contains Codex package and presentation metadata;
  keep its identity and version aligned with the Claude plugin manifest.
- `.claude-plugin/plugin.json` contains the package metadata and explicit list
  of skill directories under `skills/` used by Claude and by OpenAI's skills-only
  conversion path.
- `.claude-plugin/marketplace.json` is the public Claude marketplace catalog;
  keep its root-source entry aligned with the plugin manifest.
- `evals/evals.json` checks behavior and `evals/trigger-evals.json` checks
  routing. Treat both as part of the skill contract.
- `README.md` is the public inventory and installation guide. Keep it aligned
  with the canonical skill directories and their invocation policies.

## Working rules

- Inspect `git status --short` before editing and preserve unrelated changes.
- Read the complete `SKILL.md` before changing a skill. Load only the supporting
  files relevant to the change.
- Keep every skill focused on one job. Prefer concise imperative instructions
  with explicit inputs, outputs, evidence labels, and stopping conditions.
- Do not weaken mathematical safeguards for convenience. In particular, never
  present bounded computation as universal proof, failed search as global
  novelty, or manuscript integration as validation.
- Do not hard-code a local checkout or installation path. Installed skills may
  be copied, symlinked, or loaded by a host.
- Keep one canonical copy of each skill under `skills/`. Do not duplicate
  skill packages to satisfy a host-specific plugin layout.
- Do not add dependencies or generated artifacts unless the skill genuinely
  needs them. Standard-library Python is preferred for helper scripts.
- Update the relevant behavioral and trigger evals whenever a description,
  trigger boundary, workflow, or output contract changes.
- Update `README.md` in the same change when adding, renaming, or removing a
  skill.

## Cross-agent compatibility

- Keep `SKILL.md` frontmatter portable. The current skills use only the required
  Agent Skills fields `name` and `description`; do not put host-specific
  interface or invocation settings there.
- Express shared routing boundaries in `description` and the skill body. Keep
  OpenAI-specific presentation and invocation policy in `agents/openai.yaml`.
- Use a precise `description` with positive triggers and exclusions. Update
  trigger evals whenever that routing contract changes.
- Preserve valid relative Markdown links from `SKILL.md` to bundled resources.
- Keep `CLAUDE.md` as the small compatibility shim that imports this file. Put
  shared repository guidance here rather than duplicating it.

## Validation

There is no single repository-wide test runner. Run checks proportionate to the
files changed. At minimum, run:

```bash
for file in \
  .codex-plugin/*.json \
  .claude-plugin/*.json \
  skills/*/evals/*.json \
  skills/*/assets/*.json; do
  python3 -m json.tool "$file" >/dev/null || exit 1
done
claude plugin validate .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
git diff --check
```

Root plugin validation reports that the repository's `CLAUDE.md` is not loaded
as plugin context. This warning is expected: keep the file as the repository
compatibility shim, and keep all plugin behavior under `skills/`.

For Python helper changes, also run:

```bash
PYTHONPYCACHEPREFIX=/tmp/mathbox-pycache \
  python3 -m py_compile skills/*/scripts/*.py
```

When touching the computation manifest or its validator, run:

```bash
python3 skills/computation-audit/scripts/validate_manifest.py \
  skills/computation-audit/assets/computation-manifest.json
```

When touching the repository inspector, smoke-test it with:

```bash
python3 skills/research-init/scripts/inspect_repo.py \
  --root . --format json >/dev/null
```

In the final report, list the files changed, checks run, and any check not run
with its reason.
