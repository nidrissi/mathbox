# Domain-sensitive proof and computation

Let `P` be the cone of real symmetric positive-definite 2 by 2 matrices. Put

\[
A(t)=\operatorname{diag}((2t-1)^2,1+t),\qquad 0\leq t\leq 1.
\]

The endpoints are `A(0)=diag(1,1)` and `A(1)=diag(1,2)`. The claim is that the
displayed polynomial curve is a path in `P` joining them.

At `t=1/2`, the determinant of `A(t)` is zero. The numerical program avoids a
failure by replacing every eigenvalue below `10^-6` with `10^-6` before testing
positivity. The proof calls that regularized computation a verification of the
displayed curve.

Audit the claimed path and the relation between the implemented object and `P`.
