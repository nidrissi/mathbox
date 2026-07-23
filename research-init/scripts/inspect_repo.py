#!/usr/bin/env python3
"""Read-only inspection for AI-assisted mathematical research repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

EXCLUDE = {
    '.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__',
    'build', 'dist', 'target', '.tox', '.nox', '.pytest_cache', '.mypy_cache'
}
CANONICAL = {
    'research-init', 'research-attempt', 'proof-audit', 'literature-check',
    'computation-audit', 'manuscript-integrate', 'proofread-math',
    'research-retrospective'
}
ROLE_NAMES = {
    'PROJECT_CHARTER.md', 'RESEARCH_STATUS.md', 'HANDOFF.md',
    'PROOF_OBLIGATIONS.md', 'CLAIMS.md', 'CONVENTIONS.md',
    'CONVENTION_REGISTRY.md', 'LITERATURE.md', 'LITERATURE_LEDGER.md',
    'RESEARCH_LOG.md', 'VERIFICATION.md', 'CODE_MAP.md', 'README.md'
}


def git(root: Path, *args: str) -> str | None:
    try:
        p = subprocess.run(['git', '-C', str(root), *args], text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=10, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def root_of(path: Path) -> Path:
    path = path.expanduser().resolve()
    found = git(path, 'rev-parse', '--show-toplevel')
    return Path(found).resolve() if found else path


def walk(root: Path, depth: int):
    for current, dirs, files in os.walk(root):
        p = Path(current)
        rel = p.relative_to(root)
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE)
        if len(rel.parts) >= depth:
            dirs[:] = []
        for name in sorted(files):
            yield p / name


def info(root: Path, path: Path) -> dict:
    try:
        data = path.read_bytes()
        lines = None if b'\0' in data else len(data.splitlines())
        size = len(data)
    except OSError:
        lines, size = None, -1
    return {'path': str(path.relative_to(root)), 'bytes': size, 'lines': lines}


def inspect(root: Path, depth: int) -> dict:
    files = list(walk(root, depth))
    instructions = []
    roles = []
    skills = []
    misplaced = []
    manifests = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        name = path.name
        if name in {'AGENTS.md', 'AGENTS.override.md', 'CLAUDE.md', 'CLAUDE.local.md'} or '/.claude/rules/' in '/' + rel:
            instructions.append(info(root, path))
        if name in ROLE_NAMES:
            roles.append(info(root, path))
        if name == 'SKILL.md':
            entry = info(root, path)
            parts = path.relative_to(root).parts
            if '.agents' in parts and 'skills' in parts or '.claude' in parts and 'skills' in parts:
                skills.append(entry)
            elif len(parts) >= 3 and parts[0] == 'skills':
                misplaced.append(entry)
        if name in {'Makefile', 'justfile', 'Justfile', 'pyproject.toml', 'package.json', 'latexmkrc', '.latexmkrc'}:
            manifests.append(info(root, path))
    local_names = []
    for entry in skills:
        parts = Path(entry['path']).parts
        try:
            i = parts.index('skills')
            local_names.append(parts[i + 1])
        except (ValueError, IndexError):
            pass
    duplicates = sorted(CANONICAL.intersection(local_names))
    return {
        'root': str(root),
        'git_status': git(root, 'status', '--short'),
        'instructions': instructions,
        'research_role_files': roles,
        'skill_files': skills,
        'misplaced_root_skills': misplaced,
        'canonical_name_overrides': duplicates,
        'build_manifests': manifests,
    }


def markdown(obj: dict) -> str:
    lines = [f"# Repository inspection: `{obj['root']}`", '']
    lines += ['## Git status', '', '```text', obj['git_status'] or '(clean, unavailable, or not a Git repository)', '```', '']
    for key, title in [
        ('instructions', 'Instruction files'),
        ('research_role_files', 'Research role files'),
        ('skill_files', 'Recognized project skills'),
        ('misplaced_root_skills', 'Misplaced root skills'),
        ('build_manifests', 'Build/verification manifests')
    ]:
        lines += [f'## {title}', '']
        items = obj[key]
        if not items:
            lines.append('- None found within scan depth.')
        else:
            lines.extend(f"- `{x['path']}` — {x['lines']} lines, {x['bytes']} bytes" for x in items)
        lines.append('')
    lines += ['## Canonical-name project overrides', '']
    lines.append(', '.join(f'`{x}`' for x in obj['canonical_name_overrides']) or 'None.')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--max-depth', type=int, default=5)
    ap.add_argument('--format', choices=('markdown', 'json'), default='markdown')
    ns = ap.parse_args()
    obj = inspect(root_of(Path(ns.root)), ns.max_depth)
    print(json.dumps(obj, indent=2) if ns.format == 'json' else markdown(obj))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
