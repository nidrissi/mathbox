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

try:
    import resource
except ImportError:  # pragma: no cover - the guarded paths are POSIX-only
    resource = None

from validate_manifest import validate


THREAD_LIMIT_VARIABLES = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "BLIS_NUM_THREADS",
)
RESERVED_RUN_FILES = {"manifest.json", "stdout.txt", "stderr.txt"}


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


def positive_limit(value, name):
    if value is not None and (type(value) is not int or value < 1):
        raise ValueError(f"{name} must be a positive integer")
    return value


def resource_configuration(args):
    """Return recorded limits, child setup, and child environment."""
    requested_memory = positive_limit(getattr(args, "max_memory_bytes", None), "max memory")
    requested_cpu = positive_limit(getattr(args, "max_cpu_seconds", None), "max CPU time")
    requested_cores = positive_limit(getattr(args, "max_cores", None), "max cores")
    requested_threads = positive_limit(getattr(args, "max_threads", None), "max threads")

    if (requested_memory or requested_cpu) and (os.name != "posix" or resource is None):
        raise ValueError("memory and CPU limits require POSIX resource limits")
    if requested_memory and not hasattr(resource, "RLIMIT_AS"):
        raise ValueError("address-space limits are unavailable on this platform")
    if requested_cpu and not hasattr(resource, "RLIMIT_CPU"):
        raise ValueError("CPU-time limits are unavailable on this platform")

    affinity = None
    if requested_cores:
        if os.name != "posix" or not hasattr(os, "sched_getaffinity") or not hasattr(os, "sched_setaffinity"):
            raise ValueError("CPU affinity limits are unavailable on this platform")
        available = sorted(os.sched_getaffinity(0))
        if not available:
            raise ValueError("no CPUs are available to the runner")
        affinity = available[:requested_cores]

    effective_memory = requested_memory
    effective_cpu = requested_cpu
    if requested_memory:
        _, inherited_hard = resource.getrlimit(resource.RLIMIT_AS)
        if inherited_hard != resource.RLIM_INFINITY:
            effective_memory = min(requested_memory, inherited_hard)
    if requested_cpu:
        _, inherited_hard = resource.getrlimit(resource.RLIMIT_CPU)
        if inherited_hard != resource.RLIM_INFINITY:
            effective_cpu = min(requested_cpu, inherited_hard)

    def configure_child():
        if effective_memory:
            resource.setrlimit(resource.RLIMIT_AS, (effective_memory, effective_memory))
        if effective_cpu:
            _, inherited_hard = resource.getrlimit(resource.RLIMIT_CPU)
            hard = effective_cpu + 1
            if inherited_hard != resource.RLIM_INFINITY:
                hard = min(hard, inherited_hard)
            hard = max(effective_cpu, hard)
            resource.setrlimit(resource.RLIMIT_CPU, (effective_cpu, hard))
        if affinity:
            os.sched_setaffinity(0, affinity)

    child_environment = None
    if requested_threads:
        child_environment = os.environ.copy()
        for variable in THREAD_LIMIT_VARIABLES:
            child_environment[variable] = str(requested_threads)

    recorded = {
        "memory_bytes": effective_memory,
        "cpu_seconds": effective_cpu,
        "max_cores": len(affinity) if affinity else None,
        "max_threads": requested_threads,
    }
    needs_child_setup = bool(effective_memory or effective_cpu or affinity)
    return recorded, configure_child if needs_child_setup else None, child_environment


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
    software = contract.get("software")
    if not isinstance(software, list) or not software:
        raise ValueError("contract software must list the computation's own version records")
    inputs = []
    input_names = set()
    for name in args.input:
        path = relative_path(root, name)
        if not path.is_file():
            raise ValueError(f"input missing: {name}")
        normalized = path.relative_to(root).as_posix()
        if normalized in input_names:
            raise ValueError(f"input listed more than once: {normalized}")
        input_names.add(normalized)
        inputs.append({"path": normalized, "sha256": sha(path)})
    if not inputs:
        raise ValueError("pin at least one --input, including executed project code and data")

    contract_artifacts = contract.get("execution_artifacts")
    if contract_artifacts is not None:
        if not isinstance(contract_artifacts, list) or not contract_artifacts:
            raise ValueError("contract execution_artifacts must be a nonempty array of project-relative files")
        declared_inputs = []
        for name in contract_artifacts:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("contract execution_artifacts must contain nonempty paths")
            path = relative_path(root, name)
            declared_inputs.append(path.relative_to(root).as_posix())
        if len(declared_inputs) != len(set(declared_inputs)):
            raise ValueError("contract execution_artifacts contains duplicate paths")
        if set(declared_inputs) != input_names:
            raise ValueError("contract execution_artifacts must exactly match the repeated --input paths")

    output = relative_path(root, args.output)
    if output.exists():
        raise ValueError("output directory already exists; each run needs a fresh directory")
    output_name = output.relative_to(root).as_posix()
    declared_results = []
    for name in getattr(args, "result", []):
        path = relative_path(root, name)
        try:
            within_output = path.relative_to(output)
        except ValueError as exc:
            raise ValueError(f"declared result must be inside the fresh output directory: {name}") from exc
        if not within_output.parts:
            raise ValueError(f"declared result must be a file below the output directory: {name}")
        if len(within_output.parts) == 1 and within_output.name in RESERVED_RUN_FILES:
            raise ValueError(f"declared result collides with a runner-owned file: {name}")
        normalized = path.relative_to(root).as_posix()
        if normalized in declared_results:
            raise ValueError(f"result listed more than once: {normalized}")
        if normalized in input_names:
            raise ValueError(f"declared result cannot also be an input: {normalized}")
        if path.exists():
            raise ValueError(f"declared result already exists: {normalized}")
        declared_results.append(normalized)

    resource_limits, configure_child, child_environment = resource_configuration(args)
    dirty = git(root, "status", "--porcelain")
    residual_risks = [
        "Command success does not establish the mathematical interpretation.",
        "Only listed input artifacts are pinned; external dependencies need recorded versions.",
    ]
    if contract_artifacts is None:
        residual_risks.append(
            "The contract did not declare execution_artifacts, so its artifact list was not checked against --input."
        )
    if resource_limits["max_threads"]:
        residual_risks.append(
            "The thread cap uses conventional environment variables; a child program may ignore them."
        )
    if resource_limits["cpu_seconds"]:
        residual_risks.append("The POSIX CPU-time limit is per process, not an aggregate descendant budget.")
    manifest = {
        "schema_version": 2, "claim_id": contract.get("claim_id"),
        "repository": {"commit": git(root, "rev-parse", "HEAD") or "unavailable", "dirty": dirty != ""},
        "command": command,
        "environment": {"software": [{"name": "runner-python", "version": platform.python_version()},
                                      *software], "hardware": platform.platform()},
        "mathematics": contract["mathematics"],
        "randomness": contract.get("randomness", {"used": False, "generator": "", "seed": None}),
        "run": {"started_at": datetime.now(timezone.utc).isoformat(), "runtime_seconds": 0, "exit_status": 1,
                "status": "failed", "timeout_seconds": args.timeout, "max_output_bytes": args.max_output_bytes,
                "resource_limits": resource_limits},
        "execution_artifacts": [record["path"] for record in inputs],
        "input_artifacts": [dict(record, sha256_after=record["sha256"]) for record in inputs],
        "output_directory": output_name,
        "declared_results": declared_results,
        "outputs": [{"path": f"{output_name}/stdout.txt", "sha256": "0" * 64, "kind": "log"},
                    {"path": f"{output_name}/stderr.txt", "sha256": "0" * 64, "kind": "log"}],
        "checks": [], "result": "Execution only; mathematical assertion not independently verified.",
        "residual_risks": residual_risks}
    errors = validate(manifest)
    if errors:
        raise ValueError("invalid contract: " + "; ".join(errors))
    output.mkdir(parents=True)
    start, count = time.monotonic(), [0]
    limit, io_failed, mutex = threading.Event(), [], threading.Lock()
    unterminated, proc, threads = [], None, []

    def stop():
        # Signal the group only while a member is provably alive. A reaped child
        # with no live pipe writer no longer owns the group ID, so signalling it
        # could reach an unrelated group that reused the PID.
        if proc is None or (proc.poll() is not None and not any(t.is_alive() for t in threads)):
            return
        try:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except ProcessLookupError:
            pass
        except OSError as exc:
            unterminated.append(f"Process-group termination failed, descendants may survive: {exc}")
            try:
                proc.kill()
            except OSError:
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

    # Only a failed launch is recorded as launch-failed; a later error must never
    # overwrite the logs and status of a command that actually ran.
    try:
        popen_options = {
            "cwd": root,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "start_new_session": os.name == "posix",
        }
        if configure_child is not None:
            popen_options["preexec_fn"] = configure_child
        if child_environment is not None:
            popen_options["env"] = child_environment
        proc = subprocess.Popen(command, **popen_options)
    except (OSError, subprocess.SubprocessError) as exc:
        manifest["run"].update(status="launch-failed", exit_status=127)
        (output / "stderr.txt").write_text(str(exc), encoding="utf-8")
        (output / "stdout.txt").touch()
    else:
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
        cpu_signal = getattr(signal, "SIGXCPU", None)
        if (cpu_signal is not None and manifest["run"]["status"] == "failed"
                and resource_limits["cpu_seconds"] and proc.returncode == -cpu_signal):
            manifest["run"]["status"] = "resource-limit"
            manifest["residual_risks"].append("The child reached its POSIX CPU-time limit.")
        elif (manifest["run"]["status"] == "failed" and resource_limits["cpu_seconds"]
              and proc.returncode == -signal.SIGKILL):
            manifest["run"]["status"] = "resource-limit"
            manifest["residual_risks"].append(
                "SIGKILL is consistent with the CPU hard limit but cannot distinguish it from an external kill."
            )
    if limit.is_set():
        manifest["run"]["status"] = "output-limit"
    if io_failed:
        manifest["run"]["status"] = "failed"
        manifest["residual_risks"].extend(io_failed)
    manifest["residual_risks"].extend(sorted(set(unterminated)))
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
    try:
        safe_output = relative_path(root, output_name)
    except ValueError as exc:
        raise ValueError("run output directory became unsafe; refusing to write a manifest") from exc
    if not safe_output.is_dir():
        raise ValueError("run output directory was removed or replaced; refusing to write a manifest")
    manifest["outputs"] = [
        {"path": (output / name).relative_to(root).as_posix(), "sha256": sha(output / name), "kind": "log"}
        for name in ("stdout.txt", "stderr.txt")
    ]
    missing_results, invalid_results = [], []
    for normalized in declared_results:
        try:
            result_path = relative_path(root, normalized)
        except ValueError:
            invalid_results.append(normalized)
            continue
        if not result_path.exists():
            missing_results.append(normalized)
        elif not result_path.is_file():
            invalid_results.append(normalized)
        else:
            manifest["outputs"].append({"path": normalized, "sha256": sha(result_path), "kind": "result"})
    if invalid_results:
        manifest["residual_risks"].append("Declared results were not safe regular files: " + ", ".join(invalid_results))
        if manifest["run"]["status"] == "completed":
            manifest["run"]["status"] = "result-invalid"
    if missing_results:
        manifest["residual_risks"].append("Declared results were not produced: " + ", ".join(missing_results))
        if manifest["run"]["status"] == "completed":
            manifest["run"]["status"] = "result-missing"
    manifest["run"]["missing_results"] = missing_results
    manifest["run"]["invalid_results"] = invalid_results
    if resource_limits["memory_bytes"] and manifest["run"]["status"] == "failed":
        manifest["residual_risks"].append(
            "A nonzero exit under an address-space cap does not by itself show whether the cap was reached."
        )
    process_ok = manifest["run"]["exit_status"] == 0 and manifest["run"]["status"] not in {
        "timeout", "output-limit", "launch-failed", "resource-limit"
    }
    manifest["checks"] = [
        {"check": "input hashes unchanged", "passed": not changed},
        {"check": "process exited successfully within enforced limits", "passed": process_ok},
        {"check": "declared result files are present and regular", "passed": not missing_results and not invalid_results},
    ]
    manifest["result"] = f"Run {manifest['run']['status']}; mathematical assertion requires interpretation and review."
    destination = output / "manifest.json"
    errors = validate(manifest, root=root)
    if errors:
        raise ValueError("recorded run failed manifest validation: " + "; ".join(errors))
    temporary = output / ".manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, destination)
    return manifest, destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", required=True, help="new project-relative run directory")
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--result", action="append", default=[],
                        help="project-relative result file below the fresh output directory")
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--max-output-bytes", type=int, default=4 * 1024 * 1024)
    parser.add_argument("--max-memory-bytes", type=int, help="POSIX child address-space cap")
    parser.add_argument("--max-cpu-seconds", type=int, help="POSIX per-process CPU-time cap")
    parser.add_argument("--max-cores", type=int, help="POSIX CPU-affinity cap where supported")
    parser.add_argument("--max-threads", type=int,
                        help="set conventional numerical-library thread environment caps")
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
