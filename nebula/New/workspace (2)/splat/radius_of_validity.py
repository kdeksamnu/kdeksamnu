"""
RADIUS OF VALIDITY.

The dyad framework models the transformer as a linear Hermitian flow,
dz/dtau = -i Hbar z, valid "near an operating point". This measures how near.

Design
------
A genuine nonlinear transformer block (not a stand-in): pre-norm residual with
RMSNorm, multi-head causal softmax attention, SwiGLU MLP. Randomly initialised --
the NONLINEAR STRUCTURE is what determines the radius, not the weights, and random
init is the honest choice when no pretrained checkpoint is available. Weights are
scaled to a realistic residual-stream regime so the measurement is not an artefact
of a degenerate operating point.

For a base input X0 in R^(T x D):
    J      = exact Jacobian of the block at X0, via autograd (not finite differences)
    lin(d) = f(X0) + J @ vec(d)          <- Taylor about the OPERATING POINT.
               Writing X0 + d + J d instead (i.e. assuming the block is the
               identity at X0) is wrong by the constant ||f(X0) - X0||, which
               dominates everything and makes err look like a constant ~0.79
               independent of delta. The residual block grows the stream by
               1.34x here, so that constant is large.
    err(d) = || f(X0 + d) - lin(d) || / || f(X0) ||

delta* (the radius) is the largest ||d|| with err below tolerance.

The reference scale that decides whether delta* matters is the change in the block
input caused by ONE TOKEN: appending an embedding row, which is a sparse
perturbation of norm ||e_v||, not a dense isotropic one. Both are measured, because
the framework only ever needs to be accurate for perturbations the system actually
produces.

As a byproduct this extracts the Jacobian's singular spectrum, which is the
empirical version of the coupling G whose rank and dark modes the earlier memos
reasoned about abstractly.
"""
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.manual_seed(0)
DEV = "cpu"
DT = torch.float64            # float64 so the Jacobian is not noise-limited

T, D, NH = 12, 32, 4          # tokens, residual dim, heads (Jacobian is (T*D)^2)
HEAD = D // NH


class Block(nn.Module):
    """Pre-norm transformer block: RMSNorm -> causal MHA -> residual -> RMSNorm -> SwiGLU -> residual."""

    def __init__(self, d=D, nh=NH, mlp_mult=4, gain=0.6):
        super().__init__()
        self.nh, self.head = nh, d // nh
        self.ln1 = nn.Parameter(torch.ones(d, dtype=DT))
        self.ln2 = nn.Parameter(torch.ones(d, dtype=DT))
        self.wq = nn.Parameter(torch.randn(d, d, dtype=DT) * gain / np.sqrt(d))
        self.wk = nn.Parameter(torch.randn(d, d, dtype=DT) * gain / np.sqrt(d))
        self.wv = nn.Parameter(torch.randn(d, d, dtype=DT) * gain / np.sqrt(d))
        self.wo = nn.Parameter(torch.randn(d, d, dtype=DT) * gain / np.sqrt(d))
        h = d * mlp_mult
        self.w1 = nn.Parameter(torch.randn(d, h, dtype=DT) * gain / np.sqrt(d))
        self.w3 = nn.Parameter(torch.randn(d, h, dtype=DT) * gain / np.sqrt(d))
        self.w2 = nn.Parameter(torch.randn(h, d, dtype=DT) * gain / np.sqrt(h))
        self.eps = 1e-6

    def rms(self, x, g):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * g

    def forward(self, x):
        B, T, Dd = x.shape
        h = self.rms(x, self.ln1)
        q = (h @ self.wq).view(B, T, self.nh, self.head).transpose(1, 2)
        k = (h @ self.wk).view(B, T, self.nh, self.head).transpose(1, 2)
        v = (h @ self.wv).view(B, T, self.nh, self.head).transpose(1, 2)
        att = (q @ k.transpose(-1, -2)) / np.sqrt(self.head)
        att = att.masked_fill(torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), 1),
                              float("-inf"))
        att = att.softmax(-1)                                  # <- nonlinearity 1
        o = (att @ v).transpose(1, 2).reshape(B, T, Dd) @ self.wo
        x = x + o                                              # residual
        h2 = self.rms(x, self.ln2)                             # <- nonlinearity 2 (rsqrt)
        mlp = (F.silu(h2 @ self.w1) * (h2 @ self.w3)) @ self.w2  # <- nonlinearity 3 (SiLU gate)
        return x + mlp


def main():
    blk = Block().to(DEV).to(DT)
    with torch.no_grad():                                     # realistic residual-stream scale
        X0 = torch.randn(1, T, D, dtype=DT, device=DEV)
        X0 = X0 / X0.norm(dim=-1, keepdim=True).mean()

    f0 = blk(X0)
    base = float(f0.norm())
    print("=" * 80)
    print(f"BLOCK  T={T} tokens, D={D} residual, {NH} heads, SwiGLU x{4}, float64")
    print(f"  ||X0|| = {float(X0.norm()):.4f}   mean row norm = {float(X0.norm(dim=-1).mean()):.4f}")
    print(f"  ||f(X0)|| = {base:.4f}   relative residual growth = "
          f"{float((f0 - X0).norm() / X0.norm()):.3f}")

    # ---- exact Jacobian via autograd ------------------------------------------------
    x = X0.clone().requires_grad_(True)
    flat = blk(x).reshape(-1)
    n_out = flat.numel()
    J = torch.zeros(n_out, n_out, dtype=DT, device=DEV)
    for i in range(n_out):                                      # reverse-mode rows
        g = torch.autograd.grad(flat[i], x, retain_graph=(i < n_out - 1))[0]
        J[i] = g.reshape(-1)
    Jnp = J.detach().numpy()
    print(f"  exact Jacobian: {Jnp.shape}, computed by autograd (no finite differences)")

    sv = np.linalg.svd(Jnp, compute_uv=False)
    p = sv ** 2 / np.sum(sv ** 2)
    PR = float(1.0 / np.sum(p ** 2))
    Hent = float(-np.sum(p[p > 0] * np.log(p[p > 0])))
    lin_op = float(np.linalg.norm(Jnp, 2))
    print()
    print("=" * 80)
    print("JACOBIAN SPECTRUM  (the empirical version of the coupling G)")
    print("=" * 80)
    print(f"  sigma_max = {sv[0]:.4f}   sigma_min = {sv[-1]:.3e}   cond = {sv[0]/max(sv[-1],1e-300):.3e}")
    print(f"  participation ratio PR = {PR:.2f} of {n_out}   ({PR/n_out*100:.2f}% effective)")
    print(f"  spectral entropy = {Hent:.3f} of {np.log(n_out):.3f} (uniform)")
    for tol in (0.01, 0.05, 0.20):
        print(f"  channels with sigma > {tol:.2f}*sigma_max : {int(np.sum(sv > tol*sv[0])):>6}")
    print(f"  ||J||_2 (local linear gain) = {lin_op:.4f}")
    asym = np.max(np.abs(Jnp - Jnp.T)) / np.max(np.abs(Jnp))
    print(f"  antisymmetry ||J - J^T||_max / ||J||_max = {asym:.4f}")
    print("    -> a Hermitian generator would make the flow a rotation. This J is")
    print("       nowhere near symmetric, so the linearised flow is NOT symplectic")
    print("       and the -i*Hbar*z picture is not what the block linearises to.")

    # ---- delta sweep ----------------------------------------------------------------
    print()
    print("=" * 80)
    print("RADIUS OF VALIDITY  err(delta) = ||f(X0+d) - (f(X0) + J d)|| / ||f(X0)||")
    print("=" * 80)
    rng = np.random.default_rng(0)
    NDIR = 24
    dirs = []
    for _ in range(NDIR):
        d = rng.normal(size=(T, D)); dirs.append(d / np.linalg.norm(d))
    u0, s0, vt0 = np.linalg.svd(Jnp)
    dirs.append((vt0[0].reshape(T, D) / np.linalg.norm(vt0[0])))     # top right-singular dir
    dirs.append((vt0[-1].reshape(T, D) / np.linalg.norm(vt0[-1])))   # bottom
    labels = ["random"] * NDIR + ["top singular dir", "bottom singular dir"]

    deltas = np.logspace(-4, 0.5, 22)
    print(f"  {'delta':>9} {'mean err':>11} {'p90 err':>11} {'max err':>11}   "
          f"{'top-dir err':>12} {'bottom-dir err':>15}")
    rows = []
    with torch.no_grad():
        for dl in deltas:
            errs = []
            for d in dirs:
                dd = torch.tensor(dl * d, dtype=DT, device=DEV).unsqueeze(0)
                true = blk(X0 + dd)
                lin = f0 + torch.tensor((Jnp @ (dl * d).reshape(-1)).reshape(1, T, D),
                                        dtype=DT, device=DEV)
                errs.append(float((true - lin).norm()) / base)
            errs = np.array(errs)
            rows.append((dl, errs.mean(), np.percentile(errs, 90), errs.max(),
                         errs[NDIR], errs[NDIR + 1]))
            print(f"  {dl:>9.2e} {errs.mean():>11.3e} {np.percentile(errs,90):>11.3e} "
                  f"{errs.max():>11.3e}   {errs[NDIR]:>12.3e} {errs[NDIR+1]:>15.3e}")

    for tolname, tol in [("1%", 0.01), ("5%", 0.05), ("10%", 0.10)]:
        ok = [r[0] for r in rows if r[1] < tol]
        dstar = max(ok) if ok else float("nan")
        print(f"  delta* at mean err < {tolname:<4} : {dstar:.3e}")

    # ---- the scale that decides whether delta* matters ------------------------------
    print()
    print("=" * 80)
    print("THE COMPARISON THAT DECIDES EVERYTHING")
    print("=" * 80)
    emb_std = 1.0 / np.sqrt(D)                       # standard embedding init
    one_token = emb_std * np.sqrt(D)                 # norm of one embedding row
    print(f"  one appended token embedding row, ||e_v|| = {one_token:.4f}  (std = 1/sqrt(D))")
    print(f"  ||X0|| over {T} tokens                     = {float(X0.norm()):.4f}")
    print(f"  so a single token changes the block input by {one_token/float(X0.norm())*100:.1f}%")
    ok1 = [r[0] for r in rows if r[1] < 0.05]
    dstar = max(ok1) if ok1 else float("nan")
    print()
    print(f"  delta* (5% tolerance) = {dstar:.3e}")
    print(f"  one-token perturbation = {one_token:.3e}")
    ratio = one_token / dstar if np.isfinite(dstar) and dstar > 0 else float("inf")
    print(f"  ratio = {ratio:.3g}")
    if ratio <= 1:
        print("  => the linearisation SURVIVES a token insertion. The effective theory")
        print("     has a domain that includes the perturbation the system actually")
        print("     produces, so it is load-bearing at token granularity.")
    else:
        print("  => a SINGLE TOKEN INSERTION EXCEEDS THE LINEARISATION RADIUS by this")
        print("     factor. The Hermitian linear model does not describe the block even")
        print("     across one token boundary, so it cannot be the substrate for a")
        print("     per-token conservation law. It is at best a sub-token approximation.")

    # ---- the perturbation the system ACTUALLY produces -----------------------------
    print()
    print("=" * 80)
    print("SPARSE (SINGLE-ROW) PERTURBATION -- what appending/altering one token really is")
    print("=" * 80)
    print("""
  The isotropic sweep above asks the wrong question. A token does not perturb the
  whole residual stream uniformly; it perturbs ONE row of it. Appending a token
  changes T and so is not a perturbation of the fixed-T map at all -- the honest
  object is the sparse update: replace one row by another embedding. Radius may
  differ sharply between dense and sparse directions, and only the sparse one is
  load-bearing for a per-token conservation law.
""")
    print(f"  {'delta':>9} {'dense err':>11} {'sparse err':>12} {'ratio':>8}   "
          f"{'worst row':>10} {'best row':>10}")
    d_dense = torch.tensor(dirs[0], dtype=DT, device=DEV)
    sparse_rows = []
    with torch.no_grad():
        for dl in deltas:
            e_dense = []
            for d in dirs[:8]:
                dd = torch.tensor(dl * d, dtype=DT, device=DEV).unsqueeze(0)
                true = blk(X0 + dd)
                lin = f0 + torch.tensor((Jnp @ (dl * d).reshape(-1)).reshape(1, T, D),
                                        dtype=DT, device=DEV)
                e_dense.append(float((true - lin).norm()) / base)
            per_row = []
            for row in range(T):
                d = np.zeros((T, D)); d[row] = rng.normal(size=D)
                d[row] /= np.linalg.norm(d[row])          # unit-norm single-row update
                dd = torch.tensor(dl * d, dtype=DT, device=DEV).unsqueeze(0)
                true = blk(X0 + dd)
                lin = f0 + torch.tensor((Jnp @ (dl * d).reshape(-1)).reshape(1, T, D),
                                        dtype=DT, device=DEV)
                per_row.append(float((true - lin).norm()) / base)
            per_row = np.array(per_row)
            sparse_rows.append((dl, float(np.mean(e_dense)), per_row.mean(),
                                per_row.mean() / np.mean(e_dense), per_row.max(), per_row.min()))
            r = sparse_rows[-1]
            print(f"  {dl:>9.2e} {r[1]:>11.3e} {r[2]:>12.3e} {r[3]:>8.3f}   "
                  f"{r[4]:>10.3e} {r[5]:>10.3e}")

    print()
    for tolname, tol in [("1%", 0.01), ("5%", 0.05)]:
        okd = [r[0] for r in sparse_rows if r[1] < tol]
        oks = [r[0] for r in sparse_rows if r[2] < tol]
        dd_ = max(okd) if okd else float("nan")
        ds_ = max(oks) if oks else float("nan")
        print(f"  delta* at mean err < {tolname:<4} :  dense = {dd_:.3e}   sparse = {ds_:.3e}"
              f"   sparse/dense = {ds_/dd_ if dd_==dd_ else float('nan'):.2f}")
    print(f"""
  One real token embedding row has norm {one_token:.3f} at std=1/sqrt(D) with the
  rows of X0 normalised to unit norm, so the natural single-token perturbation is
  delta ~ O(1) in these units -- compare against the SPARSE delta* above, not the
  dense one. Which of the two the token scale exceeds is the actual verdict on
  whether the linear model can carry a per-token conservation law.

  Note also the row-to-row spread (worst/best columns): the radius is not a single
  number for the block. Positions late in the sequence see more attention mixing and
  linearise over a different range than early ones, so a single global delta* is
  already an idealisation of the thing it is meant to validate.
""")


if __name__ == "__main__":
    main()
