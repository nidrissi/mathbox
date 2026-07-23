#!/usr/bin/env python3
"""Validate a mathematical research repository's agent scaffold.

This is a static, read-only validator. It does not execute project commands or
interpret mathematical truth.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

PLACEHOLDER_PATTERNS = (
    re.compile(r"\{\{[^{}]+\}\}"),
    re.compile(r"\bUNRESOLVED\b"),
)

AUTHORITY_INVERSION_PATTERNS = (
    re.compile(r"handoff\.md.{0,80}(supersedes|overrides|takes precedence)", re.I | re.S),
    re.compile(r"research_status\.md.{0,80}(supersedes|overrides|takes precedence)", re.I | re.S),
    re.compile(r"status.{0,40}(supersedes|overrides).{0,40}agents\.md", re.I | re.S),
)

DANGEROUS_GENERIC_PATTERNS = (
    re.compile(r"\bcommit and push\b", re.I),
    re.compile(r"\binstall (all )?dependencies automatically\b", re.I),
    re.compile(r"\bfull network access\b", re.I),
)

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BACKTICK_PATH = re.compile(r"`([^`\n]+\.(?:md|tex|py|toml|yml|yaml|json|bib))`")


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def line_count(text: str) -> int:
    return len(text.splitlines())


def has_authority_inversion(text: str) -> bool:
    """Detect a positive mutable-status override claim, not a prohibition."""
    normalized = re.sub(r"\s+", " ", text)
    normalized = re.sub(
        r"\b(?:never|does not|do not|must not|cannot|can not)\s+"
        r"(?:it\s+)?(?:supersedes?|overrides?|takes? precedence)",
        "",
        normalized,
        flags=re.I,
    )
    return any(pattern.search(normalized) for pattern in AUTHORITY_INVERSION_PATTERNS)


def existing_instruction_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for name in ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md"):
        path = root / name
        if path.exists() and path.is_file():
            files.append(path)
    for base in (root / ".agents" / "skills", root / ".claude" / "skills"):
        if base.exists():
            files.extend(base.rglob("SKILL.md"))
    return sorted(set(files))


def referenced_local_paths(root: Path, source: Path, text: str) -> Iterable[tuple[str, Path]]:
    candidates: set[str] = set()
    for match in MARKDOWN_LINK.finditer(text):
        value = match.group(1).strip().split("#", 1)[0]
        if value and "://" not in value and not value.startswith(("mailto:", "#")):
            candidates.add(value)
    for match in BACKTICK_PATH.finditer(text):
        value = match.group(1).strip()
        if any(char.isspace() for char in value):
            continue
        if not any(char in value for char in ("*", "{", "}", "<", ">", "|")):
            candidates.add(value)
    for value in sorted(candidates):
        if value.startswith("/") or value.startswith("~"):
            continue
        target = (source.parent / value).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError:
            continue
        yield value, target


def validate(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"

    if not agents.exists():
        findings.append(Finding("ERROR", "AGENTS.md", "Root AGENTS.md is missing."))
    else:
        text = read_text(agents)
        lines = line_count(text)
        size = len(text.encode("utf-8"))
        if lines > 200:
            findings.append(Finding("WARN", "AGENTS.md", f"Always-loaded core is {lines} lines; investigate context bloat."))
        elif lines > 160:
            findings.append(Finding("INFO", "AGENTS.md", f"Core is {lines} lines; consider moving procedures to skills."))
        if size > 32 * 1024:
            findings.append(Finding("ERROR", "AGENTS.md", f"File is {size} bytes and alone exceeds Codex's default 32 KiB project-doc budget."))
        if "RESEARCH_STATUS.md" in text and not re.search(r"does not override|never overrides|reports status", text, re.I):
            findings.append(Finding("WARN", "AGENTS.md", "Status file is referenced without an explicit non-authority rule."))
        if not re.search(r"proved|computationally verified|conjectural", text, re.I):
            findings.append(Finding("INFO", "AGENTS.md", "No explicit evidence-status vocabulary detected."))
        if not re.search(r"git status|preserve unrelated", text, re.I):
            findings.append(Finding("INFO", "AGENTS.md", "No explicit unrelated-change preservation rule detected."))

    if not claude.exists():
        findings.append(Finding("WARN", "CLAUDE.md", "Claude Code will not read AGENTS.md directly; add a CLAUDE.md import bridge."))
    else:
        text = read_text(claude)
        if not re.search(r"(?m)^\s*@(?:\./)?AGENTS\.md\s*$", text):
            findings.append(Finding("WARN", "CLAUDE.md", "No standalone @AGENTS.md import detected; duplicated instructions may drift."))
        if line_count(text) > 200:
            findings.append(Finding("WARN", "CLAUDE.md", "Claude recommends targeting under 200 lines per CLAUDE.md."))

    for path in existing_instruction_files(root):
        text = read_text(path)
        relative = path.relative_to(root).as_posix()
        if has_authority_inversion(text):
            findings.append(Finding("ERROR", relative, "Mutable status/handoff material appears able to override agent instructions."))
        for pattern in DANGEROUS_GENERIC_PATTERNS:
            if pattern.search(text):
                findings.append(Finding("WARN", relative, "Broad autonomous action detected; verify explicit authorization and safeguards."))
        for pattern in PLACEHOLDER_PATTERNS:
            count = len(pattern.findall(text))
            if count:
                level = "WARN" if pattern.pattern.startswith("\\{\\{") else "INFO"
                findings.append(Finding(level, relative, f"Contains {count} unresolved placeholder marker(s)."))
        if path.name.endswith("_AGENT.md") or path.name == "AGENT.md":
            findings.append(Finding("WARN", relative, "Nonstandard filename may not be discovered by Codex or Claude Code."))

        for literal, target in referenced_local_paths(root, path, text):
            if literal.startswith(("http", "$", "{{")):
                continue
            if not target.exists():
                findings.append(Finding("INFO", relative, f"Referenced local path does not exist: {literal}"))

    status = root / "RESEARCH_STATUS.md"
    if status.exists():
        text = read_text(status)
        if not re.search(r"does not override|never overrides", text, re.I):
            findings.append(Finding("WARN", "RESEARCH_STATUS.md", "Add an explicit statement that status never overrides instructions or proofs."))

    standard_singular = list(root.glob("*_AGENT.md")) + list(root.glob("AGENT.md"))
    for path in standard_singular:
        findings.append(Finding("WARN", path.name, "Rename/copy to exact AGENTS.md at the intended scope for discovery."))

    return sorted(findings, key=lambda f: ({"ERROR": 0, "WARN": 1, "INFO": 2}[f.level], f.path, f.message))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as a nonzero exit")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    findings = validate(root)
    if findings:
        for finding in findings:
            print(f"{finding.level:5} {finding.path}: {finding.message}")
    else:
        print("OK: no scaffold issues detected by static checks.")
    errors = sum(f.level == "ERROR" for f in findings)
    warnings = sum(f.level == "WARN" for f in findings)
    print(f"Summary: {errors} error(s), {warnings} warning(s), {len(findings) - errors - warnings} info item(s).")
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
