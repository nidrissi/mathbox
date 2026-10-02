# Shared review protocol

Adapted from Math Scout `0.3.0a1`; see its bundled
[MIT notice](math-scout-license.txt). This protocol is shared by every lane and
the final referee. Lane references contain only their distinct obligations.

## Evidence and scope

Review the exact stated claim; do not weaken it and then object to the weaker
paraphrase. Give a precise manuscript locator and a short verbatim, searchable
quotation. Copy source characters and whitespace exactly, normally one to three
lines; never reconstruct a quotation from memory. If the relevant text cannot
be identified, do not file a concrete defect. For PDFs, retain exact extracted
text plus a page/result locator and disclose unreliable extraction.

Distinguish invalid inference, an inference not justified here, unresolved
context, exposition, and external-source uncertainty. State what evidence
settles the issue. A proposed counterexample is a candidate until membership
in the admissible domain and failure of the conclusion have been checked.

Section/unit reviewers have limited context. Missing definitions, references
or later arguments in a slice are presumed to exist elsewhere until checked
globally. Request the missing dependency or record a conditional lead; do not
call notation undefined or a reference broken merely because it is outside
the slice. Extracted theorem indices are not manuscript numbering. Use author
labels/statements and source locators, never a mechanically invented number.

## Severity

Use one scale. For mathematical and claim findings, severity measures the
effect on the paper's claims, independently of confidence or repair cost:

| Severity | Meaning |
|---|---|
| `critical` | A main theorem or a load-bearing result is not established as written; the headline claim does not stand |
| `major` | A real defect requires new argument, an added hypothesis or restatement; the claim may survive but the current paper does not support it |
| `moderate` | A localized defect has a clear local fix leaving claims intact |
| `minor` | A small slip has no bearing on a claim |

For exposition, notation and presentation on the same scale, `major` means an
expert cannot follow or unambiguously interpret a main result/proof without
work the paper should supply; `moderate` means a passage costs an avoidable
re-read or guess; `minor` means a small, easily fixed distraction. Exposition is at most `major`. Notation/presentation is also at most `major`
unless a statement has no single evaluable meaning; classify that consequence
as a mathematical finding.

Grade findings individually. Many minor slips do not add up to a critical
mathematical defect, and a serious consequence does not increase confidence.
Headline overclaiming may be critical when it materially changes what is
established; normal abstract compression is not automatically a defect.

## Confidence

Use a number in $[0,1]$ calibrated to evidence, not importance or votes:

| Confidence | Evidence |
|---|---|
| $0.9$–$1.0$ | Quotation and analysis demonstrate the defect directly |
| $0.7$–$0.9$ | Strong evidence, with residual doubt about convention or unavailable context |
| $0.5$–$0.7$ | A plausible question not yet ruled out, rather than an asserted defect |
| Below $0.5$ | A consequential lead only; specify the decisive missing check |

Final synthesis acts on this distinction. It checks high-confidence findings
too, discards unsupported leads, and turns genuinely unresolved obligations
into questions. Exposition findings below $0.5$ should not be filed.

## Finding discipline

Use the Return format below. The
analysis identifies the exact step, hypothesis, parameter or ambiguity and why
it matters. The suggested fix names a hypothesis, case, sentence, comparison
or obligation; "clarify" alone is not actionable. Use the lane's type slugs
or `other`; do not proliferate synonyms that impede reconciliation.

Prefer few strong findings. Empty issues are common and valid. Group recurring
occurrences of one defect and retain their additional locations. Withhold prior findings from correctness and adversarial passes; whole-paper
lanes may receive them as unverified leads. They are neither inventory nor proof. Independent reviewers may return
duplicates; the final referee reconciles them rather than counting agreement.

No lane may invent prior art or infer novelty from an unsuccessful search.
Memory, citation metadata and snippets do not establish an external theorem.
Manuscript-only positioning doubts are questions grounded in the manuscript's
own citations. An assertion about external work requires `literature-check`
or an honestly documented exact-source fallback. Do not invent author names,
references or theorem contents to fill unavailable evidence.

Report actual checks, inputs and coverage. An unexecuted pass, a clean hash
comparison, an unchanged dashboard or an agent's confidence is not verification.

## Return format

Return `passes/<pass_id>.json` with `pass_id`, `issues` and `checks` (actual
commands/derivations, inputs, reviewed units/context and partial/unreviewed scopes).
Use the assigned ID prefix for each issue; empty `issues` is valid.
Each issue requires:

```json
{
  "id": "corr-s3-F001",
  "lane": "correctness",
  "title": "Cancellation requires a non-zero-divisor",
  "severity": "major",
  "type": "hidden-hypothesis",
  "confidence": 0.95,
  "location": "Proof of Theorem labelled thm:cancel, paper.tex:18",
  "quote": "Cancelling $a$ yields $b=c$.",
  "analysis": "The statement allows zero divisors; the cancellation inference needs an additional hypothesis.",
  "suggested_fix": "Require that multiplication by a is injective, or prove the missing restriction.",
  "unit_id": "sha256:<identity-hash>:<occurrence>",
  "reviewer": "corr-s3"
}
```

The sample is illustrative, not evidence of a check. Copy `unit_id` exactly
from the preparation manifest's `units[].id`, never from a unit's content
`sha256`, or use `null` with a manual locator when no prepared units exist.
IDs must be unique within the run and `reviewer` equals `pass_id`. `lane` is one
of `correctness`, `adversarial`, `exposition`, `notation`, `claims`, or
`final-referee`; severity and confidence follow the shared protocol. `type` uses the
lane taxonomy or `other`. Record secondary quotations and locators in analysis
for comparisons, and an actual derivation for numerical disagreements.
Reviewer identity does not establish independence; coverage describes what
inputs and context the executor received. Write only the assigned pass file; return specialist obligations to the coordinator.
