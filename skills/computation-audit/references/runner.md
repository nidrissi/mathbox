# Reproducible bounded runs

Use `scripts/run_experiment.py` only for a command the user has authorized. It
is a provenance helper, not a sandbox or mathematical oracle. It does not fetch
dependencies, execute commands from manifests, capture environment variables,
or install SageMath/other software.

Create a contract JSON with these fields (this is a concrete small example):

```json
{
  "claim_id": "C_PARITY",
  "mathematics": {
    "assertion_tested": "n(n+1) is even for each tested n",
    "coefficient_domain": "Z, exact integers",
    "conventions": "ordinary integer multiplication",
    "inputs": ["checks/parity.py"],
    "bounds": {"n_min": -100, "n_max": 100},
    "non_claims": ["Does not establish the assertion for all integers"]
  },
  "execution_artifacts": ["checks/parity.py"],
  "software": [{"name": "computation Python", "version": "record actual version"}],
  "randomness": {"used": false, "generator": "", "seed": null}
}
```

Record actual software versions in a real contract: `software` is required and
each entry needs a name and a version. The runner records its own interpreter
separately and cannot infer the version of the program it launches. State a
seed and generator when random sampling is used; the runner records them but
does not configure the child program's RNG.

`mathematics.inputs` describes mathematical inputs and may include objects or
families that are not files. The optional top-level `execution_artifacts` is a
machine-checkable list of project-relative code, import, convention, and data
files. When it is present, it must exactly match the repeated `--input` paths;
when absent, the manifest reports that this cross-check was unavailable. The
runner cannot infer the dependency closure of arbitrary programs or authenticate
a declared mathematical bound.

```bash
python3 "$SKILL_DIR/scripts/run_experiment.py" \
  --root /path/to/project --contract /path/to/project/contract.json \
  --input checks/parity.py --output computations/parity-001 \
  --result computations/parity-001/table.json \
  --timeout 30 --max-output-bytes 1048576 \
  --max-memory-bytes 1073741824 --max-cpu-seconds 20 \
  --max-cores 1 --max-threads 1 -- python3 checks/parity.py
python3 "$SKILL_DIR/scripts/validate_manifest.py" \
  /path/to/project/computations/parity-001/manifest.json --root /path/to/project
```

The example assumes `checks/parity.py` itself creates
`computations/parity-001/table.json`; `--result` declares and checks that file but
does not redirect stdout or synthesize the result.

`SKILL_DIR` is the resolved installed computation-audit directory, not a guessed
path inside the research project. The output directory must be new and inside
the project. Every repeated `--result` is a project-relative regular file that
the command must create below that fresh directory. Results cannot be inputs or
runner-owned `manifest.json`, `stdout.txt`, or `stderr.txt`; missing, symlinked,
or non-file results make an otherwise successful run unsuccessful. These rules
prevent overwriting an input or pre-existing scientific result.

The command uses project root as its working directory and runs as an argv array
with `shell=False`. Shell pipelines need an explicitly authorized shell
invocation. Do not put credentials in argv or emitted logs.

The runner writes `stdout.txt`, `stderr.txt`, `manifest.json`, and any command-
generated result files. It hashes declared results only after the child exits.
It records the Git commit and dirty state, supplied-input hashes before and after
execution, UTC start, elapsed time, process exit code, effective limits, and
actual run status. When a parent process already has a stricter hard limit, the
manifest records the effective enforced limit. It is written atomically after it
validates.

Wall-clock time and combined log bytes are always bounded. The following caps
are optional:

- `--max-memory-bytes` uses POSIX `RLIMIT_AS` and bounds each process's address
  space. A program can turn allocation failure into an ordinary nonzero exit, so
  the manifest reports that ambiguity rather than claiming an out-of-memory event.
- `--max-cpu-seconds` uses POSIX `RLIMIT_CPU`. It is inherited but is a per-process,
  not aggregate-process-tree, CPU budget. A matching limit signal receives
  `resource-limit`; a hard-limit `SIGKILL` is recorded as consistent with, but
  not uniquely diagnostic of, that cap.
- `--max-cores` restricts inherited CPU affinity where the platform provides it.
  The recorded number is the effective cap after any stricter parent affinity.
- `--max-threads` sets conventional numerical-library thread variables in the
  child environment. Libraries may ignore them, so the manifest keeps that risk.

Unsupported requested POSIX limits fail before the output directory is created;
no requested hard limit is silently dropped. On POSIX, timeout or log overflow
kills the process group including descendants. If the kernel refuses that signal,
the runner terminates the direct process and records the surviving-descendant
risk. On other platforms, termination is limited to the direct process; use an
appropriate project runner for process trees.

Statuses distinguish `completed`, `failed`, `timeout`, `output-limit`,
`launch-failed`, `inputs-changed`, `resource-limit`, `result-missing`, and
`result-invalid`. A command failure remains the primary status even if it also
omits a declared result; the missing result and failed check remain explicit in
the record. Exit codes: 0 completed; 1 recorded unsuccessful run; 2 invalid input
or recording failure. A failed run can be a valid provenance record. Even a
completed run requires review of the implemented assertion and output before
being registered as finite evidence. It never automatically records a proof.

Version 2 is emitted by the runner and requires structured software
`name`/`version` records plus input provenance. Historical version 1 records may
instead contain nonempty human-readable software version strings and may lack a
repository revision. The validator accepts those historical shapes and reports
the missing provenance rather than inventing it.

With `--root`, a v1 output path is resolved against the project root first. Only
when that file is absent may it fall back to the manifest directory, and the
successful validation reports the fallback. If distinct files exist at both
interpretations, validation rejects the ambiguous record. V2 output paths are
always project-relative.

The validator reports that v1 cannot establish execution-input freshness,
declared-result completeness, or machine-checkable resource limits. This is
compatibility, not an evidence upgrade: both versions still reject empty outputs,
invalid hashes, missing bounds, and incomplete run metadata.

Unfilled templates must be checked with `validate_manifest.py --template`;
they are not evidence. `--root` additionally checks stored output hashes and,
for v2, whether pinned inputs still match the end of the run.
