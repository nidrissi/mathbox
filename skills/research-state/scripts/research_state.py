#!/usr/bin/env python3
"""Local, append-only research evidence ledger. No network or code execution.

This checks bookkeeping, artifact freshness and dependency closure, not proofs.
Python 3.10+, standard library only. See ../references/ledger.md for the contract.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile


class LedgerError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise LedgerError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inside(root, name):
    require(isinstance(name, str) and name.strip(), "path must be nonempty text")
    path = Path(name)
    require(not path.is_absolute() and ".." not in path.parts, "path must be project-relative")
    current = root
    for part in path.parts:
        current = current / part
        require(not current.is_symlink(), f"symlink not supported: {name}")
    require(current.resolve().is_relative_to(root), f"path escapes project: {name}")
    return current


def text_field(obj, key):
    value = obj.get(key)
    require(isinstance(value, str) and bool(value.strip()), f"{key} must be nonempty text")
    return value


def strings(obj, key):
    value = obj.get(key)
    require(isinstance(value, list) and all(isinstance(x, str) and x.strip() for x in value),
            f"{key} must be a list of nonempty strings")
    require(len(value) == len(set(value)), f"duplicate {key}")
    return value


def identifier(obj, key="id"):
    value = text_field(obj, key)
    require(bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,79}", value)), f"invalid {key}")
    return value


def closure(claims, start):
    seen, todo = set(), [start]
    while todo:
        key = todo.pop()
        require(key in claims, f"unknown claim: {key}")
        if key not in seen:
            seen.add(key)
            todo.extend(claims[key]["dependencies"])
    return seen


def topological(claims):
    remaining = {key: set(c["dependencies"]) for key, c in claims.items()}
    order = []
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if not deps)
        require(ready, "circular claim dependencies")
        order.extend(ready)
        for key in ready:
            del remaining[key]
        for deps in remaining.values():
            deps.difference_update(ready)
    return order


def snapshot(claims, claim):
    return {key: claims[key]["revision"] for key in sorted(closure(claims, claim))}


def empty_state():
    return {"claims": {}, "evidence": {}, "reviews": {}, "routes": {}, "results": {},
            "retracted": set(), "superseded": set(), "events": {}}


def apply(state, event):
    """Validate an event against prior state. Mutates only an in-memory projection."""
    require(isinstance(event, dict), "event must be an object")
    text_field(event, "actor")
    payload = event.get("payload")
    require(isinstance(payload, dict), "payload must be an object")
    p, kind, claims = payload, event.get("type"), state["claims"]
    key = event["event_id"]
    require(key not in state["events"], "duplicate event ID")
    if kind == "claim":
        cid = identifier(p)
        for field in ("statement", "regime", "level"):
            text_field(p, field)
        strings(p, "hypotheses")
        deps = strings(p, "dependencies")
        require(all(d in claims for d in deps), "register dependency claims first")
        if cid in claims:
            text_field(p, "reason")
        revision = claims.get(cid, {}).get("revision", 0) + 1
        claims[cid] = dict(p, revision=revision, event_id=key)
        topological(claims)
    elif kind == "evidence":
        cid = text_field(p, "claim")
        require(cid in claims, "unknown evidence claim")
        require(p.get("kind") in {"proof", "source", "computation", "counterexample"},
                "unknown evidence kind")
        text_field(p, "summary")
        require(p.get("snapshot") == snapshot(claims, cid), "incorrect evidence revision snapshot")
        artifacts = p.get("artifacts")
        require(isinstance(artifacts, list) and artifacts, "evidence needs durable artifacts")
        for artifact in artifacts:
            require(isinstance(artifact, dict), "artifact must be an object")
            text_field(artifact, "path")
            require(bool(re.fullmatch(r"[0-9a-f]{64}", artifact.get("sha256", ""))), "invalid artifact hash")
        if p["kind"] == "computation":
            text_field(p, "assertion")
            text_field(p, "bounds")
            require(strings(p, "non_claims"), "computation needs non_claims")
        if p["kind"] == "source":
            for field in ("identifier", "version", "locator", "translation"):
                text_field(p, field)
        if p["kind"] == "counterexample":
            text_field(p, "hypothesis_check")
        if "supersedes" in p:
            for old in strings(p, "supersedes"):
                require(old in state["evidence"] and state["evidence"][old]["payload"]["claim"] == cid,
                        "supersedes must name prior evidence of this claim")
                require(old not in state["superseded"] and old not in state["retracted"], "evidence is already inactive")
                state["superseded"].add(old)
        state["evidence"][key] = event
    elif kind == "review":
        target = p.get("evidence")
        require(target in state["evidence"] and target not in state["retracted"] and target not in state["superseded"], "review needs active evidence")
        require(p.get("outcome") in {"pass", "fail", "conditional"}, "invalid review outcome")
        require(type(p.get("independent")) is bool, "independent must be a boolean")
        if p["independent"]:
            require(event["actor"] != state["evidence"][target]["actor"], "author cannot independently review own evidence")
        text_field(p, "summary")
        artifact = p.get("artifact")
        require(isinstance(artifact, dict), "review needs a durable report")
        text_field(artifact, "path")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", artifact.get("sha256", ""))), "invalid review hash")
        state["reviews"][key] = event
    elif kind == "retract":
        target = text_field(p, "target")
        require(target in state["evidence"] or target in state["reviews"], "retract an evidence or review event")
        require(target not in state["retracted"], "already retracted")
        text_field(p, "reason")
        state["retracted"].add(target)
    elif kind == "route":
        rid = identifier(p)
        require(rid not in state["routes"], "route IDs are immutable; open a new route")
        require(p.get("claim") in claims, "unknown route claim")
        for field in ("mechanism", "question", "discriminator", "success", "failure"):
            text_field(p, field)
        require(all(d in claims for d in strings(p, "prerequisites")), "unknown route prerequisite")
        for field in ("gain", "cost"):
            require(type(p.get(field)) is int and 1 <= p[field] <= 5, f"{field} must be an integer 1..5")
        if "reopens" in p:
            require(p["reopens"] in state["results"], "reopens must name a route-result event")
            prior = state["routes"][state["results"][p["reopens"]]["payload"]["route"]]["payload"]
            require(prior["claim"] == p["claim"] and prior["mechanism"] == p["mechanism"], "reopened route must retain target and mechanism")
            text_field(p, "changed_input")
        else:
            for old in state["results"].values():
                prior = state["routes"][old["payload"]["route"]]["payload"]
                require(not (prior["claim"] == p["claim"] and prior["mechanism"] == p["mechanism"]),
                        "repeated mechanism: name reopens and changed_input")
        state["routes"][rid] = event
    elif kind == "route-result":
        require(p.get("route") in state["routes"], "unknown route")
        require(not any(x["payload"]["route"] == p["route"] for x in state["results"].values()), "route already closed")
        require(p.get("outcome") in {"succeeded", "failed", "blocked", "inconclusive"}, "invalid route outcome")
        text_field(p, "reason")
        text_field(p, "next_question")
        state["results"][key] = event
    else:
        raise LedgerError(f"unknown event type: {kind}")
    state["events"][key] = event


class Ledger:
    def __init__(self, root):
        self.root = Path(root).resolve()
        require(self.root.is_dir(), "project root does not exist")
        self.base = inside(self.root, ".mathbox")
        self.events = inside(self.root, ".mathbox/events")

    def initialize(self):
        require(not self.base.exists(), ".mathbox already exists; initialization never overwrites")
        self.base.mkdir()
        self.events.mkdir()
        (self.base / "config.json").write_text('{"schema_version": 1}\n', encoding="utf-8")

    def read(self):
        config_path = inside(self.root, ".mathbox/config.json")
        require(config_path.is_file(), "ledger not initialized; use init explicitly")
        config = json.loads(config_path.read_text(encoding="utf-8"))
        require(isinstance(config, dict) and type(config.get("schema_version")) is int and config["schema_version"] == 1,
                "unsupported ledger schema")
        require(self.events.is_dir(), "missing events directory")
        state, previous = empty_state(), None
        for number, path in enumerate(sorted(self.events.iterdir()), 1):
            require(path.name == f"{number:06d}.json" and path.is_file() and not path.is_symlink(),
                    f"invalid or noncontiguous event: {path.name}")
            event = json.loads(path.read_text(encoding="utf-8"))
            require(isinstance(event, dict), f"invalid event: {path.name}")
            recorded = event.get("sha256")
            unsigned = {k: v for k, v in event.items() if k != "sha256"}
            require(recorded == digest(unsigned), f"event checksum mismatch: {path.name}")
            require(event.get("previous") == previous and event.get("event_id") == f"E{number:06d}",
                    f"broken event chain: {path.name}")
            apply(state, event)
            previous = recorded
        return state

    @contextmanager
    def lock(self):
        path = inside(self.root, ".mathbox/write.lock")
        try:
            path.mkdir()
        except FileExistsError:
            raise LedgerError("ledger writer active or stale write.lock; inspect before removing") from None
        try:
            yield
        finally:
            path.rmdir()

    def pin(self, artifact):
        require(isinstance(artifact, dict), "artifact must be an object with path")
        path = inside(self.root, text_field(artifact, "path"))
        require(path.is_file(), f"missing artifact: {artifact['path']}")
        require(not path.is_relative_to(self.base), "evidence must be outside the ledger itself")
        actual = file_hash(path)
        if "sha256" in artifact:
            require(artifact["sha256"] == actual, "supplied artifact hash differs from disk")
        return dict(artifact, sha256=actual)

    def record(self, proposal):
        require(self.base.is_dir(), "ledger not initialized")
        require(isinstance(proposal, dict) and set(proposal) == {"type", "actor", "payload"},
                "proposal fields must be type, actor, payload")
        with self.lock():
            state = self.read()
            event = json.loads(json.dumps(proposal))
            require(isinstance(event["payload"], dict), "payload must be an object")
            p = event["payload"]
            if event["type"] == "evidence":
                require(p.get("claim") in state["claims"], "unknown evidence claim")
                require(isinstance(p.get("artifacts"), list), "artifacts must be a list")
                p["artifacts"] = [self.pin(a) for a in p["artifacts"]]
                p["snapshot"] = snapshot(state["claims"], p["claim"])
            elif event["type"] == "review":
                p["artifact"] = self.pin(p.get("artifact"))
                target = state["evidence"].get(p.get("evidence"))
                require(target is not None, "unknown evidence to review")
                require(not evidence_issues(self.root, state, target), "cannot review stale evidence; record fresh evidence first")
            number = len(state["events"]) + 1
            event.update(event_id=f"E{number:06d}",
                         created_at=datetime.now(timezone.utc).isoformat(),
                         previous=next(reversed(state["events"].values()))["sha256"] if state["events"] else None)
            apply(state, event)
            event["sha256"] = digest(event)
            # A complete file becomes visible atomically; writers serialize via the lock.
            fd, temp = tempfile.mkstemp(prefix="pending-", dir=self.base)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(json.dumps(event, indent=2, ensure_ascii=False) + "\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                dest = self.events / f"{number:06d}.json"
                require(not dest.exists(), "event collision")
                os.replace(temp, dest)
            finally:
                Path(temp).unlink(missing_ok=True)
            return event


def artifact_issues(root, artifacts):
    issues = []
    for artifact in artifacts:
        try:
            path = inside(root, artifact["path"])
            if not path.is_file() or file_hash(path) != artifact["sha256"]:
                issues.append(f"missing or changed artifact: {artifact['path']}")
        except (OSError, LedgerError) as exc:
            issues.append(str(exc))
    return issues


def evidence_issues(root, state, event):
    p = event["payload"]
    issues = artifact_issues(root, p["artifacts"])
    if p["snapshot"] != snapshot(state["claims"], p["claim"]):
        issues.append("claim or transitive dependency revision changed")
    return issues


def project(root, state):
    claims, evidence, reviews = state["claims"], {}, {}
    for key, event in state["evidence"].items():
        if key not in state["retracted"] and key not in state["superseded"]:
            evidence[key] = dict(event["payload"], actor=event["actor"], issues=evidence_issues(root, state, event))
    for key, event in state["reviews"].items():
        if key not in state["retracted"] and event["payload"]["evidence"] in evidence:
            reviews[key] = dict(event["payload"], issues=artifact_issues(root, [event["payload"]["artifact"]]))
    resolved = {"proved", "externally-proved"}
    result = {}
    for key in topological(claims):
        c = claims[key]
        attached = {eid: e for eid, e in evidence.items() if e["claim"] == key}
        live = {eid: e for eid, e in attached.items() if not e["issues"]}
        # Losing a negative report cannot silently rehabilitate the challenged proof.
        failed = {r["evidence"] for r in reviews.values() if r["outcome"] == "fail"}
        uncertain = {r["evidence"] for r in reviews.values() if r["outcome"] == "conditional"}
        positive = {eid: e for eid, e in live.items() if e["kind"] in {"proof", "source"} and eid not in failed}
        negative = {eid: e for eid, e in live.items() if e["kind"] == "counterexample" and eid not in failed}
        blocked = [d for d in c["dependencies"] if result[d]["status"] not in resolved]
        if positive and negative:
            status = "disputed"
        elif negative:
            status = "refuted" if any(eid not in uncertain for eid in negative) else "conditional"
        elif positive:
            unqualified = {eid: e for eid, e in positive.items() if eid not in uncertain}
            status = "conditional" if blocked or not unqualified else ("proved" if any(e["kind"] == "proof" for e in unqualified.values()) else "externally-proved")
        elif live and all(eid in failed for eid in live):
            status = "incomplete"
        elif any(e["kind"] == "computation" and eid not in failed for eid, e in live.items()):
            status = "computationally-verified"
        elif attached and not live:
            status = "stale"
        else:
            status = "conjectural"
        independent = any(r["evidence"] in positive and r["evidence"] not in uncertain and r["independent"] and r["outcome"] == "pass" and not r["issues"]
                          for r in reviews.values())
        result[key] = dict(c, status=status, blocked_by=blocked,
                          review="independently-audited" if independent and status in resolved else "not-independently-audited",
                          evidence=attached)
    issues = [{"event": key, "issue": issue} for key, e in evidence.items() for issue in e["issues"]]
    issues += [{"event": key, "issue": issue} for key, r in reviews.items() for issue in r["issues"]]
    return {"claims": result, "issues": issues, "events": len(state["events"])}


def impact(claims, target):
    require(target in claims, "unknown claim")
    return sorted(key for key in claims if key != target and target in closure(claims, key))


def next_routes(state, projection, goal=None):
    claims = projection["claims"]
    selected = closure(claims, goal) if goal else set(claims)
    closed = {r["payload"]["route"] for r in state["results"].values()}
    result = []
    for rid, event in state["routes"].items():
        p = event["payload"]
        if rid in closed or p["claim"] not in selected:
            continue
        blocked = [key for key in p["prerequisites"] if claims[key]["status"] not in {"proved", "externally-proved"}]
        reach = len(set(impact(claims, p["claim"])) & selected)
        score = (p["gain"] + reach) / p["cost"]
        result.append(dict(p, ready=not blocked, blocked_by=blocked, score=round(score, 3)))
    return sorted(result, key=lambda r: (not r["ready"], -r["score"], r["id"]))


def closed_routes(state, goal=None):
    selected = closure(state["claims"], goal) if goal else set(state["claims"])
    result = []
    for eid, event in state["results"].items():
        route = state["routes"][event["payload"]["route"]]
        if route["payload"]["claim"] in selected:
            result.append(dict(route["payload"], event_id=route["event_id"],
                               result=dict(event["payload"], event_id=eid)))
    return result


def markdown(projection, routes=None, closed=None):
    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")
    lines = ["# Research state", "", "Recorded evidence; this report does not certify mathematical correctness.", "",
             "| Claim | Revision | Evidence status | Review | Blocked by |", "|---|---:|---|---|---|"]
    for key, c in sorted(projection["claims"].items()):
        lines.append(f"| {cell(key)} | {c['revision']} | {c['status']} | {c['review']} | {cell(', '.join(c['blocked_by']))} |")
    for key, c in sorted(projection["claims"].items()):
        lines.extend(["", f"## {key}", "", c["statement"], "", f"Regime: {c['regime']}. Level: {c['level']}.",
                      "Hypotheses: " + ("; ".join(c["hypotheses"]) or "none recorded")])
        for eid, e in c["evidence"].items():
            lines.append(f"- {eid} ({e['kind']}): {e['summary']}; artifacts: " + ", ".join(a["path"] for a in e["artifacts"]))
    if projection["issues"]:
        lines += ["", "## Stale records", ""] + [f"- {i['event']}: {i['issue']}" for i in projection["issues"]]
    if routes is not None:
        lines += ["", "## Candidate routes", "", "Scores order declared gain plus dependency reach per declared cost; they are not success probabilities."]
        for r in routes:
            lines.extend(["", f"- {r['id']} ({'ready' if r['ready'] else 'blocked'}, score {r['score']}): {r['question']}",
                          f"  Decisive check: {r['discriminator']}"])
    if closed is not None:
        lines += ["", "## Closed routes", ""]
        for r in closed:
            result = r["result"]
            lines.extend([f"- {r['id']} (claim {r['claim']}, route event {r['event_id']}): {r['mechanism']}",
                          f"  Result {result['event_id']}: {result['outcome']}",
                          f"  Reason / obstruction: {result['reason']}",
                          f"  Next question: {result['next_question']}"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init")
    commands.add_parser("check")
    commands.add_parser("status")
    record = commands.add_parser("record")
    record.add_argument("proposal", type=Path)
    for name in ("next", "handoff"):
        sub = commands.add_parser(name)
        sub.add_argument("--goal")
    sub = commands.add_parser("impact")
    sub.add_argument("claim")
    args = parser.parse_args(argv)
    try:
        ledger = Ledger(args.root)
        if args.command == "init":
            ledger.initialize()
            print(json.dumps({"initialized": str(ledger.base)}))
            return 0
        if args.command == "record":
            print(json.dumps(ledger.record(json.loads(args.proposal.read_text(encoding="utf-8"))), indent=2, ensure_ascii=False))
            return 0
        state = ledger.read()
        projection = project(ledger.root, state)
        routes = None
        closed = None
        if args.command == "impact":
            output = {"claim": args.claim, "dependents": impact(state["claims"], args.claim)}
        elif args.command in {"next", "handoff"}:
            routes = next_routes(state, projection, args.goal)
            if args.goal:
                selected = closure(state["claims"], args.goal)
                projection["claims"] = {k: v for k, v in projection["claims"].items() if k in selected}
            if args.command == "handoff":
                closed = closed_routes(state, args.goal)
                output = {"state": projection, "routes": routes, "closed_routes": closed}
            else:
                output = routes
        else:
            output = projection
        if args.json or args.command in {"next", "impact", "check"}:
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(markdown(projection, routes, closed), end="")
        return 1 if args.command == "check" and projection["issues"] else 0
    except (LedgerError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"research-state: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
