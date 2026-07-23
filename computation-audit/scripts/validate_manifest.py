#!/usr/bin/env python3
"""Validate the minimal structure of a math-research computation manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path

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


def fail(message: str) -> int:
    print(f"invalid manifest: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_manifest.py MANIFEST.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return fail(str(exc))
    except json.JSONDecodeError as exc:
        return fail(f"JSON error at line {exc.lineno}, column {exc.colno}: {exc.msg}")
    if not isinstance(obj, dict):
        return fail("top level must be an object")
    missing = REQUIRED_TOP - obj.keys()
    if missing:
        return fail("missing top-level keys: " + ", ".join(sorted(missing)))
    if obj["schema_version"] != 1:
        return fail("schema_version must be 1")
    if not isinstance(obj["mathematics"], dict):
        return fail("mathematics must be an object")
    missing_math = REQUIRED_MATH - obj["mathematics"].keys()
    if missing_math:
        return fail("missing mathematics keys: " + ", ".join(sorted(missing_math)))
    if not isinstance(obj["outputs"], list):
        return fail("outputs must be a list")
    for index, output in enumerate(obj["outputs"]):
        if not isinstance(output, dict) or not {"path", "sha256"} <= output.keys():
            return fail(f"outputs[{index}] must contain path and sha256")
    print(f"valid computation manifest: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
