#!/usr/bin/env python3
"""Read-only probe for AI-assisted mathematical research repositories.

The script intentionally avoids dependency installation, network access, and file
mutation. It summarizes repository structure and instruction-system risks so an
initialization skill can ask informed questions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}

INSTRUCTION_NAMES = {
    "AGENTS.md",
    "AGENTS.override.md",
    "CLAUDE.md",
    "CLAUDE.local.md",
    ".cursorrules",
    ".windsurfrules",
    ".clinerules",
}

IMPORTANT_NAMES = {
    "README.md",
    "PROJECT_CHARTER.md",
    "RESEARCH_STATUS.md",
    "RESEARCH_LOG.md",
    "HANDOFF.md",
    "VERIFICATION.md",
    "LITERATURE_LEDGER.md",
    "PLAN.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "uv.lock",
    "poetry.lock",
    "requirements.txt",
    "environment.yml",
    "environment.yaml",
    "flake.lock",
    "lakefile.toml",
    "lean-toolchain",
    "Makefile",
    "justfile",
    "Taskfile.yml",
    "Cargo.toml",
    "Project.toml",
    "Manifest.toml",
    "package.json",
}

LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".pyx": "Cython",
    ".sage": "SageMath",
    ".ipynb": "Jupyter",
    ".tex": "TeX",
    ".lean": "Lean",
    ".v": "Coq/Verilog",
    ".agda": "Agda",
    ".thy": "Isabelle",
    ".jl": "Julia",
    ".m": "Mathematica/MATLAB",
    ".rs": "Rust",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".hs": "Haskell",
    ".js": "JavaScript",
    ".ts": "TypeScript",
}

STATUS_OVERRIDE_RE = re.compile(
    r"(?:handoff(?:\.md)?|research[_ -]?status(?:\.md)?|status (?:file|snapshot|dashboard))"
    r".{0,240}(?:supersedes?|overrides?|takes? precedence)"
    r".{0,240}(?:this file|agents\.md|agent instructions)",
    re.I | re.S,
)


def has_authority_inversion(text: str) -> bool:
    """Detect positive override claims while ignoring explicit prohibitions."""
    normalized = re.sub(r"\s+", " ", text)
    normalized = re.sub(
        r"\b(?:never|does not|do not|must not|cannot|can not)\s+"
        r"(?:it\s+)?(?:supersedes?|overrides?|takes? precedence)",
        "",
        normalized,
        flags=re.I,
    )
    return bool(STATUS_OVERRIDE_RE.search(normalized))


@dataclass(frozen=True)
class FileMetric:
    path: str
    lines: int
    bytes: int


@dataclass
class ProbeResult:
    root: str
    git_root: str | None
    git_status: list[str]
    top_level: list[str]
    instructions: list[FileMetric]
    important_files: list[str]
    skill_files: list[str]
    hook_files: list[str]
    ci_files: list[str]
    language_counts: dict[str, int]
    likely_profiles: list[str]
    warnings: list[str]
    scan_truncated: bool


def run_git(root: Path, args: Sequence[str]) -> tuple[int, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 127, ""
    return completed.returncode, completed.stdout.strip()


def line_count(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def safe_text(path: Path, max_bytes: int = 256_000) -> str:
    try:
        raw = path.read_bytes()[:max_bytes]
    except OSError:
        return ""
    return raw.decode("utf-8", errors="replace")


def iter_files(root: Path, max_files: int, max_depth: int) -> tuple[list[Path], bool]:
    files: list[Path] = []
    truncated = False
    root_depth = len(root.parts)
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.parts) - root_depth
        dirnames[:] = [
            name
            for name in sorted(dirnames)
            if name not in SKIP_DIRS and not name.startswith(".cache")
        ]
        if depth >= max_depth:
            dirnames[:] = []
        for name in sorted(filenames):
            path = current_path / name
            if path.is_symlink() and not path.exists():
                continue
            files.append(path)
            if len(files) >= max_files:
                truncated = True
                return files, truncated
    return files, truncated


def is_instruction(path: Path) -> bool:
    if path.name in INSTRUCTION_NAMES or path.name == "AGENT.md" or path.name.endswith("_AGENT.md"):
        return True
    parts = path.parts
    if path.name == "SKILL.md" and any(part in {"skills", ".agents", ".claude"} for part in parts):
        return True
    if ".claude" in parts and "rules" in parts and path.suffix == ".md":
        return True
    if ".github" in parts and path.name == "copilot-instructions.md":
        return True
    return False


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def infer_profiles(files: Iterable[Path], language_counts: Counter[str]) -> list[str]:
    names = {p.name.lower() for p in files}
    profiles: list[str] = []
    if language_counts["Lean"] or language_counts["Coq/Verilog"] or language_counts["Agda"] or language_counts["Isabelle"]:
        profiles.append("formalization")
    if language_counts["Python"] or language_counts["SageMath"] or language_counts["Julia"] or "pyproject.toml" in names:
        profiles.append("computation/software")
    if language_counts["TeX"] or any(name.endswith(".bib") for name in names):
        profiles.append("manuscript")
    proof_markers = {"proof.md", "proofs.md", "conjectures.md", "theorems.md", "research_log.md", "plan.md"}
    if names.intersection(proof_markers) or language_counts["TeX"]:
        profiles.append("proof-first")
    return profiles or ["undetermined"]


def probe(root: Path, max_files: int, max_depth: int) -> ProbeResult:
    root = root.resolve()
    rc, git_root_text = run_git(root, ["rev-parse", "--show-toplevel"])
    git_root = Path(git_root_text).resolve() if rc == 0 and git_root_text else None
    scan_root = git_root or root

    files, truncated = iter_files(scan_root, max_files=max_files, max_depth=max_depth)
    language_counts: Counter[str] = Counter()
    instructions: list[FileMetric] = []
    important: list[str] = []
    skills: list[str] = []
    hooks: list[str] = []
    ci: list[str] = []
    warnings: list[str] = []

    for path in files:
        language = LANGUAGE_EXTENSIONS.get(path.suffix.lower())
        if language:
            language_counts[language] += 1
        relative = rel(scan_root, path)
        if is_instruction(path):
            try:
                size = path.stat().st_size
            except OSError:
                size = 0
            instructions.append(FileMetric(relative, line_count(path), size))
            text = safe_text(path)
            if has_authority_inversion(text):
                warnings.append(f"Possible mutable-authority inversion in {relative}")
            if path.name.endswith("_AGENT.md") or path.name == "AGENT.md":
                warnings.append(f"Nonstandard agent filename may not be discovered: {relative}")
        if path.name in IMPORTANT_NAMES:
            important.append(relative)
        if path.name == "SKILL.md" or "/skills/" in f"/{relative}/":
            skills.append(relative)
        if "hooks" in path.parts or relative.startswith(".claude/settings"):
            hooks.append(relative)
        if relative.startswith(".github/workflows/") or path.name in {".gitlab-ci.yml", "Jenkinsfile"}:
            ci.append(relative)

    for metric in instructions:
        if metric.path.endswith("AGENTS.md") or metric.path.endswith("CLAUDE.md"):
            if metric.lines > 200:
                warnings.append(f"Always-loaded instruction file exceeds 200 lines: {metric.path} ({metric.lines})")
            if metric.bytes > 32 * 1024:
                warnings.append(f"Instruction file alone exceeds 32 KiB: {metric.path} ({metric.bytes} bytes)")

    if any(metric.path.endswith("AGENTS.md") for metric in instructions) and not any(
        metric.path.endswith("CLAUDE.md") for metric in instructions
    ):
        warnings.append("AGENTS.md found without a CLAUDE.md bridge")

    rc, status_text = run_git(scan_root, ["status", "--short"])
    status = status_text.splitlines() if rc == 0 and status_text else []

    try:
        top_level = sorted(p.name + ("/" if p.is_dir() else "") for p in scan_root.iterdir() if p.name != ".git")
    except OSError:
        top_level = []

    return ProbeResult(
        root=str(scan_root),
        git_root=str(git_root) if git_root else None,
        git_status=status,
        top_level=top_level[:200],
        instructions=sorted(instructions, key=lambda item: item.path),
        important_files=sorted(set(important)),
        skill_files=sorted(set(skills)),
        hook_files=sorted(set(hooks)),
        ci_files=sorted(set(ci)),
        language_counts=dict(language_counts.most_common()),
        likely_profiles=infer_profiles(files, language_counts),
        warnings=sorted(set(warnings)),
        scan_truncated=truncated,
    )


def markdown(result: ProbeResult) -> str:
    lines = [
        "# Repository probe",
        "",
        f"- Root: `{result.root}`",
        f"- Git root: `{result.git_root or 'not detected'}`",
        f"- Likely profiles: {', '.join(result.likely_profiles)}",
        f"- Scan truncated: {'yes' if result.scan_truncated else 'no'}",
        "",
        "## Git status",
        "",
    ]
    if result.git_status:
        lines.extend(f"- `{entry}`" for entry in result.git_status)
    else:
        lines.append("- Clean, unavailable, or not a Git repository.")

    lines.extend(["", "## Instruction files", ""])
    if result.instructions:
        lines.append("| Path | Lines | Bytes |")
        lines.append("|---|---:|---:|")
        for item in result.instructions:
            lines.append(f"| `{item.path}` | {item.lines} | {item.bytes} |")
    else:
        lines.append("- None detected.")

    sections = [
        ("Important project files", result.important_files),
        ("Skills", result.skill_files),
        ("Hooks/settings", result.hook_files),
        ("CI", result.ci_files),
    ]
    for title, values in sections:
        lines.extend(["", f"## {title}", ""])
        lines.extend(f"- `{value}`" for value in values) if values else lines.append("- None detected.")

    lines.extend(["", "## Language signals", ""])
    if result.language_counts:
        lines.extend(f"- {name}: {count} files" for name, count in result.language_counts.items())
    else:
        lines.append("- No recognized source extensions in scan range.")

    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- None detected.")

    lines.extend(["", "## Top level", ""])
    lines.extend(f"- `{name}`" for name in result.top_level)
    return "\n".join(lines) + "\n"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository or working-directory root")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-files", type=int, default=20_000)
    parser.add_argument("--max-depth", type=int, default=5)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    result = probe(root, max_files=args.max_files, max_depth=args.max_depth)
    if args.format == "json":
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
    else:
        print(markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
