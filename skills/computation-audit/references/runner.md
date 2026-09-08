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
  "software": [{"name": "computation Python", "version": "record actual version"}],
  "randomness": {"used": false, "generator": "", "seed": null}
}
```

Record actual software versions in a real contract: `software` is required and
each entry needs a name and a version. The runner records its own interpreter
separately and cannot infer the version of the program it launches. State a
seed and generator when random sampling is used; the runner records
them but does not configure the child program's RNG. Pin executed project code,
imports, convention files and data explicitly with repeated `--input`. It cannot
infer the full dependency closure of arbitrary programs or authenticate a
declared bound.

```bash
python3 "$SKILL_DIR/scripts/run_experiment.py" \
  --root /path/to/project --contract /path/to/project/contract.json \
  --input checks/parity.py --output computations/parity-001 \
  --timeout 30 --max-output-bytes 1048576 -- python3 checks/parity.py
python3 "$SKILL_DIR/scripts/validate_manifest.py" \
  /path/to/project/computations/parity-001/manifest.json --root /path/to/project
```

`SKILL_DIR` is the resolved installed computation-audit directory, not a guessed
path inside the research project. The output directory must be new and inside
the project. The command runs there with project root as its working directory,
as an argv array with `shell=False`. Shell pipelines need an explicitly
authorized shell invocation. Do not put credentials in argv or emitted logs.

The runner writes `stdout.txt`, `stderr.txt`, and `manifest.json`. It records the
Git commit and dirty state, hashes of supplied inputs before and after execution,
UTC start, elapsed time, process exit code, resource bounds and actual run status.
Logs have a combined byte limit. On POSIX, timeout/output overflow kills the
process group including descendants. If the kernel refuses that signal, the
runner terminates the direct process and records the surviving-descendant risk.
On other platforms, termination is limited to the direct process; use an
appropriate project runner for process trees.

Statuses distinguish completed, failed, timeout, output-limit, launch-failed and
inputs-changed. Exit codes: 0 completed; 1 recorded unsuccessful run; 2 invalid
input or recording failure. A failed run can be a valid provenance record. Even
a completed run requires review of the implemented assertion and output before
being registered as finite evidence. It never automatically records a proof.

Version 2 is emitted by the runner. Complete version 1 evidence records remain
valid. Unfilled templates must be checked with `validate_manifest.py --template`;
the default rejects empty statements, missing bounds, absent versions, incomplete
run metadata and invalid hashes. `--root` additionally checks stored outputs and whether pinned inputs still match the end of the run.
