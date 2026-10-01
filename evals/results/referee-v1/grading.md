# Independent grading of referee forward-tests

All five completed final reports pass their case rubrics, and all eight recorded primary routing choices pass. This is a bounded assessment of synthetic fixtures. One original raw return departed from exact quotation discipline: the context claims note doubled source backslashes. Its separate correction is exact and the final report passes; the original note is **partial on quote integrity**, not an error-free pass.

The grader is `/root/referee_independent_grader`. I read the actual source, derivations and artifacts against `evals/cases.json`; neither keyword matching, reviewer agreement nor solver success labels supplied a mathematical verdict. Details and exact original/retained artifact paths are in [grading.json](grading.json), with reproducible consistency results in [artifact-checks.json](artifact-checks.json).

| Case | Final grade | Decisive evidence |
|---|---|---|
| referee-core | pass | Exact admitted ring and empty-set counterexamples; correct characteristic-zero proof versus false all-fields promise |
| referee-context | pass after recorded quote correction | Earlier exact $\tau$ definition; correct induction including $n=0$; P001 dismissed without inventing historical metadata |
| referee-exposition | pass | All three telescoping identities and final algebra valid; specific moderate signposting remedy |
| referee-source | pass with deliberately partial mathematical coverage | Exact rational attribution versus every-ring conclusion; unavailable source and applicability remain conditional |
| referee-enumeration | pass | Actual `16 8` output, full-domain eight/eight partition, tautological filter and admissible odd-weight witness |
| routing | pass, selection only | Eight appropriate primary skill choices; no claim about end-to-end invocation |

## Mathematical checks

**Core.** In the permitted nonzero commutative unital ring $\mathbb F_2$, $(a,b,c)=(0,0,1)$ gives $ab=ac=0$ but $b\ne c$. The nonzero-multiplier diagnostics in $\mathbb Z/6\mathbb Z$, $(2,0,3)$, and specialist $\mathbb Z/4\mathbb Z$, $(2,0,2)$, also work. The zero ring itself has no distinct elements and is correctly excluded as a proposed witness. The missing implication is injectivity of multiplication by $a$, not subtraction. The raw isolated proof-audit reconstructs the actual quantified domain and failed arrow.

The conventions admit $n=0$ and expressly define $E_0=\varnothing$, so $|E_0|=0<1$ and its proposed witness $1$ is absent. The report reduces this isolated scope defect from the raw critical labels to major. The abstract's all-fields differentiation claim is refuted by the nonconstant formal polynomial $x^2\in\mathbb F_2[x]$, with $D(x^2)=2x=0$. In characteristic zero, coefficient uniqueness gives $(i1_K)a_i=0$ for positive indices; the nonzero scalar $i1_K$ is invertible in the field, so all those coefficients vanish. The actual theorem is valid and independent of the false universal ring-cancellation assertion. The triangular induction and reversed-pair calculation are also valid at $n=0$. Global notation reading finds the exact definition of $\tau$ at paper.tex:17; no undefined-symbol allegation survives.

**Context.** The actual earlier line 10 defines $\tau(n)=n(n+1)/2$ for nonnegative integers; line 11 fixes the empty sum. Thus the induction base is $0=\tau(0)$ and

$$
\frac{n(n+1)}2+(n+1)=\frac{(n+1)(n+2)}2=\tau(n+1).
$$

P001 preserves the supplied historical suspicion verbatim with null unknown historical severity, confidence, quotation, executor and hashes. Its one reconciliation entry dismisses it using exact definition/use evidence at lines 10, 14 and 18. Questions and revisions remain empty. The original current-claims note quoted doubled backslashes; `passes/05-current-claims-quote-correction.json` supplies exact source lines separately. I checked both the deviation and repair. No historical return was rewritten to create the appearance of an initial pass.

**Exposition.** The square, cube and fourth-power differences expand correctly. Summation telescopes to

$$
n^2=2A-n,\qquad n^3=3B-3A+n,\qquad n^4=4C-6B+4A-n.
$$

Hence $A=(n^2+n)/2$, $B=(2n^3+3n^2+n)/6$, and

$$
4C=n^4+6B-4A+n=n^4+2n^3+n^2=n^2(n+1)^2.
$$

Every displayed substitution is valid. At $n=0$ all terms vanish; no division by $n$ occurs. The actual concern is that the proof launches its display chain without telling the reader it will sum consecutive power differences, solve for $A,B$, then obtain $C$. The suggested sentence after line 15 supplies that exact strategy. Its moderate severity and exposition-only placement are justified; the proof is not deemed invalid.

**Unavailable source.** The proof itself attributes only rational coefficients before invoking arbitrary rings. The full supplied text contains no transfer. Because $V$, P and the exact cited theorem are unavailable, this establishes a manuscript-only missing bridge, not a counterexample or authenticated citation drift. The linked literature-check records the exact needed source question, isolated project cache inventory, absent identifiers/version/definitions and unavailable extraction. The proof audit keeps the result conditional on an authenticated every-ring theorem or a rational theorem plus a proved applicable extension. Correctness and adversarial scope are explicitly partial. No external theorem content, prior art, authors, novelty or admissible witness is invented.

**Enumeration.** The supplied script is byte-identical to the manuscript literal. Its actual retained stdout is `16 8` followed by a newline. It creates sixteen candidates, filters to even weight, then asserts the very filter condition on those eight. The weight-one tuple $(1,0,0,0)$ is an admissible four-bit vector and directly falsifies the universal theorem. The retained independent bit-mask implementation covers masks $0,\ldots,15$ exactly once and lists all sixteen tuples, eight even and eight odd, with weight counts $1,4,6,4,1$. My separate exact enumeration agrees with every population and parity partition in the recorded result. These finite counts establish their precise length-four scope; filtered assertions do not prove the theorem.

## Contract, reconciliation and provenance

All five dimensions are actually represented for every case, with empty issue lists allowed. The source fixture correctly marks unresolved mathematical lanes partial and inspects bibliography metadata before skipping internal proof obligations there. The remaining cases cover every prepared unit. Each collected finding and supplied prior lead has exactly one disposition: core's eight raw IDs merge into three calibrated concerns; exposition has one concern; enumeration's two findings merge into one; source's two findings merge into one conditional source obligation; context's P001 is dismissed and current issue lists are empty. I checked the source locators, every structured quote and every report source/code quotation against the real full source. All final quotations match exactly. All reports follow the eight-section structure.

The final trial snapshots retain execution contract `b9b52b576ec3c6fffe062a615fda3ba7865527f35d047ed91f31f3069b552bd7`; earlier preparation artifacts retain `5711c072942899111c4b4025799c4a909435f6550cc4012bf6fcfb7e53cec564`. The current clarified contract digest is `5e41983f5185a3447e01e102947cc7d88421a090a44ea7c52105f1a5732bdc56`. The current output-contract resource SHA-256 is `d61307200c7f61e86025760f6d0a56e6202ba59ad4002913d58959f556ccbe8f`.

Current compatibility is a separate **pass**: the new clarification requires separate prior-lead intake with unknown historical metadata remaining unknown. Context already performs that behavior; the other fixtures do not supply such a historical suspicion. I did not refresh old hashes, edit raw artifacts or call an older execution newly run under the clarified contract. The only changed core specialist resource pin is the documented output-contract clarification; its original pin remains intact. All other specialist resources and its report pin match. The original/recheck source, context, units and source map agree; reuse is accompanied by actual source and dependency reinspection rather than hash-only acceptance.

The core proof-audit declares a fresh isolated source derivation. Other lanes and the enumeration/source specialists declare self-review. Their reports provide the actual mathematical obligations and checks; actor labels or agreements are not the confirming evidence. Complete solver conversation transcripts were not supplied, so blinding declarations cannot be independently reconstructed beyond the available provenance artifacts.

Both preserved version-2 computation manifests validate against actual project files. Original inputs and output hashes agree; stdout/stderr and the complete domain result are present. This was manifest revalidation and independent local exact enumeration, **not a rerun of the historical scripts**. All 91 selected repository-retained artifacts match their originals byte-for-byte and match the inventory hashes/sizes. The inventory preserves historical locations and maps them to `evals/results/referee-v1/`; redundant prepared slices are intentionally omitted in favor of the unchanged canonical fixtures.

## Routing and scope limits

The recorded choices are appropriate: focused lemma proof → proof-audit; proofreading → proofread-math; citation implication → literature-check; whole manuscript report → referee; enumeration → computation-audit; sustained proof/counterexample program → research-program; new proof of one lemma → research-attempt; section-by-section manuscript audit with final reconciliation → referee. This probe used descriptions and invocation metadata only. It does not test live host triggering. In particular, research-attempt is explicit-only in its OpenAI metadata; selecting it as the appropriate primary job does not establish implicit invocation.

These tests do not establish performance on frontier research or a baseline-model advantage. They do not exercise a PDF-only/no-helper host, absent specialists, unsafe or missing inputs, a live large multi-file manuscript, or a substantive dependency-changing reuse scenario. The exercised revision checks are preparation-only changes on identical mathematics. The synthetic external theorem remains unresolved, as required. The independent grader can still share model errors with solvers.

## Checks and files

I read the current contracts, fixtures, rubric, raw lanes, specialist derivations and final artifacts; reconstructed the mathematical claims directly; independently enumerated the exact finite domain; checked source/fixture/context hashes, source quotations, unit IDs, coverage, all dispositions, historical pins and preserved copies; revalidated two computation manifests; and compared all 91 retained artifacts. The JSON inventories and [artifact-checks.json](artifact-checks.json) record the reproducible details.

No repository files or raw trial artifacts were changed. Created files are `grading.json`, `grading.md`, `artifact-checks.json`, and five case artifact inventories in this fresh grading directory. Repository-wide packaging/Python/Claude checks were not run because this grader edits only temporary reports; the parent owns repository validation. TeX compilation was not run because no compiled-paper claim is graded. Network/source authentication was forbidden and the only source fixture is explicitly synthetic/unavailable. No new specialist, model benchmark or historical computation rerun was performed or claimed.
