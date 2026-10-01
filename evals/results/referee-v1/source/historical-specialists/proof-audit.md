# Focused proof audit — self-review

Normalized claim template: for every finite complex X satisfying condition P and every commutative ring R, $V(X;R)=0$. Exact locus: thm:extension, paper.tex:14-16. The mathematical semantics of V and P cannot be reconstructed because their source is unavailable. This typing limitation is reported before any proposed witness; none is fabricated.

Primary verdict: **conditional on a named input** — E1, an authenticated general-coefficient version of Theorem 3 (with the exact definitions/hypotheses), or E2, an authenticated rational version plus a proved coefficient-extension implication applicable to V and P.

Dependency graph: cited construction → definition/type of V; source or missing local definition → condition P; claimed rational Theorem 3 → $V(X;\mathbb Q)=0$; missing E1/E2 → $V(X;R)=0$ for all commutative R. The theorem depends entirely on unresolved external leaves, with no computational dependency.

| Obligation | Status | Evidence |
|---|---|---|
| Resolve exact statement/version | passed | Manuscript source and contract hashes pinned; thm:extension at paper.tex:14-16 |
| Reconstruct V and P in admissible domain | conditional | V deferred externally; P not defined in full supplied source |
| Authenticate rational Theorem 3 | conditional | Synthetic source unavailable; literature-check cannot extract it |
| Obtain every-ring conclusion | conditional | Manuscript-only rational attribution does not supply this arrow; E1/E2 needed |
| Search later/internal extension arguments | passed | Full source paper.tex:1-25 contains none |
| Test actual ring-specific or complex-specific witness | not addressed | No available definition supports an admissible witness |
| Computation checks | out of scope | No load-bearing code or table |

Decisive evidence is the exact proof at paper.tex:18-20, attributing a rational conclusion followed by the arbitrary-ring invocation. This demonstrates what justification is presented, not the contents of the absent source. It is not a counterexample to the actual invariant, nor a claim that an extension theorem is impossible.

No commands beyond local source inventory and global textual search were needed. The linked literature-check preserves the authentication and extraction failures. The exact remaining gap is general-coefficient applicability under the true source definitions and hypotheses.

Strongest safe statement: the manuscript reports a rational case, conditional on authentication of its citation; no vanishing theorem for the actual V has been independently verified here. Cheapest next check is to obtain the precise cited theorem and definitions. If it proves only the rational case, then obtain the E2 transfer proof or narrow the statement. No manuscript edits or new proof route were attempted.
