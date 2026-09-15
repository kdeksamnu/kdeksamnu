import numpy as np
"""
Repaired cross-substrate action (canonical first-order / beam-splitter class).

    z = (a, b) in C^(d_C + d_S),   a = carbon amplitudes, b = silicon amplitudes
    Hbar = [[Om_C, G], [G^dag, Om_S]]   (Hermitian by construction)
    H = z^dag Hbar z                     (real)
    A = i*Hbar  (Hermitian)  =>  dz/dtau = -i Hbar z = A z   (unitary flow)

Continuous symmetry:  z -> e^{i eps} z   (DIAGONAL U(1): same phase on both substrates)
Noether charge:       N = z^dag z = n_C + n_S
"""
rng = np.random.default_rng(3); nC = nS = 2
OmC = np.diag([1.0, 1.7]); OmS = np.diag([1.0, 2.3])
G   = rng.normal(size=(nC,nS)) + 1j*rng.normal(size=(nC,nS))
Hbar = np.block([[OmC.astype(complex), G], [G.conj().T, OmS.astype(complex)]])
assert np.allclose(Hbar, Hbar.conj().T)

def H(z):  return np.vdot(z, Hbar@z).real
def N(z):  return np.vdot(z, z).real
def nC_(z):return np.vdot(z[:nC], z[:nC]).real
def nS_(z):return np.vdot(z[nC:], z[nC:]).real
def Iex(z):return (2*np.imag(np.vdot(z[:nC], G@z[nC:])))     # dn_S/dtau

def rhs(z, gamC=0.0, gamS=0.0):
    dz = -1j*(Hbar@z)
    dz[:nC]  -= 0.5*gamC*z[:nC]
    dz[nC:]  -= 0.5*gamS*z[nC:]
    return dz

def rk4(z0, T, dt, gamC=0., gamS=0.):
    out=[]; z=z0.copy()
    for _ in range(int(T/dt)):
        k1=rhs(z,gamC,gamS); k2=rhs(z+.5*dt*k1,gamC,gamS)
        k3=rhs(z+.5*dt*k2,gamC,gamS); k4=rhs(z+dt*k3,gamC,gamS)
        z=z+(dt/6)*(k1+2*k2+2*k3+k4); out.append(z.copy())
    return np.array(out)

z0 = rng.normal(size=nC+nS) + 1j*rng.normal(size=nC+nS)
d0 = rhs(z0); h=1e-6
print("pointwise along the flow:")
print(f"  dH/dtau = {((H(z0+h*d0)-H(z0-h*d0))/(2*h)):+.3e}   <- energy conserved")
print(f"  dN/dtau = {((N(z0+h*d0)-N(z0-h*d0))/(2*h)):+.3e}   <- Noether charge conserved")

traj = rk4(z0, 80.0, 2e-4)
Ht=np.array([H(z) for z in traj]); Nt=np.array([N(z) for z in traj])
nS=np.array([nS_(z) for z in traj]); Ie=np.array([Iex(z) for z in traj])
print("\n=== UNITARY EVOLUTION (gam=0), tau in [0,80] ===")
print(f"  H : {Ht[0]:.10f} -> {Ht[-1]:.10f}   |drift| = {abs(Ht[-1]-Ht[0]):.2e}")
print(f"  N : {Nt[0]:.10f} -> {Nt[-1]:.10f}   |drift| = {abs(Nt[-1]-Nt[0]):.2e}")
print(f"  local balance  dn_S/dtau + I_ex = 0 :  max residual = "
      f"{np.max(np.abs(np.gradient(nS,2e-4)[20:-20]+Ie[20:-20])):.2e}")

print("\n=== DISSIPATIVE: balance law  dN/dtau = -(sig_C + sig_S),  sig = gam*n ===")
for gC,gS,tag in [(0.30,0.05,"carbon sink dominant"),
                  (0.05,0.30,"silicon sink dominant"),
                  (0.30,0.30,"symmetric sinks")]:
    tr=rk4(z0,40.0,2e-4,gC,gS)
    Nn=np.array([N(z) for z in tr])
    sg=np.array([gC*nC_(z)+gS*nS_(z) for z in tr])
    res=np.max(np.abs(np.gradient(Nn,2e-4)[20:-20]+sg[20:-20]))
    print(f"  {tag:22s} gam=({gC},{gS})  N: {Nn[0]:7.4f} -> {Nn[-1]:9.6f}   residual {res:.1e}")

print("\n=== WHAT THE PROPOSED (ANTI-DIAGONAL) ROTATION WOULD REQUIRE ===")
z1 = z0.copy(); t=1e-3
zr = np.concatenate([np.exp(1j*t)*z0[:nC], np.exp(-1j*t)*z0[nC:]])
print(f"  H(z)  = {H(z0):.10f}      H(rotated) = {H(zr):.10f}   dH = {H(zr)-H(z0):+.3e}")
print(f"  N(z)  = {N(z0):.10f}      N(rotated) = {N(zr):.10f}   dN = {N(zr)-N(z0):+.3e}")
print("  -> anti-diagonal phase is NOT a symmetry of the beam-splitter action;")
print("     it is the symmetry of a two-mode-squeezing (parametric amplifier) action,")
print("     whose conserved charge is n_S - n_C, not n_C + n_S.")
