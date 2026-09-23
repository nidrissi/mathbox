import argparse
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import unittest
from unittest import mock

from run_experiment import execute, main as run_main, sha
from validate_manifest import legacy_limits, main as validate_main, validate


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.contract = self.root / "contract.json"
        self.contract.write_text(json.dumps({"claim_id":"A", "mathematics":{
            "assertion_tested":"The listed integer products are even", "coefficient_domain":"Z",
            "conventions":"ordinary multiplication", "inputs":["run.py"], "bounds":{"n":[0,20]},
            "non_claims":["Not a universal proof"]},
            "execution_artifacts":["run.py"],
            "software":[{"name":"computation Python", "version":sys.version.split()[0]}]}))
        self.code = self.root / "run.py"
        self.code.write_text("assert all(n*(n+1)%2 == 0 for n in range(21))\nprint('21 cases checked')\n")

    def args(self, **extra):
        values = dict(root=self.root, contract=self.contract, output="runs/one", input=["run.py"],
                      result=[], timeout=2.0, max_output_bytes=4096, max_memory_bytes=None,
                      max_cpu_seconds=None, max_cores=None, max_threads=None,
                      argv=["--", sys.executable, "run.py"])
        values.update(extra)
        return argparse.Namespace(**values)

    def test_actual_run_records_hashes_and_no_automatic_proof(self):
        manifest, path = execute(self.args())
        self.assertEqual(manifest["run"]["status"], "completed")
        self.assertEqual(manifest["command"], [sys.executable, "run.py"])
        self.assertEqual(manifest["input_artifacts"][0]["sha256"], manifest["input_artifacts"][0]["sha256_after"])
        self.assertEqual(validate(manifest, root=self.root), [])
        self.assertTrue(path.exists())
        self.assertEqual(manifest["mathematics"]["bounds"], {"n":[0,20]})
        self.assertEqual(manifest["execution_artifacts"], ["run.py"])

    def test_failed_assertion_is_recorded_failure(self):
        self.code.write_text("assert False, 'mathematical benchmark failed'\n")
        manifest, _ = execute(self.args())
        self.assertEqual(manifest["run"]["status"], "failed")
        self.assertNotEqual(manifest["run"]["exit_status"], 0)
        self.assertEqual(validate(manifest), [])

    def test_timeout_has_manifest(self):
        self.code.write_text("import time\ntime.sleep(30)\n")
        manifest, path = execute(self.args(timeout=0.1))
        self.assertEqual(manifest["run"]["status"], "timeout")
        self.assertTrue(path.exists())
        self.assertLess(manifest["run"]["runtime_seconds"], 5)

    def test_unbounded_output_is_stopped(self):
        self.code.write_text("while True: print('x' * 1000)\n")
        manifest, _ = execute(self.args(max_output_bytes=1000))
        self.assertEqual(manifest["run"]["status"], "output-limit")
        total = sum((self.root / o["path"]).stat().st_size for o in manifest["outputs"])
        self.assertLessEqual(total, 1000)

    def test_input_mutation_is_not_completed_evidence(self):
        self.code.write_text("from pathlib import Path\nPath('run.py').write_text('changed')\n")
        manifest, _ = execute(self.args())
        self.assertEqual(manifest["run"]["status"], "inputs-changed")

    def test_launch_failure_is_recorded(self):
        manifest, _ = execute(self.args(argv=["no-such-mathbox-test-executable"]))
        self.assertEqual(manifest["run"]["status"], "launch-failed")
        self.assertEqual(manifest["run"]["exit_status"], 127)

    def test_never_overwrites_a_run(self):
        _, path = execute(self.args())
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            execute(self.args())
        self.assertEqual(path.read_bytes(), before)

    def test_empty_template_rejected_as_evidence(self):
        template = json.loads((Path(__file__).parents[1] / "assets/computation-manifest.json").read_text())
        self.assertTrue(validate(template))
        self.assertEqual(validate(template, template=True), [])

    def test_tampered_logs_fail_validation(self):
        manifest, _ = execute(self.args())
        (self.root / manifest["outputs"][0]["path"]).write_text("forged success")
        self.assertTrue(validate(manifest, root=self.root))

    def test_declared_scientific_result_is_hashed_and_tampering_is_detected(self):
        self.code.write_text(
            "from pathlib import Path\n"
            "Path('runs/one/table.json').write_text('{\\\"verified_cases\\\": 21}\\n')\n"
        )
        manifest, _ = execute(self.args(result=["runs/one/table.json"]))
        self.assertEqual(manifest["run"]["status"], "completed")
        result = next(output for output in manifest["outputs"] if output.get("kind") == "result")
        self.assertEqual(result["path"], "runs/one/table.json")
        self.assertEqual(result["sha256"], sha(self.root / result["path"]))
        (self.root / result["path"]).write_text("changed\n")
        self.assertTrue(validate(manifest, root=self.root))

    def test_cli_accepts_declared_results(self):
        self.code.write_text(
            "from pathlib import Path\n"
            "Path('runs/one/result.txt').write_text('synthetic result\\n')\n"
        )
        output = io.StringIO()
        with redirect_stdout(output):
            code = run_main([
                "--root", str(self.root), "--contract", str(self.contract),
                "--output", "runs/one", "--input", "run.py",
                "--result", "runs/one/result.txt", "--", sys.executable, "run.py",
            ])
        self.assertEqual(code, 0)
        response = json.loads(output.getvalue())
        self.assertEqual(response["status"], "completed")
        manifest = json.loads(Path(response["manifest"]).read_text())
        self.assertEqual(manifest["declared_results"], ["runs/one/result.txt"])

    def test_missing_or_nonregular_declared_result_has_specific_status(self):
        missing, _ = execute(self.args(result=["runs/one/missing.json"]))
        self.assertEqual(missing["run"]["status"], "result-missing")
        self.assertEqual(missing["run"]["missing_results"], ["runs/one/missing.json"])

        self.code.write_text("from pathlib import Path\nPath('runs/two/a-directory').mkdir(parents=True)\n")
        invalid, _ = execute(self.args(output="runs/two", result=["runs/two/a-directory"]))
        self.assertEqual(invalid["run"]["status"], "result-invalid")
        self.assertEqual(invalid["run"]["invalid_results"], ["runs/two/a-directory"])

    def test_result_paths_cannot_escape_or_collide_with_runner_files(self):
        for result in (["result.json"], ["runs/one/stdout.txt"], ["runs/one/manifest.json"],
                       ["runs/one"], ["runs/one/result.json", "runs/one/result.json"]):
            with self.assertRaises(ValueError):
                execute(self.args(result=result))
        self.assertFalse((self.root / "runs").exists())

    def test_stale_or_missing_input_provenance_is_detected(self):
        manifest, _ = execute(self.args())
        malformed = copy.deepcopy(manifest)
        malformed["input_artifacts"] = [{}]
        self.assertTrue(validate(malformed))
        self.code.write_text("print('different computation')")
        self.assertTrue(validate(manifest, root=self.root))

    def test_contract_failure_has_no_run_side_effect(self):
        self.contract.write_text('{}')
        with self.assertRaises(ValueError):
            execute(self.args())
        self.assertFalse((self.root / "runs").exists())

    def test_declared_execution_artifacts_must_match_cli_pins(self):
        contract = json.loads(self.contract.read_text())
        contract["execution_artifacts"] = ["run.py", "missing-data.json"]
        self.contract.write_text(json.dumps(contract))
        with self.assertRaises(ValueError):
            execute(self.args())
        self.assertFalse((self.root / "runs").exists())

    def test_command_metacharacters_remain_literal(self):
        self.code.write_text("import sys\nassert sys.argv[1] == '$(touch injected); echo unsafe'\n")
        manifest, _ = execute(self.args(argv=[sys.executable, "run.py", "$(touch injected); echo unsafe"]))
        self.assertEqual(manifest["run"]["status"], "completed")
        self.assertFalse((self.root / "injected").exists())

    def test_escape_and_invalid_resource_limit_rejected(self):
        for changes in ({"output":"../escape"}, {"input":["../escape"]}, {"timeout":float("nan")},
                        {"max_output_bytes":0}, {"max_memory_bytes":0}, {"max_cpu_seconds":-1},
                        {"max_cores":0}, {"max_threads":0}):
            with self.assertRaises(ValueError):
                execute(self.args(**changes))
        self.assertFalse((self.root / "runs").exists())

    def test_historical_v1_shape_with_software_strings_remains_supported(self):
        archive = self.root / "archive" / "synthetic-run"
        archive.mkdir(parents=True)
        artifact = archive / "legacy-output.txt"
        artifact.write_text("12 synthetic cases checked\n")
        old = {
            "schema_version": 1,
            "claim_id": "SYNTHETIC-V1",
            "repository": {"commit": None, "dirty": False},
            "command": "python3 finite_check.py --bound 12",
            "environment": {"software": ["CPython 3.10 (standard library)"], "hardware": "unrecorded"},
            "mathematics": {
                "assertion_tested": "A finite synthetic identity holds in the listed range",
                "coefficient_domain": "exact integers",
                "conventions": "zero-based indexing",
                "inputs": ["indices 0 through 11"],
                "bounds": {"index_max": 11},
                "non_claims": ["This finite run is not a universal proof"],
            },
            "randomness": {"used": False, "generator": "", "seed": None},
            "run": {"started_at": "2025-01-01T00:00:00Z", "runtime_seconds": 0.25, "exit_status": 0},
            "outputs": [{"path": "legacy-output.txt", "sha256": sha(artifact)}],
            "checks": [{"check": "synthetic benchmark", "passed": True}],
            "result": "Finite synthetic check completed.",
            "residual_risks": ["No hashes of execution inputs were recorded."],
        }
        manifest_path = archive / "legacy-manifest.json"
        manifest_path.write_text(json.dumps(old))
        for archived_commit in (None, "", "unavailable"):
            old["repository"]["commit"] = archived_commit
            self.assertEqual(validate(old, root=self.root, manifest_path=manifest_path), [])
        old["repository"]["commit"] = None
        self.assertTrue(legacy_limits(old))
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(validate_main([str(manifest_path), "--root", str(self.root)]), 0)
        self.assertIn("valid legacy version 1", output.getvalue())
        self.assertIn("does not require hashes of execution inputs", output.getvalue())
        self.assertIn("does not identify a repository revision", output.getvalue())
        self.assertIn("resolved relative to the manifest directory", output.getvalue())

    def test_ambiguous_v1_output_resolution_is_rejected(self):
        archive = self.root / "archive"
        archive.mkdir()
        root_output = self.root / "same-name.txt"
        local_output = archive / "same-name.txt"
        root_output.write_text("root interpretation\n")
        local_output.write_text("manifest interpretation\n")
        record = {
            "schema_version": 1, "claim_id": "AMBIGUOUS-V1",
            "repository": {"commit": "unavailable", "dirty": False},
            "command": "python3 synthetic.py", "environment": {"software": ["CPython 3.10"]},
            "mathematics": {"assertion_tested": "synthetic finite assertion", "coefficient_domain": "Z",
                            "conventions": "fixed", "inputs": [], "bounds": {"n": 1},
                            "non_claims": ["not universal"]},
            "randomness": {"used": False},
            "run": {"started_at": "2025-01-01T00:00:00Z", "runtime_seconds": 0.1, "exit_status": 0},
            "outputs": [{"path": "same-name.txt", "sha256": sha(root_output)}],
            "checks": [], "result": "synthetic", "residual_risks": [],
        }
        errors = validate(record, root=self.root, manifest_path=archive / "manifest.json")
        self.assertTrue(any("ambiguous legacy output path" in error for error in errors))

    def test_v1_compatibility_does_not_weaken_v2_software_or_outputs(self):
        manifest, _ = execute(self.args())
        bad_software = copy.deepcopy(manifest)
        bad_software["environment"]["software"] = ["CPython 3.10"]
        self.assertTrue(validate(bad_software))
        bad_commit = copy.deepcopy(manifest)
        bad_commit["repository"]["commit"] = None
        self.assertTrue(validate(bad_commit))
        historical = copy.deepcopy(manifest)
        historical["schema_version"] = 1
        historical.pop("input_artifacts")
        historical["outputs"] = []
        self.assertTrue(validate(historical))

    @unittest.skipUnless(
        os.name == "posix" and hasattr(os, "sched_getaffinity") and hasattr(os, "sched_setaffinity"),
        "POSIX resource and affinity limits are required",
    )
    def test_optional_resource_and_thread_caps_are_applied_and_recorded(self):
        self.code.write_text(
            "import json, os, resource\n"
            "from pathlib import Path\n"
            "record = {'as': resource.getrlimit(resource.RLIMIT_AS)[0], "
            "'cpu': resource.getrlimit(resource.RLIMIT_CPU)[0], "
            "'cores': len(os.sched_getaffinity(0)), 'threads': os.environ['OMP_NUM_THREADS']}\n"
            "Path('runs/one/caps.json').write_text(json.dumps(record))\n"
        )
        manifest, _ = execute(self.args(
            result=["runs/one/caps.json"], max_memory_bytes=1024 ** 3,
            max_cpu_seconds=2, max_cores=1, max_threads=2,
        ))
        self.assertEqual(manifest["run"]["status"], "completed")
        observed = json.loads((self.root / "runs/one/caps.json").read_text())
        limits = manifest["run"]["resource_limits"]
        self.assertEqual(observed["as"], limits["memory_bytes"])
        self.assertEqual(observed["cpu"], limits["cpu_seconds"])
        self.assertEqual(observed["cores"], limits["max_cores"])
        self.assertEqual(observed["threads"], str(limits["max_threads"]))
        self.assertEqual(validate(manifest, root=self.root), [])

    @unittest.skipUnless(
        os.name == "posix" and hasattr(signal, "SIGXCPU"),
        "POSIX CPU-limit signals are required",
    )
    def test_cpu_limit_has_a_distinct_recorded_status(self):
        self.code.write_text(
            "import os, resource, signal\n"
            "assert resource.getrlimit(resource.RLIMIT_CPU)[0] == 1\n"
            "os.kill(os.getpid(), signal.SIGXCPU)\n"
        )
        # Leave room for CI scheduling and log draining after the child exits.
        manifest, _ = execute(self.args(max_cpu_seconds=1, timeout=10))
        self.assertEqual(manifest["run"]["status"], "resource-limit")
        self.assertTrue(any("CPU" in risk for risk in manifest["residual_risks"]))
        self.assertEqual(validate(manifest, root=self.root), [])

    @unittest.skipUnless(os.name == "posix", "process group termination is POSIX-specific")
    def test_descendant_holding_log_pipe_is_bounded(self):
        self.code.write_text("import subprocess, sys\nsubprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])\n")
        manifest, _ = execute(self.args(timeout=0.2))
        self.assertEqual(manifest["run"]["status"], "timeout")
        self.assertLess(manifest["run"]["runtime_seconds"], 5)

    @unittest.skipUnless(os.name == "posix", "process group termination is POSIX-specific")
    def test_group_signal_only_fires_while_the_group_is_alive(self):
        real_killpg = os.killpg
        with mock.patch("run_experiment.os.killpg") as killpg:
            completed, _ = execute(self.args())
        self.assertEqual(completed["run"]["status"], "completed")
        killpg.assert_not_called()
        self.code.write_text("import time\ntime.sleep(30)\n")
        with mock.patch("run_experiment.os.killpg", side_effect=real_killpg) as killpg:
            timed_out, _ = execute(self.args(output="runs/two", timeout=0.2))
        self.assertEqual(timed_out["run"]["status"], "timeout")
        self.assertTrue(killpg.called)

    @unittest.skipUnless(os.name == "posix", "process group termination is POSIX-specific")
    def test_failed_group_signal_never_rewrites_an_executed_run(self):
        self.code.write_text("import sys, time\nsys.stderr.write('partial diagnostics\\n')\n"
                             "sys.stderr.flush()\ntime.sleep(30)\n")
        with mock.patch("run_experiment.os.killpg", side_effect=PermissionError("operation not permitted")):
            manifest, _ = execute(self.args(timeout=0.3))
        self.assertEqual(manifest["run"]["status"], "timeout")
        self.assertIn("partial diagnostics", (self.root / "runs/one/stderr.txt").read_text())
        self.assertTrue(any("termination failed" in risk for risk in manifest["residual_risks"]))
        self.assertEqual(validate(manifest, root=self.root), [])

    def test_run_requires_the_computation_software_versions(self):
        contract = json.loads(self.contract.read_text())
        del contract["software"]
        self.contract.write_text(json.dumps(contract))
        with self.assertRaises(ValueError):
            execute(self.args())
        self.assertFalse((self.root / "runs").exists())

    def test_unversioned_software_record_is_not_evidence(self):
        manifest, _ = execute(self.args())
        manifest["environment"]["software"] = [{"name": "SageMath"}]
        self.assertTrue(validate(manifest))

    def test_missing_field_errors_name_the_absent_keys(self):
        manifest, _ = execute(self.args())
        del manifest["claim_id"]
        del manifest["mathematics"]["bounds"]
        errors = "; ".join(validate(manifest))
        self.assertIn("claim_id", errors)
        self.assertIn("bounds", errors)

    def test_missing_pinned_input_fails_the_on_disk_check(self):
        manifest, _ = execute(self.args())
        record = copy.deepcopy(manifest)
        record["run"].update(status="failed", exit_status=1)
        record["input_artifacts"][0]["sha256_after"] = None
        self.assertEqual(validate(record), [])
        self.code.unlink()
        self.assertTrue(validate(record, root=self.root))


if __name__ == "__main__":
    unittest.main()
