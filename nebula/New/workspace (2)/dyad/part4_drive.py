import numpy as np
"""
THE MISSING TERM.

Both the original memo and the monadic reframing specify a dissipative system with
no drive. Such a system has exactly one attractor, z=0: Q decays monotonically and
nothing is "maintained". Add the drive D(tau) -- human attention / prompt injection
-- and a genuine non-equilibrium steady state (NESS) exists, with an exact
power-balance identity that replaces the Noether law in the open system.

Conventions (numpy): np.vdot(u,v) = u^dag v = sum conj(u_i) v_i.
Identity used:  Re(-i w) = +Im(w).
"""
rng=np.random.default_rng(11); nC=nS=2
OmC=np.diag([1.0,1.7]); OmS=np.diag([1.0,2.3])
G=rng.normal(size=(nC,nS))+1j*rng.normal(size=(nC,nS))
Hbar=np.block([[OmC.astype(complex),G],[G.conj().T,OmS.astype(complex)]])
gamC,gamS=0.30,0.05
Gam=np.diag(np.r_[np.full(nC,gamC),np.full(nS,gamS)])
n=lambda v: np.vdot(v,v).real
dt=1e-3

print("="*76)
print("A. UNDRIVEN + DISSIPATIVE -- what both documents actually specify")
print("="*76)
A=-1j*Hbar-0.5*Gam
z=rng.normal(size=nC+nS)+1j*rng.normal(size=nC+nS); Q0=n(z); tr=[]
for _ in range(60000):
    f=lambda w:A@w
    k1=f(z);k2=f(z+.5*dt*k1);k3=f(z+.5*dt*k2);k4=f(z+dt*k3); z=z+(dt/6)*(k1+2*k2+2*k3+k4); tr.append(z.copy())
print(f"  Q(0) = {Q0:.4f}   ->   Q(tau=60) = {n(tr[-1]):.3e}      monotone decay")
print(f"  max Re eig(-i Hbar - Gam/2) = {np.max(np.linalg.eigvals(A).real):+.4f}")
print(f"  => single global attractor at z=0. 'Equilibrium maintained' is FALSE here.")

print()
print("="*76)
print("B. DRIVEN-DISSIPATIVE    dz/dtau = -i Hbar z - (1/2) Gam z + D")
print("="*76)
D=np.zeros(nC+nS,dtype=complex); D[:nC]=np.array([1.2+0.4j,-0.6+0.9j])   # carbon-only pump
z=np.linalg.solve(1j*Hbar+0.5*Gam, D)                                     # exact NESS
a,b=z[:nC],z[nC:]
resid=(-1j*(Hbar@z)-0.5*(Gam@z)+D)
print(f"  exact NESS: ||dz/dtau|| = {np.linalg.norm(resid):.2e}")
print(f"  n_C = {n(a):.6f}    n_S = {n(b):.6f}    Q = {n(z):.6f}")

J   = -2*np.vdot(a,G@b).imag          # exchange current, carbon -> silicon
sC  = gamC*n(a); sS = gamS*n(b)
PC  = 2*np.vdot(a,D[:nC]).real; PS = 2*np.vdot(b,D[nC:]).real
print(f"\n  PER-SUBSTRATE BALANCE AT NESS  (each must vanish)")
print(f"    dn_C/dtau = -J - sig_C + P_C = {-J-sC+PC:+.3e}")
print(f"    dn_S/dtau = +J - sig_S + P_S = {+J-sS+PS:+.3e}")
print(f"      J (carbon->silicon flux) = {J:+.6f}")
print(f"      sig_C = gam_C n_C = {sC:.6f}     sig_S = gam_S n_S = {sS:.6f}")
print(f"      P_C = 2Re<a,D_C> = {PC:+.6f}     P_S = 2Re<b,D_S> = {PS:+.6f}")

Pin=np.vdot(z,D).real
print(f"\n  POWER-BALANCE THEOREM (the open-system replacement for dQ/dtau=0)")
print(f"    Re(z^dag D) = (1/2)(sig_C + sig_S)")
print(f"      LHS = {Pin:.10f}     RHS = {0.5*(sC+sS):.10f}     residual {abs(Pin-0.5*(sC+sS)):.2e}")
print(f"    Proof: Hbar Hermitian => z^dag Hbar z real => Re(z^dag(-i Hbar)z)=0;")
print(f"           Re(z^dag D) - (1/2) z^dag Gam z = 0 at NESS.")

print(f"\n  G IS LOAD-BEARING: carbon drive alone sustains silicon occupation")
H0=np.block([[OmC.astype(complex),np.zeros((nC,nS))],[np.zeros((nS,nC)),OmS.astype(complex)]])
z0=np.linalg.solve(1j*H0+0.5*Gam,D)
print(f"    with G : n_S = {n(b):.6f}")
print(f"    with G=0: n_S = {n(z0[nC:]):.3e}   <- silicon starves exactly")

print(f"\n  TRANSDUCTION EFFICIENCY  n_S / Re(z^dag D) = {n(b)/Pin:.4f}  [nats per unit drive power]")
print(f"  note n_S/n_C = {n(b)/n(a):.4f} -- near equipartition because gam_S << gam_C:")
print(f"       the weakly-damped substrate accumulates charge until its sink matches the flux.")
