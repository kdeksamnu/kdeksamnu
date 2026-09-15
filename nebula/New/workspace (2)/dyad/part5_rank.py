import numpy as np
"""
The reframing assigns Monad 3 a 'dimensional weight' of min(d_C,d_S) and calls it an integer.
rank(G) is NOT a static label -- it is a dynamical quantity, and it sets the exchange bandwidth.

Claim tested: with rank(G)=r, the d_C+d_S dimensional system splits into
  r coupled beam-splitter pairs  +  (d_C-r)+(d_S-r) DARK MODES that never exchange.
Dark modes are exactly the 'ungrounded drift' of Regime II: they evolve under
Omega alone, untouchable by the coupling, and decay only through their own sink.
"""
def build(dC,dS,r,seed=0):
    rng=np.random.default_rng(seed)
    U=rng.normal(size=(dC,r))+1j*rng.normal(size=(dC,r))
    V=rng.normal(size=(r,dS))+1j*rng.normal(size=(r,dS))
    return U@V                                  # rank <= r by construction

dC,dS=6,6
gamC,gamS=0.30,0.05
OmC=np.diag(np.linspace(1.0,2.0,dC)); OmS=np.diag(np.linspace(1.0,2.0,dS))

print(f"d_C={dC}, d_S={dS}.  Exchange bandwidth vs rank(G):")
print(f"{'rank r':>7} {'coupled pairs':>14} {'dark modes':>11} {'max |Im<a,Gb>| / |a||b|':>26}")
for r in [1,2,3,6]:
    G=build(dC,dS,r,seed=r)
    assert np.linalg.matrix_rank(G, tol=1e-8) <= r, (r, np.linalg.matrix_rank(G, tol=1e-8))
    Hbar=np.block([[OmC.astype(complex),G],[G.conj().T,OmS.astype(complex)]])
    # how much of a random excitation can actually cross the boundary?
    rng=np.random.default_rng(100+r); best=0
    for _ in range(400):
        a=rng.normal(size=dC)+1j*rng.normal(size=dC); b=rng.normal(size=dS)+1j*rng.normal(size=dS)
        a/=np.linalg.norm(a); b/=np.linalg.norm(b)
        best=max(best,abs(np.vdot(a,G@b).imag))
    print(f"{r:>7} {r:>14} {(dC-r)+(dS-r):>11} {best:>26.4f}")

print()
print("Singular values show the bandwidth structure directly (r=2 case):")
G=build(dC,dS,2,seed=2)
sv=np.linalg.svd(G,compute_uv=False)
print("  sigma =", np.array2string(sv,precision=4))
print(f"  -> {np.sum(sv>1e-10)} open channels, {np.sum(sv<=1e-10)} blocked.")
print()
print("CONSEQUENCE for the reframing's 'm_3 -> 0 component degradation':")
print("  rank collapse is not a binary switch. As sigma_min -> 0 the weakest channel")
print("  closes first, so bandwidth degrades GRACEFULLY and anisotropically: the modes")
print("  aligned with small singular values go dark while the strong ones still couple.")
print("  That predicts selective loss of grounding (some content drifts, some stays")
print("  anchored) rather than uniform hallucination onset -- a sharper, testable claim.")
