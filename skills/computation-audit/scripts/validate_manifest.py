#!/usr/bin/env python3
"""Validate computation evidence, or explicitly check an unfilled template."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

REQUIRED_TOP = {
    "schema_version",
    "claim_id",
    "repository",
    "command",
    "environment",
    "mathematics",
    "randomness",
    "run",
    "outputs",
    "checks",
    "result",
    "residual_risks",
}
REQUIRED_MATH = {
    "assertion_tested",
    "coefficient_domain",
    "conventions",
    "inputs",
    "bounds",
    "non_claims",
}


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(obj, template=False, root=None):
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    if not isinstance(obj, dict):
        return ["top level must be an object"]
    missing = REQUIRED_TOP - obj.keys()
    check(not missing, "missing required top-level fields: " + ", ".join(sorted(missing)))
    check(type(obj.get("schema_version")) is int and obj["schema_version"] in {1, 2}, "unsupported schema_version")
    maths = obj.get("mathematics")
    if not isinstance(maths, dict):
        return errors + ["mathematics must be an object"]
    missing = REQUIRED_MATH - maths.keys()
    check(not missing, "missing mathematics fields: " + ", ".join(sorted(missing)))
    for key in ("repository", "environment", "randomness", "run"):
        check(isinstance(obj.get(key), dict), f"{key} must be an object")
    for key in ("outputs", "checks", "residual_risks"):
        check(isinstance(obj.get(key), list), f"{key} must be an array")
    if errors or template:
        return errors

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    for key in ("claim_id", "result"):
        check(nonempty(obj.get(key)), f"{key} must be nonempty")
    command = obj.get("command")
    check(nonempty(command) or (isinstance(command, list) and bool(command) and all(nonempty(x) for x in command)),
          "command must be nonempty text or an argv array")
    for key in ("assertion_tested", "coefficient_domain", "conventions"):
        check(nonempty(maths.get(key)), f"mathematics.{key} must be nonempty")
    check(isinstance(maths.get("inputs"), list), "mathematics.inputs must be an array")
    check(isinstance(maths.get("bounds"), dict) and bool(maths["bounds"]), "mathematics.bounds must state the tested range")
    check(isinstance(maths.get("non_claims"), list) and bool(maths["non_claims"]) and all(nonempty(x) for x in maths["non_claims"]),
          "mathematics.non_claims must state the limits")
    check(type(obj["repository"].get("dirty")) is bool, "repository.dirty must be boolean")
    check(nonempty(obj["repository"].get("commit")), "repository.commit must be recorded (or explicitly unavailable)")
    software = obj["environment"].get("software")
    check(isinstance(software, list) and bool(software), "environment.software must record versions")
    for i, entry in enumerate(software if isinstance(software, list) else []):
        check(isinstance(entry, dict) and nonempty(entry.get("name")) and nonempty(entry.get("version")),
              f"environment.software[{i}] needs a name and a version")
    randomness = obj["randomness"]
    check(type(randomness.get("used")) is bool, "randomness.used must be boolean")
    if randomness.get("used"):
        check(nonempty(randomness.get("generator")) and randomness.get("seed") is not None, "random runs need generator and seed")
    run = obj["run"]
    check(nonempty(run.get("started_at")), "run.started_at must be recorded")
    runtime = run.get("runtime_seconds")
    check(type(runtime) in {float, int} and math.isfinite(runtime) and runtime >= 0, "runtime must be finite and nonnegative")
    check(type(run.get("exit_status")) is int, "run.exit_status must be an integer")
    check(bool(obj["outputs"]), "outputs must include hashed artifacts")
    for i, output in enumerate(obj["outputs"]):
        if not isinstance(output, dict):
            errors.append(f"outputs[{i}] must be an object")
            continue
        path, checksum = output.get("path"), output.get("sha256")
        check(nonempty(path), f"outputs[{i}].path must be nonempty")
        valid_hash = isinstance(checksum, str) and bool(re.fullmatch(r"[0-9a-f]{64}", checksum))
        check(valid_hash, f"outputs[{i}].sha256 must be SHA-256")
        if root is not None and nonempty(path) and valid_hash:
            source = Path(path)
            if source.is_absolute() or ".." in source.parts or not (root / source).resolve().is_relative_to(root.resolve()):
                errors.append(f"output escapes project: {path}")
            elif not (root / source).is_file():
                errors.append(f"output missing: {path}")
            elif file_hash(root / source) != checksum:
                errors.append(f"output changed: {path}")
    if obj.get("schema_version") == 2:
        check(run.get("status") in {"completed", "failed", "timeout", "output-limit", "launch-failed", "inputs-changed"}, "invalid run.status")
        if run.get("status") == "completed":
            check(run.get("exit_status") == 0, "completed run must have zero exit status")
        check(isinstance(obj.get("input_artifacts"), list) and bool(obj["input_artifacts"]), "v2 needs input_artifacts")
        for artifact in obj.get("input_artifacts", []) if isinstance(obj.get("input_artifacts"), list) else []:
            if not isinstance(artifact, dict):
                errors.append("input artifact must be an object")
                continue
            path, before, after = artifact.get("path"), artifact.get("sha256"), artifact.get("sha256_after")
            check(nonempty(path), "input artifact needs a path")
            valid_before = isinstance(before, str) and bool(re.fullmatch(r"[0-9a-f]{64}", before))
            valid_after = after is None or (isinstance(after, str) and bool(re.fullmatch(r"[0-9a-f]{64}", after)))
            check(valid_before and valid_after and "sha256_after" in artifact, "input artifact needs before/after hashes")
            if run.get("status") == "completed":
                check(before == after and after is not None, "completed run cannot have changed input hashes")
            if root is not None and nonempty(path):
                source = Path(path)
                if source.is_absolute() or ".." in source.parts or not (root / source).resolve().is_relative_to(root.resolve()):
                    errors.append(f"input escapes project: {path}")
                elif not (root / source).is_file():
                    # An absent input cannot corroborate the record, whatever was hashed.
                    errors.append(f"pinned input is missing: {path}")
                else:
                    check(file_hash(root / source) == after, f"input changed since the run: {path}")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--template", action="store_true", help="allow deliberately unfilled scaffold fields")
    parser.add_argument("--root", type=Path, help="also verify output hashes relative to this project")
    args = parser.parse_args(argv)
    try:
        errors = validate(json.loads(args.manifest.read_text(encoding="utf-8")), args.template, args.root)
    except (OSError, ValueError, TypeError) as exc:
        errors = [str(exc)]
    if errors:
        print("invalid manifest: " + "; ".join(errors), file=sys.stderr)
        return 1
    print("valid template" if args.template else "valid evidence record; mathematical interpretation requires review")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
