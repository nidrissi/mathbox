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

`artifacts` contains complete UTF-8 text for **new** project-relative files.
Paths cannot escape the project, traverse symlinks, or enter `.mathbox/`.
Existing files cannot be replaced. Do not embed the conversation; write the
actual durable proof, report, or route record. Keep licensed or private source
material under its existing retention policy.

`index_append` is either `null` or one guarded append to an **existing** UTF-8
index. `expected_tail` is the exact last line, including its newline; use `""`
only for an empty index. `content` is one complete, nonempty line ending in a
newline. The index guard rejects a changed tail. Use the project's designated
route index and follow its immutable-entry convention.

`proposals` is a nonempty `record-batch` proposal list in dependency order.
The same `alias` and `{"$event":"alias"}` references work within the packet.
Proposals omit generated event IDs, timestamps, hashes, snapshots, and manifest
closure fields. The helper supplies them, checks proposal validity, and pins
staged artifacts from their exact UTF-8 bytes. Existing artifacts may also be
referenced. A packet does not certify the mathematics in those artifacts.

This version does not accept arbitrary file replacements, deletes, binary data,
commands, or patches. A workflow that needs edits to existing live files must
handle those edits separately under the project's normal authority rules.

## Local ingest

After resolving this skill's `scripts/research_state.py` as `TOOL`:

```bash
python3 "$TOOL" --root PROJECT ingest PACKET.json --dry-run
python3 "$TOOL" --root PROJECT ingest PACKET.json
python3 "$TOOL" --root PROJECT ingest -
```

The last form reads one JSON packet from standard input. The default receipt
lists proposed or recorded events and pins; `--json` before `ingest` prints
the complete events. Dry-run takes the writer lock and validates the whole
packet without leaving files or events. Ingest validates everything under that
lock, creates each artifact atomically, replaces the index atomically with its
old bytes plus the new entry, then appends the prepared events. An I/O failure
may leave created artifacts, the index entry, or a valid prefix of events.
Inspect the project and journal head before any retry. The original packet will
usually fail its base guard after even one event was appended.

## Response shape

Give the mathematical finding and its limits in ordinary prose. State that the
packet has **not** been applied. Make the complete packet the last fenced block
in the response, using a `json` fence. Include no ellipses, placeholders,
pseudo-content, or text after that block. If the exact ledger head or required
artifact content is unavailable, say so instead of inventing a packet.
