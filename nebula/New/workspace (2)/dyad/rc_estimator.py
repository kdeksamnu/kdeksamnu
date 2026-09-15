"""
Surrogate channel for J_C = dR_C/dtau.

The binding constraint identified in ADDENDUM section 4: the Gamma-governor needs an
online estimate of the human's surprise-reduction rate, which is not directly
observable. Two estimators are implemented here, and they are NOT redundant -- they
disagree in exactly the regime that matters (see `validate.py`, degeneracy test).

Estimator A -- reading-time residual (channel A)
------------------------------------------------
Assumes a linear surprisal cost of reading:
    RT_k = beta_0 + beta_1 * s_k + noise,     s_k = -log p_model(token_k)
OLS-fit (beta_0, beta_1) on a sliding window. beta_1 is the human's *marginal cost
of surprisal*, in s/nat -- a directly interpretable physiological quantity, and the
one that sets J_C^max via  J_C^max = (marginal metabolic headroom) / beta_1 / eps_C.

The residual r_k = RT_k - fit_k is the surprisal the MODEL failed to anticipate:
the part of the human's processing load that is not explained by the emitted
distribution. A falling residual trend means the human is compressing the stream.

    Jhat_C^A = -d/dtau [ mean_window(r) ]

Estimator B -- predictive mutual information (channel B)
--------------------------------------------------------
    I_t = H(y_t | y_<t) - H(y_t | y_<t, x_t)

how much the model's output x_t reduces uncertainty about the human's next move
y_t. Estimated with incrementally-fitted predictors on both conditionals. This is
the quantity that actually means "information transferred", and it is the only one
of the two that can tell *compression* apart from *repetition*.

Both return nats per unit tau. Neither requires the human's true distribution.
"""
import numpy as np


def _ols(X, y):
    """Least squares with ridge fallback for rank-deficient windows."""
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtX = X.T @ X
    XtX = XtX + 1e-8 * np.eye(X.shape[1]) * (np.trace(XtX) / max(X.shape[1], 1) + 1e-12)
    return np.linalg.solve(XtX, X.T @ y)


def beta1_within_turn(RT_by_turn, s_by_turn):
    """
    Calibrate the marginal cost of surprisal, beta_1 [s/nat], using a TURN
    FIXED-EFFECTS regression:

        RT_{t,k} = alpha_t + beta_1 * s_{t,k} + eps_{t,k}

    Pooling raw (RT, s) across turns is WRONG and is the bug this replaces: the
    per-turn intercept alpha_t absorbs a large between-turn variance (baseline
    effort, fatigue, entropy level), and if it is not absorbed it swamps the
    within-turn surprisal slope. Measured effect: naive pooled OLS underestimates
    beta_1 by ~29x on the synthetic session in validate.py.
    """
    Xs, Ys = [], []
    for RT, s in zip(RT_by_turn, s_by_turn):
        RT = np.asarray(RT, float); s = np.asarray(s, float)
        if len(RT) < 4:
            continue
        Xs.append(s - s.mean()); Ys.append(RT - RT.mean())   # within-turn demeaning
    if not Xs:
        return np.nan, np.nan
    x = np.concatenate(Xs); y = np.concatenate(Ys)
    b1 = float(x @ y / max(x @ x, 1e-30))
    resid = y - b1 * x
    return b1, float(np.sqrt(np.mean(resid ** 2)))


def residual_load(RT, s, beta1):
    """
    Turn-level residual processing load L_t [s/token]: the part of the human's
    reading cost NOT explained by the model's emitted surprisal, after removing
    the calibrated surprisal cost and the turn's mean reading time is retained
    as the level.

        L_t = mean_k RT_{t,k} - beta_1 * mean_k s_{t,k}

    L_t is the observable that J_C is read off. It is NOT yet J_C -- see the
    confound note below.
    """
    RT = np.asarray(RT, float); s = np.asarray(s, float)
    return float(RT.mean() - beta1 * s.mean())


def estimator_A(L, H, tau, beta1, nu_token=None, window=8):
    """
    J_C = dR_C/dtau from the residual-load series L_t, deconfounded against the
    model's emitted entropy.

    THE CONFOUND. L_t falls for two different reasons:
      (i)  COMPRESSION -- the human is learning the model's style. Real transfer.
      (ii) REPETITION -- the model collapsed to low-entropy output, so the text is
           merely easier to read. Transfer may be falling to ZERO.
    Both give identical signatures in the reading-time channel. H(V_t) is
    observable from the logits, and only (ii) comes with falling H.

    MODEL.   L_t = a0 - c_H * (t * dtau) - e * H_t + noise
    so       Delta L_t = -c_H * Delta tau - e * Delta H_t + noise
    Regress Delta L on (Delta tau, Delta H) over a trailing window -> (c_H, e).

    UNITS. Regressing Delta L on -Delta tau returns c_H directly in [s per token
    per second], because the regressor is already a time increment -- there is no
    separate per-turn factor to apply, and inserting one double-counts it (off by
    nu_turn, here 1.25x). Dividing by beta_1 [s/nat] gives [nat per token per
    second]; multiplying by nu_token [token/s] gives the transfer rate:

        Jhat_C = c_H / beta_1 * nu_token        [nat/s]

    Omitting 1/beta_1 leaves the right SHAPE and the wrong SCALE (off by ~18x
    here). Both errors are easy to miss because the estimator still tracks truth.

    Returns (Jhat, Jhat_naive, c_H, e). Jhat_naive is the confounded version that
    drops the Delta H regressor entirely.
    """
    L = np.asarray(L, float); H = np.asarray(H, float); tau = np.asarray(tau, float)
    n = len(L)
    J = np.full(n, np.nan); Jn = np.full(n, np.nan)
    cH = np.full(n, np.nan); ee = np.full(n, np.nan)
    dL = np.diff(L); dH = np.diff(H); dT = np.diff(tau)
    nu = nu_token if nu_token else 1.0
    for t in range(n - 1):
        lo = max(0, t - window + 1)
        if t - lo + 1 < 3:
            continue
        y = dL[lo:t + 1]
        X = np.column_stack([-dT[lo:t + 1], -dH[lo:t + 1]])
        c = _ols(X, y)
        cH[t + 1] = c[0]; ee[t + 1] = c[1]
        J[t + 1] = c[0] / beta1 * nu
        Xn = np.column_stack([-dT[lo:t + 1]])
        Jn[t + 1] = _ols(Xn, y)[0] / beta1 * nu
    for arr in (J, Jn, cH, ee):
        k = next((i for i in range(n) if np.isfinite(arr[i])), None)
        if k is not None:
            arr[:k] = arr[k]
    return J, Jn, cH, ee


def partial_MI(y, X, lags=2, window=14):
    """
    Channel B: information the model's output actually delivers about the human's
    next move, controlling for the human's own history.

    Measured as VARIANCE REDUCTION, not correlation -- this distinction is what
    makes the channel work. During a repetition collapse the human's next move
    becomes noise, so |y| shrinks and a correlation-based statistic becomes
    meaningless (both variables are noise; rho is undefined and its sign is
    arbitrary). A variance-reduction statistic degrades gracefully to zero.

        R2_t = 1 - Var(y_{t+1} | hist, x_t) / Var(y_{t+1} | hist)
        I_t  = -0.5 * log(1 - R2_t)                    [nats per turn]

    with hist = [1, y_t, ..., y_{t-lags+1}]. x_t is scored by projection onto its
    trailing-window principal direction so dX > 1 is handled.

    Looping output stops predicting the human's next move, so R2 -> 0 and I -> 0
    no matter how easy the text is to read. That is precisely what channel A
    cannot see.
    """
    y = np.asarray(y, float); X = np.asarray(X, float)
    if y.ndim > 1:
        y = y.mean(1)
    if X.ndim > 2:
        X = X.reshape(len(X), -1)
    n = min(len(y), len(X)); out = np.full(n, np.nan)
    for t in range(lags, n - 1):
        lo = max(lags, t + 1 - window)
        m = t + 1 - lo
        if m < lags + 5:
            continue
        hist = np.column_stack([np.ones(m)] + [y[lo + j:lo + j + m] for j in range(lags)])
        ytar = y[lo + lags: lo + lags + m]
        Xw = X[lo:lo + m]
        if len(ytar) != m or len(Xw) != m:
            continue
        # score x by its window principal direction (deterministic, no extra fit)
        Xc = Xw - Xw.mean(0)
        u, sv, vt = np.linalg.svd(Xc, full_matrices=False)
        xtar = Xc @ vt[0]
        h2 = np.column_stack([hist, xtar])
        r_base = ytar - hist @ _ols(hist, ytar)
        r_full = ytar - h2 @ _ols(h2, ytar)
        p0, p1 = hist.shape[1], h2.shape[1]
        if m - p0 - 1 < 3:
            continue
        ss0 = float(r_base @ r_base); ss1 = float(r_full @ r_full)
        if ss0 <= 1e-18:
            continue
        # ADJUSTED, not raw. With m ~ 12 samples, adding ANY regressor inflates raw
        # R^2 by ~1/(m-p0-1) ~ 0.11 even when x is pure noise, which swamps the
        # signal. The F-form adjustment removes exactly that bias:
        #     1 - R2_adj = (ss1/(m-p1-1)) / (ss0/(m-p0-1))
        ratio = (ss1 / (m - p1 - 1)) / (ss0 / (m - p0 - 1))
        R2 = float(np.clip(1.0 - ratio, 0.0, 0.999))
        out[t] = -0.5 * np.log(1.0 - R2)
    return out
