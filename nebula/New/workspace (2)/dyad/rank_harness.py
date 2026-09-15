"""
Anisotropic rank-tracking harness for the cross-substrate coupling G.

Per turn t, given paired carbon and silicon feature matrices over a token window,
estimate the effective linear coupling by cross-covariance and report the spectral
statistics that ADDENDUM section 3 argues are the real bandwidth variables.

    G_t = Cov_centered(X_carbon, Y_silicon)        (dC x dS)
    sigma_1 >= ... >= sigma_min                     singular spectrum
    noise floor  eps_t = median(sigma) * tol        (or a supplied estimate)

Reported per turn
-----------------
rank_eff   : #{sigma_i > eps}                       integer, but discontinuous --
             do NOT use as a control variable, it jumps
PR         : participation ratio (sum p)^2/sum p^2, p_i = sigma_i^2/sum sigma^2
             continuous, dimensionless, in [1, min(dC,dS)]  <- USE THIS
spec_entropy : -sum p_i log p_i, continuous, in [0, log min(dC,dS)]
f_dark     : (sum_{sigma<=eps} sigma^2) / (sum sigma^2)
             the "dark-mode energy fraction" of ADDENDUM section 4.3 / section 6.3,
             now actually defined: fraction of coupling energy in closed channels

IMPORTANT -- see `cert_test.py`. Every statistic above is invariant under a unitary
re-labeling of the channel basis, and therefore cannot distinguish a grounded
coupling from a confidently wrong one. These are BANDWIDTH measures, not CORRECTNESS
measures. They bound how much can cross the boundary; they say nothing about whether
what crosses is true. Any "safety certificate" built on them alone is unsound.
"""
import numpy as np


def coupling_spectrum(Xc, Ys, tol=0.15):
    """
    Estimate the effective coupling spectrum from paired feature windows.

    Xc : (n_samples, dC) carbon-side features over the window
    Ys : (n_samples, dS) silicon-side features over the window
    Returns dict of spectral statistics.
    """
    Xc = np.asarray(Xc, float); Ys = np.asarray(Ys, float)
    n = min(len(Xc), len(Ys))
    if n < 3:
        return {k: np.nan for k in ("rank_eff", "PR", "spec_entropy", "f_dark",
                                    "smax", "smin", "cond")}
    A = Xc[:n] - Xc[:n].mean(0); B = Ys[:n] - Ys[:n].mean(0)
    # cross-covariance, scaled so the spectrum is in correlation units
    G = (A.T @ B) / max(n - 1, 1)
    nrm = np.sqrt(np.sum(G ** 2))
    if nrm < 1e-12:
        return dict(rank_eff=0, PR=0.0, spec_entropy=0.0, f_dark=1.0,
                    smax=0.0, smin=0.0, cond=np.inf)
    sigma = np.linalg.svd(G, compute_uv=False)
    p = sigma ** 2 / np.sum(sigma ** 2)
    eps = tol * sigma[0]
    open_mask = sigma > eps
    return dict(
        rank_eff=int(np.sum(open_mask)),
        PR=float(np.sum(p) ** 2 / np.sum(p ** 2)),
        spec_entropy=float(-np.sum(p[p > 0] * np.log(p[p > 0]))),
        f_dark=float(np.sum(sigma[~open_mask] ** 2) / np.sum(sigma ** 2)),
        smax=float(sigma[0]),
        smin=float(sigma[-1]),
        cond=float(sigma[0] / max(sigma[-1], 1e-300)),
        spectrum=sigma,
    )


class RankTracker:
    """Accumulate coupling spectra across a session and expose them as a dataframe-ish dict."""

    FIELDS = ("rank_eff", "PR", "spec_entropy", "f_dark", "smax", "smin", "cond")

    def __init__(self, tol=0.15):
        self.tol = tol
        self.rows = []

    def push(self, turn, Xc, Ys, **extra):
        st = coupling_spectrum(Xc, Ys, tol=self.tol)
        rec = {"turn": turn}
        rec.update({k: st[k] for k in self.FIELDS})
        rec.update(extra)
        self.rows.append(rec)
        return st

    def column(self, key):
        return np.array([r[key] for r in self.rows], float)

    def table(self):
        keys = ("turn",) + self.FIELDS
        hdr = [r for r in self.rows[0] if r in keys or r == "divergence"]
        lines = ["  ".join(f"{h:>12}" for h in hdr)]
        for r in self.rows:
            lines.append("  ".join(f"{r.get(h, float('nan')):>12.4f}" for h in hdr))
        return "\n".join(lines)


def spearman(x, y):
    """Rank correlation without scipy, so the harness has no hard dependency."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 4:
        return np.nan
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    rx -= rx.mean(); ry -= ry.mean()
    d = np.sqrt(np.sum(rx ** 2) * np.sum(ry ** 2))
    return float(np.sum(rx * ry) / d) if d > 0 else np.nan
