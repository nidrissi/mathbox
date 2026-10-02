# Deterministic manuscript preparation

Resolve [prepare_manuscript.py](../scripts/prepare_manuscript.py) in this installed
skill. Python 3.10+ and the standard library suffice; it runs no TeX, models or
network requests and emits no review verdict.

```bash
python3 <skill-directory>/scripts/prepare_manuscript.py paper.tex --root PROJECT --output RUN
python3 <skill-directory>/scripts/prepare_manuscript.py paper.tex --root PROJECT --output NEW_RUN --previous RUN/manifest.json
```

`--root` is the authorized input boundary, defaulting to the main file's directory.
With it, relative manuscript paths resolve against that root; otherwise against
the current directory. `--output` and `--previous` remain caller-relative.
Inputs resolve from the main directory, then the including file as a lenient
fallback. Confine paths/symlinks before reading; never open refused content or widen
the boundary without authority.

Missing inputs, cycles, dynamic filenames, invalid UTF-8, unclosed literals or
arguments and exceeded limits fail with exit 2. Limits are 32 levels, 512 unique
files, 4096 expansions, 16 MiB expanded characters and 16 MiB per input file.
Write failures may leave an incomplete directory; the manifest is written last.
Retry with a fresh directory. Existing output paths, symlinks and `.mathbox/`
outputs are refused.

The run contains immutable `manifest.json`, `full-source.tex`, `context.json`
and `sections/*.tex`. Add raw `passes/<pass_id>.json`, `prior-leads.md`, collected
`findings.json`, `reconciliation.json` and `report.md` beside them; do not edit
snapshot files or overwrite old runs.

## Inventory and limitations

The schema-1 manifest carries `main`, hashed `sources`, `source_files_sha256`,
expanded `source_sha256`, `global_context_sha256`, `source_map`, `units`,
`limitations`, `comparison`, global `contract_sha256` and a portable
`contract_files` map of relative skill paths to SHA-256 values.

Unit keys used for review are `id`, `sha256`, `identity_sha256`, `file`,
`reviewable`, `skip_reason` and `location`, plus title/kind and expanded spans.
Copy `id` exactly: its kind/title/text identity plus occurrence is independent
of position. Duplicate identities are ambiguous. Cite author labels, original locators and
exact quotes, never extracted numbering/offsets. Source maps resolve multi-file units.

Inspect skipped bibliography/acknowledgment material before excluding it from
proof coverage. Context is an index, not a complete dependency graph. Macro-defined
headings, conditionals, catcodes, custom literals, `includeonly`, `TEXINPUTS`,
import paths and bibliography/graphics/package contents need manual inspection.
Disclose affected coverage; the script docstring explains internals.

## Incremental comparison

`--previous` validates metadata only and never reads paths named in it. It reports
candidate unchanged/added/removed/ambiguous units, main/context/contract changes,
`contract_files_changed` (null for old manifests lacking per-file hashes), and
`whole_paper_invalidated`. Any source/inventory/main/context/contract change
requires fresh whole-paper notation/claims passes and final reconciliation.

Local reuse requires actual prior artifacts, matching unit text and checked
definitions, conventions, dependencies and source/computation leaves. Refresh
locators. Inspect the shared protocol and lane hashes in `contract_files`; rerun
or justify rechecking changed contracts/methods. If per-file history is absent,
a global contract change requires rerunning local passes. A changed preparation
script or entry point affects every local pass. `candidate_unchanged` never means
reviewed or correct. Preserve provenance and hashes; do not hide staleness or build a review database.
