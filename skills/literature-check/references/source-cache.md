# Project-local source cache

Use the bundled `scripts/literature_cache.py` helper when a project authorizes
local retention of source material. Locate the active `literature-check` skill
directory; do not guess an installation path.

The helper stores ignored local state under
`.research-cache/literature/` at the project root:

```text
pdf/<PDF SHA-256>.pdf
text/<PDF SHA-256>.txt
records/<PDF SHA-256>.json
```

The JSON records are the index. They contain schema version, identifiers,
bibliographic metadata, local relative paths, content hashes, date checked,
retention basis, and extraction provenance. One record per PDF avoids a
database dependency and deduplicates identical files.

## Workflow

Before fetching, query an exact stable identifier:

```bash
python3 <literature-check-directory>/scripts/literature_cache.py find \
  --root <project-root> --id doi:10.1000/example --format json
```

Use `arxiv:<id>v<n>` when a version is known. A result labeled
`arxiv-version-candidate` is not an exact hit and must be authenticated before
use. For discovery within retained material, use `find --query <text>`; this
searches metadata and cached plaintext and returns bounded snippets.

On a cache miss, acquire the source through the host's normal authorized
network workflow. The helper intentionally does not fetch URLs or handle
credentials. Ingest the local PDF afterward, stating the policy or explicit
authorization that permits retention:

```bash
python3 <literature-check-directory>/scripts/literature_cache.py add \
  --root <project-root> --pdf <downloaded.pdf> \
  --id arxiv:2401.00001v2 --title <title> --version v2 \
  --source-url <stable-url> --retention-basis <authorization>
```

`add` invokes `pdftotext -layout` when available. Extraction failure does not
invalidate the PDF entry. Pass `--text <file>` to retain text produced by
another tool, with `--text-tool <name>` to record its provenance, or
`--no-extract` to store only the PDF. Re-ingesting identical content merges
compatible identifiers and locators.

Use `show <sha256-or-prefix>` to inspect one record and `verify` to recompute
artifact hashes and detect missing or orphaned files.

## Git and rights invariants

- Prefer a tracked `/.research-cache/` rule in the project root `.gitignore`.
- The helper creates an internal ignore rule and verifies effective Git ignore
  coverage before storing source content. It refuses ingestion if that check
  fails.
- Record only the SHA-256 and extraction status in the tracked literature
  ledger. The conventional local path may be mentioned, but availability is
  never assumed on another clone.
- Do not cache licensed, private, embargoed, or unpublished material unless the
  project's policy or the user explicitly authorizes local retention. Never
  upload cached material to an external service without separate authorization.
- A cache lookup, extracted-text match, or hash establishes identity and local
  availability only. It does not verify a theorem or support a novelty claim.
