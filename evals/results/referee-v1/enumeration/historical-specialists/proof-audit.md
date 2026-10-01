# Focused proof audit — self-review

Normalized claim: for every $v\in\{0,1\}^4$, the integer $\sum_{i=1}^4 v_i$ is even. Exact statement: thm:binary, paper.tex:13-15. Definitions are paper.tex:10-11. No extra hypotheses, conventions or coefficient domains beyond ordinary exact integer parity apply.

Primary verdict: **refuted, with the smallest valid counterexample** (smallest possible nonzero weight).

Dependency graph: binary vector definition → predicate P; product enumeration → coverage of all 16 objects; filtered `checked` list → asserted P only on that subset; manuscript attempts to infer P on the full domain. The whole-domain arrow fails.

| Obligation | Status | Evidence |
|---|---|---|
| Reconstruct the admissible domain | passed | Exactly four coordinates, each 0 or 1, paper.tex:10 |
| Identify the exact predicate | passed | Number of one coordinates even, paper.tex:11 |
| Enumerator generates whole domain | passed | Four binary choices yield $2^4=16$; actual stdout is `16 8` |
| Assertion loop covers the whole domain | failed | paper.tex:23 retains only even weights |
| Every domain element has P | failed | $(1,0,0,0)$ has weight one |
| External-source authentication | out of scope | No external source leaves |

Decisive derivation: each coordinate of $(1,0,0,0)$ lies in $\{0,1\}$ and there are four coordinates. Its sum is $1$, an odd integer. It is admissible and the exact conclusion fails. No code execution is required for this counterexample.

Source/computation check: reviewed verbatim program at paper.tex:21-26; computation-audit reproduced its successful exit and output `16 8` and separately enumerated all masks $0,\ldots,15$. Commands and versions are in `../specialist-command-log.json` and the two project `computations/` manifests.

There is no missing implication that could rescue the stated theorem under the current domain: it is false. Strongest safe replacement established by the bounded domain check is that exactly 8 of these 16 vectors have P. Hand cross-check: weight multiplicities are $1,4,6,4,1$, so even weights contribute $1+6+1=8$ and odd weights contribute $4+4=8$. The cheapest decisive check is the weight-one witness, already performed. No manuscript edits were made.
