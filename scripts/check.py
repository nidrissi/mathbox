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
import textwrap


@contextmanager
def guard(errors, label):
    """Record one unit's failure and keep checking the rest of the repository."""
    try:
        yield
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.CalledProcessError) as exc:
        errors.append(f"{label}: {exc}")


def skill_frontmatter(body, name):
    """Parse the suite's portable name and folded/literal description subset."""
    parts = body.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("missing opening/closing frontmatter")
    header = parts[1]
    keys = re.findall(r"^([^\s:#][^:]*):", header, re.M)
    if sorted(keys) != ["description", "name"]:
        raise ValueError("frontmatter must contain only name and description, once each")
    if not re.search(r"^name: " + re.escape(name) + r"\s*$", header, re.M):
        raise ValueError("frontmatter name differs from skill directory")
    match = re.search(r"^description:[ \t]*([^\n]*)\n((?:[ \t]+[^\n]*\n|\n)*)", header, re.M)
    if match is None:
        raise ValueError("missing description")
    initial, continuation = match.groups()
    initial = initial.strip()
    if initial in {">", ">-", "|", "|-"}:
        description = textwrap.dedent(continuation).rstrip("\n")
        if initial.startswith(">"):
            description = description.replace("\n", " ")
        if not initial.endswith("-"):
            description += "\n"
    elif initial.startswith(('"', "'")):
        if continuation.strip():
            raise ValueError("quoted descriptions must use one line")
        if initial.startswith('"'):
            description = json.loads(initial)
        elif len(initial) >= 2 and initial.endswith("'"):
            inner = initial[1:-1]
            if "'" in inner.replace("''", ""):
                raise ValueError("invalid single-quoted description")
            description = inner.replace("''", "'")
        else:
            raise ValueError("invalid quoted description")
    else:
        plain = [initial, *textwrap.dedent(continuation).splitlines()]
        if (not initial or initial[0] in "[{&*!#>|"
                or initial.lower() in {"true", "false", "yes", "no", "on", "off", "null", "~"}
                or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", initial)
                or any(re.search(r":[ \t]|[ \t]#", line) for line in plain)):
            raise ValueError("description must be a supported YAML string scalar")
        description = " ".join(line.strip() for line in plain if line.strip())
    if not description.strip() or len(description) > 1024:
        raise ValueError("description must contain 1..1024 characters")
    other = header[:match.start()] + header[match.end():]
    other = re.sub(r"^name: " + re.escape(name) + r"[ \t]*$|^#[^\n]*$", "", other, flags=re.M)
    if other.strip():
        raise ValueError("unsupported frontmatter content outside name and description")
    return description


def trigger_contract(cases):
    if not isinstance(cases, list) or not cases:
        raise ValueError("trigger evals must be a nonempty array")
    seen = set()
    for case in cases:
        if (not isinstance(case, dict) or set(case) != {"query", "should_trigger"}
                or not isinstance(case["query"], str) or not case["query"].strip()
                or type(case["should_trigger"]) is not bool):
            raise ValueError("trigger case must be {query: nonempty str, should_trigger: bool}")
        if case["query"] in seen:
            raise ValueError(f"duplicate trigger query: {case['query']}")
        seen.add(case["query"])


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
        if codex["description"] != claude["description"] or market["plugins"][0]["description"] != claude["description"]:
            errors.append("package descriptions disagree")
        releases = re.findall(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\] — \d{4}-\d{2}-\d{2} — .+$",
                              (root / "docs/CHANGELOG.md").read_text(encoding="utf-8"), re.M)
        if not releases or releases[0] != claude["version"]:
            errors.append("latest changelog release differs from manifest version")
    with guard(errors, "README invocation inventory"):
        readme = (root / "README.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| \[`([^`]+)`\]\(skills/([^/]+)/\) \| [^\n]+ \| (automatic|explicit) \|$", readme, re.M)
        if len(rows) != len(names) or sorted(row[0] for row in rows) != names:
            errors.append("README skill inventory differs from canonical skills")
        for name, directory, mode in rows:
            if name != directory or name not in names:
                errors.append(f"invalid README skill link: {name}")
                continue
            metadata = (root / "skills" / name / "agents/openai.yaml").read_text(encoding="utf-8")
            policy = re.search(r"^  allow_implicit_invocation: (true|false)$", metadata, re.M)
            if policy is None or (mode == "automatic") != (policy[1] == "true"):
                errors.append(f"README invocation policy differs: {name}")
    with guard(errors, "inspector canonical inventory"):
        tree = ast.parse((root / "skills/research-init/scripts/inspect_repo.py").read_text(encoding="utf-8"))
        catalogs = [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(target, ast.Name) and target.id == "CANONICAL" for target in node.targets)]
        if catalogs != [set(names)]:
            errors.append("inspector CANONICAL differs from skill directories")
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
            skill_frontmatter(body, skill.parent.name)
            for name in ("evals/evals.json", "evals/trigger-evals.json", "agents/openai.yaml"):
                if not (skill.parent / name).is_file():
                    errors.append(f"missing {name}: {skill.parent.name}")
            openai = skill.parent / "agents/openai.yaml"
            if openai.is_file() and not re.search(r"^  allow_implicit_invocation: (true|false)$",
                                                  openai.read_text(encoding="utf-8"), re.M):
                errors.append(f"undeclared OpenAI invocation policy: {skill.parent.name}")
            behavior = json.loads((skill.parent / "evals/evals.json").read_text(encoding="utf-8"))
            trigger_contract(json.loads((skill.parent / "evals/trigger-evals.json").read_text(encoding="utf-8")))
            cases = behavior.get("evals") if isinstance(behavior.get("evals"), list) else []
            if behavior.get("skill_name") != skill.parent.name or not cases:
                errors.append(f"invalid behavior evals: {skill.parent.name}")
            ids = [case.get("id") for case in cases if isinstance(case, dict)]
            if len(ids) != len(set(ids)):
                errors.append(f"duplicate eval IDs: {skill.parent.name}")
            for path in [skill, *skill.parent.glob("references/**/*.md")]:
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
        for directory in [root / "scripts", *sorted((root / "skills").glob("*/scripts"))]:
            if list(directory.glob("test_*.py")):
                completed = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(directory),
                                            "-p", "test_*.py"], cwd=root, env=env)
                if completed.returncode:
                    return completed.returncode
    print("Gate passed. Model behavior and mathematical correctness require separate evaluation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
