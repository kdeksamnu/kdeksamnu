import numpy as np
rng=np.random.default_rng(7); n=2; M=4.0
H=rng.normal(size=(n,n)); H=H@H.T+3*np.eye(n); K=rng.normal(size=(n,n))
xc=rng.normal(size=n)+1j*rng.normal(size=n); xdc=rng.normal(size=n)+1j*rng.normal(size=n)
sc=rng.normal(size=n)+1j*rng.normal(size=n); sdc=rng.normal(size=n)+1j*rng.normal(size=n)

T  = lambda: 0.5*M*np.real(np.vdot(xdc,xdc))+0.5*M*np.real(np.vdot(sdc,sdc))
V  = lambda: 0.5*np.real(np.vdot(xc,H@xc))+0.5*np.real(np.vdot(sc,H@sc))
Cs = lambda x,s: np.real(np.vdot(x,K@s))     # sesquilinear coupling
Cb = lambda x,s: np.real(x@K@s)              # bilinear coupling

print("Per-term response to  x->e^(+it) x ,  s->e^{-i t} s   (the PROPOSED rotation)")
t=1e-3; p=np.exp(1j*t)
print(f"  kinetic  T : {0.5*M*np.real(np.vdot(p*xdc,p*xdc))-0.5*M*np.real(np.vdot(xdc,xdc)):+.2e}")
print(f"  potential V: {0.5*np.real(np.vdot(p*xc,H@(p*xc)))-0.5*np.real(np.vdot(xc,H@xc)):+.2e}")
print(f"  coupling <x|Ks>: {Cs(p*xc,1/p*sc)-Cs(xc,sc):+.3e}   <- phase DOUBLES: e^(2it) (sesquilinear breaks)")
print(f"  coupling  x^T K s: {Cb(p*xc,1/p*sc)-Cb(xc,sc):+.3e}   <- phase CANCELS (bilinear likes opposite phases)")

print("\nPer-term response to  x->e^(+it) x ,  s->e^(+it) s   (SAME phase)")
print(f"  kinetic  T : {0.5*M*np.real(np.vdot(p*xdc,p*xdc))-0.5*M*np.real(np.vdot(xdc,xdc)):+.2e}")
print(f"  coupling <x|Ks>: {Cs(p*xc,p*sc)-Cs(xc,sc):+.2e}   <- phase CANCELS")
print(f"  coupling  x^T K s: {Cb(p*xc,p*sc)-Cb(xc,sc):+.3e}   <- phase DOUBLES (bilinear breaks)")
