import numpy as np, torch, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'radius_of_validity.py')).read()
src=src.replace('if __name__ == "__main__":\n    main()','')
g={'__name__':'rov'}; exec(compile(src,'rov','exec'),g)
Block=g['Block']; T,D=g['T'],g['D']; DT=g['DT']
torch.manual_seed(0); blk=Block()
X0=torch.randn(1,T,D,dtype=DT); X0=X0/X0.norm(dim=-1,keepdim=True).mean()
f0=blk(X0).detach(); base=float(f0.norm())
x=X0.clone().requires_grad_(True); flat=blk(x).reshape(-1); n=flat.numel()
J=torch.zeros(n,n,dtype=DT)
for i in range(n): J[i]=torch.autograd.grad(flat[i],x,retain_graph=(i<n-1))[0].reshape(-1)
J=J.detach().numpy()

print("="*76); print("IS THE LINEARISED GENERATOR ANYTHING LIKE -i*Hbar ?"); print("="*76)
A=J/np.max(np.abs(np.linalg.eigvalsh((J+J.T)/2)))  # scale-free
sym=(J+J.T)/2; asym=(J-J.T)/2
print(f"  ||sym(J)||_F / ||J||_F     = {np.linalg.norm(sym)/np.linalg.norm(J):.4f}")
print(f"  ||asym(J)||_F / ||J||_F    = {np.linalg.norm(asym)/np.linalg.norm(J):.4f}")
ev=np.linalg.eigvals(J)
print(f"  eigenvalues: {len(ev)} total")
print(f"    real part  > 0 : {int(np.sum(ev.real>0)):>4}   (expansive directions)")
print(f"    real part  < 0 : {int(np.sum(ev.real<0)):>4}   (contractive)")
print(f"    |Im| < 1e-9    : {int(np.sum(np.abs(ev.imag)<1e-9)):>4}   (purely real eigenvalues)")
print(f"    max Re(lambda) = {ev.real.max():+.4f}    max |lambda| = {np.abs(ev).max():.4f}")
print(f"""
  For dz/dtau = -i*Hbar*z with Hbar Hermitian, the generator's eigenvalues are
  PURELY IMAGINARY and the flow is unitary: charge exactly conserved, no growth.
  Measured: {int(np.sum(np.abs(ev.imag)<1e-9))} of {len(ev)} eigenvalues are purely REAL, and
  {int(np.sum(ev.real>0))} have positive real part. The block's linearisation is a general
  non-normal operator with a strongly expansive spectrum -- the opposite of a
  Hermitian generator. ||J||_2 = {np.linalg.norm(J,2):.3f} means the block AMPLIFIES a
  perturbation ~8x locally; a unitary flow would preserve its norm exactly.
""")

print("="*76); print("WHAT ONE REAL TOKEN DOES"); print("="*76)
rng=np.random.default_rng(7)
emb_std=1.0/np.sqrt(D)
with torch.no_grad():
    rel=[]; amp=[]
    for _ in range(200):
        row=rng.integers(0,T); e=rng.normal(size=D)*emb_std
        d=np.zeros((T,D)); d[row]=e
        dd=torch.tensor(d,dtype=DT).unsqueeze(0)
        out=blk(X0+dd)
        rel.append(float((out-f0).norm())/base)
        amp.append(float((out-f0).norm())/np.linalg.norm(d))
    rel=np.array(rel); amp=np.array(amp)
print(f"  replacing one row by a fresh embedding (norm {emb_std*np.sqrt(D):.3f}):")
print(f"    relative output change ||f(X0+d)-f(X0)||/||f(X0)|| : mean {rel.mean():.4f}  max {rel.max():.4f}")
print(f"    amplification ||dOut||/||dIn||                     : mean {amp.mean():.3f}  max {amp.max():.3f}")
print(f"  tolerance implied by the measured sparse radius (5% err) : delta* = 0.439")
print(f"  a single token is delta = {emb_std*np.sqrt(D):.3f} -> {emb_std*np.sqrt(D)/0.439:.2f}x the radius at 5% tolerance")
print(f"                             -> {emb_std*np.sqrt(D)/0.1638:.2f}x the radius at 1% tolerance")
