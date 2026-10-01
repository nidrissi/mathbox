Current-contract self-review recheck. Prior artifact: project:.mathbox/referee/run-001/raw/adversarial.md

Fresh source/domain check confirms P is even weight on exactly {0,1}^4; (1,0,0,0) is admissible and odd. The filter still restricts assertions to the true subset. Prior complete computation outputs, code inputs and result hashes inspected and revalidated; no computational rerun.

The prior lane observations were inspected against the full current source and remain applicable:

Self-review of paper.tex:1-28. Weight zero and four satisfy P; minimal nonzero weight one fails. Candidate witness (1,0,0,0) is in exactly {0,1}^4 with sum=1. No global hypothesis excludes it. The conclusion of thm:binary fails, rather than merely its proof being incomplete. Independent mask enumeration includes this witness and lists all eight omitted odd vectors. The filtering reduction preserves only cases satisfying the intended conclusion and has no coverage argument.
