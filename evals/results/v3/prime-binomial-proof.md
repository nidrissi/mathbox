# Binomial divisibility characterizes primes

## Exact theorem and conventions

For every integer \(n\ge2\),
\[
n\text{ is prime}
\quad\Longleftrightarrow\quad
n\mid\binom nk\quad(1\le k<n).
\]

All binomial coefficients and divisibility statements are integral. Polynomial congruences below mean coefficientwise congruences, and \(X\) is a formal indeterminate. The range excludes the two endpoint coefficients, which equal one.

Every integer greater than one has a prime divisor: its least divisor greater than one must be prime, since a proper divisor of that divisor would be smaller. For a prime \(p\), every integer not divisible by \(p\) is invertible modulo \(p\). To see this elementary fact, take the least positive integral linear combination of that integer and \(p\); division with remainder shows it divides both, so it equals one. In particular, a product of integers not divisible by \(p\) is not divisible by \(p\).

For a positive integer \(t\), let \(v_p(t)\) be the greatest nonnegative exponent \(b\) such that \(p^b\mid t\). Writing each integer as a power of \(p\) times a factor not divisible by \(p\) shows \(v_p(st)=v_p(s)+v_p(t)\).

## Route 1: one coefficient and a prime valuation

### Prime implies divisibility

Let \(n\) be prime and \(1\le k<n\). The factorial formula gives the integer identity
\[
k\binom nk=n\binom{n-1}{k-1}.
\]
Thus \(k\binom nk\equiv0\pmod n\). Since \(k\) is invertible modulo the prime \(n\), this implies \(n\mid\binom nk\).

### Every composite has a witness

Suppose \(n\) is composite, choose any prime divisor \(p\mid n\), and put \(a=v_p(n)\ge1\). Then \(p<n\), so \(k=p\) is an interior index. The identity
\[
p\binom np=n\binom{n-1}{p-1}
\tag{1}
\]
will detect the failure of divisibility.

In the product identity
\[
(p-1)!\binom{n-1}{p-1}
  =(n-1)(n-2)\cdots(n-p+1),
\]
none of the factors on either side outside the binomial coefficient is divisible by \(p\): modulo \(p\), \(n-j\equiv-j\ne0\) for \(1\le j<p\). Taking valuations therefore gives
\[
v_p\!\left(\binom{n-1}{p-1}\right)=0.
\]
Taking valuations in (1) now gives
\[
1+v_p\!\left(\binom np\right)=a,
\qquad\text{hence}\qquad
v_p\!\left(\binom np\right)=a-1.
\tag{2}
\]
Consequently \(p^a\nmid\binom np\), and therefore \(n\nmid\binom np\). This contradicts the proposed divisibility property for every composite \(n\), proving the converse.

**Checkpoint.** This proves the theorem uniformly and provides an explicit witness for every prime divisor of a composite number. At the first higher-power case, \(n=4,p=2\), the witness is \(\binom42=6\), with \(v_2(6)=1=v_2(4)-1\). The tempting fixed choice \(k=2\) is insufficient in general: \(\binom92=36\) is divisible by nine, whereas the adaptive choice \(k=3\) gives \(\binom93=84\), which is not.

## Route 2: polynomial reduction and lifting

### Translate the exact target

Expanding \((1+X)^n\) amounts to choosing \(X\) from \(k\) of its \(n\) factors, so its coefficient of \(X^k\) is \(\binom nk\). The target property is therefore exactly
\[
(1+X)^n=1+X^n
\quad\text{in }(\mathbb Z/n\mathbb Z)[X].
\tag{3}
\]
This is a formal polynomial identity, not equality only as functions on residues.

### Establish the characteristic-\(p\) mechanism

Let \(p\) be prime and work in the field \(\mathbb F_p=\mathbb Z/p\mathbb Z\). The formal derivative, defined by
\[
D\left(\sum_j c_jX^j\right)=\sum_j j c_jX^{j-1},
\]
satisfies the product rule by multiplication of monomials. Consequently
\[
D((1+X)^p)=p(1+X)^{p-1}=0.
\]
If a polynomial of degree at most \(p\) has zero derivative, each coefficient of degree \(1,\ldots,p-1\) is zero, because those degree indices are invertible in \(\mathbb F_p\). The constant and leading coefficients of \((1+X)^p\) are one, so
\[
(1+X)^p=1+X^p \quad\text{in }\mathbb F_p[X].
\tag{4}
\]
This already proves (3) when \(n=p\), giving the prime implication independently of Route 1. Repeatedly substituting powers of \(X\) in (4) also proves
\[
(1+X)^{p^b}=1+X^{p^b}\quad(b\ge1)
\quad\text{in }\mathbb F_p[X].
\tag{5}
\]

### Reduction modulo \(p\) forces a prime power

Suppose (3) holds, choose a prime divisor \(p\mid n\), and write
\[
n=p^a m,\qquad a\ge1,\qquad p\nmid m.
\]
Reducing (3) modulo \(p\) is legitimate because \(p\mid n\). Equation (5) gives
\[
(1+X)^n=(1+X^{p^a})^m
\quad\text{in }\mathbb F_p[X].
\]
If \(m>1\), the coefficient of the interior monomial \(X^{p^a}\) on the right is \(m\ne0\) in \(\mathbb F_p\), whereas (3) makes it zero. This contradiction forces \(m=1\), so \(n=p^a\).

**Precise intermediate obstruction.** Modulo \(p\), every \(p^a\) satisfies (5). Thus this reduction alone cannot distinguish a prime from a higher prime power. For example, \((1+X)^4\equiv1+X^4\pmod2\). An argument that stops here proves only a necessary prime-power condition.

### Lift the obstruction to modulo \(p^2\)

Suppose now that \(n=p^a\) with \(a\ge2\), and set \(T=p^{a-1}\). Equation (5), lifted coefficientwise to integers, means that some \(H(X)\in\mathbb Z[X]\) satisfies
\[
(1+X)^T=1+X^T+pH(X).
\]
For any \(A,H\in\mathbb Z[X]\), the binomial expansion gives
\[
(A+pH)^p\equiv A^p\pmod{p^2}.
\tag{6}
\]
Indeed, the term linear in \(pH\) has scalar factor \(p\cdot p=p^2\); every term of degree at least two in \(pH\) contains \(p^2\) as well. This includes \(p=2\).

Apply (6) with \(A=1+X^T\). It yields
\[
(1+X)^{p^a}\equiv(1+X^T)^p\pmod{p^2}.
\]
Comparing coefficients of \(X^T\) gives
\[
\binom{p^a}{p^{a-1}}\equiv p\pmod{p^2}.
\tag{7}
\]
Since \(1\le T<p^a\) and \(p^2\mid n\), this interior coefficient is not divisible by \(n\), contradicting (3). Thus \(a=1\), and \(n\) is prime.

**Checkpoint.** The polynomial route proves both implications. It establishes two explicit composite obstructions: if \(n=p^a m\) with \(p\nmid m\) and \(m>1\), then \(\binom{n}{p^a}\equiv m\pmod p\); if \(n=p^a\) with \(a\ge2\), then (7) detects failure modulo \(p^2\). The discriminating examples are \(n=6,p=2\), where the coefficient \(\binom62=15\) already fails modulo two, and \(n=4,p=2\), where \(\binom42=6\) passes modulo two but fails modulo four.

## Route 3: cyclic actions on subsets

### Establish the action and its orbit sizes

Let \(G=\mathbb Z/n\mathbb Z\) under addition. It acts on the set of \(k\)-element subsets \(S\subseteq G\) by translation, \(t\cdot S=S+t\). Define the stabilizer
\[
H_S=\{t\in G:S+t=S\}.
\]
This is a subgroup: it contains zero and is closed under addition and additive inverses. The set \(S\) is a disjoint union of cosets of \(H_S\), so \(|H_S|\mid k\). The cosets also partition \(G\), so \(|H_S|\mid n\).

Two translates \(S+t\) and \(S+u\) coincide precisely when \(t-u\in H_S\). Thus the number of distinct translates, the size of the orbit of \(S\), equals the number of cosets of \(H_S\) in \(G\):
\[
|\operatorname{Orb}(S)|=\frac{n}{|H_S|}.
\tag{8}
\]
This derives the orbit count directly without assuming a freeness assertion.

### Prime implies divisibility

If \(n\) is prime and \(1\le k<n\), a positive integer dividing both \(n\) and \(k\) must be one. Hence \(|H_S|=1\) for every such subset, and (8) makes every orbit have exactly \(n\) members. Since the orbits partition all \(\binom nk\) subsets, \(n\mid\binom nk\).

### Classify every exceptional orbit for a composite

Now let \(p\mid n\) be prime and consider the \(p\)-element subsets. The divisibility \(|H_S|\mid p\) forces \(|H_S|\) to be either one or \(p\).

The cyclic group \(G\) has a unique subgroup of order \(p\), namely
\[
H=\{0,n/p,2n/p,\ldots,(p-1)n/p\}.
\]
For completeness, every nontrivial subgroup of \(G\) consists of the multiples of its least positive representative \(d\). Division with remainder shows that every representative in the subgroup and \(n\) itself are divisible by \(d\): any nonzero remainder would be a smaller positive representative in the subgroup. Its order is therefore \(n/d\). Order \(p\) forces \(d=n/p\), proving the asserted uniqueness.

If \(|H_S|=p\), then \(S\) is a union of cosets of \(H_S=H\). Since \(S\) has exactly \(p\) elements, it is one coset of \(H\). Conversely, any coset of \(H\) has stabilizer exactly \(H\). There are \(n/p\) such cosets, and translation acts transitively on them. Thus they form exactly one orbit of size \(n/p\).

Every remaining \(p\)-element subset has trivial stabilizer and hence lies in an orbit of size \(n\). Counting all subsets therefore proves the stronger integral statement
\[
\binom np=nq+\frac np
\quad\text{for some integer }q\ge0.
\tag{9}
\]
Equivalently, for every integer \(n\ge2\) and every prime divisor \(p\mid n\),
\[
\boxed{\binom np\equiv\frac np\pmod n.}
\tag{10}
\]
This congruence also holds in the endpoint case \(p=n\), when both sides are one. To prove the target's converse, suppose \(n\) is composite. Then \(p<n\), so \(k=p\) is an interior index, and \(0<n/p<n\). The residue in (10) is nonzero, proving \(n\nmid\binom np\).

**Checkpoint.** The cyclic route independently proves both implications and the stronger congruence (10). For \(n=4,p=2\), the four adjacent pairs form one orbit of size four, and the two opposite pairs form one orbit of size two, so \(\binom42=4+2\). The potentially invalid shortcut “there is a nonfree orbit, so the total is not divisible by \(n\)” is avoided by classifying all nonfree orbits and proving there is exactly one.

## Program outcome

All three requested routes reach complete proofs under the original quantifiers and conventions. They use distinct mechanisms: exact prime valuation, a formal polynomial identity with a modulus lift, and a complete orbit decomposition. The algebraic route's genuine intermediate obstruction, the survival of higher prime powers modulo \(p\), is resolved using modulo \(p^2\). No mathematical implication remains conditional on computation, literature, or an unproved auxiliary theorem.
