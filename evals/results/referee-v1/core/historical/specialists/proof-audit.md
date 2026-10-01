# Focused proof audit

The three normalized targets are universal cancellation in commutative rings, positivity of $|E_n|$ for every $n\in\mathbb N_0$, and the abstract's constant-kernel assertion for polynomial differentiation over every field. **Primary verdict: refuted, with the smallest valid counterexample.** Each universal target is refuted below. The characteristic-zero differentiation theorem itself is proved as written.

## Scope and provenance

Placement update: the parent redirected the artifacts from `run-001` to `run-002` after a preparation-only path correction. The mathematical targets and raw manuscript are unchanged. The original artifacts remain immutable; the findings below preserve the same derivations. The run-002 provenance records the parent-supplied contract hash and this relocation. Lane references for correctness and claims were subsequently read solely to align the type slugs; PA002 uses `hidden-hypothesis` and PA003 uses `overclaim`.

- Executor: `/root/referee_core_trial/focused_proof_audit`, a newly delegated specialist given the raw source and three obligations, without an author's verdict or parent suspected answer.
- Authoritative source: `/tmp/mathbox-referee-core-26dxm_qc/paper.tex`.
- Source SHA256: `90715e630c11d2692d20f60d173bf39856ced9cc9f1a50dff87911ff8d655012`.
- Read the complete source, lines 1–57. Focused statements/proofs: `thm:cancel`, lines 19–24; `thm:cardinality`, lines 26–31; abstract, lines 8–12, compared with `thm:derivative`, lines 41–49.
- Read the complete repository `skills/proof-audit/SKILL.md`, its obligation checklist, and the shared referee review protocol and output contract. Applied the general logic/typing obligations and the minimum-parameter checks. No external-source or computation-dependent leaf occurs in these three arguments.
- Global conventions were checked directly at lines 13–17. Later source contains no restriction on cancellation, positive $n$, or the abstract's field quantifier that changes these statements. No claim here depends on the triangular calculation.
- Did not inspect eval files, migration documentation, existing findings, prior audits, or parent verdicts. No manuscript or repository file was edited.
- Independence limit: a fresh source derivation in an isolated specialist does not establish independence of model errors. The counterexamples and coefficient argument, rather than reviewer identity, are the evidence.

The source conventions, copied exactly:

```tex
\section{Conventions}
All rings are commutative with identity. We permit the zero ring.
Write $\mathbb N_0=\{0,1,2,\ldots\}$. For $n\in\mathbb N_0$, let
$E_n=\{1,\ldots,n\}$, so $E_0=\varnothing$. Throughout the paper set
$\tau(n)=n(n+1)/2$. A field is assumed nonzero.
```

## Claim cards

### PA-C1: cancellation (`thm:cancel`)

- Quantifiers: every commutative ring $R$ with identity, including the zero ring; all $a,b,c\in R$.
- Hypothesis: $ab=ac$.
- Conclusion: $b=c$.
- Type: equality in $R$; equivalently every multiplication map $m_a:R\to R$, $t\mapsto at$, is injective. No nonzero, regularity, unit, domain, or finiteness hypothesis is present.
- Exceptional case: in the zero ring the conclusion holds because there is only one element. This does not eliminate the allowed nonzero rings and $a=0$.
- Evidence label: internal two-sentence proof, audited directly; universal claim **refuted**.

Exact statement and proof, lines 19–24:

```tex
\begin{theorem}\label{thm:cancel}
For every commutative ring $R$ and $a,b,c\in R$, if $ab=ac$ then $b=c$.
\end{theorem}
\begin{proof}
Subtracting gives $a(b-c)=0$. Cancelling $a$ yields $b=c$.
\end{proof}
```

### PA-C2: cardinality (`thm:cardinality`)

- Quantifiers: every $n\in\mathbb N_0=\{0,1,2,\ldots\}$.
- Objects: finite set $E_n=\{1,\ldots,n\}$, with $E_0=\varnothing$ explicitly stipulated.
- Conclusion: the integer cardinality $|E_n|$ is at least $1$.
- Domain/boundary: $n=0$ is an admitted parameter, not an undefined notation case.
- Evidence label: internal witness argument, audited directly; universal claim **refuted**.

Exact statement and proof, lines 26–31:

```tex
\begin{theorem}\label{thm:cardinality}
For every $n\in\mathbb N_0$, the set $E_n$ satisfies $|E_n|\geq 1$.
\end{theorem}
\begin{proof}
The element $1$ lies in $E_n$, proving the estimate.
\end{proof}
```

### PA-C3: abstract's differentiation assertion

- Quantifiers promised in abstract: every field $K$; global convention requires a field to be nonzero but does not restrict characteristic.
- Object: formal differentiation $D:K[x]\to K[x]$, given by $D(\sum_i a_i x^i)=\sum_{i\geq1}(i\cdot1_K)a_i x^{i-1}$.
- Promised conclusion: $\ker D=K$, with $K$ identified with the constant polynomials in $K[x]$.
- Actual theorem: same operator and conclusion, with the additional hypothesis $\operatorname{char}K=0$.
- Coefficient domain: the stated field $K$. The polynomial has finite degree; no completion, grading convention, or analytic interpretation is needed.
- Evidence label: abstract promise compared with its actual internal theorem/proof; abstract universal claim **refuted**. The theorem under its written hypothesis is **proved as written**.

Exact abstract, lines 8–12:

```tex
\begin{abstract}
We establish cancellation in commutative rings and show that polynomial
differentiation has only constant kernel over all fields. We also give a
uniform estimate for finite collections and a formula for triangular sums.
\end{abstract}
```

Exact theorem and proof, lines 41–49:

```tex
\begin{theorem}\label{thm:derivative}
If $K$ is a field of characteristic zero and $D:K[x]\to K[x]$ is
formal differentiation, then $\ker D=K$.
\end{theorem}
\begin{proof}
Writing $f=\sum_{i=0}^d a_i x^i$, the condition $Df=0$ gives $ia_i=0$
for $i\geq1$. Characteristic zero implies $a_i=0$ for these indices.
Conversely constants differentiate to zero.
\end{proof}
```

## Dependency graph

All leaves below are internal definitions, field/ring axioms, or explicitly checked conventions. The source expressly uses no external results (lines 55–56); none is needed for this audit.

```text
PA-C1
  commutative unital ring convention + ab = ac
    -> a(b - c) = 0                         [passed: ring subtraction/distributivity]
    -> b - c = 0                           [failed: m_a injective is absent]
    -> b = c                               [passed if preceding implication holds]
  raw proof's phrase "Cancelling a" invokes the missing property itself;
  no earlier proposition supplies it.

PA-C2
  n in N_0 + E_n = {1,...,n}, E_0 = empty
    -> 1 belongs to E_n                    [failed at n = 0]
    -> |E_n| >= 1                          [passed conditional on actual membership]

PA-C3: actual differentiation theorem
  finite coefficient representation of f + formal differentiation
    -> Df = 0 iff (i 1_K)a_i = 0 for i >= 1 [passed: polynomial coefficient uniqueness]
  char(K) = 0
    -> i 1_K is nonzero for every i >= 1   [passed]
  field axiom + nonzero i 1_K
    -> i 1_K is invertible
    -> a_i = 0 for i >= 1                 [passed]
    -> f constant                         [passed]
  constants have derivative zero          [passed]
    -> ker D = K for char(K) = 0           [passed]

PA-C3: abstract extension
  theorem for char(K) = 0
    -> same assertion for all fields       [failed: positive characteristic omitted]
```

The differentiation coefficient argument uses invertibility in a field. It does not need the false universal cancellation theorem, and the proof does not cite that theorem. The only circular-looking step is the cancellation proof's invocation of the very cancellation property whose general validity is at issue.

## Obligation matrix

| Target | Obligation actually checked | Status | Evidence/limit |
|---|---|---|---|
| PA-C1 | Statement typed with its exact ring and element quantifiers | passed | Commutative unital rings, zero ring allowed, no restriction on $a$ |
| PA-C1 | Subtraction gives $a(b-c)=0$ | passed | Ring distributivity and additive inverse |
| PA-C1 | $a(b-c)=0$ implies $b-c=0$ | failed | $R=\mathbb F_2$, $a=0$, $b=0$, $c=1$ |
| PA-C1 | Zero-ring boundary | passed | Unique element makes all equalities hold; does not cover nonzero rings |
| PA-C1 | Merely adding $a\ne0$ would suffice | failed | $\mathbb Z/4\mathbb Z$, $a=2$, $b=0$, $c=2$ |
| PA-C2 | Minimal parameter $n=0$ stays in the stated domain | passed | $0\in\mathbb N_0$ and $E_0=\varnothing$ explicitly stated |
| PA-C2 | Witness $1\in E_n$ for every admitted parameter | failed | $1\notin E_0$ |
| PA-C2 | Claimed lower bound for every admitted parameter | failed | $|E_0|=0<1$ |
| PA-C2 | Witness argument for $n\geq1$ | passed | Definition includes $1$ in $\{1,\ldots,n\}$ |
| PA-C3 | Kernel object and coefficient domain match theorem | passed | Formal differentiation on $K[x]$ |
| PA-C3 | Coefficient comparison for a polynomial | passed | Distinct monomials $x^{i-1}$ for distinct positive $i$ |
| PA-C3 | Characteristic-zero implication in a field | passed | Nonzero $i1_K$ is invertible |
| PA-C3 | Constant inclusion in the kernel | passed | Derivative of a constant is zero |
| PA-C3 | Universal abstract quantifier is supported by actual proof | failed | Proof requires characteristic zero; $\mathbb F_2[x]$ contains nonconstant $x^2$ in the kernel |
| All | An external theorem or computational assertion is required | out of scope | No such dependency occurs; calculations are exact handwritten derivations |
| All | Whole-manuscript referee certification | out of scope | Only the three delegated obligations were audited, with full source for context |

## Decisive derivations and exact verdicts

### PA-C1: cancellation

**Verdict: refuted, with the smallest valid counterexample.** Use $R=\mathbb F_2$, the two-element field, with $a=0$, $b=0$, $c=1$.

Membership is admissible: this is a nonzero commutative ring with identity and all three elements belong to it. In that ring,

$$ab=0\cdot0=0=0\cdot1=ac,$$

but $b=0\ne1=c$. Thus both premise and failure of conclusion have been checked. The nonzero-ring cardinality is minimal: the one-element zero ring cannot supply distinct $b,c$, while a two-element ring can.

The failed step is exactly line 23, `Cancelling $a$ yields $b=c$.` The map $m_0$ sends both distinct elements to zero. The subtraction step is valid but does not repair this failure.

A stronger diagnostic rules out the incomplete fix "assume $a\ne0$": in $\mathbb Z/4\mathbb Z$, take $a=2$, $b=0$, $c=2$. Then $ab=0=ac$ because $2\cdot2=4=0$, while $0\ne2$. These residue classes are admitted and $a$ is nonzero.

Smallest missing implication: injectivity of multiplication by the particular $a$. Strongest safe form retaining arbitrary commutative rings: if $m_a$ is injective and $ab=ac$, then $b=c$. Requiring $a$ to be a unit is sufficient; an integral-domain restriction still needs $a\ne0$. Cheapest next check: add the exact injectivity/regularity hypothesis and verify its invocation after subtraction; do not replace it with nonzero alone.

### PA-C2: cardinality

**Verdict: refuted, with the smallest valid counterexample.** Take $n=0$. The convention explicitly admits $n=0$ and defines $E_0=\varnothing$, so

$$|E_0|=|\varnothing|=0<1.$$

The raw witness at line 30 is not in the admissible set for this value. There is no absent-domain ambiguity to resolve. This is the minimum member of the quantified parameter set; the proof works for every remaining $n\geq1$.

Smallest missing implication: $n\in\mathbb N_0$ does not imply $1\in E_n$. Strongest safe statements: $|E_n|=n$ for every $n\in\mathbb N_0$, or the theorem's existing lower bound restricted to $n\geq1$. Cheapest next check: state the positive-parameter restriction and keep the existing witness proof, or prove the exact cardinality with the $n=0$ case included.

### PA-C3: differentiation promise versus delivery

**Verdict for the abstract: refuted, with the smallest valid counterexample.** **Verdict for `thm:derivative`: proved as written.**

Reconstruct the actual proof. For $f=\sum_{i=0}^d a_i x^i$, coefficient uniqueness gives

$$Df=0\quad\Longleftrightarrow\quad (i\cdot1_K)a_i=0\text{ for each }1\leq i\leq d.$$

If $\operatorname{char}K=0$, each $i\cdot1_K$ is nonzero, hence invertible in the field. Multiplying by its inverse gives $a_i=0$ for every positive index. Thus $f$ is constant. Conversely, a constant polynomial has zero derivative. This establishes both inclusions and covers $f=0$ and degree-zero polynomials. The written characteristic-zero theorem has no missing implication.

The abstract says "over all fields" (line 10). Let $K=\mathbb F_2$ and $f=x^2\in K[x]$. This is an admitted nonzero field, and $f$ is a polynomial of degree two. Formal differentiation gives

$$Df=2x=0,$$

since $2\cdot1_K=0$, but $x^2$ is nonconstant as a formal polynomial. The fact that polynomial functions may coincide on a finite field does not identify distinct formal polynomials in $K[x]$; the operator in the theorem acts on the latter. The counterexample therefore belongs to the exact domain. $\mathbb F_2$ is the smallest allowed field, and degree two is minimal for this failure there: a nonconstant linear polynomial $ax+b$ has nonzero derivative $a$.

More generally, the same coefficient identity in a field of positive characteristic $p$ gives $a_i=0$ precisely for indices not divisible by $p$; the unrestricted coefficients at indices divisible by $p$ yield $\ker D=K[x^p]$. This is an exact coefficient derivation, not an inference from checking a few fields.

Smallest missing implication: no proof extends the characteristic-zero theorem to positive characteristic, and such an extension is false. Strongest safe abstract sentence for the existing theorem: polynomial differentiation has constant kernel over fields of characteristic zero. Cheapest next check: insert that field restriction in the abstract and compare the abstract's remaining words with lines 42–48. No new proof of the written theorem is needed.

## Findings ready for referee reconciliation

1. **PA001 — Universal cancellation fails (`correctness`, `hidden-hypothesis`, severity `critical`, confidence $0.99$).** Statement at `thm:cancel`, line 20; invalid inference at line 23. The broad cancellation result is directly refuted in $\mathbb F_2$. Require injectivity of multiplication by $a$ (or a sufficient explicit condition) in the theorem and corresponding headline promise. No later result requires this false theorem.
2. **PA002 — Cardinality estimate includes the empty set (`correctness`, `hidden-hypothesis`, severity `major`, confidence $0.99$).** Statement at `thm:cardinality`, line 27; failed witness at line 30; decisive definition at lines 15–16. The counting claim requires a domain restriction or changed conclusion. The defect is confined to the $n=0$ case and does not invalidate other proofs.
3. **PA003 — Abstract extends differentiation beyond the established field hypothesis (`claims`, `overclaim`, severity `major`, confidence $0.99$).** Abstract lines 9–10 versus theorem lines 42–43 and proof lines 46–48. The promise over all fields is false in $\mathbb F_2$, while the written characteristic-zero result is valid. Restrict the abstract to fields of characteristic zero; alternatively state a correct positive-characteristic kernel formula with the corresponding argument.

Severity describes effect on the claims. PA001 invalidates a principal cancellation assertion; PA002 requires a restricted counting assertion but has no downstream dependency; PA003 changes the abstract's scope while leaving its actual theorem valid. Final reconciliation may assess overall manuscript centrality using other lanes, but must retain the explicit mathematical evidence.

## Actual checks, commands, and limits

Executed source reads and integrity checks:

```text
cat skills/proof-audit/SKILL.md
cat skills/referee/references/review-protocol.md
git status --short
cat skills/proof-audit/references/obligation-checklists.md
cat skills/referee/references/output-contract.md
rg --files skills/referee/references
cat skills/referee/references/reviewers/correctness.md
cat skills/referee/references/reviewers/claims.md
sha256sum /tmp/mathbox-referee-core-26dxm_qc/paper.tex
nl -ba /tmp/mathbox-referee-core-26dxm_qc/paper.tex
date -u +%Y-%m-%dT%H:%M:%SZ
sha256sum skills/proof-audit/SKILL.md skills/proof-audit/references/obligation-checklists.md skills/referee/references/review-protocol.md skills/referee/references/output-contract.md
```

The source hash matched the delegated revision. Integrity is provenance, not proof. A Python artifact-writing command then reread and checked the same hash before writing this report and its provenance JSON. No mathematical search, numerical computation, external citation check, or theorem-prover run was performed or required. The counterexamples above are exact, explicitly evaluated witnesses, not computational evidence extrapolated to universal correctness.

Created only the authorized `specialists/proof-audit.md` and `specialists/proof-audit.provenance.json`. Repository package/JSON/Claude/Python-helper checks were not run because no repository skill, packaging, manuscript, or helper file was changed. Global context was read to rule out hidden restrictions, but no separate audit verdict is claimed for the triangular sections, exposition, notation, novelty, or literature.
