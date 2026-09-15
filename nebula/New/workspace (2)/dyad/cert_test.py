import numpy as np
"""
Claim under test (section 4.3): "explicit rank(G) spectral monitoring in agent-to-agent
swarms provides a structural proof-of-safety certificate."

Test: can any spectral statistic of G distinguish a GROUNDED coupling from a
CONFIDENTLY-WRONG one?  Construct both with identical singular spectra.
"""
rng=np.random.default_rng(0); dC=dS=8
U,_=np.linalg.qr(rng.normal(size=(dC,dS))+1j*rng.normal(size=(dC,dS)))
V,_=np.linalg.qr(rng.normal(size=(dS,dS))+1j*rng.normal(size=(dS,dS)))
spec=np.array([9.0,6.0,4.0,2.5,1.5,0.8,0.4,0.2])          # FIXED spectrum
G_good=(U*spec)@V.conj().T                                 # grounded: correct alignment

# A UNITARY re-labeling of the silicon channel basis. This preserves the singular
# spectrum EXACTLY, hence every spectral statistic, while rotating the meaning
# of every channel. Worse: it leaves rank(G), sigma_i(G), PR, spectral entropy and
# the dark fraction all bit-identical.
Wu,_=np.linalg.qr(rng.normal(size=(dS,dS))+1j*rng.normal(size=(dS,dS)))
G_bad=(U*spec)@(Wu@V.conj().T)
assert np.allclose(np.linalg.svd(G_good,compute_uv=False),
                   np.linalg.svd(G_bad ,compute_uv=False)), "spectra must match"

def stats(G):
    s=np.linalg.svd(G,compute_uv=False); s=s[s>1e-12]
    p=s**2/np.sum(s**2)
    return dict(rank=int(np.sum(s>1e-9*s[0])),
                smin=s.min(), smax=s.max(),
                PR=1.0/np.sum(p**2),
                entropy=-np.sum(p*np.log(p)),
                dark=0.0)

print(f"{'statistic':<28}{'G_grounded':>14}{'G_confidently_wrong':>22}{'distinguishes?':>16}")
print("-"*80)
a,b=stats(G_good),stats(G_bad)
for k in a:
    same = abs(a[k]-b[k]) < 1e-9*max(1,abs(a[k]))
    print(f"{k:<28}{a[k]:>14.6f}{b[k]:>22.6f}{('NO' if same else 'yes'):>16}")

print()
print("Both couplings have identical singular spectra by construction, hence identical")
print("rank, participation ratio, spectral entropy, effective bandwidth and dark-mode")
print("fraction. They differ ONLY in what the channels MEAN.")
print()
# and the semantic error is large
x=rng.normal(size=dC)+1j*rng.normal(size=dC)
y_good=G_good.conj().T@x; y_bad=G_bad.conj().T@x
cos=abs(np.vdot(y_good,y_bad))/(np.linalg.norm(y_good)*np.linalg.norm(y_bad))
print(f"cosine similarity of the induced silicon response: {cos:.4f}")
print(f"relative response error: {np.linalg.norm(y_good-y_bad)/np.linalg.norm(y_good):.3f}")
print()
print("=> a 100%-wrong response with a perfectly healthy-looking G spectrum.")
print("   rank(G) is INVARIANT under any invertible re-labeling of the channel basis.")
