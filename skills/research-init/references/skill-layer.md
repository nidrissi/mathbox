# Skill-layer decision

## Default

Create no repository-local skills. The installed `mathbox` plugin supplies the
canonical common workflows; the repository supplies local data and rules.

## Vendor exact copies only when

- collaborators need the same workflow from version control;
- a remote/cloud environment cannot install the `mathbox` plugin; or
- an institutional policy requires repository-contained configuration.

Record the `mathbox` version and checksum. Do not edit vendored canonical skill
bodies.

## Create a new project skill only when all are true

1. The procedure recurs.
2. The procedure itself is unique to this project.
3. It cannot be represented by a `mathbox` plugin skill plus `AGENTS.md`,
   conventions, verification commands, templates, or scripts.
4. It has a distinct project-qualified name.
5. Correct recognized paths are used: `.agents/skills/<name>` for Codex and/or
   `.claude/skills/<name>` for Claude Code.
6. Trigger and behavior evals are supplied.
7. The user approves the proposal.

Same-name wrappers around `mathbox` plugin skills are prohibited because tool
precedence differs and neither tool merges their contents reliably.
