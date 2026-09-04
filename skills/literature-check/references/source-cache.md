# Project-local source cache

Use the bundled `scripts/literature_cache.py` helper when a project authorizes
local retention of source material. Locate the active `literature-check` skill
directory; do not guess an installation path.

The helper stores ignored local state under
`.research-cache/literature/` at the project root:

```text
.research-cache/.gitignore          internal ignore rule covering the whole tree
.research-cache/literature/pdf/<PDF SHA-256>.pdf
.research-cache/literature/text/<PDF SHA-256>.txt
.research-cache/literature/records/<PDF SHA-256>.json
```

The JSON records are the index. They contain schema version, identifiers,
bibliographic metadata, local relative paths, content hashes, date checked,
retention basis, and extraction provenance. One record per PDF avoids a
database dependency and deduplicates identical files.

`find`, `show`, and `verify` never create or modify the cache. Only `init` and
`add` write to it, so a lookup in a project that has not opted into local
retention leaves nothing behind.

Exit status: `0` success; `1` the cache is invalid (`verify` only); `2` a usage
or cache error; `3` an unexpected internal failure. A crash is therefore never
mistaken for an invalid-cache verdict.

## Workflow

Before fetching, query an exact stable identifier:

```bash
python3 <literature-check-directory>/scripts/literature_cache.py find \
  --root <project-root> --id doi:10.1000/example --format json
```

A result with `"cache_present": false` means the project has no cache yet, not
that the source is absent. Use `arxiv:<id>v<n>` when a version is known. A
result labeled `arxiv-version-candidate` is not an exact hit and must be
authenticated before use. For discovery within retained material, use
`find --query <text>`; this searches metadata and cached plaintext and returns
bounded snippets. `--limit` bounds both identifier and text searches.

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
compatible identifiers and locators. A differing title or version is reported
as a conflict rather than merged silently; resolve it deliberately, and pass
`--replace-metadata` only when the new value is the correct one.

Use `show <sha256-or-prefix>` to inspect one record and `verify` to recompute
artifact hashes and detect missing or orphaned files. A record the helper
cannot read is reported under `unreadable_records` and skipped; it never fails
an otherwise usable lookup.

## Git and rights invariants

- Keep a tracked `/.research-cache/` rule in the project root `.gitignore`.
  This is the durable invariant; the helper's own internal rule is a fallback,
  not a substitute.
- The helper reports both `git_ignored` (whether cache content is effectively
  ignored) and `git_ignore_repository_rule` (whether a rule *outside* the cache
  directory supplies that coverage). When only its own rule applies, it warns
  and names the rule that would have to be added. `inspect_repo.py` reports the
  same distinction, so repository setup can tell the two cases apart.
- Before writing any artifact, the helper checks that Git ignores that exact
  path. Because `git check-ignore` consults the index, this also refuses to
  overwrite a cached file that is already tracked.
- Record only the SHA-256 and extraction status in the tracked literature
  ledger. The conventional local path may be mentioned, but availability is
  never assumed on another clone.
- Do not cache licensed, private, embargoed, or unpublished material unless the
  project's policy or the user explicitly authorizes local retention. Never
  upload cached material to an external service without separate authorization.
- A cache lookup, extracted-text match, or hash establishes identity and local
  availability only. It does not verify a theorem or support a novelty claim.
