import numpy as np, torch, os
"""Is the verdict an artefact of random init / small dims? Re-run at several depths,
dims and residual-growth gains, and check whether the qualitative findings hold."""
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'radius_of_validity.py')).read()
src=src.replace('if __name__ == "__main__":\n    main()','')
g={'__name__':'rov'}; exec(compile(src,'rov','exec'),g)
Block=g['Block']; DT=g['DT']

def probe(T,D,NH,gain,seed=0,label=""):
    torch.manual_seed(seed)
    blk=Block(d=D,nh=NH,gain=gain)
    X0=torch.randn(1,T,D,dtype=DT); X0=X0/X0.norm(dim=-1,keepdim=True).mean()
    f0=blk(X0).detach(); base=float(f0.norm())
    x=X0.clone().requires_grad_(True); flat=blk(x).reshape(-1); n=flat.numel()
    J=torch.zeros(n,n,dtype=DT)
    for i in range(n): J[i]=torch.autograd.grad(flat[i],x,retain_graph=(i<n-1))[0].reshape(-1)
    J=J.detach().numpy()
    ev=np.linalg.eigvals(J)
    symF=np.linalg.norm((J+J.T)/2)/np.linalg.norm(J)
    posfrac=np.mean(ev.real>0)
    # sparse radius at 5%
    rng=np.random.default_rng(1); dirs=[]
    for _ in range(12):
        row=rng.integers(0,T); d=np.zeros((T,D)); d[row]=rng.normal(size=D); d[row]/=np.linalg.norm(d[row])
        dirs.append(d)
    dstar=np.nan
    for dl in np.logspace(-2,0.3,14):
        errs=[]
        with torch.no_grad():
            for d in dirs:
                dd=torch.tensor(dl*d,dtype=DT).unsqueeze(0)
                lin=f0+torch.tensor((J@(dl*d).reshape(-1)).reshape(1,T,D),dtype=DT)
                errs.append(float((blk(X0+dd)-lin).norm())/base)
        if np.mean(errs)<0.05: dstar=dl
        else: break
    growth=float((f0-X0).norm()/X0.norm())
    print(f"  {label:<26} growth={growth:5.2f}  sym(J)/||J||={symF:.3f}  Re(lam)>0:{posfrac*100:5.1f}%  "
          f"||J||2={np.linalg.norm(J,2):6.2f}  delta*_sparse(5%)={dstar:.3f}")
    return dstar, growth

print("="*118)
print("SENSITIVITY: does the verdict depend on random init, block size, or residual gain?")
print("="*118)
for T,D,NH,gain,lbl in [(12,32,4,0.6,"T12 D32 gain0.6 (base)"),
                        (12,32,4,0.2,"T12 D32 gain0.2 (mild)"),
                        (12,32,4,1.2,"T12 D32 gain1.2 (hot)"),
                        (16,48,6,0.6,"T16 D48 gain0.6"),
                        (8,64,8,0.6,"T8  D64 gain0.6"),
                        (24,32,4,0.6,"T24 D32 gain0.6")]:
    probe(T,D,NH,gain,label=lbl)
print("""
  Read across the rows: sym(J)/||J|| stays far from 0 in every configuration, so the
  linearised generator is nowhere near antisymmetric and the -i*Hbar*z picture fails
  structurally rather than by bad luck of initialisation. The expansive eigenvalue
  fraction and ||J||_2 do move with gain, as expected. delta*_sparse moves by ~an
  order of magnitude across configurations, which is the honest caveat: the RADIUS
  is configuration-dependent and a single number quoted from one random init means
  little. The QUALITATIVE verdict does not depend on it.
""")
