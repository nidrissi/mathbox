#!/usr/bin/env python3
"""Read-only inspection for AI-assisted mathematical research repositories."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote

EXCLUDE = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__",
    "build", "dist", "target", ".tox", ".nox", ".pytest_cache", ".mypy_cache",
    ".research-cache", ".mathbox",
}
CANONICAL = {
    "research-init", "research-attempt", "proof-audit", "literature-check",
    "computation-audit", "manuscript-integrate", "proofread-math",
    "research-retrospective", "research-program", "research-state", "referee",
}
TEXT_ROLE_SUFFIXES = {".md", ".txt", ".rst"}
KNOWN_PATH_SUFFIXES = {
    ".bib", ".csv", ".json", ".md", ".pdf", ".py", ".rst", ".tex",
    ".toml", ".tsv", ".txt", ".yaml", ".yml",
}
# Directory parts and filename tokens that mark archived or imported history.
# Current route records are durable, not historical: their broken links stay current.
HISTORICAL_PARTS = {"archive", "archives", "imports", "legacy", "migrations", "quarantine"}
HISTORICAL_TOKENS = {"archive", "archived", "historical", "legacy", "old", "superseded"}
# History plus records, templates, tooling and run output: never the live dashboard.
NON_LIVE_PARTS = HISTORICAL_PARTS | {
    "assets", "computations", "experiments", "fixtures", "records", "references",
    "runs", "skills", "templates", "vendor", "vendored",
}
NON_LIVE_TOKENS = HISTORICAL_TOKENS | {"proposed", "template"}
DECLARED_PATH_LABELS = {
    "charter": ("charter", "project charter"),
    "status": ("live status", "status", "dashboard"),
    "claims": ("claims", "claim obligations", "proof obligations"),
    "conventions": ("conventions", "convention registry"),
    "literature": ("literature", "literature ledger"),
    "research_log": ("research log", "research-history index", "history index", "history entry point"),
    "route_index": ("route index", "route indexes"),
    "verification": ("verification", "verification commands"),
    "records": ("research records", "detailed research records", "route records"),
    "project_map": ("project map", "repository map", "code map", "path migration map"),
    "source_cache": ("local literature cache", "literature cache", "source cache", "paper cache"),
}


def git_run(root: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess | None:
    """Run Git in root; None when it cannot start or times out."""
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args], text=True, input=stdin,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=10, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def git(root: Path, *args: str, stdin: str | None = None) -> str | None:
    """Return stdout for a successful Git invocation, otherwise None."""
    process = git_run(root, *args, stdin=stdin)
    return process.stdout.strip() if process is not None and process.returncode == 0 else None


def git_state(root: Path, cache_paths: tuple[str, ...] = ()) -> dict:
    """Distinguish a clean worktree from unavailable or failed Git metadata."""
    if shutil.which("git") is None:
        return {
            "state": "unavailable", "repository": False, "porcelain": None,
            "toplevel": None, "reason": "git executable unavailable",
        }
    try:
        probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "state": "unavailable", "repository": False, "porcelain": None,
            "toplevel": None, "reason": "git probe timed out",
        }
    if probe.returncode != 0:
        return {
            "state": "unavailable", "repository": False, "porcelain": None,
            "toplevel": None, "reason": "not a Git worktree",
        }
    try:
        exclusions = [f":(exclude,literal){path}" for path in cache_paths]
        status = subprocess.run(
            ["git", "-C", str(root), "--no-optional-locks", "--no-literal-pathspecs",
             "status", "--short", "--", ".", *exclusions],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10, check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "state": "error", "repository": True, "porcelain": None,
            "toplevel": probe.stdout.strip(), "reason": "git status timed out",
        }
    if status.returncode != 0:
        return {
            "state": "error", "repository": True, "porcelain": None,
            "toplevel": probe.stdout.strip(), "reason": "git status failed",
        }
    porcelain = status.stdout.rstrip("\n")
    return {
        "state": "dirty" if porcelain else "clean", "repository": True,
        "porcelain": porcelain, "toplevel": probe.stdout.strip(), "reason": None,
    }


def unverified_coverage(note: str | None = None) -> dict:
    return {"git_ignored": None, "ignore_rule_source": None, "repository_ignore_rule": None,
            "tracked_entries": None, "coverage_note": note}


def applicable_ignore_files(path: str) -> list[str]:
    """Project .gitignore files whose rules can match the directory itself."""
    return [(parent / ".gitignore").as_posix() for parent in Path(path).parents]


def indexed_ignore_files(root: Path, names: list[str]) -> tuple[set[str], set[str]] | None:
    """Return (tracked, unchanged-from-index) among names, reading only those files."""
    staged = git(root, "--literal-pathspecs", "ls-files", "--stage", "-z", "--", *names)
    if staged is None:
        return None
    tracked, blobs = set(), {}
    for entry in filter(None, staged.split("\0")):
        meta, _, name = entry.partition("\t")
        tracked.add(name)
        fields = meta.split()
        if len(fields) == 3 and fields[2] == "0":
            blobs[name] = fields[1]
    present = sorted(name for name in blobs
                     if (root / name).is_file() and not (root / name).is_symlink())
    output = git(root, "hash-object", "--", *present) if present else ""
    hashes = output.split() if output is not None else []
    if len(hashes) != len(present):
        return None
    return tracked, {name for name, digest in zip(present, hashes) if blobs[name] == digest}


def cache_ignore_coverage(root: Path, paths: list[str]) -> dict[str, dict]:
    """Check each cache directory's ignore coverage and whether the index carries its rule.

    A rule counts as tracked only when its ignore file is in the index and every
    applicable tracked ignore file matches its index entry, so the coverage
    observed here is what a checkout of the index would see.
    """
    rule_files = sorted({name for path in paths for name in applicable_ignore_files(path)})
    indexed = indexed_ignore_files(root, rule_files) if paths else None
    results = {}
    for path in paths:
        coverage = directory_ignore_coverage(root, path, indexed)
        index = git(root, "--literal-pathspecs", "ls-files", "--cached", "-z", "--", path)
        coverage["tracked_entries"] = index.count("\0") if index is not None else None
        results[path] = coverage
    return results


def directory_ignore_coverage(root: Path, path: str,
                              indexed: tuple[set[str], set[str]] | None) -> dict:
    parts = Path(path).parts
    if any((root.joinpath(*parts[:end]) / ".git").exists() for end in range(1, len(parts))):
        # The enclosing repository's rules do not govern a nested repository.
        return unverified_coverage("inside a nested repository or submodule")
    # --no-index: an already tracked entry must not hide the directory's rule.
    # A trailing slash can match an empty child in "dir/*", which still
    # permits exceptions among the children. Query the directory itself.
    process = git_run(root, "check-ignore", "--no-index", "-v", "-z", "--stdin", stdin=path + "\0")
    if process is None or process.returncode not in (0, 1):
        return unverified_coverage("git check-ignore failed")
    fields = process.stdout.split("\0")
    ignored = len(fields) >= 4 and not fields[2].startswith("!")
    if not ignored and not (root / path).is_dir():
        # A directory rule cannot match a directory that does not exist yet.
        return unverified_coverage()
    source = fields[0] if ignored else None
    relevant = set(applicable_ignore_files(path))
    tracked = bool(ignored and indexed is not None and source in relevant
                   and source in indexed[0] and (relevant & indexed[0]) <= indexed[1])
    return {"git_ignored": ignored, "ignore_rule_source": source,
            "repository_ignore_rule": tracked, "tracked_entries": None, "coverage_note": None}


def root_of(path: Path) -> Path:
    path = path.expanduser().resolve()
    found = git(path, "rev-parse", "--show-toplevel")
    return Path(found).resolve() if found else path


def safe_relative(root: Path, value: str) -> Path | None:
    """Resolve a declared project-relative path without allowing path escape."""
    if not value or value.startswith(("/", "~")) or "://" in value:
        return None
    try:
        candidate = (root / value).resolve()
    except (OSError, RuntimeError):
        return None
    return candidate if candidate.is_relative_to(root.resolve()) else None


def read_refusal(root: Path, path: Path, excluded: set[Path], *, walk_rules: bool) -> str | None:
    """Why a direct read of path is refused, or None. Every direct read uses this policy.

    Symlinks (including parents) and source caches are always refused. With
    walk_rules, so are the walker's excluded directory names.
    """
    if any(path.is_relative_to(cache) for cache in excluded):
        return "inside a source cache"
    if safe_relative(root, path.relative_to(root).as_posix()) != path:
        return "symlinked or outside the scan root"
    if walk_rules and EXCLUDE.intersection(path.relative_to(root).parts):
        return "under an excluded directory"
    return None


DECLARATION_LABELS = {alias.casefold(): role for role, aliases in DECLARED_PATH_LABELS.items() for alias in aliases}


def instruction_declarations(root: Path, skipped: set[str]) -> list[dict]:
    """Read only explicit, labeled path declarations from root instructions."""
    found: list[dict] = []
    for source in (root / "AGENTS.md", root / "CLAUDE.md"):
        if source.name in skipped or not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for number, line in unfenced_lines(text):
            match = re.match(
                r"^\s*[-*]?\s*(?:\*\*)?([^:*`]+?)(?::(?:\*\*)?|\*\*:)\s*`([^`]+)`",
                line,
            )
            if not match:
                continue
            label = re.sub(r"\s+", " ", match.group(1).strip()).casefold()
            role = DECLARATION_LABELS.get(label)
            value = match.group(2)
            target = cache_reference(root, value) if role == "source_cache" else clean_reference(value)
            if target is None:
                continue
            target = target.rstrip("/")
            destination = safe_relative(root, target)
            if (role == "verification" and Path(target).suffix.casefold() not in KNOWN_PATH_SUFFIXES
                    and (destination is None or not destination.is_dir())):
                continue
            if role and destination is not None:
                found.append({
                    "role": role, "path": target, "source": source.name,
                    "line": number,
                })
    return found


def config_declarations(root: Path) -> list[dict]:
    """Read path roles from the ledger config; the caller decides whether it may be read."""
    found: list[dict] = []
    config = root / ".mathbox" / "config.json"
    if not config.is_file():
        return found
    try:
        data = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return found
    if not isinstance(data, dict):
        return found
    for container in (data.get("paths"), data.get("roles")):
        if not isinstance(container, dict):
            continue
        for key, value in container.items():
            normalized = str(key).replace("_", " ").replace("-", " ").casefold()
            role = DECLARATION_LABELS.get(normalized)
            if role and isinstance(value, str) and safe_relative(root, value.rstrip("/")) is not None:
                found.append({
                    "role": role, "path": value.rstrip("/"),
                    "source": ".mathbox/config.json", "line": None,
                })
    return found


def unique_declarations(found: list[dict]) -> list[dict]:
    unique = {(item["role"], item["path"], item["source"], item["line"]): item for item in found}
    return sorted(unique.values(), key=lambda item: (item["role"], item["path"], item["source"]))


def root_cache_declarations(root: Path, declarations: list[dict]) -> list[dict]:
    """Declared caches that resolve to the scan root, which cannot be excluded."""
    return [dict(item, reason="resolves to the scan root")
            for item in declarations
            if item["role"] == "source_cache" and safe_relative(root, item["path"]) == root]


def source_cache_conventions(root: Path, declarations: list[dict], requested: set[Path]) -> list[dict]:
    """Report standard, explicit, and unmistakably named cache conventions."""
    records: dict[str, dict] = {}

    def add(value: str, basis: str, confidence: str, declared: bool = False):
        path = safe_relative(root, value.rstrip("/"))
        if path is None or path == root:
            return
        relative = path.relative_to(root).as_posix()
        existing = records.get(relative)
        item = {
            "path": relative, "exists": path.is_dir(), "declared": declared,
            "basis": basis, "confidence": confidence,
        }
        if existing is None or declared or existing["confidence"] == "tentative":
            records[relative] = item

    add(".research-cache/literature", "standard mathbox convention", "high")
    for item in declarations:
        if item["role"] == "source_cache":
            add(item["path"], f"declared in {item['source']}", "high", True)
    for path in requested:
        add(path.relative_to(root).as_posix(), "designated in request", "high", True)
    for name in (".literature-cache", "literature-cache", ".source-cache", "source-cache", ".paper-cache", "paper-cache"):
        if (root / name).is_dir():
            add(name, "cache-specific directory name", "high")
    # Generic names are only candidates when they visibly contain source files;
    # no source bytes are opened.
    for name in ("papers", "refs", "references", "sources"):
        path = root / name
        if path.is_symlink() or not path.is_dir() or name in records:
            continue
        try:
            has_sources = any(child.is_file() and child.suffix.casefold() in {".pdf", ".djvu", ".epub"}
                              for child in path.iterdir())
        except OSError:
            has_sources = False
        if has_sources:
            add(name, "source-like files under a conventional directory name", "tentative")
    return sorted(records.values(), key=lambda item: item["path"])


def walk(root: Path, depth: int, excluded_paths: set[Path] | None = None):
    excluded_paths = {path.resolve() for path in (excluded_paths or set())}
    if root in excluded_paths:
        return
    for current, dirs, files in os.walk(root):
        path = Path(current)
        rel = path.relative_to(root)
        kept = []
        for name in sorted(dirs):
            unresolved_child = path / name
            if unresolved_child.is_symlink() or name in EXCLUDE or unresolved_child in excluded_paths:
                continue
            kept.append(name)
        dirs[:] = kept
        if len(rel.parts) >= depth:
            dirs[:] = []
        for name in sorted(files):
            candidate = path / name
            if not candidate.is_symlink():
                yield candidate


def info(root: Path, path: Path) -> dict:
    try:
        data = path.read_bytes()
        lines = None if b"\0" in data else len(data.splitlines())
        size = len(data)
    except OSError:
        lines, size = None, -1
    return {"path": str(path.relative_to(root)), "bytes": size, "lines": lines}


def normalized_stem(path: Path) -> str:
    return re.sub(r"[^a-z0-9]+", "_", path.stem.casefold()).strip("_")


def located_in(path: Path, parts: set[str], tokens: set[str]) -> bool:
    """Whether a relative path's directories or filename tokens meet the given sets."""
    return bool({part.casefold() for part in path.parts[:-1]} & parts
                or set(normalized_stem(path).split("_")) & tokens)


def semantic_roles(path: Path) -> list[str]:
    """Classify conventional and common aliased research-role filenames."""
    if path.suffix.casefold() not in TEXT_ROLE_SUFFIXES | {".json", ".yaml", ".yml"}:
        return []
    stem = normalized_stem(path)
    tokens = set(stem.split("_"))
    roles = []

    def add(role: str, condition: bool):
        if condition:
            roles.append(role)

    add("charter", "charter" in tokens)
    add("plan", "plan" in tokens)
    add("status", "status" in tokens or "dashboard" in tokens)
    add("outline", "outline" in tokens)
    add("manifest", "manifest" in tokens)
    add("theorem_inventory", "theorems" in tokens or stem in {"theorem_inventory", "theorem_index", "theorem_ledger", "theorem_list"}
        or ("theorem" in tokens and bool(tokens & {"inventory", "index", "ledger", "list"})))
    add("fact_inventory", "facts" in tokens or stem in {"fact_inventory", "fact_index", "fact_ledger", "fact_list"}
        or ("fact" in tokens and bool(tokens & {"inventory", "index", "ledger", "list"})))
    add("handoff", "handoff" in tokens)
    add("claims", stem in {"claims", "claim_inventory", "claim_ledger"})
    add("proof_obligations", stem in {"proof_obligations", "obligations"})
    add("conventions", stem in {"conventions", "convention_registry", "notation"})
    add("literature", stem in {"literature", "literature_ledger", "sources_ledger", "bibliography_ledger"})
    add("research_log", stem in {"research_log", "research_history", "route_log"}
        or {"research", "log"} <= tokens or {"route", "log"} <= tokens)
    add("verification", stem in {"verification", "verification_matrix", "checks"})
    add("project_map", stem in {"code_map", "project_map", "repository_map", "path_map", "path_migrations"})
    add("readme", stem == "readme")
    return roles


def unfenced_lines(text: str):
    """Yield original line numbers and prose outside Markdown code fences."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if (marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence)
                    and not marker[2].strip()):
                fence = None
        elif marker and (marker[1][0] != "`" or "`" not in marker[2]):
            fence = marker[1]
        else:
            yield number, line


def classify_research_log(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {"classification": "unreadable", "linked_entries": 0, "route_markers": 0}
    text = "\n".join(line for _, line in unfenced_lines(text))
    linked = len(re.findall(r"(?m)^\s*[-*]\s+.*\[[^]]+\]\([^)]+\)", text))
    dated_headings = len(re.findall(r"(?m)^#{1,4}\s+(?:\d{4}-\d{2}-\d{2}\b|(?:19|20)\d{2}\b)", text))
    fields = len(re.findall(
        r"(?im)^\s*[-*]\s+\*\*(?:idea|target|route|outcome|failure analysis|next step|computations?|why it might work)\*\*\s*:",
        text,
    ))
    route_markers = dated_headings + fields
    meaningful = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not meaningful:
        classification = "empty"
    elif linked and route_markers:
        classification = "mixed"
    elif route_markers:
        classification = "long-form-legacy"
    elif linked:
        classification = "compact-linked-index"
    else:
        classification = "unstructured"
    return {
        "classification": classification, "linked_entries": linked,
        "route_markers": route_markers,
    }


def checkpoint_markers(path: Path) -> int:
    """Count dated or previous-checkpoint headings as a review prompt, not a verdict."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return 0
    return sum(bool(re.match(r"^\s*(?:#{1,6}\s+|>\s*\*\*)"
                             r"(?:previous\s+checkpoint\b|[^\n]*\b20\d{2}-\d{2}-\d{2}\b)",
                             line, re.IGNORECASE))
               for line in text.splitlines())


def computation_manifest(root: Path, path: Path) -> dict | None:
    if path.suffix.casefold() != ".json":
        return None
    parts = {part.casefold() for part in path.relative_to(root).parts}
    name_like = "manifest" in normalized_stem(path)
    located_in_manifest_dir = bool(parts & {"manifest", "manifests"})
    located_as_computation = bool(parts & {"check", "checks", "computation", "computations", "experiment", "experiments", "runs"})
    if not (name_like or located_in_manifest_dir or located_as_computation):
        return None
    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        if name_like or located_in_manifest_dir:
            return dict(info(root, path), classification="candidate-unreadable")
        return None
    mathbox_like = isinstance(data, dict) and {"claim_id", "mathematics", "run", "outputs"} <= data.keys()
    if not (mathbox_like or name_like or located_in_manifest_dir):
        return None
    outputs = data.get("outputs") if isinstance(data, dict) else None
    return dict(
        info(root, path),
        classification="mathbox-like" if mathbox_like else "location/name-candidate",
        schema_version=data.get("schema_version") if isinstance(data, dict) else None,
        claim_id=data.get("claim_id") if isinstance(data, dict) else None,
        output_count=len(outputs) if isinstance(outputs, list) else None,
    )


def cache_reference(root: Path, value: str) -> str | None:
    """Read a declared cache path, where spaces are expected rather than suspicious.

    Accept the Markdown angle-bracket form. Percent-decoding is a fallback that
    applies only when the decoded path names an existing directory, because
    "%" can occur in a real directory name.
    """
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
    if not value:
        return None
    decoded = unquote(value)
    if decoded != value:
        literal = safe_relative(root, value.rstrip("/"))
        candidate = safe_relative(root, decoded.rstrip("/"))
        if not (literal is not None and literal.is_dir()) and candidate is not None and candidate.is_dir():
            return decoded
    return value


def clean_reference(value: str) -> str | None:
    value = value.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
    elif " " in value or "\t" in value:
        # Markdown destinations with spaces require angle brackets. For prose
        # code spans, whitespace is more likely a command or example.
        return None
    value = unquote(value).split("#", 1)[0].split("?", 1)[0]
    value = re.sub(r":\d+(?::\d+)?$", "", value)
    if (not value or value.startswith(("/", "~", "#", "--")) or "://" in value
            or any(char in value for char in "*{}$|;<>")):
        return None
    return value


def looks_like_backtick_path(value: str) -> bool:
    cleaned = clean_reference(value)
    if cleaned is None:
        return False
    candidate = Path(cleaned)
    if candidate.parts and candidate.parts[0] in EXCLUDE:
        return False
    if cleaned.startswith(("./", "../")):
        return True
    # Bare filenames and directory conventions are frequently illustrative.
    # Require a file-shaped path with a directory component before calling a
    # prose code span a broken-path candidate.
    return "/" in cleaned and candidate.suffix.casefold() in KNOWN_PATH_SUFFIXES


def path_exists(root: Path, source: Path, value: str, *, backtick: bool) -> bool | None:
    cleaned = clean_reference(value)
    if cleaned is None:
        return None
    if backtick:
        bases = []
        base = source.parent
        while base.is_relative_to(root.resolve()):
            bases.append(base)
            if base == root.resolve():
                break
            base = base.parent
    else:
        bases = [source.parent]
    inside = [path for base in bases
              if (path := safe_relative(root, (base / cleaned).relative_to(root).as_posix())) is not None]
    if not inside:
        return None
    return any(candidate.exists() for candidate in inside)


def broken_references(root: Path, files: list[Path]) -> list[dict]:
    findings = []
    known_paths = {path.relative_to(root).as_posix() for path in files}
    link_pattern = re.compile(r"!?\[[^]]*\]\(([^)\n]+)\)")
    code_pattern = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
    for path in files:
        if path.suffix.casefold() not in TEXT_ROLE_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for number, line in unfenced_lines(text):
            occupied = []
            for match in link_pattern.finditer(line):
                occupied.append(match.span())
                value = match.group(1)
                exists = path_exists(root, path, value, backtick=False)
                if exists is False:
                    findings.append({
                        "source": path.relative_to(root).as_posix(), "line": number,
                        "reference": value.strip(), "kind": "markdown-link",
                        "confidence": "high",
                    })
            for match in code_pattern.finditer(line):
                if any(start <= match.start() < end for start, end in occupied):
                    continue
                value = match.group(1)
                if not looks_like_backtick_path(value):
                    continue
                exists = path_exists(root, path, value, backtick=True)
                cleaned = clean_reference(value)
                if (exists is False and cleaned is not None
                        and any(item == cleaned or item.endswith("/" + cleaned) for item in known_paths)):
                    # Backtick paths do not have Markdown's fixed resolution
                    # semantics. If a unique-looking suffix exists elsewhere,
                    # avoid calling the prose reference broken.
                    exists = True
                if exists is False:
                    findings.append({
                        "source": path.relative_to(root).as_posix(), "line": number,
                        "reference": value.strip(), "kind": "backtick-path",
                        "confidence": "candidate",
                    })
    return findings


def claude_bridge(root: Path, skipped: set[str]) -> dict:
    agents = root / "AGENTS.md"
    claude = root / "CLAUDE.md"
    imports = False
    agents_exists = "AGENTS.md" not in skipped and agents.is_file()
    claude_exists = "CLAUDE.md" not in skipped and claude.is_file()
    if claude_exists:
        try:
            imports = bool(re.search(r"(?m)^\s*@AGENTS\.md\s*$", claude.read_text(encoding="utf-8")))
        except (OSError, UnicodeError):
            imports = False
    issue = None
    if skipped.intersection({"AGENTS.md", "CLAUDE.md"}):
        issue = "Root instruction outside the inspection boundary or symlinked; bridge unverified"
    elif agents_exists and claude_exists and not imports:
        issue = "CLAUDE.md does not import @AGENTS.md"
    return {
        "agents_exists": agents_exists, "claude_exists": claude_exists,
        "imports_agents": imports, "issue": issue,
    }


def inspect(root: Path, depth: int, cache_dirs: tuple[str, ...] = ()) -> dict:
    root = root.resolve()
    requested = set()
    for value in cache_dirs:
        path = safe_relative(root, value)
        if path is None or path == root:
            raise ValueError(f"Cache directory must resolve inside the scan root: {value}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Designated cache is not a directory: {value}")
        requested.add(path)
    direct_paths = ("AGENTS.md", "CLAUDE.md", ".mathbox/config.json")
    skipped = {name for name in direct_paths
               if read_refusal(root, root / name, requested, walk_rules=False)}
    declarations = instruction_declarations(root, skipped)
    rejected_caches = root_cache_declarations(root, declarations)
    declared_caches = {
        path for item in declarations if item["role"] == "source_cache"
        for path in [safe_relative(root, item["path"])] if path not in (None, root)
    }
    config = root / ".mathbox" / "config.json"
    if any(config.is_relative_to(cache) for cache in declared_caches):
        skipped.add(".mathbox/config.json")
    if ".mathbox/config.json" not in skipped:
        config_found = config_declarations(root)
        declarations += config_found
        rejected_caches += root_cache_declarations(root, config_found)
    declarations = unique_declarations(declarations)
    caches = source_cache_conventions(root, declarations, requested)
    cache_exclusions = {
        path for item in caches
        if item["declared"] or item["confidence"] == "high"
        for path in [safe_relative(root, item["path"])] if path is not None
    }
    files = list(walk(root, depth, cache_exclusions))
    instructions = []
    role_entries = []
    role_map: dict[str, list[dict]] = {}
    skills = []
    misplaced = []
    build_manifests = []
    computation_manifests = []
    project_maps = []
    research_logs = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        name = path.name
        if name in {"AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md"} or "/.claude/rules/" in "/" + rel:
            instructions.append(info(root, path))
        roles = semantic_roles(path)
        if roles:
            entry = dict(info(root, path), roles=roles)
            role_entries.append(entry)
            for role in roles:
                role_map.setdefault(role, []).append(info(root, path))
            if "research_log" in roles:
                research_logs.append(dict(info(root, path), **classify_research_log(path)))
            if "project_map" in roles:
                project_maps.append(dict(info(root, path), basis="filename"))
        if name == "SKILL.md":
            entry = info(root, path)
            parts = path.relative_to(root).parts
            if (".agents" in parts and "skills" in parts) or (".claude" in parts and "skills" in parts):
                skills.append(entry)
            elif len(parts) >= 3 and parts[0] == "skills":
                misplaced.append(entry)
        if name in {"Makefile", "justfile", "Justfile", "pyproject.toml", "package.json", "latexmkrc", ".latexmkrc"}:
            build_manifests.append(info(root, path))
        manifest = computation_manifest(root, path)
        if manifest is not None:
            computation_manifests.append(manifest)
    known_map_paths = {entry["path"] for entry in project_maps}
    for declaration in declarations:
        if declaration["role"] != "project_map" or declaration["path"] in known_map_paths:
            continue
        candidate = root / declaration["path"]
        basis = f"declared in {declaration['source']}"
        refusal = read_refusal(root, candidate, cache_exclusions, walk_rules=True)
        if refusal is None and candidate.is_file():
            project_maps.append(dict(info(root, candidate), basis=basis))
            continue
        project_maps.append({
            "path": declaration["path"], "bytes": -1, "lines": None,
            "basis": f"{basis}; not inspected: {refusal}" if refusal else f"{basis}; missing",
        })
    local_names = []
    for entry in skills:
        parts = Path(entry["path"]).parts
        try:
            index = parts.index("skills")
            local_names.append(parts[index + 1])
        except (ValueError, IndexError):
            pass
    duplicates = sorted(CANONICAL.intersection(local_names))

    def live_candidates(role: str) -> list[str]:
        return sorted({
            item["path"] for item in role_map.get(role, [])
            if not located_in(Path(item["path"]), NON_LIVE_PARTS, NON_LIVE_TOKENS)
        })

    dashboard = live_candidates("status")
    handoff = live_candidates("handoff")
    live_state = {
        "dashboard_candidates": dashboard,
        "handoff_candidates": handoff,
        "duplicate_dashboard_candidates": len(dashboard) > 1,
        "duplicate_handoff_candidates": len(handoff) > 1,
        "multiple_live_state_candidates": len(dashboard) > 1 or len(handoff) > 1,
        "summary_sizes": [dict(info(root, root / path),
                               checkpoint_markers=checkpoint_markers(root / path))
                          for path in sorted(set(dashboard + handoff))],
    }
    cache_paths = tuple(sorted(path.relative_to(root).as_posix() for path in cache_exclusions))
    git_info = git_state(root, cache_paths)
    git_info["status_excludes"] = list(cache_paths)
    standard = ".research-cache/literature"
    literature_cache = {"path": standard, "exists": False, **unverified_coverage()}
    checked = [cache for cache in caches if cache["confidence"] == "high"]
    coverage = (cache_ignore_coverage(root, [cache["path"] for cache in checked])
                if git_info["repository"] else {})
    for cache in checked:
        result = coverage.get(cache["path"], unverified_coverage())
        cache.update(result)
        if cache["path"] == standard:
            literature_cache = {"path": standard, "exists": cache["exists"], **result}
    config_skipped = ".mathbox/config.json" in skipped
    ledger_exists = None if config_skipped else (root / ".mathbox/config.json").is_file()
    return {
        "root": str(root),
        "max_depth": depth,
        "skipped_direct_paths": sorted(skipped),
        "git": git_info,
        # Backward-compatible field: empty string means clean; None means unavailable.
        "git_status": git_info["porcelain"],
        "instructions": instructions,
        "claude_bridge": claude_bridge(root, skipped),
        "research_role_files": role_entries,
        "semantic_roles": {key: sorted(value, key=lambda item: item["path"]) for key, value in sorted(role_map.items())},
        "live_state_candidates": live_state,
        "research_logs": sorted(research_logs, key=lambda item: item["path"]),
        "declared_paths": declarations,
        "project_maps": sorted(project_maps, key=lambda item: item["path"]),
        "computation_manifests": sorted(computation_manifests, key=lambda item: item["path"]),
        "broken_path_references": broken_references(root, files),
        "skill_files": skills,
        "misplaced_root_skills": misplaced,
        "canonical_name_overrides": duplicates,
        "build_manifests": build_manifests,
        "literature_cache": literature_cache,
        "source_cache_conventions": caches,
        "rejected_cache_declarations": rejected_caches,
        "research_ledger": {"path": ".mathbox", "exists": ledger_exists,
                            "status": "unverified" if config_skipped else "present" if ledger_exists else "absent"},
    }


def cache_status(cache: dict) -> str:
    if cache["repository_ignore_rule"]:
        status = f"directory covered by tracked rule in `{cache['ignore_rule_source']}`"
    elif cache["git_ignored"] is None:
        status = "Git ignore coverage unverified"
    elif cache["git_ignored"]:
        status = f"directory ignored by `{cache['ignore_rule_source']}`; tracked project coverage unverified"
    else:
        status = "no directory-wide Git ignore coverage verified"
    if cache.get("coverage_note"):
        status += f" ({cache['coverage_note']})"
    if cache["tracked_entries"]:
        status += f"; already tracked index entries: {cache['tracked_entries']}"
    return status


def rejected_cache_lines(obj: dict) -> list[str]:
    return [f"Rejected source-cache declaration `{item['path']}` "
            f"({item['source']}{':' + str(item['line']) if item['line'] else ''}): "
            f"{item['reason']}; not excluded from inspection or Git status."
            for item in obj["rejected_cache_declarations"]]


def markdown(obj: dict) -> str:
    lines = [f"# Repository inspection: `{obj['root']}`", ""]
    git_info = obj["git"]
    if git_info["state"] == "clean":
        display = "(clean within inspected paths)"
    elif git_info["state"] == "dirty":
        display = git_info["porcelain"]
    else:
        display = f"({git_info['state']}: {git_info['reason']})"
    lines += ["## Git status", "", "```text", display, "```", ""]
    if git_info["repository"] and git_info["status_excludes"]:
        lines.append("Git status excludes source caches: " + ", ".join(git_info["status_excludes"]))
    if obj["skipped_direct_paths"]:
        lines.append("Skipped symlinked or excluded paths: " + ", ".join(obj["skipped_direct_paths"]))
    for key, title in [
        ("instructions", "Instruction files"),
        ("research_role_files", "Research role files and aliases"),
        ("computation_manifests", "Computation manifests"),
        ("project_maps", "Project/path maps"),
        ("skill_files", "Recognized project skills"),
        ("misplaced_root_skills", "Misplaced root skills"),
        ("build_manifests", "Build/verification manifests"),
    ]:
        lines += [f"## {title}", ""]
        items = obj[key]
        if not items:
            lines.append("- None found within scan depth.")
        else:
            lines.extend(f"- `{item['path']}` — {item['lines']} lines, {item['bytes']} bytes"
                         + (f"; {item['basis']}" if "basis" in item else "") for item in items)
        lines.append("")
    lines += ["## Semantic roles and computation classifications", "", "```json",
              json.dumps({"semantic_roles": obj["semantic_roles"],
                          "computation_manifests": obj["computation_manifests"]}, indent=2), "```", ""]
    bridge = obj["claude_bridge"]
    if bridge["issue"]:
        claude_status = bridge["issue"]
    elif bridge["agents_exists"] and not bridge["claude_exists"]:
        claude_status = "Root AGENTS.md can load directly in supported Claude Code sessions."
    elif bridge["imports_agents"]:
        claude_status = "Root CLAUDE.md imports AGENTS.md."
    else:
        claude_status = "No conflicting root instruction files detected."
    lines += ["## Claude instructions", "", claude_status, ""]
    live = obj["live_state_candidates"]
    lines += ["## Live dashboard/handoff candidates", ""]
    lines.append("Dashboards: " + (", ".join(f"`{path}`" for path in live["dashboard_candidates"]) or "none"))
    lines.append("Handoffs: " + (", ".join(f"`{path}`" for path in live["handoff_candidates"]) or "none"))
    if live["duplicate_dashboard_candidates"] or live["duplicate_handoff_candidates"]:
        lines.append("Potential duplicate candidates require authority review; filenames alone do not establish duplication.")
    for item in live["summary_sizes"]:
        lines.append(f"`{item['path']}` — {item['lines']} lines, {item['bytes']} bytes; "
                     f"{item['checkpoint_markers']} dated/previous checkpoint marker(s), tentative.")
    lines.append("")
    lines += ["## Research-log classification", ""]
    if obj["research_logs"]:
        lines.extend(f"- `{item['path']}` — {item['classification']}" for item in obj["research_logs"])
    else:
        lines.append("- No research log found within scan depth.")
    lines.append("")
    lines += ["## Broken relative path candidates", ""]
    if obj["broken_path_references"]:
        lines.extend(
            f"- `{item['source']}:{item['line']}` — {item['kind']} `{item['reference']}` ({item['confidence']})"
            for item in obj["broken_path_references"]
        )
    else:
        lines.append("- None detected conservatively.")
    lines.append("")
    lines += ["## Canonical-name project overrides", ""]
    lines.append(", ".join(f"`{name}`" for name in obj["canonical_name_overrides"]) or "None.")
    lines.append("")
    cache = obj["literature_cache"]
    lines += ["## Local literature cache", ""]
    lines.append(f"`{cache['path']}` — {'present' if cache['exists'] else 'not found'}; {cache_status(cache)}")
    alternates = [item for item in obj["source_cache_conventions"] if item["path"] != cache["path"]]
    for item in alternates:
        coverage = cache_status(item) if "git_ignored" in item else "tentative candidate"
        lines.append(f"`{item['path']}` — {item['basis']}; {coverage}")
    lines.extend(rejected_cache_lines(obj))
    lines.append("")
    ledger = obj["research_ledger"]
    ledger_detail = {"present": "present; use research-state for integrity and freshness checks",
                     "absent": "not found; optional", "unverified": "unverified; metadata inspection skipped"}
    lines += ["## Research ledger", "", f"`{ledger['path']}` — {ledger_detail[ledger['status']]}", ""]
    lines += ["", "Declared paths and source-cache conventions:",
              "```json", json.dumps({"declared_paths": obj["declared_paths"],
                                      "source_cache_conventions": obj["source_cache_conventions"]}, indent=2),
              "```"]
    return "\n".join(lines)


def brief_markdown(obj: dict) -> str:
    """Bound the inspection shown to an agent while retaining full JSON/Markdown."""
    lines = [f"# Repository inspection: `{obj['root']}`", ""]
    git_info = obj["git"]
    lines.append(f"Git: {git_info['state']}.")
    if git_info["repository"] and git_info["status_excludes"]:
        lines.append("Git status excludes source caches (see source-cache conventions).")
    if git_info["state"] == "dirty":
        changed = git_info["porcelain"].splitlines()
        lines.extend(f"- {entry}" for entry in changed[:8])
        if len(changed) > 8:
            lines.append(f"- … {len(changed) - 8} more worktree entries.")
    elif git_info["reason"]:
        lines.append(f"Git detail: {git_info['reason']}.")
    if obj["skipped_direct_paths"]:
        lines.append("Skipped symlinked or excluded paths: " + ", ".join(obj["skipped_direct_paths"]))

    absent = []

    def items(title: str, entries: list[dict], limit: int = 8, detail: str | None = None) -> None:
        if not entries:
            absent.append(title.lower())
            return
        lines.extend(["", f"## {title} ({len(entries)})", ""])
        for entry in entries[:limit]:
            size = f"{entry.get('lines', '?')} lines, {entry.get('bytes', '?')} bytes"
            lines.append(f"- `{entry['path']}` — " + (f"{entry[detail]}; {size}" if detail else size))
        if len(entries) > limit:
            lines.append(f"- … {len(entries) - limit} more; use --full or --format json.")

    items("Instructions", obj["instructions"])
    live = obj["live_state_candidates"]
    lines.extend(["", "## Live state candidates", "",
                  "Dashboards: " + (", ".join(live["dashboard_candidates"][:8]) or "none"),
                  "Handoffs: " + (", ".join(live["handoff_candidates"][:8]) or "none")])
    for label, values in (("dashboards", live["dashboard_candidates"]),
                          ("handoffs", live["handoff_candidates"])):
        if len(values) > 8:
            lines.append(f"… {len(values) - 8} more {label}; use --full or --format json.")
    if live["multiple_live_state_candidates"]:
        lines.append("Multiple candidates require authority review.")
    for item in live["summary_sizes"][:8]:
        lines.append(f"`{item['path']}` — {item['lines']} lines, {item['bytes']} bytes; "
                     f"{item['checkpoint_markers']} dated/previous checkpoint marker(s), tentative.")
    if len(live["summary_sizes"]) > 8:
        lines.append(f"… {len(live['summary_sizes']) - 8} more live-file sizes; use --full or --format json.")
    items("Research role files", obj["research_role_files"])
    items("Computation manifests", obj["computation_manifests"], detail="classification")
    items("Research logs", obj["research_logs"], detail="classification")
    items("Project maps", obj["project_maps"], detail="basis")
    items("Project skill files", obj["skill_files"])
    items("Misplaced root skills", obj["misplaced_root_skills"])
    if obj["misplaced_root_skills"]:
        lines.append("Root `skills/` is not a project skill location; review these before setup.")
    items("Build/verification manifests", obj["build_manifests"])
    if absent:
        lines.extend(["", "None found within scan depth: " + ", ".join(absent) + "."])
    bridge = obj["claude_bridge"]
    if bridge["issue"]:
        lines.extend(["", f"Claude bridge: {bridge['issue']}."])
    if obj["canonical_name_overrides"]:
        lines.append("Canonical skill overrides: " + ", ".join(obj["canonical_name_overrides"][:8]))

    broken = obj["broken_path_references"]
    live_broken = [entry for entry in broken
                   if not located_in(Path(entry["source"]), HISTORICAL_PARTS, HISTORICAL_TOKENS)]
    historical = len(broken) - len(live_broken)
    lines.extend(["", f"## Broken path candidates ({len(broken)})", "",
                  f"Current-path candidates: {len(live_broken)}; historical-path candidates: {historical}."])
    for entry in live_broken[:8]:
        lines.append(f"- `{entry['source']}:{entry['line']}` — {entry['kind']} `{entry['reference']}` ({entry['confidence']})")
    if len(live_broken) > 8:
        lines.append(f"- … {len(live_broken) - 8} more current-path candidates; use --full or --format json.")
    if historical:
        lines.append("Historical candidates are preserved in the full report; their location does not prove a live link is broken.")
    cache = obj["literature_cache"]
    lines.extend(["", f"Literature cache: `{cache['path']}`; "
                  f"{'present' if cache['exists'] else 'absent'}; "
                  f"{cache_status(cache)}.",
                  *rejected_cache_lines(obj),
                  f"Research ledger: {obj['research_ledger']['status']}.",
                  f"Use --full or --format json for all findings at scan depth {obj['max_depth']}."])
    for key, title in (("declared_paths", "Declared paths"),
                       ("source_cache_conventions", "Source-cache conventions")):
        entries = obj[key]
        lines += ["", f"{title}: {len(entries)}."]
        for item in entries[:8]:
            label = item.get("role", item.get("basis", "candidate"))
            coverage = f" — {cache_status(item)}" if "git_ignored" in item else ""
            lines.append(f"- {label}: `{item['path']}`{coverage}")
        if len(entries) > 8:
            lines.append(f"- … {len(entries) - 8} more; inspect --full or --format json before decisions.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="scan root; resolves to Git top level when available (default: current directory)")
    parser.add_argument("--max-depth", type=int, default=5, help="maximum directory scan depth (default: %(default)s)")
    parser.add_argument("--cache-dir", action="append", default=[], help="exclude a designated cache relative to the scan root (repeatable)")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--full", action="store_true", help="all Markdown findings at the selected depth")
    arguments = parser.parse_args()
    try:
        obj = inspect(root_of(Path(arguments.root)), arguments.max_depth, tuple(arguments.cache_dir))
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(obj, indent=2) if arguments.format == "json" else
          markdown(obj) if arguments.full else brief_markdown(obj))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
