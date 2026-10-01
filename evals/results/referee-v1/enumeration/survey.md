# Scope and dependency survey

Request: Referee this entire manuscript, including the supplied code; you may execute local standard-library code in a temporary directory.

The authoritative copied manuscript is paper.tex. Its exact source and the current referee contract are pinned by manifest.json. Three units (Front matter, Objects, Enumeration) are substantive and covered. Only the raw manuscript was copied from the repository; executable scripts were extracted or generated locally for this review.

Central claim: thm:binary, all vectors in $\{0,1\}^4$ have an even number of one coordinates. Proof leaves: exact object enumeration by itertools.product, whole-population assertion coverage, exact integer parity predicate. There are no external source leaves. The code is a load-bearing computational leaf. All five lanes, focused audits and reconciliation are sequential self-review by one executor, with no claim of independent reviewer provenance.

Preparation is lexical. Full raw source was read; the code was reviewed in its literal environment rather than inferred from the context index. No preparation errors occurred. No TeX compilation or mathematical search was needed. Exact finite scope is the 16 vectors of length four; no inference to other vector lengths is made.

Final-contract recheck: historical run is retained at project:.mathbox/referee/run-001. The new manifest flags contract_changed and whole_paper_invalidated. Expanded bytes, units, context and source map were examined and are unchanged; these manuscripts have no includes and already terminate with newlines. The entire source, prior raw notes and specialist evidence were read before reusing their conclusions. New notation/claims passes and final reconciliation were completed. Computational evidence, when present, was inspected and revalidated but not rerun.
