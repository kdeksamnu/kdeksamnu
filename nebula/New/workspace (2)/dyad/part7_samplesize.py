import numpy as np
from rank_harness import coupling_spectrum, spearman
"""
How many samples per turn does the coupling spectrum need before rank(G) is
recoverable? The harness estimates an dC x dS cross-covariance from the tokens in
one turn; with n ~ d the estimated spectrum is Marchenko-Pastur noise and carries
almost no information about the true rank.
"""
rng=np.random.default_rng(4); D=8
def trial(n, r, noise=0.30):
    A=rng.normal(size=(D,r)); B=rng.normal(size=(D,r))
    A/=np.linalg.norm(A,axis=0,keepdims=True); B/=np.linalg.norm(B,axis=0,keepdims=True)
    G=(A*np.linspace(1.0,0.35,r))@B.T
    lat=rng.normal(size=(n,r)); Ys=lat@(B*np.linspace(1.0,0.35,r)).T+rng.normal(size=(n,D))*noise
    Xc=Ys@G/max(np.linalg.norm(G,2),1e-9)+rng.normal(size=(n,D))*noise
    st=coupling_spectrum(Xc,Ys,tol=0.15)
    return st["rank_eff"], st["PR"], st["f_dark"]

print(f"{'n samples/turn':>15}{'n/d':>7}{'true r':>8}{'mean rank_eff':>15}{'corr(rank_eff,r)':>19}{'corr(PR,r)':>12}")
print("-"*88)
for n in [40,80,160,400,1000]:
    rs=np.arange(1,9); accs=[]; prs=[]
    for r in rs:
        for _ in range(25):
            re_,pr,fd=trial(n,r); accs.append(re_); prs.append(pr)
    print(f"{n:>15}{n/D:>7.1f}{'1-8':>8}{np.mean(accs):>15.2f}"
          f"{spearman(accs,np.repeat(rs,25)):>+19.3f}{spearman(prs,np.repeat(rs,25)):>+12.3f}")

print()
print("At n=40 (the token count of one turn in validate.py) and d=8, n/d=5: the")
print("estimated spectrum is still noise-dominated and rank_eff is nearly")
print("uncorrelated with the truth. Pooling across turns, or tracking the spectrum")
print("on a trailing window of several hundred tokens, is not optional -- it is the")
print("difference between a measurement and a random number.")
print()
print("Bias direction matters for a halt rule: at small n, rank_eff is biased LOW")
print("(noise floor eats real channels), so a dark-mode halt trigger would fire on")
print("healthy sessions -- false positives, not false negatives.")
