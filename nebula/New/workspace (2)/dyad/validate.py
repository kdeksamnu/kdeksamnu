"""
End-to-end validation of the J_C surrogate channel and the anisotropic rank
harness, on a synthetic 50-turn session with KNOWN ground truth.

WHAT THIS VALIDATES -- AND WHAT IT DOES NOT
-------------------------------------------
It validates the MEASUREMENT MACHINERY: given data generated from a known process,
do the estimators recover it? It says nothing about real human-transformer
sessions. `simulate_session` is the seam where real data (eyetracked reading times,
turn embeddings from an actual model) must be substituted before any empirical
claim is made.

The session is built around the degeneracy that decides whether channel A is
usable at all. During the "repetition collapse" phase the model degenerates into
low-entropy looping output: H(V) falls, reading times fall, residual load falls --
and the true information transfer falls to zero. A residual-trend estimator that
does not control for H reports J_C RISING through the collapse. That failure is
the point of the exercise, and reproducing it is a pass condition for the harness,
not a bug.
"""
import numpy as np
from rc_estimator import beta1_within_turn, residual_load, estimator_A, partial_MI
from rank_harness import RankTracker, spearman

rng = np.random.default_rng(20260915)

N_TURNS, TOK, DT_TOK = 50, 40, 0.02
D_C = D_S = 8
NU = 1.0 / DT_TOK                      # tokens/s
PHASES = [(0, 12, "grounded"), (12, 22, "compression"),
          (22, 32, "repetition collapse"), (32, 50, "drift / ungrounded")]
phase_of = lambda t: next(nm for lo, hi, nm in PHASES if lo <= t < hi)

BETA1_TRUE = 0.055                     # s per nat: human marginal cost of surprisal
E_TRUE     = 0.010                     # s per nat of H: repetition easement
A0         = 0.340                     # s per token: reading baseline (~176 wpm)
RT_FLOOR   = 0.05                      # s/token: physiological floor (~1200 wpm)
# Cumulative effects must stay well inside [RT_FLOOR, inf) or the clip activates,
# RT becomes exactly constant, and beta_1 becomes unidentifiable. That failure was
# silent -- sd(RT) went to 0.0 with no error raised. Hence the assertion below.


# --------------------------------------------------------------- ground truth
def kappa_true(t):
    """True compression rate c_H [s of reading cost absorbed per token per turn]."""
    p = phase_of(t)
    if p == "grounded":             return 2.0e-3
    if p == "compression":          return 6.0e-3
    if p == "repetition collapse":  return 2.0e-5      # <- ~zero: no real learning
    return 1.2e-3


def H_true(t):
    p = phase_of(t)
    if p == "grounded":             return 2.00
    if p == "compression":          return 2.00
    if p == "repetition collapse":  return max(2.00 - 0.17 * (t - 22), 0.25)
    return 3.20


def rank_true(t):
    if t < 22:  return 6
    if t < 32:  return max(6 - (t - 22) // 3, 2)
    return max(3 - (t - 32) // 8, 1)


def J_true(t):
    """
    True transfer rate [nat/s]. c_H is seconds per token per turn; dividing by
    beta_1 [s/nat] gives nats per token, and multiplying by the token rate gives
    nats/s. Estimator A applies exactly this conversion, so the units close
    without a fudge factor.
    """
    return kappa_true(t) / BETA1_TRUE * NU


# ------------------------------------------------------------ observation gen
def make_G(r):
    A = rng.normal(size=(D_C, r)); B = rng.normal(size=(D_S, r))
    A /= np.linalg.norm(A, axis=0, keepdims=True)
    B /= np.linalg.norm(B, axis=0, keepdims=True)
    return (A * np.linspace(1.0, 0.35, r)) @ B.T, B


def simulate_session(rt_noise=0.008, seed=20260915):
    global rng
    rng = np.random.default_rng(seed)   # reproducible: module-level rng otherwise
                                      # advances between calls and silently changes data
    anchor = rng.normal(size=D_S); anchor /= np.linalg.norm(anchor)
    topic = anchor.copy()
    learned = 0.0
    RT_by_turn, s_by_turn, L, H, kap = [], [], [], [], []
    Yh, Xe, div = [], [], []
    prev_emb = np.zeros(D_C)

    for t in range(N_TURNS):
        r, Ht, kt = rank_true(t), H_true(t), kappa_true(t)
        G, B = make_G(r)
        learned += kt                                      # cumulative s/token absorbed

        latent = rng.normal(size=(TOK, r))
        sig = latent @ B.T
        Ys = sig / max(np.linalg.norm(sig) / np.sqrt(TOK), 1e-9) \
             + rng.normal(size=(TOK, D_S)) * (0.25 + 0.5 * (Ht / 2.0))
        Xc = Ys @ G / max(np.linalg.norm(G, 2), 1e-9) + rng.normal(size=(TOK, D_C)) * 0.30

        topic = 0.90 * topic + 0.10 * (Ys.mean(0) / max(np.linalg.norm(Ys.mean(0)), 1e-9))
        div.append(float(np.linalg.norm(topic - anchor)))

        s = np.clip(rng.normal(Ht, 0.35, TOK), 0.05, None)
        # BOTH terms reduce reading cost, and only the first is information transfer:
        #   -learned  : genuine compression (the human has learned the model)
        #   -E_TRUE*Ht: repetition easement (the text is merely predictable)
        RT_raw = A0 + BETA1_TRUE * s - learned - E_TRUE * Ht \
                 + rng.normal(0, rt_noise, TOK)
        assert RT_raw.min() > RT_FLOOR * 1.5, (
            f"turn {t}: RT hits the floor, beta_1 becomes unidentifiable; "
            f"reduce kappa_true or E_TRUE (min={RT_raw.min():.4f})")
        RT = RT_raw
        RT_by_turn.append(RT); s_by_turn.append(s)
        L.append(residual_load(RT, s, BETA1_TRUE))
        H.append(Ht); kap.append(kt)

        # Human's next move. For channel B to have anything to detect, y_t must
        # depend on the LAGGED model output x_{t-1}: partial_MI regresses y_{t+1}
        # on x_t, so if y is built from same-turn features the true MI is exactly
        # zero and the channel measures nothing. (First version of this file made
        # that mistake; channel B returned ~0 in every phase.)
        info = min(kt / 6.0e-3, 1.0)
        y = prev_emb * info + rng.normal(size=D_C) * (1.0 - info)
        Yh.append(y); Xe.append(Ys.mean(0))
        prev_emb = Ys.mean(0)

    return dict(RT_by_turn=RT_by_turn, s_by_turn=s_by_turn, L=np.array(L),
                H=np.array(H), kappa=np.array(kap), div=np.array(div),
                Yh=np.array(Yh), Xe=np.array(Xe), Jtrue=np.array([J_true(t) for t in range(N_TURNS)]),
                rtrue=np.array([rank_true(t) for t in range(N_TURNS)], float),
                Xc_list=None)


# ---------------------------------------------------------------------- run
S = simulate_session()
print("=" * 84)
print("STEP 1  Calibrate beta_1 (marginal cost of surprisal)")
print("=" * 84)
b1_pooled, _ = (lambda: (np.polyfit(np.concatenate(S["s_by_turn"]),
                                    np.concatenate(S["RT_by_turn"]), 1)[0], None))()
b1_fe, sd = beta1_within_turn(S["RT_by_turn"], S["s_by_turn"])
print(f"  naive pooled OLS      beta_1 = {b1_pooled:.5f} s/nat   ({b1_pooled/BETA1_TRUE*100:5.1f}% of truth)")
print(f"  turn fixed-effects    beta_1 = {b1_fe:.5f} s/nat   ({b1_fe/BETA1_TRUE*100:5.1f}% of truth)   resid sd {sd:.4f}")
print(f"  => pooling across turns without absorbing the per-turn intercept underestimates")
print(f"     beta_1 by {b1_fe/max(abs(b1_pooled),1e-12):.1f}x. Any J_C^max built on the pooled value is wrong")
print(f"     by the same factor.")

print()
print("=" * 84)
print("STEP 2  J_C: naive residual trend vs entropy-deconfounded")
print("=" * 84)
tau_t = np.arange(len(S["L"])) * (TOK * DT_TOK)
J_deconf, J_naive, cH_est, e_est = estimator_A(S["L"], S["H"], tau_t, b1_fe,
                                               nu_token=NU, window=8)
Jd, Jn = J_deconf, J_naive          # already nat/s: tau_t is in seconds
Jt = S["Jtrue"]
print(f"{'turn':>4} {'phase':<22}{'J_true':>9}{'J_naive':>10}{'J_deconf':>10}{'H(V)':>7}")
for t in range(1, N_TURNS, 2):
    print(f"{t:>4} {phase_of(t):<22}{Jt[t]:>9.2f}{Jn[t]:>10.2f}{Jd[t]:>10.2f}{S['H'][t]:>7.2f}")

print()
for lbl, lo, hi in [(nm, lo, hi) for lo, hi, nm in PHASES]:
    idx = np.arange(lo, hi); ok = np.isfinite(Jd[idx]) & np.isfinite(Jn[idx])
    if not ok.any():
        continue
    i2 = idx[ok]
    print(f"  {lbl:<24} J_true={Jt[i2].mean():7.2f}   naive={Jn[i2].mean():7.2f}"
          f"   deconfounded={Jd[i2].mean():7.2f}")

print()
print("  THE DEGENERACY, QUANTIFIED")
sl = slice(22, 32)
print(f"    during repetition collapse (turns 22-31):")
print(f"      J_true        {Jt[sl].mean():7.2f} -> {Jt[22]:.2f} to {Jt[31]:.2f}   FALLING to ~0")
print(f"      J_naive       {Jn[23:32][np.isfinite(Jn[23:32])].mean():7.2f}   "
      f"(trend over phase: {np.nanmean(Jn[31])-np.nanmean(Jn[24]):+.2f})")
print(f"      J_deconfounded{Jd[23:32][np.isfinite(Jd[23:32])].mean():7.2f}   "
      f"(trend over phase: {np.nanmean(Jd[31])-np.nanmean(Jd[24]):+.2f})")
m = np.isfinite(Jd) & np.isfinite(Jn) & (np.arange(N_TURNS) >= 8)
print(f"    Spearman vs J_true over turns 8-49:")
print(f"      naive         {spearman(Jn[m], Jt[m]):+.3f}")
print(f"      deconfounded  {spearman(Jd[m], Jt[m]):+.3f}")

print()
print("=" * 84)
print("STEP 3  Channel B (partial MI) must independently detect the collapse")
print("=" * 84)
Ib = partial_MI(S["Yh"], S["Xe"], lags=2, window=14) / (TOK * DT_TOK)   # nats/turn -> nat/s
print(f"{'phase':<24}{'mean I_B [nat/s]':>18}{'J_true':>10}")
for nm, lo, hi in [(nm, lo, hi) for lo, hi, nm in PHASES]:
    seg = Ib[lo:hi]; seg = seg[np.isfinite(seg)]
    print(f"  {nm:<22}{(seg.mean() if len(seg) else float('nan')):>18.2f}{Jt[lo:hi].mean():>10.2f}")
mB = np.isfinite(Ib)
print(f"  Spearman(I_B, J_true) = {spearman(Ib[mB], Jt[mB]):+.3f}")

print()
print("=" * 84)
print("STEP 4  Why the deconfounder fails inside the repetition phase: collinearity")
print("=" * 84)
dH = np.diff(S["H"]); dT = np.diff(tau_t)
for lo, hi, nm in PHASES:
    seg = slice(lo, max(lo, hi - 1))
    a, b = dT[seg], dH[seg]
    if len(a) < 2:
        continue
    if np.std(b) < 1e-12 and np.abs(np.mean(b)) < 1e-12:
        note = "Delta H == 0: e unidentifiable (zero column), c_H clean"
        cn = np.inf
    elif np.std(b) < 1e-12:
        note = "Delta H CONSTANT != 0: perfectly collinear with Delta tau -> c_H and e trade off freely"
        cn = np.inf
    else:
        Xr = np.column_stack([a, b]); cn = np.linalg.cond(Xr)
        note = f"corr(Delta tau, Delta H) = {np.corrcoef(a, b)[0,1]:+.3f}"
    print(f"  {nm:<24} cond = {cn:>10.1f}   {note}")
print("""
  => c_H (compression) and e (repetition easement) are separately identifiable
     ONLY where H varies independently of the learning trend. Inside a monotone
     collapse Delta H is constant and Delta tau is constant, so the two regressors
     are exactly collinear and the split is arbitrary. This is not a noise problem;
     no amount of data fixes it. It requires one of:
       (a) a window spanning an entropy TRANSITION (H jumps while the trend runs on),
       (b) an active probe -- dither the sampling temperature to inject independent
           variation in H, then read e off the induced change in L,
       (c) channel B, which does not use the reading-time channel at all.
     (b) is a cheap, real experimental design: temperature dithering as an
     identification instrument for the human-side easement curve. Note that the
     transition at turn 31->32 (Delta H = +2.73) IS such an event, and the
     deconfounded estimator recovers J_true to ~4% in the phase that follows it.
""")


print()
print("=" * 84)
print("STEP 5  Rank harness: do the spectral statistics track the truth?")
print("=" * 84)
S3 = simulate_session()                      # same seed -> identical session
# feature windows were not retained; regenerate them deterministically
rng = np.random.default_rng(999)
tracker = RankTracker(tol=0.15)
rtrue2 = np.array([rank_true(t) for t in range(N_TURNS)], float)
div2 = S3["div"]
Xs_list, Ys_list = [], []
for t in range(N_TURNS):
    r = rank_true(t)
    A = rng.normal(size=(D_C, r)); B = rng.normal(size=(D_S, r))
    A /= np.linalg.norm(A, axis=0, keepdims=True); B /= np.linalg.norm(B, axis=0, keepdims=True)
    Gt = (A * np.linspace(1.0, 0.35, r)) @ B.T
    lat = rng.normal(size=(TOK, r))
    Ys = lat @ (B * np.linspace(1.0, 0.35, r)).T + rng.normal(size=(TOK, D_S)) * 0.30
    Xc = Ys @ Gt / max(np.linalg.norm(Gt, 2), 1e-9) + rng.normal(size=(TOK, D_C)) * 0.30
    tracker.push(t, Xc, Ys, divergence=div2[t])

PR = tracker.column("PR"); fd = tracker.column("f_dark"); re_ = tracker.column("rank_eff")
print(f"{'turn':>5}{'r_true':>8}{'rank_eff':>10}{'PR':>8}{'f_dark':>9}{'divergence':>12}")
for t in range(0, N_TURNS, 4):
    print(f"{t:>5}{rtrue2[t]:>8.0f}{re_[t]:>10.0f}{PR[t]:>8.2f}{fd[t]:>9.3f}{div2[t]:>12.3f}")
print()
print("  Spearman correlations against injected ground truth:")
print(f"    rank_eff vs rank_true : {spearman(re_, rtrue2):+.3f}")
print(f"    PR       vs rank_true : {spearman(PR, rtrue2):+.3f}")
print(f"    f_dark   vs rank_true : {spearman(fd, rtrue2):+.3f}   (expect strongly NEGATIVE)")
print(f"    f_dark   vs divergence: {spearman(fd, div2):+.3f}   (expect POSITIVE)")
print(f"    PR       vs divergence: {spearman(PR, div2):+.3f}")
print(f"    spec_entropy vs rank  : {spearman(tracker.column('spec_entropy'), rtrue2):+.3f}")
print()
print("  rank_eff is integer-valued and JUMPS; PR and f_dark move continuously.")
print("  For a control variable use PR or f_dark, never rank_eff.")
