#!/usr/bin/env python3
"""Run explicit argv with bounded logs and provenance. This is not a sandbox.

Use authorized commands only. Never pass credentials in argv: it is recorded.
Environment variables are not dumped. Python 3.10+, standard library only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import threading
import time

from validate_manifest import validate


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def relative_path(root, name):
    path = Path(name)
    if path.is_absolute() or ".." in path.parts or not (root / path).resolve().is_relative_to(root):
        raise ValueError(f"path must stay inside project: {name}")
    current = root
    for part in path.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink not supported: {name}")
    return current


def git(root, *argv):
    try:
        run = subprocess.run(["git", "-C", str(root), *argv], capture_output=True, text=True, timeout=5)
        return run.stdout.strip() if run.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def execute(args):
    root = args.root.resolve()
    command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    if not root.is_dir() or not command:
        raise ValueError("existing root and explicit command argv required")
    if not math.isfinite(args.timeout) or args.timeout <= 0 or args.max_output_bytes < 1:
        raise ValueError("timeout and output limit must be finite and positive")
    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    if not isinstance(contract, dict) or not isinstance(contract.get("mathematics"), dict):
        raise ValueError("contract needs claim_id and mathematics")
    if not isinstance(contract.get("software", []), list):
        raise ValueError("contract software must be a list of version records")
    inputs = []
    for name in args.input:
        path = relative_path(root, name)
        if not path.is_file():
            raise ValueError(f"input missing: {name}")
        inputs.append({"path": path.relative_to(root).as_posix(), "sha256": sha(path)})
    if not inputs:
        raise ValueError("pin at least one --input, including executed project code and data")
    output = relative_path(root, args.output)
    if output.exists():
        raise ValueError("output directory already exists; each run needs a fresh directory")
    dirty = git(root, "status", "--porcelain")
    manifest = {
        "schema_version": 2, "claim_id": contract.get("claim_id"),
        "repository": {"commit": git(root, "rev-parse", "HEAD") or "unavailable", "dirty": dirty != ""},
        "command": command,
        "environment": {"software": [{"name": "runner-python", "version": platform.python_version()},
                                      *contract.get("software", [])], "hardware": platform.platform()},
        "mathematics": contract["mathematics"],
        "randomness": contract.get("randomness", {"used": False, "generator": "", "seed": None}),
        "run": {"started_at": datetime.now(timezone.utc).isoformat(), "runtime_seconds": 0, "exit_status": 0,
                "status": "completed", "timeout_seconds": args.timeout, "max_output_bytes": args.max_output_bytes},
        "input_artifacts": [dict(record, sha256_after=record["sha256"]) for record in inputs],
        "outputs": [{"path": "preflight", "sha256": "0" * 64}],
        "checks": [], "result": "Execution only; mathematical assertion not independently verified.",
        "residual_risks": ["Command success does not establish the mathematical interpretation.",
                           "Only listed input artifacts are pinned; external dependencies need recorded versions."]}
    errors = validate(manifest)
    if errors:
        raise ValueError("invalid contract: " + "; ".join(errors))
    output.mkdir(parents=True)
    start, count = time.monotonic(), [0]
    limit, io_failed, mutex = threading.Event(), [], threading.Lock()
    proc = None

    def stop():
        if proc is not None:
            try:
                if os.name == "posix":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
            except ProcessLookupError:
                pass

    def drain(pipe, destination):
        try:
            with destination.open("wb") as stream:
                while True:
                    data = pipe.read(8192)
                    if not data:
                        break
                    with mutex:
                        keep = max(0, args.max_output_bytes - count[0])
                        stream.write(data[:keep])
                        count[0] += min(keep, len(data))
                        if len(data) > keep:
                            limit.set()
                    if limit.is_set():
                        stop()
                        break
        except OSError as exc:
            io_failed.append(str(exc))
            stop()
        finally:
            pipe.close()

    threads = []
    try:
        proc = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=os.name == "posix")
        for pipe, name in ((proc.stdout, "stdout.txt"), (proc.stderr, "stderr.txt")):
            thread = threading.Thread(target=drain, args=(pipe, output / name), daemon=True)
            thread.start()
            threads.append(thread)
        try:
            proc.wait(timeout=args.timeout)
            for thread in threads:
                thread.join(timeout=max(0, args.timeout - (time.monotonic() - start)))
            if any(thread.is_alive() for thread in threads):
                raise subprocess.TimeoutExpired(command, args.timeout)
            manifest["run"]["status"] = "completed" if proc.returncode == 0 else "failed"
        except subprocess.TimeoutExpired:
            manifest["run"]["status"] = "timeout"
        finally:
            stop()
            proc.wait()
            for thread in threads:
                thread.join(timeout=2)
        manifest["run"]["exit_status"] = proc.returncode
    except OSError as exc:
        manifest["run"].update(status="launch-failed", exit_status=127)
        (output / "stderr.txt").write_text(str(exc), encoding="utf-8")
        (output / "stdout.txt").touch()
    if limit.is_set():
        manifest["run"]["status"] = "output-limit"
    if io_failed:
        manifest["run"]["status"] = "failed"
        manifest["residual_risks"].extend(io_failed)
    changed = []
    for record in inputs:
        try:
            current = sha(relative_path(root, record["path"]))
        except (OSError, ValueError):
            current = None
        record["sha256_after"] = current
        if current != record["sha256"]:
            changed.append(record["path"])
    if changed:
        manifest["residual_risks"].append("Input files changed during execution: " + ", ".join(changed))
        if manifest["run"]["status"] == "completed":
            manifest["run"]["status"] = "inputs-changed"
    manifest["run"]["runtime_seconds"] = round(time.monotonic() - start, 6)
    manifest["input_artifacts"] = inputs
    manifest["outputs"] = [{"path": (output / name).relative_to(root).as_posix(), "sha256": sha(output / name)}
                           for name in ("stdout.txt", "stderr.txt")]
    manifest["checks"] = [{"check": "input hashes unchanged", "passed": not changed},
                           {"check": "process completed within resource limits", "passed": manifest["run"]["status"] == "completed"}]
    manifest["result"] = f"Run {manifest['run']['status']}; mathematical assertion requires interpretation and review."
    destination = output / "manifest.json"
    destination.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = validate(manifest, root=root)
    if errors:
        raise ValueError("recorded run failed manifest validation: " + "; ".join(errors))
    return manifest, destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", required=True, help="new project-relative run directory")
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--max-output-bytes", type=int, default=4 * 1024 * 1024)
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    try:
        manifest, path = execute(args)
        print(json.dumps({"manifest": str(path), "status": manifest["run"]["status"]}))
        return 0 if manifest["run"]["status"] == "completed" else 1
    except (OSError, ValueError, TypeError) as exc:
        print(f"run-experiment: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
