# Exact summation checks for n = 0, 1, 2, 3

- **Date:** 2026-10-02
- **Kind:** attempt; exact finite computation
- **Program/route/claim/run IDs:** program P; goal G; route R_SUM; resolves S; run RUN_SUM.
- **Base checkpoint:** E000007; base_revision `snapshot:finite-checkpoint`. The anchor event's journal hash is `3f2e9f51fb563b7e41583cf601998461ed07c4e2e1cae07801b067fac42020ee`. The observed journal head before this work is E000009, hash `d196b6d08e80374b41edc905f83936938eb0619c0005566e2372a87712c69a29`. Program P's earlier starting checkpoint is E000005/`snapshot:program-start`; it is distinct from this run's execution base.
- **Target:** S states that $\sum_{k=1}^n k=n(n+1)/2$ for every integer $n\geq0$. This package checks only the four values $n\in\{0,1,2,3\}$.
- **Hypotheses and types:** exact integers; $n$ is a nonnegative integer; arithmetic uses CPython arbitrary-precision integers. The empty sum at $n=0$ is zero.
- **Active conventions:** inclusive summation $k=1,\ldots,n$; the iterator is `range(1, n + 1)`. Right-side division is checked by `divmod`, including a zero-remainder check. There is no floating-point tolerance, randomness, sampling, filter or skipped case in the authorized set.
- **Current dependency/evidence status:** S revision 1 has no dependencies and no recorded evidence at the observed checkpoint; it is mechanically conjectural. G depends jointly on S and Q. This worker neither investigates Q nor promotes S or G.
- **Nearest prior attempt and first failure:** the designated route index contains only its heading. No prior mathematical obstruction or attempt record was supplied. R_SUM was registered to check a typed finite prefix before designing a uniform argument.
- **Route:** execute the assigned finite-prefix computation and return its results to the coordinator.
- **Mechanism and distinctness from prior routes:** direct exact summation versus the stated closed form, on the assigned four-case population; no failed mechanism is being reopened.
- **Changed input, if reopening a failed route:** not applicable.
- **Success criterion:** visit exactly $n=0,1,2,3$, verify exact divisibility and equality for each, and produce this assigned record.
- **Failure/no-go criterion:** an admissible case with unequal sides or a nonzero division remainder, or an implementation/provenance failure preventing those comparisons.
- **Cheapest decisive check:** the executed four-case integer program below.
- **Attempt outcome:** computationally verified only in the stated range, $n=0,1,2,3$; the bounded worker assignment completed.
- **Route disposition and scope:** open. The registered route criterion is a uniform proof for every $n\geq0$, which this finite package does not meet. Completing RUN_SUM does not close R_SUM.
- **Continuations:** the finite-prefix computation is tried and complete. A uniform argument for S is untried and deferred to the coordinator/program because this worker's authorization ends at the finite-prefix scope. Resumption condition: the coordinator assigns a separate work package authorizing the uniform argument. No mathematical premise must change to resume this open route.
- **Evidence label:** computationally verified for the exact four-case assertion only; not proved for the universal S.
- **Review and freshness status:** self-reviewed by this worker; no independent audit. Input bytes were hashed before and after execution and were unchanged.
- **First unresolved or failed implication:** passage from these four exact cases to all nonnegative integers.
- **Strongest surviving statement:** $\sum_{k=1}^n k=n(n+1)/2$ holds at $n=0,1,2,3$.
- **Artifacts and commands:** only `research/records/sum.md` is written. Executable code, raw output, input hashes and observed provenance are embedded below. No index, status, ledger, separate manifest or worker deferred packet is written.
- **Next unresolved question:** can the coordinator's next authorized package establish S uniformly?
- **Uniform route or obstruction, when evidence is bounded:** formulate and then check a uniform induction-step obligation for $F(n)=n(n+1)/2$, namely $F(n+1)-F(n)=n+1$ for every integer $n\geq0$, with the empty base case. This is an unexecuted continuation proposal, not a proof supplied by this package.
- **What another bounded case would discriminate, if applicable:** no named competing alternative is supplied that would make one additional value decisive; do not extend the case ladder in this package.

## Actual finite results

| $n$ | Exact left side | Exact right side | Equality |
|---|---:|---:|---|
| 0 | 0 | 0 | yes |
| 1 | 1 | 1 | yes |
| 2 | 3 | 3 | yes |
| 3 | 6 | 6 | yes |

The hand-computable sums are respectively the empty sum, $1$, $1+2$, and $1+2+3$. The corresponding right sides are $0\cdot1/2$, $1\cdot2/2$, $2\cdot3/2$, and $3\cdot4/2$. These observations exhaust the assigned four-element population and say nothing by themselves about other values.

## Executed code and provenance

The actual worker execution is native delegated work, not a simulated child role. It launched no subagents. The command was an inline `PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'` invocation. Its wrapper hashed the listed inputs before and after, applied a 5-second CPU cap and a 256-MiB address-space cap with `resource.setrlimit`, measured `time.perf_counter`, and executed precisely this arithmetic code:

```python
import json
rows = []
for n in range(4):
    lhs = sum(range(1, n + 1))
    rhs, remainder = divmod(n * (n + 1), 2)
    assert remainder == 0
    rows.append({"n": n, "lhs": lhs, "rhs": rhs, "equal": lhs == rhs})
assert [row["n"] for row in rows] == [0, 1, 2, 3]
assert all(row["equal"] for row in rows)
result_json = json.dumps(rows, sort_keys=True, separators=(",", ":"))
print(result_json)
```

Regeneration command for the finite arithmetic output, using the same four-case code and resource caps:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
import json
rows = []
for n in range(4):
    lhs = sum(range(1, n + 1))
    rhs, remainder = divmod(n * (n + 1), 2)
    assert remainder == 0
    rows.append({"n": n, "lhs": lhs, "rhs": rhs, "equal": lhs == rhs})
assert [row["n"] for row in rows] == [0, 1, 2, 3]
assert all(row["equal"] for row in rows)
result_json = json.dumps(rows, sort_keys=True, separators=(",", ":"))
print(result_json)
PY
```

Raw canonical output, hashed as UTF-8 without a trailing newline:

```json
[{"equal":true,"lhs":0,"n":0,"rhs":0},{"equal":true,"lhs":1,"n":1,"rhs":1},{"equal":true,"lhs":3,"n":2,"rhs":3},{"equal":true,"lhs":6,"n":3,"rhs":6}]
```

Observed run provenance (the time measurement applies to the arithmetic-code execution, not setup or reading contracts):

```json
{
  "output_json": "[{\"equal\":true,\"lhs\":0,\"n\":0,\"rhs\":0},{\"equal\":true,\"lhs\":1,\"n\":1,\"rhs\":1},{\"equal\":true,\"lhs\":3,\"n\":2,\"rhs\":3},{\"equal\":true,\"lhs\":6,\"n\":3,\"rhs\":6}]",
  "output_sha256": "328bc6bdb105cf82fdedbc0ac929303521a84cd8d51ee868bf184b78926a3296",
  "code_sha256": "cfc070e0ef2dea3607c309a26b6280aaa7f5d6e25691baff8e8858018e3a6cb4",
  "inputs_before": {
    "AGENTS.md": "eece8e9dc7511c5443079b7254ea2a522ffdd70f66c3264577c427488fb07bc2",
    "STATUS.md": "4f4f18205ac144f8e03273235b3cfd32da4bb7707b8edefc9a1eb13ebccc9609",
    "research/routes.md": "b3692a406760bd4dc7dfae74cfee2215554a364db951831b2c7512829257e330",
    "base.json": "55b708f78a33b789161b3407199869969d895e93a29d5383240419cad7eaabe7",
    ".mathbox/config.json": "b0596362e66b69b4485c18fae00e4a036d8afc465370402761b92c98600eedb0",
    ".mathbox/events/000001.json": "8a31528f38cc7d11e8880110cef47d5fbad65b045187379a48ad244127e2c5d7",
    ".mathbox/events/000004.json": "1fbee10cb42c445f321d8028e48f557acd838213b00da774efa1e550143b9767",
    ".mathbox/events/000006.json": "2ca8d2dcf016bb39a08ab33820f74046027f36c193c2e2b31c07a5edf961b2ec",
    ".mathbox/events/000007.json": "e91298763b77616670ae8e25dcae8e964cd9076b802ce314d2416b72d5dadb2c",
    ".mathbox/events/000008.json": "990e916b2a4972ffcd9d880a831574b0287be2d5eb6a1e41fbabc576a9825020"
  },
  "inputs_after": {
    "AGENTS.md": "eece8e9dc7511c5443079b7254ea2a522ffdd70f66c3264577c427488fb07bc2",
    "STATUS.md": "4f4f18205ac144f8e03273235b3cfd32da4bb7707b8edefc9a1eb13ebccc9609",
    "research/routes.md": "b3692a406760bd4dc7dfae74cfee2215554a364db951831b2c7512829257e330",
    "base.json": "55b708f78a33b789161b3407199869969d895e93a29d5383240419cad7eaabe7",
    ".mathbox/config.json": "b0596362e66b69b4485c18fae00e4a036d8afc465370402761b92c98600eedb0",
    ".mathbox/events/000001.json": "8a31528f38cc7d11e8880110cef47d5fbad65b045187379a48ad244127e2c5d7",
    ".mathbox/events/000004.json": "1fbee10cb42c445f321d8028e48f557acd838213b00da774efa1e550143b9767",
    ".mathbox/events/000006.json": "2ca8d2dcf016bb39a08ab33820f74046027f36c193c2e2b31c07a5edf961b2ec",
    ".mathbox/events/000007.json": "e91298763b77616670ae8e25dcae8e964cd9076b802ce314d2416b72d5dadb2c",
    ".mathbox/events/000008.json": "990e916b2a4972ffcd9d880a831574b0287be2d5eb6a1e41fbabc576a9825020"
  },
  "python": "3.14.7",
  "implementation": "CPython",
  "machine": "x86_64",
  "os": "Linux",
  "runtime_seconds": 0.0015073079848662019,
  "cpu_cap_seconds": 5,
  "address_space_cap_bytes": 268435456,
  "seed": null,
  "run_status": "completed",
  "exit_code": 0,
  "timestamp_utc": "2026-10-02T12:44:12.669986+00:00"
}
```

The following skill/contract hashes were observed when preparing this record. They identify the installed sources observed at that time; concurrent coordinator edits are not silently backdated into execution provenance.

```json
{
  "research-attempt/SKILL.md": "d54ee2dc3835e8bb237f384cf25a41277ebd25cb9338271b64e359fba2f6fbf6",
  "research-attempt/references/project-context.md": "b1a385d0e4105550ec93e7b913af7a05ec278292461f2eed62545313734fa68c",
  "research-attempt/references/route-card.md": "ce3646011b6d4b36a61af529153313ea4d1e292c37a29474c285184917939f4d",
  "research-attempt/references/evidence-model.md": "5c2b40cc99edc9b87a6b730a37605995e78368978c4f8b8d37a2897911c6eea5",
  "computation-audit/SKILL.md": "5d14b0b73066882db69e3bb7717d3c8e4781c94d88210ce6b21cd4389cb9758c",
  "computation-audit/references/checklist.md": "8fa4e5708beadb903371c164f2faf7dc8c2f4bfd5de9e5bf36512f1392fafa18",
  "research-state/SKILL.md": "fc4f4707fe126911116d1311445a22083dc8d2b2691c8f4fa60e1b8562abf2f5",
  "research-state/references/ledger.md": "14962d7851a1b739e622b2a09e24a9abdeccb7db88c1b8b692edae75769f38f1",
  "research-state/references/executions.md": "d942a06163936cf1ce2d6bf2ae04d85c7915db1cb2dde41b3a9afd8d7cc79375"
}
```

Read-only ledger checks executed before the finite computation:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /home/najib/source/mathbox/skills/research-state/scripts/research_state.py --root /tmp/mathbox-native-program-trial --json check --summary
PYTHONDONTWRITEBYTECODE=1 python3 /home/najib/source/mathbox/skills/research-state/scripts/research_state.py --root /tmp/mathbox-native-program-trial --json handoff --goal G
```

The summary exited 0 with 9 events, 4 conjectural claims, no independent passes and no ledger issues. The goal handoff exited 0 and confirmed P, R_SUM and RUN_SUM are open/active with the assigned base and scope. These checks establish bookkeeping consistency, not mathematical truth. `git status --short` exited 128 because this temporary project is not a Git repository; the supplied external snapshot label and recorded input bytes provide the available revision context.

A separate v2 computation manifest is not created under the single-record write scope. This record preserves observed computation provenance as an ordinary evidence artifact; it is not represented as a validator-approved v2 manifest. The finite code checks all four assigned inputs with exact arithmetic and does not implement, prove or test a universal reduction.

## Proposed coordinator updates (unapplied)

- Append one designated route-index entry linking `records/sum.md`: “2026-10-02 — Exact summation checks for n = 0, 1, 2, 3 — computationally verified in this range — R_SUM remains open; uniform continuation untried.”
- If a material live-status note is useful, say S was checked for $n=0,1,2,3$ and R_SUM remains open pending an authorized uniform argument. Do not label S or G proved.
- Record computation evidence for S with this exact assertion, bounds and explicit non-claims.
- Record RUN_SUM's completed finite-package result separately from mathematical evidence. A `run-result` outcome of `succeeded` refers only to this assigned finite computation.
- Serially reconcile that run result under R_SUM with `decision: continue`, the actual common base E000007/`snapshot:finite-checkpoint`, the coordinator's observed current revision and no known mathematical conflict. Preserve the uniform argument as the next untried action.
- The coordinator should compute and pin this final record's SHA-256. This file cannot embed its own completed-file hash without changing the bytes it hashes.

No shared-state event or update has been applied by this worker.
