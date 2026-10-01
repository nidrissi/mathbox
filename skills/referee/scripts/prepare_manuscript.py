#!/usr/bin/env python3
"""Prepare an immutable, lexical LaTeX snapshot for a native manuscript review.

Standard library only. No TeX execution, network, model calls or review verdicts.
Offset-preserving masking and root-first input lookup adapt Math Scout's
preparation methodology (MIT; see ../references/math-scout-license.txt).
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys


SCHEMA_VERSION = 1
PREPARATION_VERSION = 1
MAX_INPUT_DEPTH = 32
MAX_EXPANDED_CHARS = 16 * 1024 * 1024
MAX_SOURCE_FILES = 512
LITERAL_ENVS = {"verbatim", "Verbatim", "lstlisting", "minted", "comment", "alltt"}
SKIP_TITLES = {"references", "bibliography", "acknowledgments", "acknowledgements"}
STATEMENT_ENVS = {"theorem", "lemma", "proposition", "corollary", "definition",
                  "assumption", "conjecture", "remark"}
COMMAND_RE = re.compile(r"\\([A-Za-z@]+|[^\n])")
HASH_RE = re.compile(r"[0-9a-f]{64}")
UNIT_ID_RE = re.compile(r"sha256:[0-9a-f]{64}:[1-9][0-9]*")
LIMITATIONS = [
    "Lexical preparation only: no TeX execution or arbitrary macro expansion.",
    "Conditionals, catcode changes, includeonly and custom input/section macros need manual inspection.",
    "Literal masking covers verb/lstinline and common verbatim/listing/comment environments, not every package.",
    "Bibliography files, graphics and package inputs are not loaded or authenticated.",
    "Context is an extraction index; its order is not manuscript theorem numbering.",
    "Hash comparison identifies text candidates, not dependency freshness or completed reviews.",
]


class PreparationError(ValueError):
    """A snapshot would be incomplete, unsafe or incompatible."""


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def balanced(text: str, start: int, opening: str = "{", closing: str = "}"):
    """Return interior start/end and end offset of a balanced masked argument."""
    if start >= len(text) or text[start] != opening:
        return None
    depth = 1
    for pos in range(start + 1, len(text)):
        if text[pos] == opening:
            depth += 1
        elif text[pos] == closing:
            depth -= 1
            if depth == 0:
                return start + 1, pos, pos + 1
    raise PreparationError(f"Unclosed {opening} argument near character {start}")


def skip_space(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def argument(text: str, pos: int, optional: bool = False):
    pos = skip_space(text, pos)
    if pos < len(text) and text[pos] == "*":
        pos = skip_space(text, pos + 1)
    if optional and pos < len(text) and text[pos] == "[":
        group = balanced(text, pos, "[", "]")
        pos = skip_space(text, group[2])
    return balanced(text, pos)


def mask_non_content(tex: str) -> str:
    """Mask comments/literals/escaped control symbols without changing offsets.

    Scan in lexical order: a commented-out begin must not mask real content,
    and a percent in a literal body must not consume its real closing marker.
    """
    chars = list(tex)

    def blank(start, end):
        for pos in range(start, end):
            if chars[pos] not in "\r\n":
                chars[pos] = " "

    pos = 0
    while pos < len(tex):
        if tex[pos] == "%":
            end = tex.find("\n", pos)
            end = len(tex) if end < 0 else end
            blank(pos, end)
            pos = end
            continue
        match = COMMAND_RE.match(tex, pos)
        if match is None:
            pos += 1
            continue
        command = match[1]
        end = match.end()
        if not command[0].isalpha() and command[0] != "@":
            # In particular, \\section is an escaped slash followed by text.
            blank(pos, end)
        elif command == "begin":
            group = argument(tex, end)
            if group is not None:
                env = tex[group[0]:group[1]].strip()
                if env.rstrip("*") in LITERAL_ENVS:
                    closing = re.search(r"\\end\s*\{" + re.escape(env) + r"\}",
                                        tex[group[2]:])
                    if closing is None:
                        raise PreparationError(f"Unclosed literal environment {env!r}")
                    end = group[2] + closing.end()
                    blank(pos, end)
        elif command in {"verb", "lstinline"}:
            if end < len(tex) and tex[end] == "*":
                end += 1
            if command == "lstinline" and end < len(tex) and tex[end] == "[":
                end = balanced(tex, end, "[", "]")[2]
            if end < len(tex) and not tex[end].isspace():
                delimiter = tex[end]
                close = tex.find(delimiter, end + 1)
                newline = tex.find("\n", end + 1)
                if close < 0 or (newline >= 0 and newline < close):
                    raise PreparationError(f"Unclosed inline literal near character {pos}")
                end = close + 1
                blank(pos, end)
        pos = end
    return "".join(chars)


class SourceLoader:
    def __init__(self, root: Path):
        self.root = root.resolve()
        if not self.root.is_dir():
            raise PreparationError(f"Project boundary is not a directory: {root}")
        self.sources = {}
        self.texts = {}
        self.expanded_chars = 0

    def confined(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.root):
            raise PreparationError(f"Refusing input outside project boundary: {path}")
        return resolved

    def read(self, path: Path) -> str:
        path = self.confined(path)
        if path not in self.texts:
            if len(self.sources) >= MAX_SOURCE_FILES:
                raise PreparationError(f"More than {MAX_SOURCE_FILES} source files")
            raw = path.read_bytes()
            if len(raw) > MAX_EXPANDED_CHARS:
                raise PreparationError(f"Source exceeds preparation size limit: {path}")
            try:
                self.texts[path] = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise PreparationError(f"Source is not valid UTF-8: {path}") from exc
            self.sources[path] = {"path": path.relative_to(self.root).as_posix(),
                                  "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        return self.texts[path]

    def reference(self, name: str, parent: Path) -> Path:
        if not name or any(c in name for c in "\\{}%\x00\r\n"):
            raise PreparationError(f"Input is not a supported literal filename: {name!r}")
        candidates = [name] if name.endswith(".tex") else [name, name + ".tex"]
        escaped = False
        for directory in dict.fromkeys((self.root, parent)):
            for candidate in candidates:
                try:
                    path = self.confined(directory / candidate)
                except PreparationError:
                    escaped = True
                    continue
                if path.is_file():
                    return path
        if escaped:
            raise PreparationError(f"Refusing input outside project boundary: {name!r}")
        raise PreparationError(f"Cannot find input {name!r} from {parent.relative_to(self.root)}")

    def expand(self, path: Path, stack: tuple = ()):
        path = self.confined(path)
        if path in stack:
            chain = " -> ".join(p.relative_to(self.root).as_posix() for p in (*stack, path))
            raise PreparationError(f"Circular input: {chain}")
        if len(stack) >= MAX_INPUT_DEPTH:
            raise PreparationError(f"Input nesting exceeds {MAX_INPUT_DEPTH}")
        text = self.read(path)
        masked = mask_non_content(text)
        parts, spans = [], []
        length = 0
        cursor = 0

        def append_original(start, end):
            nonlocal length
            if start == end:
                return
            piece = text[start:end]
            self.expanded_chars += len(piece)
            if self.expanded_chars > MAX_EXPANDED_CHARS:
                raise PreparationError("Expanded source exceeds preparation size limit")
            parts.append(piece)
            spans.append({"expanded_start": length, "expanded_end": length + len(piece),
                          "path": self.sources[path]["path"], "source_start": start,
                          "source_end": end, "source_line": text.count("\n", 0, start) + 1})
            length += len(piece)

        for match in COMMAND_RE.finditer(masked):
            if match.start() < cursor or match[1] not in {"input", "include"}:
                continue
            pos = skip_space(masked, match.end())
            group = balanced(masked, pos)
            if group is None:
                # TeX permits a whitespace-delimited, brace-less \input only.
                bare = re.match(r"[^\s{}\\]+", masked[pos:]) if match[1] == "input" else None
                if bare is None:
                    raise PreparationError("Input/include requires a literal filename")
                end = pos + bare.end()
                name = text[pos:end]
            else:
                end = group[2]
                name = text[group[0]:group[1]].strip()
            target = self.reference(name, path.parent)
            append_original(cursor, match.start())
            child, child_spans = self.expand(target, (*stack, path))
            parts.append(child)
            for span in child_spans:
                spans.append(dict(span, expanded_start=length + span["expanded_start"],
                                  expanded_end=length + span["expanded_end"]))
            length += len(child)
            # A file's final comment/control word must not consume the caller's
            # next command when the included file has no terminal newline.
            if child and not child.endswith("\n"):
                self.expanded_chars += 1
                if self.expanded_chars > MAX_EXPANDED_CHARS:
                    raise PreparationError("Expanded source exceeds preparation size limit")
                parts.append("\n")
                spans.append({"expanded_start": length, "expanded_end": length + 1,
                              "path": None, "source_start": None, "source_end": None,
                              "source_line": None, "synthetic": "input-boundary-newline"})
                length += 1
            cursor = end
        append_original(cursor, len(text))
        return "".join(parts), spans


def plain_title(title: str) -> str:
    title = re.sub(r"\\[A-Za-z@]+", "", title)
    return re.sub(r"[{}$]", "", title).strip()


def locate(spans: list, tex: str, offset: int) -> dict:
    for span in spans:
        if span["expanded_start"] <= offset < span["expanded_end"]:
            if span["path"] is None:
                return {"path": None, "line": None}
            return {"path": span["path"],
                    "line": span["source_line"] + tex.count("\n", span["expanded_start"], offset)}
    return {"path": None, "line": None}


def environment_bounds(masked: str, name: str):
    pattern = re.compile(r"\\(begin|end)\s*\{" + re.escape(name) + r"\}")
    depth, begin = 0, None
    for match in pattern.finditer(masked):
        if match[1] == "begin":
            if depth == 0:
                begin = match
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0:
                yield begin.start(), begin.end(), match.start(), match.end()


def extract(tex: str, spans: list):
    masked = mask_non_content(tex)
    begin = re.search(r"\\begin\s*\{document\}", masked)
    end = re.search(r"\\end\s*\{document\}", masked)
    body_start = begin.end() if begin else 0
    body_end = end.start() if end else len(tex)
    if body_end < body_start:
        raise PreparationError("End of document precedes its beginning")
    context = {"preamble": tex[:begin.start()] if begin else "", "title": None,
               "abstracts": [], "statements": []}
    for match in COMMAND_RE.finditer(masked):
        if match[1] == "title" and context["title"] is None:
            group = argument(masked, match.end(), optional=True)
            if group:
                context["title"] = tex[group[0]:group[1]]
    for start, inner, finish, end_offset in environment_bounds(masked, "abstract"):
        context["abstracts"].append({"text": tex[inner:finish],
                                     "location": locate(spans, tex, start)})
    envs = set(STATEMENT_ENVS)
    for match in COMMAND_RE.finditer(masked):
        if match[1] == "newtheorem":
            group = argument(masked, match.end())
            if group:
                name = masked[group[0]:group[1]].strip()
                if re.fullmatch(r"[A-Za-z@]+", name):
                    envs.add(name)
    for name in sorted(envs):
        for start, inner, finish, end_offset in environment_bounds(masked, name):
            if not body_start <= start < body_end:
                continue
            label = re.search(r"\\label\s*\{([^{}]+)\}", masked[inner:finish])
            context["statements"].append({"environment": name,
                "label": label[1] if label else None, "text": tex[start:end_offset],
                "expanded_start": start, "location": locate(spans, tex, start)})
    context["statements"].sort(key=lambda entry: entry["expanded_start"])

    boundaries = []
    for match in COMMAND_RE.finditer(masked):
        if not body_start <= match.start() < body_end:
            continue
        if match[1] == "section":
            group = argument(masked, match.end(), optional=True)
            if group is None:
                raise PreparationError("Unsupported section title; inspect original source")
            boundaries.append((match.start(), tex[group[0]:group[1]], "section"))
        elif match[1] in {"bibliography", "printbibliography"}:
            boundaries.append((match.start(), "Bibliography", "bibliography"))
        elif match[1] == "begin":
            group = argument(masked, match.end())
            if group and masked[group[0]:group[1]] == "thebibliography":
                boundaries.append((match.start(), "Bibliography", "bibliography"))
    if not boundaries:
        boundaries = [(body_start, "Manuscript body", "body")]
    elif masked[body_start:boundaries[0][0]].strip():
        boundaries.insert(0, (body_start, "Front matter", "front-matter"))
    units, occurrences = [], Counter()
    width = max(3, len(str(len(boundaries))))
    for index, (start, title, kind) in enumerate(boundaries, 1):
        finish = boundaries[index][0] if index < len(boundaries) else body_end
        content = tex[start:finish]
        identity = digest(kind + "\0" + title + "\0" + content)
        occurrences[identity] += 1
        plain = plain_title(title)
        reason = "Obvious non-mathematical section title" if plain.casefold() in SKIP_TITLES else None
        if kind == "bibliography":
            reason = "Bibliography material"
        slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")[:64] or "unit"
        units.append({"id": f"sha256:{identity}:{occurrences[identity]}",
                      "sha256": digest(content), "identity_sha256": identity,
                      "title": title, "kind": kind, "reviewable": reason is None,
                      "skip_reason": reason, "file": f"sections/{index:0{width}d}-{slug}.tex",
                      "expanded_start": start, "expanded_end": finish,
                      "location": locate(spans, tex, start)})
    return units, context


def contract_digest() -> str:
    skill = Path(__file__).resolve().parent.parent
    files = [skill / "SKILL.md", Path(__file__).resolve(), *sorted((skill / "references").rglob("*.md"))]
    hasher = hashlib.sha256()
    for path in files:
        if path.is_file():
            hasher.update(path.relative_to(skill).as_posix().encode("utf-8") + b"\0")
            hasher.update(path.read_bytes() + b"\0")
    return hasher.hexdigest()


def compare_previous(current: dict, path: Path) -> dict:
    """Validate metadata only; never read or act on paths inside an old manifest."""
    previous = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(previous, dict) or previous.get("schema_version") != SCHEMA_VERSION:
        raise PreparationError("Unsupported previous manifest schema")
    for key in ("source_sha256", "source_files_sha256", "global_context_sha256", "contract_sha256"):
        if not isinstance(previous.get(key), str) or not HASH_RE.fullmatch(previous[key]):
            raise PreparationError(f"Invalid previous manifest {key}")
    units = previous.get("units")
    if not isinstance(units, list):
        raise PreparationError("Previous manifest units must be an array")
    ids = set()
    for unit in units:
        if (not isinstance(unit, dict) or not isinstance(unit.get("id"), str)
                or not UNIT_ID_RE.fullmatch(unit["id"]) or unit["id"] in ids
                or not isinstance(unit.get("identity_sha256"), str)
                or not HASH_RE.fullmatch(unit["identity_sha256"])
                or not unit["id"].startswith("sha256:" + unit["identity_sha256"] + ":")):
            raise PreparationError("Invalid previous manifest unit identity")
        ids.add(unit["id"])
    if previous.get("main") != current["main"]:
        raise PreparationError("Previous manifest describes a different main manuscript")
    old_counts = Counter(unit["identity_sha256"] for unit in units)
    new_counts = Counter(unit["identity_sha256"] for unit in current["units"])
    old = {unit["id"] for unit in units}
    new = {unit["id"] for unit in current["units"]}
    ambiguous = [unit["id"] for unit in current["units"]
                 if old_counts[unit["identity_sha256"]] > 1 or new_counts[unit["identity_sha256"]] > 1]
    contract_changed = (previous["contract_sha256"] != current["contract_sha256"]
                        or previous.get("preparation_version") != PREPARATION_VERSION)
    return {"previous_source_sha256": previous["source_sha256"],
            "candidate_unchanged": sorted((new & old) - set(ambiguous)),
            "added": sorted(new - old), "removed": sorted(old - new),
            "ambiguous": sorted(ambiguous), "contract_changed": contract_changed,
            "global_context_changed": previous["global_context_sha256"] != current["global_context_sha256"],
            "whole_paper_invalidated": (previous["source_sha256"] != current["source_sha256"]
                                       or previous["source_files_sha256"] != current["source_files_sha256"]
                                       or previous["global_context_sha256"] != current["global_context_sha256"]
                                       or contract_changed),
            "reuse_requires_context_check": True}


def prepare(main: Path, root: Path | None = None, previous: Path | None = None):
    main = Path(main)
    if root is not None and not main.is_absolute():
        main = Path(root) / main
    main = main.absolute()
    loader = SourceLoader(Path(root) if root is not None else main.parent)
    main = loader.confined(main)
    tex, spans = loader.expand(main)
    units, context = extract(tex, spans)
    context_text = json.dumps(context, ensure_ascii=False, indent=2) + "\n"
    sources = sorted(loader.sources.values(), key=lambda item: item["path"])
    manifest = {"schema_version": SCHEMA_VERSION, "preparation_version": PREPARATION_VERSION,
                "main": main.relative_to(loader.root).as_posix(), "source_sha256": digest(tex),
                "global_context_sha256": digest(context_text), "contract_sha256": contract_digest(),
                "source_files_sha256": digest(json.dumps(sources, sort_keys=True)), "sources": sources,
                "source_map": spans, "units": units, "limitations": LIMITATIONS,
                "comparison": None}
    if previous is not None:
        manifest["comparison"] = compare_previous(manifest, Path(previous))
    return manifest, tex, context_text


def write_snapshot(output: Path, manifest: dict, tex: str, context_text: str):
    output = Path(output).absolute()
    for path in (output, *output.parents):
        if path.is_symlink():
            raise PreparationError(f"Refusing output symbolic link: {path}")
    if output.exists():
        raise PreparationError("Output must be a new snapshot directory; choose a new --output")
    output.mkdir(parents=True, exist_ok=False)
    (output / "sections").mkdir()

    def write(relative, content):
        with (output / relative).open("xb") as stream:
            stream.write(content.encode("utf-8"))

    write("full-source.tex", tex)
    write("context.json", context_text)
    for unit in manifest["units"]:
        write(unit["file"], tex[unit["expanded_start"]:unit["expanded_end"]])
    # Written last: incomplete snapshots never have a completed manifest.
    write("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manuscript", type=Path)
    parser.add_argument("--root", type=Path, help="Input boundary (default: main manuscript directory)")
    parser.add_argument("--output", required=True, type=Path, help="New snapshot directory")
    parser.add_argument("--previous", type=Path, help="Earlier manifest, for candidate comparison only")
    args = parser.parse_args(argv)
    try:
        manifest, tex, context_text = prepare(args.manuscript, args.root, args.previous)
        write_snapshot(args.output, manifest, tex, context_text)
    except (OSError, ValueError) as exc:
        print(f"Preparation failed: {exc}", file=sys.stderr)
        return 2
    print(f"Prepared {len(manifest['units'])} units from {len(manifest['sources'])} files: {args.output / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
