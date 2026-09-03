#!/usr/bin/env python3
"""Manage a project-local, Git-ignored cache of mathematical sources.

Exit status: 0 success; 1 the cache is invalid (``verify`` only); 2 a usage or
cache error; 3 an unexpected internal failure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

CACHE_ROOT = Path(".research-cache")
CACHE_RELATIVE = CACHE_ROOT / "literature"
SCHEMA_VERSION = 1
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARXIV_VERSION_RE = re.compile(r"^(.*?)(v\d+)?$", re.IGNORECASE)
IGNORE_PROBE = "0" * 64

EXIT_OK = 0
EXIT_INVALID = 1
EXIT_ERROR = 2
EXIT_INTERNAL = 3


class CacheError(RuntimeError):
    """A safe, user-facing cache failure."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def utc_today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def readable_digest(path: Path) -> str | None:
    try:
        return sha256_file(path)
    except OSError:
        return None


def atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    try:
        with os.fdopen(fd, "wb") as output, source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def atomic_json(data: dict, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2, ensure_ascii=False, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def git_toplevel(root: Path) -> Path | None:
    try:
        process = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return Path(process.stdout.strip()).resolve() if process.returncode == 0 else None


def git_ignore_source(root: Path, path: Path) -> str | None:
    """Return the ignore-rule file excluding path, or None if Git does not ignore it."""
    try:
        process = subprocess.run(
            ["git", "-C", str(root), "check-ignore", "-v", "--", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if process.returncode != 0:
        return None
    line = process.stdout.strip().splitlines()
    return line[0].split(":", 1)[0] if line else ""


def has_git_marker(root: Path) -> bool:
    return any((candidate / ".git").exists() for candidate in (root, *root.parents))


def cache_paths(root: Path) -> tuple[Path, Path]:
    root = root.expanduser().resolve()
    if not root.is_dir():
        raise CacheError(f"project root is not a directory: {root}")
    return root, root / CACHE_RELATIVE


def ignore_status(root: Path, cache: Path) -> dict:
    """Describe Git ignore coverage, separating the cache's own rule from the project's.

    `ignored` is the effective answer for cache content. `repository_rule` is true
    only when a rule outside the cache directory covers it, which is the durable
    invariant a project is expected to track in its own `.gitignore`.
    """
    git_root = git_toplevel(root)
    if git_root is None:
        if has_git_marker(root):
            return {
                "git_repository": True, "verified": False, "ignored": False,
                "rule_source": None, "repository_rule": False,
            }
        return {
            "git_repository": False, "verified": True, "ignored": True,
            "rule_source": None, "repository_rule": False,
        }

    cache_root = cache.parent
    try:
        relative_root = cache_root.relative_to(git_root).as_posix()
    except ValueError as error:
        raise CacheError("cache directory is outside the containing Git repository") from error

    # A `.gitignore` never applies to its own directory, so a match on the cache
    # root can only come from a rule the project itself supplied.
    directory_source = git_ignore_source(git_root, cache_root)
    content_source = git_ignore_source(git_root, cache / "pdf" / f"{IGNORE_PROBE}.pdf")
    external = content_source is not None and not content_source.startswith(f"{relative_root}/")
    return {
        "git_repository": True,
        "verified": True,
        "ignored": content_source is not None,
        "rule_source": content_source,
        "repository_rule": bool(directory_source) or external,
    }


def ignore_fields(status: dict) -> dict:
    """Reporting fields shared by every command."""
    fields = {
        "git_ignored": status["ignored"],
        "git_ignore_source": status["rule_source"],
        "git_ignore_repository_rule": status["repository_rule"],
    }
    if status["git_repository"] and status["ignored"] and not status["repository_rule"]:
        fields["warnings"] = [
            f"the cache is ignored only by its own {CACHE_ROOT.as_posix()}/.gitignore; "
            f"add /{CACHE_ROOT.name}/ to the repository .gitignore"
        ]
    return fields


def assert_ignored(root: Path, destination: Path) -> None:
    """Refuse to write a cache artifact Git would track, including one already indexed."""
    git_root = git_toplevel(root)
    if git_root is None:
        return
    if git_ignore_source(git_root, destination) is None:
        raise CacheError(
            f"refusing to write {destination} because Git does not ignore it; "
            f"add /{CACHE_ROOT.name}/ to the repository .gitignore and untrack "
            "any cached artifact already in the index"
        )


def initialize(root: Path) -> tuple[Path, dict]:
    """Create the cache. Only `init` and `add` may call this."""
    root, cache = cache_paths(root)
    cache.parent.mkdir(parents=True, exist_ok=True)
    ignore_file = cache.parent / ".gitignore"
    if not ignore_file.exists():
        ignore_file.write_text("*\n", encoding="utf-8")
    cache.mkdir(parents=True, exist_ok=True)

    status = ignore_status(root, cache)
    if not status["verified"]:
        raise CacheError("cannot verify Git ignore coverage for the literature cache")
    if status["git_repository"] and not status["ignored"]:
        raise CacheError(
            f"refusing to store sources because Git does not ignore {cache}; "
            f"add /{CACHE_ROOT.name}/ to the repository .gitignore"
        )
    for name in ("pdf", "text", "records"):
        (cache / name).mkdir(exist_ok=True)
    return cache, status


def open_cache(root: Path) -> tuple[Path, dict, bool]:
    """Locate an existing cache without creating or writing anything."""
    root, cache = cache_paths(root)
    return cache, ignore_status(root, cache), (cache / "records").is_dir()


def normalize_identifier(raw: str) -> str:
    value = raw.strip()
    if not value or ":" not in value:
        raise CacheError(f"identifier must have the form scheme:value: {raw!r}")
    scheme, body = value.split(":", 1)
    scheme = scheme.strip().lower()
    body = body.strip()
    if not scheme or not body:
        raise CacheError(f"identifier must have the form scheme:value: {raw!r}")

    if scheme == "doi":
        body = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", body, flags=re.I)
        body = body.lower()
    elif scheme == "arxiv":
        body = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/", "", body, flags=re.I)
        body = re.sub(r"\.pdf$", "", body, flags=re.I).lower()
    elif scheme == "isbn":
        body = re.sub(r"[\s-]", "", body).upper()
    elif scheme == "url":
        parsed = urlsplit(body)
        if parsed.scheme and parsed.netloc:
            body = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path, parsed.query, ""))
    return f"{scheme}:{body}"


def arxiv_base(identifier: str) -> str | None:
    if not identifier.startswith("arxiv:"):
        return None
    match = ARXIV_VERSION_RE.fullmatch(identifier.removeprefix("arxiv:"))
    return match.group(1).lower() if match else None


def read_record(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CacheError(f"cannot read cache record {path}: {error}") from error
    if not isinstance(data, dict):
        raise CacheError(f"cache record is not a JSON object: {path}")
    return data


def load_records(cache: Path) -> tuple[list[dict], list[dict]]:
    """Read every record, isolating the unreadable ones instead of failing the query."""
    loaded: list[dict] = []
    unreadable: list[dict] = []
    for path in sorted((cache / "records").glob("*.json")):
        try:
            loaded.append(read_record(path))
        except CacheError as error:
            unreadable.append({"record": path.name, "issue": str(error)})
    return loaded, unreadable


def artifact_path(cache: Path, value: object, directory: str, filename: str | None = None) -> Path:
    if not isinstance(value, str):
        raise CacheError(f"invalid {directory} artifact path in cache record")
    path = (cache / value).resolve()
    expected_parent = (cache / directory).resolve()
    if path.parent != expected_parent or (filename is not None and path.name != filename):
        raise CacheError(f"unsafe {directory} artifact path in cache record: {value!r}")
    return path


def entry_path(cache: Path, entry: object, directory: str, filename: str) -> Path:
    if not isinstance(entry, dict):
        raise CacheError(f"invalid {directory} entry in cache record")
    return artifact_path(cache, entry.get("path"), directory, filename)


def pdf_is_plausible(path: Path) -> bool:
    try:
        with path.open("rb") as stream:
            return b"%PDF-" in stream.read(1024)
    except OSError:
        return False


def command_version(executable: str) -> str | None:
    try:
        process = subprocess.run(
            [executable, "-v"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    output = process.stdout.strip().splitlines()
    return output[0][:300] if output else None


def extract_text(
    pdf: Path, supplied_text: Path | None, disabled: bool, supplied_tool: str | None = None
) -> tuple[Path | None, dict]:
    if supplied_text is not None:
        supplied_text = supplied_text.expanduser().resolve()
        if not supplied_text.is_file():
            raise CacheError(f"supplied text is not a file: {supplied_text}")
        return supplied_text, {
            "status": "available", "tool": supplied_tool or "supplied", "command": None,
        }
    if disabled:
        return None, {"status": "not-requested", "tool": None, "command": None}

    executable = shutil.which("pdftotext")
    if executable is None:
        return None, {"status": "unavailable", "tool": "pdftotext", "command": ["pdftotext", "-layout"]}
    temporary = tempfile.NamedTemporaryFile(prefix="literature-cache-", suffix=".txt", delete=False)
    temporary.close()
    target = Path(temporary.name)
    try:
        process = subprocess.run(
            [executable, "-layout", str(pdf), str(target)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300,
            check=False,
        )
        success = process.returncode == 0 and target.is_file()
        provenance = {
            "status": "available" if success else "failed",
            "tool": "pdftotext",
            "tool_version": command_version(executable),
            "command": ["pdftotext", "-layout", "<pdf>", "<text>"],
        }
        if not success:
            provenance["error"] = (
                process.stderr.strip() or f"exit status {process.returncode}; no text produced"
            )[:500]
            target.unlink(missing_ok=True)
            return None, provenance
        return target, provenance
    except (OSError, subprocess.TimeoutExpired) as error:
        target.unlink(missing_ok=True)
        return None, {
            "status": "failed", "tool": "pdftotext",
            "command": ["pdftotext", "-layout", "<pdf>", "<text>"],
            "error": str(error)[:500],
        }


def merge_scalar(record: dict, key: str, new_value: str | None, replace: bool = False) -> None:
    if not new_value:
        return
    old_value = record.get(key)
    if old_value and old_value != new_value and not replace:
        raise CacheError(
            f"same PDF has conflicting {key}: {old_value!r} versus {new_value!r}; "
            "pass --replace-metadata to overwrite the stored value"
        )
    record[key] = new_value


def ingest(args: argparse.Namespace) -> dict:
    if args.text_tool and not args.text:
        raise CacheError("--text-tool requires --text")

    root = Path(args.root)
    cache, status = initialize(root)
    pdf = Path(args.pdf).expanduser().resolve()
    if not pdf.is_file():
        raise CacheError(f"PDF is not a file: {pdf}")
    if not pdf_is_plausible(pdf):
        raise CacheError(f"file does not appear to be a PDF: {pdf}")

    identifiers = sorted({normalize_identifier(item) for item in args.identifier})
    digest = sha256_file(pdf)
    record_path = cache / "records" / f"{digest}.json"
    destination_pdf = cache / "pdf" / f"{digest}.pdf"
    destination_text = cache / "text" / f"{digest}.txt"
    existed = record_path.exists()
    if existed:
        record = read_record(record_path)
    else:
        record = {
            "schema_version": SCHEMA_VERSION,
            "sha256": digest,
            "identifiers": [],
            "authors": [],
            "locators": [],
            "created_at": utc_now(),
        }

    record["identifiers"] = sorted(set(record.get("identifiers", [])) | set(identifiers))
    record["authors"] = list(dict.fromkeys(record.get("authors", []) + (args.author or [])))
    record["locators"] = list(dict.fromkeys(record.get("locators", []) + (args.source_url or [])))
    merge_scalar(record, "title", args.title, args.replace_metadata)
    merge_scalar(record, "version", args.version, args.replace_metadata)
    prior_bases = record.pop("retention_basis", None)
    bases = record.get("retention_bases", [])
    if prior_bases:
        bases.append(prior_bases)
    record["retention_bases"] = list(dict.fromkeys(bases + [args.retention_basis]))
    record["date_checked"] = args.date_checked or utc_today()

    assert_ignored(root, destination_pdf)
    if not destination_pdf.exists():
        atomic_copy(pdf, destination_pdf)
    elif sha256_file(destination_pdf) != digest:
        raise CacheError(f"cached PDF has unexpected content: {destination_pdf}")
    record["pdf"] = {"path": str(destination_pdf.relative_to(cache)), "sha256": digest}

    temporary_extraction = False
    text_source: Path | None = None
    provenance: dict
    existing_text = record.get("text")
    if existing_text and not args.text:
        text_source = None
        provenance = record.get("extraction", {"status": "available"})
    else:
        text_source, provenance = extract_text(
            pdf, Path(args.text) if args.text else None, args.no_extract, args.text_tool
        )
        temporary_extraction = (
            text_source is not None and provenance.get("command") is not None
            and provenance.get("tool") == "pdftotext"
        )

    try:
        if text_source is not None:
            assert_ignored(root, destination_text)
            text_digest = sha256_file(text_source)
            atomic_copy(text_source, destination_text)
            record["text"] = {
                "path": str(destination_text.relative_to(cache)),
                "sha256": text_digest,
            }
        record["extraction"] = provenance
        record["updated_at"] = utc_now()
        atomic_json(record, record_path)
    finally:
        if temporary_extraction and text_source is not None:
            text_source.unlink(missing_ok=True)

    return {
        "action": "updated" if existed else "added",
        "cache": str(cache),
        **ignore_fields(status),
        "record": record,
    }


def record_summary(record: dict, cache: Path, match: str | None = None, snippet: str | None = None) -> dict:
    """Summarize one record without letting a malformed field abort the whole query."""
    digest = record.get("sha256")
    extraction = record.get("extraction")
    summary = {
        "sha256": digest,
        "title": record.get("title"),
        "authors": record.get("authors", []),
        "identifiers": record.get("identifiers", []),
        "version": record.get("version"),
        "pdf_path": None,
        "text_path": None,
        "extraction_status": extraction.get("status") if isinstance(extraction, dict) else None,
    }
    issues: list[str] = []
    for key, suffix in (("pdf", "pdf"), ("text", "txt")):
        if record.get(key) is None:
            continue
        try:
            summary[f"{key}_path"] = str(entry_path(cache, record[key], key, f"{digest}.{suffix}"))
        except CacheError as error:
            issues.append(str(error))
    if issues:
        summary["issues"] = issues
    if match:
        summary["match"] = match
    if snippet:
        summary["snippet"] = snippet
    return summary


def bounded_snippet(text: str, query: str, width: int = 240) -> str | None:
    """Return a bounded window that always shows the match, eliding a long one."""
    position = text.casefold().find(query.casefold())
    if position < 0:
        return None
    context = width // 3
    start = max(0, position - context)
    end = min(len(text), position + len(query) + context)
    snippet = " ".join(text[start:end].split())
    if len(snippet) > width:
        head = width // 2
        snippet = f"{snippet[:head].rstrip()} … {snippet[-(width - head - 3):].lstrip()}"
    return ("…" if start else "") + snippet + ("…" if end < len(text) else "")


def searchable_metadata(record: dict) -> str:
    values = [record.get("title"), record.get("version")]
    for key in ("authors", "identifiers", "locators"):
        value = record.get(key)
        if isinstance(value, list):
            values.extend(value)
    return "\n".join(value for value in values if isinstance(value, str))


def find_records(args: argparse.Namespace) -> dict:
    cache, status, present = open_cache(Path(args.root))
    result = {"cache": str(cache), "cache_present": present, **ignore_fields(status)}
    if not present:
        result.update({"count": 0, "matches": [], "unreadable_records": []})
        return result

    all_records, unreadable = load_records(cache)
    matches: list[dict] = []
    if args.identifier:
        wanted = normalize_identifier(args.identifier)
        wanted_base = arxiv_base(wanted)
        for record in all_records:
            identifiers = record.get("identifiers")
            if not isinstance(identifiers, list):
                continue
            if wanted in identifiers:
                matches.append(record_summary(record, cache, "exact-identifier"))
            elif wanted_base and any(
                arxiv_base(item) == wanted_base for item in identifiers if isinstance(item, str)
            ):
                matches.append(record_summary(record, cache, "arxiv-version-candidate"))
            if len(matches) >= args.limit:
                break
    else:
        query = args.query.strip()
        if not query:
            raise CacheError("search query must not be empty")
        for record in all_records:
            metadata = searchable_metadata(record)
            match = "metadata" if query.casefold() in metadata.casefold() else None
            snippet = bounded_snippet(metadata, query) if match else None
            if not match and record.get("text") is not None:
                try:
                    text_path = entry_path(
                        cache, record["text"], "text", f"{record.get('sha256')}.txt"
                    )
                    text_value = text_path.read_text(encoding="utf-8", errors="replace")
                except (OSError, CacheError):
                    text_value = None
                if text_value is not None:
                    snippet = bounded_snippet(text_value, query)
                    match = "text" if snippet else None
            if match:
                matches.append(record_summary(record, cache, match, snippet))
            if len(matches) >= args.limit:
                break

    result.update({"count": len(matches), "matches": matches, "unreadable_records": unreadable})
    return result


def resolve_digest(cache: Path, value: str) -> Path:
    value = value.lower()
    if not re.fullmatch(r"[0-9a-f]{8,64}", value):
        raise CacheError("content hash must be 8 to 64 hexadecimal characters")
    candidates = sorted((cache / "records").glob(f"{value}*.json"))
    if not candidates:
        raise CacheError(f"no record matches content hash {value}")
    if len(candidates) > 1:
        raise CacheError(f"content hash prefix is ambiguous: {value}")
    return candidates[0]


def show_record(args: argparse.Namespace) -> dict:
    cache, status, present = open_cache(Path(args.root))
    if not present:
        raise CacheError(f"no literature cache at {cache}")
    record = read_record(resolve_digest(cache, args.sha256))
    return {"cache": str(cache), "cache_present": True, **ignore_fields(status), "record": record}


def verify_cache(args: argparse.Namespace) -> tuple[dict, bool]:
    cache, status, present = open_cache(Path(args.root))
    issues: list[dict] = []
    seen_pdf: set[str] = set()
    seen_text: set[str] = set()
    checked = 0

    for path in sorted((cache / "records").glob("*.json")) if present else []:
        checked += 1
        try:
            record = read_record(path)
        except CacheError as error:
            issues.append({"record": path.name, "issue": str(error)})
            continue

        digest = record.get("sha256")
        if record.get("schema_version") != SCHEMA_VERSION:
            issues.append({"record": path.name, "issue": "unsupported schema version"})
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest) or path.stem != digest:
            issues.append({"record": path.name, "issue": "invalid or mismatched content hash"})
            continue

        # Reserve the artifact names this record owns before validating its
        # metadata, so a malformed field never turns a live file into an orphan.
        seen_pdf.add(f"{digest}.pdf")
        pdf_entry = record.get("pdf")
        try:
            pdf_path = entry_path(cache, pdf_entry, "pdf", f"{digest}.pdf")
        except CacheError as error:
            issues.append({"record": path.name, "issue": str(error)})
        else:
            if not pdf_path.is_file():
                issues.append({"record": path.name, "issue": "missing PDF"})
            elif readable_digest(pdf_path) != digest:
                issues.append({"record": path.name, "issue": "PDF hash mismatch or unreadable"})

        text_entry = record.get("text")
        if text_entry is not None:
            seen_text.add(f"{digest}.txt")
            try:
                text_path = entry_path(cache, text_entry, "text", f"{digest}.txt")
            except CacheError as error:
                issues.append({"record": path.name, "issue": str(error)})
            else:
                if not text_path.is_file():
                    issues.append({"record": path.name, "issue": "missing extracted text"})
                elif readable_digest(text_path) != text_entry.get("sha256"):
                    issues.append(
                        {"record": path.name, "issue": "text hash mismatch or unreadable"}
                    )

    for directory, seen in (("pdf", seen_pdf), ("text", seen_text)):
        target = cache / directory
        if not target.is_dir():
            continue
        for path in sorted(target.iterdir()):
            if path.is_file() and path.name not in seen:
                issues.append({"path": str(path.relative_to(cache)), "issue": "orphaned artifact"})

    result = {
        "cache": str(cache), "cache_present": present, **ignore_fields(status),
        "records_checked": checked, "valid": not issues, "issues": issues,
    }
    return result, not issues


def init_result(args: argparse.Namespace) -> dict:
    cache, status = initialize(Path(args.root))
    return {
        "cache": str(cache), "cache_present": True, **ignore_fields(status),
        "schema_version": SCHEMA_VERSION,
    }


def print_warnings(result: dict) -> None:
    for warning in result.get("warnings", []):
        print(f"warning: {warning}", file=sys.stderr)


def print_human(result: dict) -> None:
    if "matches" in result:
        if not result.get("cache_present", True):
            print(f"no literature cache at {result['cache']}")
        print(f"{result['count']} match(es) in {result['cache']}")
        for item in result["matches"]:
            label = item.get("title") or item["sha256"]
            print(f"- {label} [{item.get('match', 'match')}] {item['sha256']}")
            if item.get("identifiers"):
                print(f"  identifiers: {', '.join(item['identifiers'])}")
            if item.get("snippet"):
                print(f"  {item['snippet']}")
            for issue in item.get("issues", []):
                print(f"  ! {issue}")
        for entry in result.get("unreadable_records", []):
            print(f"! skipped {entry['record']}: {entry['issue']}")
    elif "valid" in result:
        print(f"checked {result['records_checked']} record(s): {'valid' if result['valid'] else 'invalid'}")
        for issue in result["issues"]:
            print(f"- {issue.get('record') or issue.get('path')}: {issue['issue']}")
    elif "record" in result:
        record = result["record"]
        print(f"{result.get('action', 'record')}: {record.get('title') or record['sha256']}")
        print(f"sha256: {record['sha256']}")
        print(f"identifiers: {', '.join(record.get('identifiers', [])) or '(none)'}")
        print(f"extraction: {record.get('extraction', {}).get('status', 'unknown')}")
    else:
        print(f"initialized {result['cache']} (Git ignored: {result['git_ignored']})")
    print_warnings(result)


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", default=".", help="research repository root (default: current directory)")
    parser.add_argument("--format", choices=("text", "json"), default="text")


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = main.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create and verify the ignored cache")
    add_common_options(init)

    add = commands.add_parser("add", help="ingest a local PDF")
    add_common_options(add)
    add.add_argument("--pdf", required=True)
    add.add_argument("--id", dest="identifier", action="append", default=[], help="repeatable scheme:value identifier")
    add.add_argument("--title")
    add.add_argument("--author", action="append")
    add.add_argument("--version")
    add.add_argument("--source-url", action="append")
    add.add_argument("--date-checked")
    add.add_argument("--retention-basis", required=True, help="why local retention is authorized")
    add.add_argument("--text", help="pre-extracted plaintext to cache")
    add.add_argument("--text-tool", help="tool that produced supplied --text")
    add.add_argument("--no-extract", action="store_true", help="do not invoke pdftotext")
    add.add_argument(
        "--replace-metadata", action="store_true",
        help="overwrite a stored title or version instead of reporting a conflict",
    )

    find = commands.add_parser("find", help="search identifiers, metadata, or cached text")
    add_common_options(find)
    selector = find.add_mutually_exclusive_group(required=True)
    selector.add_argument("--id", dest="identifier")
    selector.add_argument("--query")
    find.add_argument("--limit", type=int, default=20)

    show = commands.add_parser("show", help="show one record by hash or hash prefix")
    add_common_options(show)
    show.add_argument("sha256")

    verify = commands.add_parser("verify", help="verify records and cached artifact hashes")
    add_common_options(verify)
    return main


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            result, success = init_result(args), True
        elif args.command == "add":
            result, success = ingest(args), True
        elif args.command == "find":
            if not 1 <= args.limit <= 100:
                raise CacheError("--limit must be between 1 and 100")
            result, success = find_records(args), True
        elif args.command == "show":
            result, success = show_record(args), True
        else:
            result, success = verify_cache(args)
        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
            print_warnings(result)
        else:
            print_human(result)
        return EXIT_OK if success else EXIT_INVALID
    except CacheError as error:
        if getattr(args, "format", "text") == "json":
            print(json.dumps({"error": str(error)}, ensure_ascii=False))
        else:
            print(f"error: {error}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001 - keep a crash distinguishable from a verdict
        message = f"internal error: {type(error).__name__}: {error}"
        if getattr(args, "format", "text") == "json":
            print(json.dumps({"error": message}, ensure_ascii=False))
        else:
            print(message, file=sys.stderr)
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
