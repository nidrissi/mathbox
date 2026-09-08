# Claimed exhaustive finite check

Target: verify an identity for every binary word of length six.

The implementation first constructs the complete lexicographically ordered list
of 64 words, but the verification loop is:

```python
for word in words[::4]:
    assert left(word) == right(word)
```

The report says “all 64 inputs verified.” No symmetry, orbit argument, or
reduction from omitted words to tested words is supplied. Audit the computation
and state the strongest justified result.
