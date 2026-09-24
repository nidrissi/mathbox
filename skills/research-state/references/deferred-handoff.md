# Deferred handoff for a non-executing host

`mathbox-deferred-v1` carries work from a session that can inspect and reason
about an initialized project but cannot execute the helper or write project
files. It is a persistence proposal, not a record that persistence happened.
The receiving local command applies it without another model pass.

## Packet

Return one complete JSON object with exactly these top-level fields:

```json
{
  "format": "mathbox-deferred-v1",
  "base": {
    "event_id": "E000137",
    "event_sha256": "0000000000000000000000000000000000000000000000000000000000000000"
  },
  "artifacts": [
    {
      "path": "research/records/2026-09-24-obstruction.md",
      "content": "# Obstruction\n\nThe complete durable route record.\n"
    },
    {
      "path": "proofs/obstruction-lemma.md",
      "content": "# Obstruction lemma\n\nThe complete argument.\n"
    }
  ],
  "index_append": {
    "path": "research/index.md",
    "expected_tail": "- 2026-09-20 — Earlier route\n",
    "content": "- 2026-09-24 — [Obstruction](records/2026-09-24-obstruction.md) — conditional\n"
  },
  "proposals": [
    {
      "type": "evidence",
      "actor": "chatgpt-web",
      "payload": {
        "claim": "C_OBSTRUCTION",
        "kind": "proof",
        "summary": "Conditional obstruction lemma; see the argument and its stated hypothesis.",
        "artifacts": [{"path": "proofs/obstruction-lemma.md"}]
      }
    }
  ]
}
```

The example's all-zero base hash is illustrative; replace it with the **actual**
`sha256` of the inspected head event before emitting a packet. For an initialized
ledger with no events, use `null` for both base values. The local command rejects
a packet if either base value differs from the current ledger head. Do not infer
the hash from an event ID or from a Git revision.

`artifacts` contains complete UTF-8 text for **new** files strictly inside an
artifact root configured under the local write policy below, with a `.md`, `.tex`, `.txt` or `.bib` suffix. No
path component may start with `.`, and agent instruction files such as
`AGENTS.md`, `CLAUDE.md`, `GEMINI.md` or `SKILL.md` are refused anywhere.
Paths cannot escape the project or traverse symlinks, and one artifact cannot
lie inside another. Existing files cannot be replaced. Do not embed the
conversation; write the actual durable proof, report, or route record. Keep
licensed or private source material under its existing retention policy.

`index_append` is either `null` or one guarded append to an **existing** UTF-8
file listed in `index_files`. `expected_tail` is the exact last line, including
its newline; use `""` only for an empty index. LF and CRLF terminators compare
equal, and the entry is written with the index's own terminator. `content` is
one complete, nonempty line ending in a newline. The index guard rejects a
changed tail. Ingest also refuses an append that would change bytes a current
claim, evidence, review, or run-result record pins; bind such records to a
stable claim-scoped artifact rather than to the index. Use the project's
designated route index and follow its immutable-entry convention.

`proposals` is a nonempty `record-batch` proposal list in dependency order.
The same `alias` and `{"$event":"alias"}` references work within the packet.
Proposals omit generated event IDs, timestamps, event hashes, snapshots, and
manifest closure fields. The helper supplies them, checks proposal validity,
and pins staged artifacts from their exact UTF-8 bytes. Existing artifacts may
also be referenced. Give such a reference a `sha256` only when a tool reported
the exact SHA-256 of the inspected bytes; never compute or guess one. Ingest
rejects a supplied hash that differs from the local file. Without one, ingest
pins the local copy, which may differ from the inspected one, and lists it under
`unverified_existing_pins`. A packet does not certify the mathematics in any
artifact.

This version does not accept arbitrary file replacements, deletes, binary data,
commands, or patches. A workflow that needs edits to existing live files must
handle those edits separately under the project's normal authority rules.

## Local write policy

The receiving project decides where a packet may write. Its
`.mathbox/config.json` may contain, beside the schema fields:

```json
"deferred": {
  "artifact_roots": ["proofs", "reviews", "research/records"],
  "index_files": ["research/index.md"]
}
```

Read these lists from the inspected config. Without `artifact_roots`, a packet
creates no files; without `index_files`, `index_append` must be `null`. A
proposals-only packet that references existing files needs no policy. If the
work needs a location the policy does not open, say so instead of emitting a
packet that ingest will refuse. Opening a location is a local decision, never
part of a packet.

## Local ingest

After resolving this skill's `scripts/research_state.py` as `TOOL`:

```bash
python3 "$TOOL" --root PROJECT ingest PACKET.json --dry-run
python3 "$TOOL" --root PROJECT ingest PACKET.json
python3 "$TOOL" --root PROJECT ingest -
```

The last form reads one JSON packet from standard input. Packets are read as
UTF-8 whatever the locale; a byte-order mark is ignored. The default output is
the compact `record-batch` summary, the index path, and the artifact and
`unverified_existing_pins` path lists, each capped at eight with an omitted
count. `--json` before `ingest` prints the complete events and lists.
Before a real ingest, check that every unverified existing pin holds the
content the remote host inspected, for example that it has no uncommitted edit.

Dry-run takes the writer lock and validates the whole packet without leaving
files or events. Ingest validates everything under that lock, creates each
artifact exclusively so that no existing entry is replaced, replaces the index
atomically with its old bytes plus the new entry, then appends the prepared
events. If a failure occurs before the first event is written, ingest deletes
each artifact it created and restores the index, provided they still hold the
bytes it wrote, and names anything left in place; the unchanged packet can then
be retried. A later failure leaves the artifacts, the index entry, and a valid
prefix of events. Inspect the journal head before any retry: the original
packet then fails its base guard.

## Response shape

Give the mathematical finding and its limits in ordinary prose. State that the
packet has **not** been applied. Make the complete packet the last fenced block
in the response, using a `json` fence. Include no ellipses, placeholders,
pseudo-content, or text after that block. If the exact ledger head or required
artifact content is unavailable, say so instead of inventing a packet.
