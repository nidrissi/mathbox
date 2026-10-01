# Deterministic manuscript preparation

Resolve [prepare_manuscript.py](../scripts/prepare_manuscript.py) in this
installed skill. Python 3.10+ and the standard library suffice. It never calls
a model, installs Math Scout, runs TeX, fetches files or emits a review verdict.

```bash
python3 <skill-directory>/scripts/prepare_manuscript.py paper.tex --root PROJECT --output RUN
python3 <skill-directory>/scripts/prepare_manuscript.py paper.tex --root PROJECT --output NEW_RUN --previous RUN/manifest.json
```

`--root` defaults to the main file's directory. Supply a wider project boundary
only when that is the actual authorized manuscript project. Files resolve
relative manuscript paths against `--root` when supplied, otherwise against
the caller's current directory. `--output` and `--previous` are explicit
caller-relative artifact paths (absolute paths also work). Input references
resolve as TeX resolves them from its working directory, the main file's
directory, then relative to the including file as a lenient fallback that TeX
itself does not perform. `--root` bounds what may be read; it never changes
lookup. A symlinked main file keeps the supplied entry point's directory for
lookup; canonical paths identify and confine the source files.
`\input{name}` tries `name.tex` before `name`; `\include{name}` reads
only `name.tex`. Brace-less `\input` is supported. Paths and symlinks must
remain inside the boundary before any content is read; an existing candidate
that escapes it fails preparation rather than falling back to a later one.

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

Output must be a new directory. Refuse an existing output path, including a
symlink there even when dangling, and any output under `.mathbox/`, including
case or trailing-dot aliases and paths reached through a link: research-state
reserves that directory for its ledger. Existing parent directories are used
as they are, including linked ones such as macOS `/var`. No prior review files
are overwritten, moved or deleted. It contains:

```text
manifest.json
full-source.tex
context.json
sections/001-<title>.tex
sections/002-<title>.tex
...
```

## Inventory and locators

The version 1 manifest records:

- `main`: canonical source path relative to the project boundary;
- `sources`: canonical relative paths, exact raw-byte SHA-256 hashes and sizes;
- `source_files_sha256`: digest of the complete input inventory;
- `source_sha256`: hash of UTF-8 expanded source, including comments;
- `global_context_sha256`: hash of the extracted context without locators
  (preamble, title, abstract texts, and each statement's environment, own
  label and text), so moving unchanged context does not change it;
- `contract_sha256`: hash of this skill's entry point, preparation script and
  all Markdown references, with relative names; installation location does
  not affect it;
- `source_map`: contiguous expanded character spans mapped to original file
  character offsets and starting lines; repeated inputs have distinct spans,
  and inserted boundary newlines have an explicit synthetic marker;
- `units`: position-independent identity, content hash, occurrence, title,
  kind, ordered filename, expanded character range, original start locator,
  reviewability and skip reason;
- `limitations` and optional `comparison`.

A unit ID is `sha256:<identity-hash>:<occurrence>`. The identity hashes kind,
raw title and raw unit text, independent of position. The content hash covers
only that unit's exact bytes. Identical repeated units receive occurrence
suffixes and are ambiguous for reuse; hashes are not manuscript theorem
numbers. Do not cite character offsets as author-facing locations. Use labels,
section names, original file/line locators and searchable quotations, consulting
the source map when a unit spans several files.

Section titles support nested braces, optional short titles and starred forms.
Front matter is retained without a minimum-prose cutoff. A document without
sections has one body unit; other sectioning schemes need adaptive manual
granularity. The last unit ends before `\end{document}` so adding an end
section need not change its neighbor's identity. Unit boundaries are lexical,
not mathematical dependency boundaries.

Obvious references/bibliography/acknowledgment headings and bibliography
commands/environments receive skip metadata. The material remains in the
snapshot and whole-paper source. Inspect the marked material before skipping
proof passes: a title cannot establish that its content is non-mathematical.

Context retains preamble, title, abstract and theorem-like environments,
including standard lemma/proposition/corollary/definition forms and simple
`\newtheorem` aliases. It records raw statements and each statement's own
author label when present; a label inside a nested equation or list does not
count. This uncapped extraction is an index, not complete dependencies or
validated theorem numbering. Macro-defined headings, conditional TeX,
catcodes, custom literals, `\includeonly`, `TEXINPUTS` or `import`-package
paths and bibliography content require
manual inspection. Do not call a lexical snapshot a faithful compiled paper
when those limits affect what was reviewed.

## Modest incremental comparison

`--previous` reads and validates prior-manifest metadata only; it never opens
paths named inside that metadata. It produces the previous main path and a
`main_changed` flag (a renamed main file is compared, not refused), candidate
unchanged IDs, added/removed IDs, ambiguous duplicates, contract/context change
flags and `whole_paper_invalidated`. This flag is true for any change to
expanded source, the input-file inventory, the main file path, extracted
context or preparation/skill contract.
Such a change requires new notation/claims passes and final reconciliation.
Changed position/line locators must be refreshed even for identical text.

To reuse a local review, inspect its actual raw artifacts and recorded source,
contract, lane, scope, executor/method and dependencies. Match the unit text;
then verify the statements, definitions, conventions, external/computational
leaves and dependency context it relied on. A global change can invalidate a
byte-identical unit. If context was not recorded, inspect it afresh or rerun
the pass. Reject ambiguous duplicates as automatic reuse candidates. A changed
lane contract or reviewer method needs a new review or an explicit justified
recheck. `candidate_unchanged` never means reviewed, correct or reusable.

Keep preparation snapshots immutable and raw findings separate from the new
report. Do not build a completed-review database, edit historical snapshots
or refresh hashes merely to hide stale evidence. An existing initialized
`research-state` ledger may record useful review provenance under its own
contract; initialization is optional and not a refereeing prerequisite.
Follow-up after realistic use: assess a thin ledger application for exact
dependency-aware reuse instead of adding a parallel state subsystem.
