#!/usr/bin/env python3
r"""Prepare an immutable, lexical LaTeX snapshot for a native manuscript review.

Standard library only. No TeX execution, network, model calls or review verdicts.
Offset-preserving masking and confined input lookup adapt Math Scout's
preparation methodology (MIT; see ../references/math-scout-license.txt).

Lexical implementation notes:
Lines end at CR, LF or CRLF, as in TeX. Comments and common literal
environments, including inline `\verb`/`\lstinline` with any delimiter or
braces, cannot cause fake inputs or sections. `alltt` is not literal: its
commands, inputs included, are processed, and a percent sign there is text.
Its lexical state flows into included files and back into the caller, including
when an included file opens or closes `alltt`.
Reading a file stops where TeX stops: after the line containing a top-level
`\endinput`, or after a top-level `\end{document}`, which also ends every
including file. Inputs past those points are never resolved or read, and the
expanded source omits the rest of the file; unfinished literals or arguments
in that ignored material cannot fail preparation. The line ending after
`\end{document}` is retained, but ignored text on that same line is omitted.
`sources` hashes still cover whole files. Insert a boundary newline after an
expanded file without a terminal newline, so its final comment or control word
cannot consume the caller's next command. The source map marks that newline
as synthetic, with null original locators.

Missing files, cycles, unsupported dynamic filenames, invalid UTF-8, unclosed
literal environments/arguments and exceeded limits fail with exit code 2,
before snapshot creation. Limits are 32 levels, 512 unique files, 4096 input
expansions in total and 16 MiB of expanded characters (also a 16 MiB limit per
input file in bytes). A cycle does not silently erase content. Repeated
noncyclic inputs are allowed; each file is read once, and reached lexical
segments are cached by their incoming state and file stopping point. A failed
write may leave an incomplete directory, but the manifest is written last;
choose a fresh output directory for a retry.
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
MAX_INPUT_EXPANSIONS = 4096
MAX_EXPANDED_CHARS = 16 * 1024 * 1024
MAX_SOURCE_FILES = 512
LITERAL_ENVS = {"verbatim", "Verbatim", "lstlisting", "minted", "comment"}
SKIP_TITLES = {"references", "bibliography", "acknowledgments", "acknowledgements"}
STATEMENT_ENVS = {"theorem", "lemma", "proposition", "corollary", "definition",
                  "assumption", "conjecture", "remark"}
COMMAND_RE = re.compile(r"\\([A-Za-z@]+|[^\n])")
# TeX ends a line at CR, LF or CRLF; a bare CR must not extend a comment.
LINE_END_RE = re.compile(r"[\r\n]")
LABEL_SCAN_RE = re.compile(r"\\(begin|end)\s*\{[^{}]*\}|\\label\s*\{([^{}]+)\}")
HASH_RE = re.compile(r"[0-9a-f]{64}")
UNIT_ID_RE = re.compile(r"sha256:[0-9a-f]{64}:[1-9][0-9]*")
LIMITATIONS = [
    "Lexical preparation only: no TeX execution or arbitrary macro expansion.",
    "Conditionals, catcode changes, includeonly, TEXINPUTS or import-package paths and "
    "custom input/section macros need manual inspection.",
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


def line_end(text: str, pos: int) -> int:
    """Offset of the line terminator at or after pos, or the end of text."""
    match = LINE_END_RE.search(text, pos)
    return match.start() if match else len(text)


def after_line(text: str, pos: int) -> int:
    """Offset just past the line terminator at or after pos."""
    end = line_end(text, pos)
    return end + 2 if text.startswith("\r\n", end) else min(end + 1, len(text))


def line_breaks(text: str, start: int, end: int) -> int:
    """Number of CR, LF or CRLF line ends in text[start:end]."""
    return (text.count("\n", start, end) + text.count("\r", start, end)
            - text.count("\r\n", start, end))


def argument(text: str, pos: int, optional: bool = False):
    pos = skip_space(text, pos)
    if pos < len(text) and text[pos] == "*":
        pos = skip_space(text, pos + 1)
    if optional and pos < len(text) and text[pos] == "[":
        group = balanced(text, pos, "[", "]")
        pos = skip_space(text, group[2])
    return balanced(text, pos)


class LexicalScanner:
    """Scan only reached text, pausing at inputs so child state can flow back.

    State shared across files is (alltt nesting, brace depth). An endinput
    deadline belongs only to the current file. Optional masking preserves
    offsets for extraction from the already expanded source.
    """
    def __init__(self, tex: str, start=0, state=(0, 0), stop=None, chars=None):
        self.tex = tex
        self.pos = start
        self.alltt, self.depth = state
        self.stop = len(tex) if stop is None else stop
        self.chars = chars
        self.document_ended = False

    @property
    def state(self):
        return self.alltt, self.depth

    def blank(self, start, end):
        if self.chars is not None:
            for pos in range(start, end):
                if self.chars[pos] not in "\r\n":
                    self.chars[pos] = " "

    def skip_trivia(self, pos):
        """Skip whitespace and ordinary comments before a command argument."""
        while pos < self.stop:
            if self.tex[pos].isspace():
                pos += 1
            elif self.tex[pos] == "%" and not self.alltt:
                end = min(line_end(self.tex, pos), self.stop)
                self.blank(pos, end)
                pos = end
            else:
                break
        return pos

    def scan(self, pause_at_input=False):
        tex = self.tex
        while self.pos < self.stop:
            pos = self.pos
            if tex[pos] == "%" and not self.alltt:
                end = min(line_end(tex, pos), self.stop)
                self.blank(pos, end)
                self.pos = end
                continue
            match = COMMAND_RE.match(tex, pos)
            if match is None:
                self.depth += {"{": 1, "}": -1}.get(tex[pos], 0)
                self.pos += 1
                continue
            command = match[1]
            end = match.end()
            if not command[0].isalpha() and command[0] != "@":
                # In particular, \\section is an escaped slash followed by text.
                self.blank(pos, end)
            elif command in {"begin", "end"}:
                group = argument(tex[:self.stop], self.skip_trivia(end))
                if group is not None:
                    env = tex[group[0]:group[1]].strip()
                    end = group[2]
                    if command == "end" and env == "document" and self.depth == 0:
                        self.pos = end
                        self.document_ended = True
                        self.blank(end, len(tex))
                        return None
                    if command == "begin" and env.rstrip("*") in LITERAL_ENVS:
                        closing = re.search(r"\\end\s*\{" + re.escape(env) + r"\}",
                                            tex[group[2]:self.stop])
                        if closing is None:
                            raise PreparationError(f"Unclosed literal environment {env!r}")
                        end = group[2] + closing.end()
                        self.blank(pos, end)
                    elif env == "alltt":
                        self.alltt = self.alltt + 1 if command == "begin" else max(self.alltt - 1, 0)
            elif command == "endinput" and self.depth == 0 and pause_at_input:
                # TeX finishes this line, including any inputs, before returning.
                self.stop = min(self.stop, after_line(tex, end))
            elif command in {"verb", "lstinline"}:
                if end < self.stop and tex[end] == "*":
                    end += 1
                if command == "lstinline" and end < self.stop and tex[end] == "[":
                    end = balanced(tex[:self.stop], end, "[", "]")[2]
                if end < self.stop and not tex[end].isspace():
                    limit = min(line_end(tex, end + 1), self.stop)
                    if command == "lstinline" and tex[end] == "{":
                        # listings also accepts a brace-delimited argument.
                        depth, close = 0, -1
                        for at in range(end, limit):
                            depth += {"{": 1, "}": -1}.get(tex[at], 0)
                            if depth == 0:
                                close = at
                                break
                    else:
                        close = tex.find(tex[end], end + 1, limit)
                    if close < 0:
                        raise PreparationError(f"Unclosed inline literal near character {pos}")
                    end = close + 1
                    self.blank(pos, end)
            elif command in {"input", "include"} and pause_at_input:
                at = self.skip_trivia(end)
                group = balanced(tex[:self.stop], at)
                if group is None:
                    bare = re.match(r"[^\s{}\\%]+" if not self.alltt else r"[^\s{}\\]+",
                                    tex[at:self.stop]) if command == "input" else None
                    if bare is None:
                        raise PreparationError("Input/include requires a literal filename")
                    end = at + bare.end()
                    name = tex[at:end]
                else:
                    end = group[2]
                    name = tex[group[0]:group[1]].strip()
                self.pos = end
                return pos, end, name, command
            self.pos = end
        return None


def mask_non_content(tex: str) -> str:
    """Mask comments, literals and ignored document tails, preserving offsets.

    The expanded source may retain endinput markers from children; they no
    longer delimit files here. SourceLoader handles them before extraction.
    """
    chars = list(tex)
    LexicalScanner(tex, chars=chars).scan()
    return "".join(chars)


class SourceLoader:
    def __init__(self, root: Path):
        self.root = root.resolve()
        if not self.root.is_dir():
            raise PreparationError(f"Project boundary is not a directory: {root}")
        # TeX's working directory; prepare() sets it to the main file's directory.
        self.base = self.root
        self.sources = {}
        self.texts = {}
        self.plans = {}
        self.expanded_chars = 0
        self.expansions = 0
        self.document_ended = False

    def confined(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.root):
            raise PreparationError(f"Refusing input outside project boundary: {path}")
        return resolved

    def read(self, path: Path) -> str:
        if path in self.texts:
            return self.texts[path]
        if len(self.sources) >= MAX_SOURCE_FILES:
            raise PreparationError(f"More than {MAX_SOURCE_FILES} source files")
        raw = path.read_bytes()
        if len(raw) > MAX_EXPANDED_CHARS:
            raise PreparationError(f"Source exceeds preparation size limit: {path}")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PreparationError(f"Source is not valid UTF-8: {path}") from exc
        self.sources[path] = {"path": path.relative_to(self.root).as_posix(),
                              "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        self.texts[path] = text
        return text

    def reference(self, name: str, parent: Path, command: str) -> Path:
        if not name or any(c in name for c in "\\{}%\x00\r\n"):
            raise PreparationError(f"Input is not a supported literal filename: {name!r}")
        # TeX tries name.tex before name; \include strips a .tex suffix, then appends it.
        if name.endswith(".tex"):
            candidates = [name]
        elif command == "include":
            candidates = [name + ".tex"]
        else:
            candidates = [name + ".tex", name]
        escaped = False
        # The including file's directory is a fallback TeX itself does not search.
        for directory in dict.fromkeys((self.base, parent)):
            for candidate in candidates:
                try:
                    path = self.confined(directory / candidate)
                except PreparationError:
                    # An existing escaping file is what TeX would read; skipping
                    # it could select a different, in-tree file.
                    if (directory / candidate).exists():
                        raise
                    escaped = True
                    continue
                if path.is_file():
                    return path
        if escaped:
            raise PreparationError(f"Refusing input outside project boundary: {name!r}")
        raise PreparationError(f"Cannot find input {name!r} from {parent.relative_to(self.root)}")

    def plan(self, path: Path, start: int, state: tuple, stop: int):
        """Cache a reached segment by offset, incoming state and file deadline."""
        key = path, start, state, stop
        if key not in self.plans:
            scanner = LexicalScanner(self.read(path), start, state, stop)
            reference = scanner.scan(pause_at_input=True)
            self.plans[key] = (scanner.pos, scanner.state, scanner.stop,
                               scanner.document_ended, reference)
        return self.plans[key]

    def expand(self, path: Path, stack: tuple = (), state: tuple = (0, 0)):
        path = self.confined(path)
        if path in stack:
            chain = " -> ".join(p.relative_to(self.root).as_posix() for p in (*stack, path))
            raise PreparationError(f"Circular input: {chain}")
        if len(stack) >= MAX_INPUT_DEPTH:
            raise PreparationError(f"Input nesting exceeds {MAX_INPUT_DEPTH}")
        text = self.read(path)
        stop = len(text)
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
                          "source_end": end, "source_line": line_breaks(text, 0, start) + 1})
            length += len(piece)

        while True:
            scanned, state, stop, ends_document, reference = self.plan(path, cursor, state, stop)
            if reference is None:
                append_original(cursor, scanned)
                if ends_document:
                    # Retain the original line ending, never ignored same-line text.
                    append_original(line_end(text, scanned), after_line(text, scanned))
                self.document_ended = ends_document
                return "".join(parts), spans, state
            start, end, name, command = reference
            # Tiny repeated inputs can multiply without approaching the size limit.
            self.expansions += 1
            if self.expansions > MAX_INPUT_EXPANSIONS:
                raise PreparationError(f"More than {MAX_INPUT_EXPANSIONS} input expansions")
            # Resolved only when reached: an earlier input may end the document.
            target = self.reference(name, path.parent, command)
            append_original(cursor, start)
            child, child_spans, state = self.expand(target, (*stack, path), state)
            parts.append(child)
            for span in child_spans:
                spans.append(dict(span, expanded_start=length + span["expanded_start"],
                                  expanded_end=length + span["expanded_end"]))
            length += len(child)
            # A file's final comment/control word must not consume the caller's
            # next command when the included file has no terminal newline.
            if child and not child.endswith(("\n", "\r")):
                self.expanded_chars += 1
                if self.expanded_chars > MAX_EXPANDED_CHARS:
                    raise PreparationError("Expanded source exceeds preparation size limit")
                parts.append("\n")
                spans.append({"expanded_start": length, "expanded_end": length + 1,
                              "path": None, "source_start": None, "source_end": None,
                              "source_line": None, "synthetic": "input-boundary-newline"})
                length += 1
            cursor = end
            if self.document_ended:
                return "".join(parts), spans, state


def plain_title(title: str) -> str:
    title = re.sub(r"\\[A-Za-z@]+", "", title)
    return re.sub(r"[{}$]", "", title).strip()


def locate(spans: list, tex: str, offset: int) -> dict:
    for span in spans:
        if span["expanded_start"] <= offset < span["expanded_end"]:
            if span["path"] is None:
                return {"path": None, "line": None}
            return {"path": span["path"],
                    "line": span["source_line"] + line_breaks(tex, span["expanded_start"], offset)}
    return {"path": None, "line": None}


def own_label(body: str):
    """First label of a statement itself, not of an equation or list nested in it."""
    depth = 0
    for match in LABEL_SCAN_RE.finditer(body):
        if match[1] == "begin":
            depth += 1
        elif match[1] == "end":
            depth = max(depth - 1, 0)
        elif depth == 0:
            return match[2]
    return None


def context_identity(context: dict) -> str:
    """Context without locators, so moving unchanged text keeps the global context hash."""
    return json.dumps({"preamble": context["preamble"], "title": context["title"],
                       "abstracts": [entry["text"] for entry in context["abstracts"]],
                       "statements": [[entry["environment"], entry["label"], entry["text"]]
                                      for entry in context["statements"]]},
                      ensure_ascii=False, sort_keys=True)


def top_level(masked: str, pattern: str):
    """First match outside braces, so a macro definition's body does not count.

    Lexically unbalanced braces fall back to the first match anywhere.
    """
    matches = list(re.finditer(pattern, masked))
    for match in matches:
        if masked.count("{", 0, match.start()) == masked.count("}", 0, match.start()):
            return match
    return matches[0] if matches else None


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
    begin = top_level(masked, r"\\begin\s*\{document\}")
    end = top_level(masked, r"\\end\s*\{document\}")
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
            context["statements"].append({"environment": name,
                "label": own_label(masked[inner:finish]), "text": tex[start:end_offset],
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


def contract_paths() -> list[Path]:
    """Canonical ordered inventory shared by aggregate and per-file revisions."""
    skill = Path(__file__).resolve().parent.parent
    files = [skill / "SKILL.md", Path(__file__).resolve(), *sorted((skill / "references").rglob("*.md"))]
    return [path for path in files if path.is_file()]


def contract_files() -> dict:
    """Portable per-file revisions for checking local lane reuse."""
    skill = Path(__file__).resolve().parent.parent
    return {path.relative_to(skill).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in contract_paths()}


def contract_digest() -> str:
    skill = Path(__file__).resolve().parent.parent
    hasher = hashlib.sha256()
    for path in contract_paths():
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
    old_contracts = previous.get("contract_files")
    if old_contracts is not None and (not isinstance(old_contracts, dict) or not old_contracts
            or any(not isinstance(name, str) or Path(name).is_absolute() or ".." in Path(name).parts
                   or not isinstance(value, str) or not HASH_RE.fullmatch(value)
                   for name, value in old_contracts.items())):
        raise PreparationError("Invalid previous manifest contract_files")
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
    if not isinstance(previous.get("main"), str):
        raise PreparationError("Invalid previous manifest main")
    # A renamed main file (common in resubmissions) still has comparable units.
    main_changed = previous["main"] != current["main"]
    old_counts = Counter(unit["identity_sha256"] for unit in units)
    new_counts = Counter(unit["identity_sha256"] for unit in current["units"])
    old = {unit["id"] for unit in units}
    new = {unit["id"] for unit in current["units"]}
    ambiguous = [unit["id"] for unit in current["units"]
                 if old_counts[unit["identity_sha256"]] > 1 or new_counts[unit["identity_sha256"]] > 1]
    contract_changed = (previous["contract_sha256"] != current["contract_sha256"]
                        or previous.get("preparation_version") != PREPARATION_VERSION)
    return {"previous_source_sha256": previous["source_sha256"],
            "previous_main": previous["main"], "main_changed": main_changed,
            "candidate_unchanged": sorted((new & old) - set(ambiguous)),
            "added": sorted(new - old), "removed": sorted(old - new),
            "ambiguous": sorted(ambiguous), "contract_changed": contract_changed,
            "contract_files_changed": (None if old_contracts is None else sorted(
                name for name in old_contracts.keys() | current["contract_files"].keys()
                if old_contracts.get(name) != current["contract_files"].get(name))),
            "global_context_changed": previous["global_context_sha256"] != current["global_context_sha256"],
            "whole_paper_invalidated": (main_changed
                                       or previous["source_sha256"] != current["source_sha256"]
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
    # TeX resolves inputs from its working directory, the main file's, not --root.
    loader.base = main.parent
    main = loader.confined(main)
    tex, spans, _ = loader.expand(main)
    units, context = extract(tex, spans)
    context_text = json.dumps(context, ensure_ascii=False, indent=2) + "\n"
    sources = sorted(loader.sources.values(), key=lambda item: item["path"])
    manifest = {"schema_version": SCHEMA_VERSION, "preparation_version": PREPARATION_VERSION,
                "main": main.relative_to(loader.root).as_posix(), "source_sha256": digest(tex),
                "global_context_sha256": digest(context_identity(context)),
                "contract_sha256": contract_digest(), "contract_files": contract_files(),
                "source_files_sha256": digest(json.dumps(sources, sort_keys=True)), "sources": sources,
                "source_map": spans, "units": units, "limitations": LIMITATIONS,
                "comparison": None}
    if previous is not None:
        manifest["comparison"] = compare_previous(manifest, Path(previous))
    return manifest, tex, context_text


def write_snapshot(output: Path, manifest: dict, tex: str, context_text: str):
    output = Path(output).absolute()
    # Case or trailing-dot aliases count too, also when reached through a link.
    if any(part.casefold().rstrip(". ") == ".mathbox"
           for path in (output, output.resolve()) for part in path.parts):
        raise PreparationError("Refusing output inside .mathbox, which research-state reserves "
                               "for its ledger; choose a review directory outside it")
    # Existing parents are the caller's environment and may be links (macOS /var);
    # only the snapshot directory itself must be new.
    if output.is_symlink():
        raise PreparationError(f"Refusing output symbolic link: {output}")
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
    parser.add_argument("manuscript", type=Path, help="main TeX file, relative to --root when supplied")
    parser.add_argument("--root", type=Path, help="authorized input boundary (default: main file directory); rebases relative manuscript paths")
    parser.add_argument("--output", required=True, type=Path, help="new snapshot directory, relative to current directory")
    parser.add_argument("--previous", type=Path, help="earlier manifest, relative to current directory; candidate comparison only")
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
