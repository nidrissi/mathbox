# Adopt the ledger without rewriting a project

1. Inspect instructions, current claims and exact supporting artifacts. Resolve
   which files currently carry authority. Do not initialize a ledger merely
   because a project contains mathematics.
2. State a concrete mapping from existing claim IDs to exact ledger contracts.
   Preserve IDs where valid. Separate differently quantified/restricted claims;
   leave ambiguous historical assertions unresolved.
3. Under the user's authorized setup/edit scope, initialize `.mathbox/`. Record
   leaves before consumers. Pin only evidence actually checked against the claim;
   an old “proved” label without an accessible argument stays conjectural.
4. Import source checks and finite runs with their original scope and provenance.
   Do not manufacture independent review metadata or upgrade historical evidence.
5. Run brief `check` and `status` first, then compare the relevant exact claim
   contracts through full or JSON detail with the old claims file. Explain disagreements
   using evidence strength, never timestamps alone. If replacing the old view,
   preserve its substantive material and designate the new authority explicitly.
6. Keep the compact research log and existing immutable route records. The ledger
   stores claim/evidence transitions; the records store reusable mathematics.

Do not infer that an old launched process is still running. If lifecycle history
is useful, register a program and route run using an existing ledger event as `base_event` (the import checkpoint if no
historical event exists), and the historical commit in `base_revision`,
then add an `unknown` observation unless liveness was actually observed. Import
parallel proposals through the current ledger's single writer. Preserve each
run's base/result revision and record explicit conflicts; never infer precedence
from import order or merge two numbered event directories.

Migration is optional. A project can retain Markdown tables and use the same
evidence distinctions manually. There is deliberately no automatic prose parser
that turns confident historical summaries into proof events.

## Register archived originals

For byte-identical files already moved into an archive, use
[artifact relocations](ledger.md#artifact-relocations), not replacement evidence.
Immutable Markdown records may become the new live authority under project policy,
but cannot replace a historical LaTeX source pin unless they have exactly the
pinned bytes. Do not recreate the old paths, rewrite old events, edit a pinned
manifest, or issue another terminal result for a completed run.

Resolve the source checkout's supporting helper as `TOOL` and inspect its version
and the consumer's state without modifying that consumer:

```bash
python3 "$TOOL" --version
python3 "$TOOL" --root PROJECT --json check
python3 "$TOOL" --root PROJECT --json pin-impact proof/ls-malin-comparison/25-sl2-equivariant-ambiguity.tex
```

Only helper 1.1 or later with `artifact-relocation-v1` supports this workflow;
Mathbox 4.0.2 does not. Start from a reviewed `archive-map.json` of exact original
paths, archive locations and hashes, for example:

```json
[
  {
    "path": "proof/ls-malin-comparison/25-sl2-equivariant-ambiguity.tex",
    "destination": "archive/proof/2026-10-07/ls-malin-comparison/25-sl2-equivariant-ambiguity.tex",
    "sha256": "8e773356f5a51e088f23851b04bbb79547a855c2e56fb8c017e527e94d8f9f4c"
  }
]
```

The following standard-library script prepares a proposal array from active pin
references returned by the verified journal. It writes only the requested proposal
file. Set the actor and reason to the actual migration provenance before recording.
The map is selection input, not authority: unmatched hashes fail here, and recording
still independently checks each original event/slot and the actual destination bytes.

```bash
python3 - "$TOOL" PROJECT archive-map.json relocations.json <<'PY'
import json
from pathlib import Path
import subprocess
import sys

tool, root, mapping, output = sys.argv[1:]
proposals, selected = [], set()
for row in json.loads(Path(mapping).read_text(encoding="utf-8")):
    report = json.loads(subprocess.check_output(
        [sys.executable, tool, "--root", root, "--json", "pin-impact", row["path"]],
        text=True))
    refs = [ref for ref in report["references"]
            if Path(ref["path"]).as_posix() == Path(row["path"]).as_posix()
            and ref["sha256"] == row["sha256"]]
    if not refs:
        raise SystemExit(f"No recorded active pins match {row['path']} and its hash")
    pins = []
    for ref in refs:
        identity = (ref["event"], ref["slot"])
        if identity in selected or ref["relocation"] is not None:
            raise SystemExit(f"Duplicate or already relocated pin: {identity}; inspect replacements")
        selected.add(identity)
        pins.append({key: ref[key] for key in ("event", "slot", "path", "sha256")})
    proposals.append({"type": "artifact-relocation", "actor": "researcher", "payload": {
        "pins": pins, "destination": {"path": row["destination"], "sha256": row["sha256"]},
        "reason": "Original source moved unchanged into the immutable proof archive."}})
Path(output).write_text(json.dumps(proposals, indent=2) + "\n", encoding="utf-8")
print(f"Prepared {len(selected)} pin references in {len(proposals)} declarations")
PY
```

For inactive historical evidence or superseded claim revisions, inspect the original
events and construct explicit slots manually; active `pin-impact` intentionally
omits these. Registration does not reactivate them. A later move must name the
current declaration in each pin's `replaces`; never feed archive paths back into
the map as if they were original pin identities.

Preview and inspect all declarations, then append under the consumer project's
existing authorization. These commands register locations and never move files:

```bash
python3 "$TOOL" --root PROJECT --json record-batch relocations.json --dry-run
python3 "$TOOL" --root PROJECT record-batch relocations.json
python3 "$TOOL" --root PROJECT --json check
python3 "$TOOL" --root PROJECT check --summary
python3 "$TOOL" --root PROJECT status
python3 "$TOOL" --root PROJECT handoff --goal CLAIM
python3 "$TOOL" --root PROJECT next --full --goal CLAIM
python3 "$TOOL" --root PROJECT --json pin-impact archive/proof/2026-10-07/ls-malin-comparison/25-sl2-equivariant-ambiguity.tex
```

Count references separately from files. In a migration with 18 artifact references
on 17 completed runs and one computation-manifest input, all 19 exact pins need
coverage even when only 17 original files moved. Check that each run recovers its
original outcome and that any remaining snapshot, dependency or review conditions
remain visible. If a batch append is interrupted, inspect the committed prefix and
prepare only the remaining declarations; replaying already recorded declarations
is a conflict, not an idempotent update. The small
[synthetic fixture](../evals/fixtures/artifact-relocation.json) exercises three missing
originals and five references, including duplicate proof slots, a review and a
completed reconciled run, without real research proofs.

Consumer validators that deliberately assert historical missing-file failures
need an explicit successor policy. Native relocation support cannot repair a
validator that requires old failures to persist. In the motivating migration,
three previously missing computation outputs now exist and match their recorded
hashes: that is a separate validator-policy discrepancy. Preserve those outputs
and their hash checks; do not delete them to reproduce an obsolete failure count.
Review the consumer validator to accept verified archive references and currently
valid outputs while continuing to reject genuine integrity/freshness problems.
Implementing this Mathbox feature does not authorize applying that migration or
changing the consumer's policy.
