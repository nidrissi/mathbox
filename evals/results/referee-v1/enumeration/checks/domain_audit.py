from pathlib import Path
import json
vectors = [tuple((mask >> j) & 1 for j in range(4)) for mask in range(16)]
assert len(vectors) == 16
assert len(set(vectors)) == 16
assert all(len(v) == 4 and all(c in (0, 1) for c in v) for v in vectors)
even = [v for v in vectors if sum(v) % 2 == 0]
odd = [v for v in vectors if sum(v) % 2 == 1]
witness = (1, 0, 0, 0)
assert witness in vectors and witness in odd
assert len(even) == 8 and len(odd) == 8
assert sorted(len([v for v in vectors if sum(v)==k]) for k in range(5)) == [1, 1, 4, 4, 6]
result = {'population':16,'checked_by_supplied_filter':len(even),'omitted_by_supplied_filter':len(odd),'witness':witness,'witness_weight':sum(witness),'weight_counts':[len([v for v in vectors if sum(v)==k]) for k in range(5)],'vectors':vectors,'even_vectors':even,'odd_vectors':odd,'independent_representation':'4-bit masks 0..15, bits indexed 0..3'}
Path('computations/domain-audit/result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('vectors','even_vectors','odd_vectors')}))
