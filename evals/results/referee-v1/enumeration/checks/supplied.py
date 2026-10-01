from itertools import product
vectors = list(product((0, 1), repeat=4))
checked = [v for v in vectors if sum(v) % 2 == 0]
for v in checked:
    assert sum(v) % 2 == 0
print(len(vectors), len(checked))
