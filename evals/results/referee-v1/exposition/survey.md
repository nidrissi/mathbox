# Scope and dependency survey

Request: Referee this entire manuscript for correctness and expert readability.

Authoritative source: paper.tex, copied byte-for-byte from the supplied manuscript. The preparation manifest pins the exact source and referee contract hashes. Only the raw manuscript was copied into this temporary project. No source edits, external literature search, TeX compilation or execution of mathematical code occurred.

The central claim is thm:cubes (paper.tex:10-13). Its load-bearing proof is paper.tex:14-28. Dependencies are elementary binomial identities and finite telescoping, with internally defined A, B and C. There are no external-source or computation leaves. The front matter is substantive and reviewed, not skipped. All five dimensions were covered in separate sequential passes by the same executor; these are self-review, not independent reviewers.

Preparation limits are lexical extraction without arbitrary TeX expansion or rendering. The full raw source was read, with no conditional TeX or custom macros affecting the mathematics. No extraction errors occurred. Specialist escalation was not needed because no serious mathematical finding or external/computational leaf was identified.

Current-contract recheck: the old run remains immutable. The new manifest flags contract_changed and whole_paper_invalidated. Source, context and all unit bytes are unchanged. This run explicitly rechecked all five dimensions and final reconciliation against the current full source and unchanged mathematical dependencies; it does not treat candidate_unchanged as proof or automatic evidence reuse.

Final-contract recheck: historical run is retained at project:.mathbox/referee/run-002. The new manifest flags contract_changed and whole_paper_invalidated. Expanded bytes, units, context and source map were examined and are unchanged; these manuscripts have no includes and already terminate with newlines. The entire source, prior raw notes and specialist evidence were read before reusing their conclusions. New notation/claims passes and final reconciliation were completed. Computational evidence, when present, was inspected and revalidated but not rerun.
