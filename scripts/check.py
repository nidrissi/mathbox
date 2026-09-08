#!/usr/bin/env python3
"""Package, local-link, syntax and executable regression gate; no keyword grading."""
import argparse
import ast
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import subprocess
import sys


@contextmanager
def guard(errors, label):
    """Record one unit's failure and keep checking the rest of the repository."""
    try:
        yield
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError) as exc:
        errors.append(f"{label}: {exc}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--static", action="store_true", help="skip executable regression suites")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = []
    skills = sorted((root / "skills").glob("*/SKILL.md"))
    names = [s.parent.name for s in skills]
    with guard(errors, "plugin manifests"):
        codex = json.loads((root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        claude = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        if codex["version"] != claude["version"] or claude["version"] != market["plugins"][0]["version"]:
            errors.append("package versions disagree")
        if codex["name"] != claude["name"] or codex["name"] != market["plugins"][0]["name"]:
            errors.append("package identities disagree")
        if codex.get("skills") != "./skills/" or sorted(claude["skills"]) != ["./skills/" + n for n in names]:
            errors.append("manifest inventory differs from canonical skills")
    for path in [*root.glob("skills/**/*.json"), *root.glob("evals/**/*.json")]:
        with guard(errors, path.relative_to(root)):
            json.loads(path.read_text(encoding="utf-8"))
    with guard(errors, "behavior fixture inventory"):
        inventory = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
        cases = inventory.get("cases") if isinstance(inventory, dict) else None
        if not isinstance(cases, list) or not cases:
            errors.append("evals/cases.json needs a nonempty cases array")
        else:
            case_ids = [case.get("id") for case in cases if isinstance(case, dict)]
            if len(case_ids) != len(cases) or len(case_ids) != len(set(case_ids)):
                errors.append("behavior fixture IDs must be present and unique")
            skill_names = set(names)
            fixtures_root = (root / "evals/fixtures").resolve()
            for case in cases:
                if not isinstance(case, dict):
                    continue
                if case.get("skill") not in skill_names:
                    errors.append(f"unknown behavior fixture skill: {case.get('skill')}")
                fixture = case.get("fixture")
                target = (root / "evals" / fixture).resolve() if isinstance(fixture, str) else None
                if target is None or not target.is_relative_to(fixtures_root) or not target.is_file():
                    errors.append(f"missing or unsafe behavior fixture: {fixture}")
                if not isinstance(case.get("obligations"), list) or not case["obligations"]:
                    errors.append(f"behavior fixture needs obligations: {case.get('id')}")
                if not isinstance(case.get("critical_failure"), str) or not case["critical_failure"].strip():
                    errors.append(f"behavior fixture needs a critical failure: {case.get('id')}")
    for path in [*root.glob("skills/**/*.py"), *root.glob("scripts/*.py"), *root.glob("evals/**/*.py")]:
        with guard(errors, path.relative_to(root)):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for skill in skills:
        with guard(errors, skill.parent.name):
            body = skill.read_text(encoding="utf-8")
            parts = body.split("---", 2)
            if len(parts) != 3 or not re.search(r"^name: " + re.escape(skill.parent.name) + r"\s*$", parts[1], re.M) or "description:" not in parts[1]:
                errors.append(f"invalid frontmatter: {skill.relative_to(root)}")
            for name in ("evals/evals.json", "evals/trigger-evals.json", "agents/openai.yaml"):
                if not (skill.parent / name).is_file():
                    errors.append(f"missing {name}: {skill.parent.name}")
            openai = skill.parent / "agents/openai.yaml"
            if openai.is_file() and not re.search(r"^  allow_implicit_invocation: (true|false)$",
                                                  openai.read_text(encoding="utf-8"), re.M):
                errors.append(f"undeclared OpenAI invocation policy: {skill.parent.name}")
            behavior = json.loads((skill.parent / "evals/evals.json").read_text(encoding="utf-8"))
            cases = behavior.get("evals") if isinstance(behavior.get("evals"), list) else []
            if behavior.get("skill_name") != skill.parent.name or not cases:
                errors.append(f"invalid behavior evals: {skill.parent.name}")
            ids = [case.get("id") for case in cases if isinstance(case, dict)]
            if len(ids) != len(set(ids)):
                errors.append(f"duplicate eval IDs: {skill.parent.name}")
            for path in [skill, *skill.parent.glob("references/*.md")]:
                prose = re.sub(r"^```[^\n]*\n.*?^```[^\n]*$", "", path.read_text(encoding="utf-8"), flags=re.M | re.S)
                for link in re.findall(r"\]\(([^)\s]+)\)", prose):
                    if ":" in link or link.startswith("#") or "<" in link:
                        continue
                    target = (path.parent / link.split("#")[0]).resolve()
                    if not target.is_relative_to(skill.parent.resolve()) or not target.exists():
                        errors.append(f"broken/nonportable resource link {link} in {path.relative_to(root)}")
    with guard(errors, "manifest template"):
        template = root / "skills/computation-audit/assets/computation-manifest.json"
        subprocess.run([sys.executable, str(root / "skills/computation-audit/scripts/validate_manifest.py"),
                        str(template), "--template"], check=True)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Static package checks passed for {len(skills)} skills.", flush=True)
    if not args.static:
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        for directory in sorted((root / "skills").glob("*/scripts")):
            if list(directory.glob("test_*.py")):
                completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(directory),
                                            "-p", "test_*.py"], cwd=root, env=env)
                if completed.returncode:
                    return completed.returncode
    print("Gate passed. Model behavior and mathematical correctness require separate evaluation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
