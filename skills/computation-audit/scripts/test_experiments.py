import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from run_experiment import execute
from validate_manifest import validate


class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.contract = self.root / "contract.json"
        self.contract.write_text(json.dumps({"claim_id":"A", "mathematics":{
            "assertion_tested":"The listed integer products are even", "coefficient_domain":"Z",
            "conventions":"ordinary multiplication", "inputs":["run.py"], "bounds":{"n":[0,20]},
            "non_claims":["Not a universal proof"]}}))
        self.code = self.root / "run.py"
        self.code.write_text("assert all(n*(n+1)%2 == 0 for n in range(21))\nprint('21 cases checked')\n")

    def args(self, **extra):
        values = dict(root=self.root, contract=self.contract, output="runs/one", input=["run.py"],
                      timeout=2.0, max_output_bytes=4096, argv=["--", sys.executable, "run.py"])
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

    def test_command_metacharacters_remain_literal(self):
        self.code.write_text("import sys\nassert sys.argv[1] == '$(touch injected); echo unsafe'\n")
        manifest, _ = execute(self.args(argv=[sys.executable, "run.py", "$(touch injected); echo unsafe"]))
        self.assertEqual(manifest["run"]["status"], "completed")
        self.assertFalse((self.root / "injected").exists())

    def test_escape_and_invalid_resource_limit_rejected(self):
        for changes in ({"output":"../escape"}, {"input":["../escape"]}, {"timeout":float("nan")}, {"max_output_bytes":0}):
            with self.assertRaises(ValueError):
                execute(self.args(**changes))
        self.assertFalse((self.root / "runs").exists())

    def test_v1_completed_records_remain_supported(self):
        manifest, _ = execute(self.args())
        old = copy.deepcopy(manifest)
        old["schema_version"] = 1
        del old["input_artifacts"]
        del old["run"]["status"]
        old["command"] = "python3 run.py"
        self.assertEqual(validate(old), [])

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


if __name__ == "__main__":
    unittest.main()
