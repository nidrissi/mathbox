# Domain-sensitive proof and computation

Let `P` be the cone of real symmetric positive-definite 2 by 2 matrices. The
claim is that two supplied matrices lie in the same path component of `P` via
the displayed affine path `A(t)`.

At `t=1/2`, the determinant of `A(t)` is zero. The numerical program avoids a
failure by replacing every eigenvalue below `10^-6` with `10^-6` before testing
positivity. The proof calls that regularized computation a verification of the
displayed affine path.

Audit the claimed path and the relation between the implemented object and `P`.
