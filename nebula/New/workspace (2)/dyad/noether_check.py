"""
Audit of the proposed Cross-Substrate Noether current.

Part 1: Is the stated Lagrangian invariant under the stated transformation?
Part 2: If not, what is the minimal repair, and is the repaired charge conserved?
"""
import numpy as np

rng = np.random.default_rng(7)
n = 2                                   # d_C = d_S = 2 for legibility
M = 4.0
H = rng.normal(size=(n, n)); H = H @ H.T + 3*np.eye(n)
K = rng.normal(size=(n, n))
x, xd, s, sd = (rng.normal(size=n) for _ in range(4))

def L_real(x, xd, s, sd):
    """Exactly as written in Section 1: real vectors, transposes, Euclidean norms."""
    return 0.5*M*xd@xd - 0.5*x@H@x - x@K@s

# The only faithful REAL representation of a U(1) phase is a rotation in a 2-plane.
def rot(th):
    c, sn = np.cos(th), np.sin(th)
    R = np.eye(n); R[0,0]=c; R[0,1]=-sn; R[1,0]=sn; R[1,1]=c
    return R

print("="*72)
print("PART 1 — invariance of the Lagrangian AS WRITTEN")
print("="*72)
a, b, eps = 0.7, 1.3, 1e-3
dL = (L_real(rot(eps*a)@x, rot(eps*a)@xd, rot(-eps*b)@s, rot(-eps*b)@sd)
      - L_real(x, xd, s, sd))
print(f"real vectors, real rotation  : dL = {dL:+.3e}   -> {'INVARIANT' if abs(dL)<1e-12 else 'BROKEN'}")

# Continuous sign-phase on reals degenerates: e^{i eps a} x is only real for eps a = 0, pi.
print(f"e^{{i·eps·a}} acting on a REAL vector leaves R^d only at eps·a in pi*Z  -> symmetry is discrete Z2, not U(1)")

xc  = x  + 1j*rng.normal(size=n); xdc = xd + 1j*rng.normal(size=n)
sc  = s  + 1j*rng.normal(size=n); sdc = sd + 1j*rng.normal(size=n)
p, q = np.exp(1j*eps*a), np.exp(-1j*eps*b)

def L_bilin(x, xd, s, sd):        # literal transcription, complexified: x^T (not x^dagger)
    return 0.5*M*np.real(xd@xd) - 0.5*np.real(x@H@x) - np.real(x@K@s)
def L_sesqui(x, xd, s, sd):       # repaired: Hermitian inner products
    return (0.5*M*np.real(np.vdot(xd,xd)) - 0.5*np.real(np.vdot(x,H@x))
            - np.real(np.vdot(x, K@s)))

for name, f in [("complex, BILINEAR  x^T K s", L_bilin),
                ("complex, SESQUILINEAR x^dag K s", L_sesqui)]:
    d = f(p*xc,p*xdc,q*sc,q*sdc) - f(xc,xdc,sc,sdc)
    print(f"{name:38s}: dL = {d:+.3e}   -> {'INVARIANT' if abs(d)<1e-12 else 'BROKEN'}")
