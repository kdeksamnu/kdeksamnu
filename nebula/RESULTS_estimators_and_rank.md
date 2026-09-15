# Results: the estimator, the rank harness, and three claims that did not survive

Companion to `MEMO_cross_substrate_noether.md` and `ADDENDUM_monadic_audit.md`.
This file reports what was built in response to the recommended next step, and what
it measured. Three claims from the summary/reframing were tested directly; **one is
refuted outright, one is unfalsifiable as stated, and one survives with a large
caveat.**

Files: `rc_estimator.py`, `rank_harness.py`, `validate.py` (+ `validate_output.txt`),
`part7_samplesize.py`, `cert_test.py`.

---

## 1. The "proof-of-safety certificate" is refuted

> §4.3: *"Replacing alignment fine-tuning with explicit rank(G) spectral monitoring
> in agent-to-agent swarms provides a structural proof-of-safety certificate: runtime
> halts execution the moment dark-mode energy fraction exceeds threshold."*

`cert_test.py` constructs two couplings, $\mathbf G_{\text{good}}$ and
$\mathbf G_{\text{bad}}$, related by a **unitary** re-labelling of the silicon
channel basis:

$$\mathbf G_{\text{bad}} = (\mathbf U\boldsymbol\sigma)\,\mathbf W_u\,\mathbf V^\dagger,\qquad \mathbf W_u\mathbf W_u^\dagger=\mathbf I$$

Because $\mathbf W_u$ is unitary the singular spectrum is preserved *exactly*, so:

```
statistic                        G_grounded     G_confidently_wrong   distinguishes?
------------------------------------------------------------------------------------
rank                                  8.000000              8.000000             NO
smin                                  0.200000              0.200000             NO
smax                                  9.000000              9.000000             NO
PR (participation ratio)              2.483668              2.483668             NO
spectral entropy                      1.151213              1.151213             NO
dark-mode fraction                    0.000000              0.000000             NO

cosine similarity of the induced silicon response: 0.2403
relative response error: 1.321      <- 132% wrong
```

**Every spectral statistic is bit-identical while the induced response is 132%
wrong.** This is not a limitation of the particular statistics chosen — it is
structural. $\mathrm{rank}(\mathbf G)$, $\sigma_i(\mathbf G)$, PR, spectral entropy,
effective bandwidth and $f_{\text{dark}}$ are all invariant under
$\mathbf G\mapsto\mathbf G\mathbf W$ for any invertible $\mathbf W$, i.e. under any
re-labelling of what the channels *mean*.

So the spectrum measures **how much can cross the boundary**, never **whether what
crosses is true**. A confidently hallucinating model can have a perfectly healthy
$\mathbf G$ spectrum. Three further problems with the claim as written:

1. **"Proof" is the wrong word for a monitor.** A certificate requires soundness —
   no unsafe state passes. The counterexample above is exactly an unsafe state that
   passes with a spectrum identical to a safe one.
2. **The threshold is undefined.** "$\eta Q(\tau_1)$" mixes a dimensionless
   fraction with a charge. And "dark-mode energy" was never defined; the harness
   here defines it as $f_{\text{dark}}=\sum_{\sigma_i\le\epsilon}\sigma_i^2\big/\sum_i\sigma_i^2$,
   which requires choosing the noise floor $\epsilon$ — a free parameter that
   determines when the system halts.
3. **Halting is not a safety property.** A halted agent that has already emitted
   10,000 tokens of confident fabrication has not been made safe.

**What survives:** spectral monitoring is a legitimate *bandwidth* and
*anomaly* signal. It can tell you the coupling is collapsing. It cannot tell you
the content is correct, and it must never be described as a certificate. Correctness
needs a correctness signal — an entailment check, a retrieval-grounding score, a
verifier — which is exactly the surrogate-$\mathbf G$ mechanism, and which is
*additional* to the spectrum, not readable from it.

---

## 2. The $d\mathcal R_C/d\tau$ estimator: built, and two real obstacles found

`rc_estimator.py` implements the surrogate channel; `validate.py` runs it against a
50-turn synthetic session with known ground truth, designed to contain the failure
mode that decides whether the reading-time channel is usable at all.

### 2.1 $\beta_1$ requires turn fixed effects — pooled OLS is wrong by 1.7×

The marginal cost of surprisal, $\beta_1$ [s/nat], is the calibration constant that
sets $J_C^{\max}$. Estimating it by pooling $(RT,s)$ across turns gives
**57.9%** of the true value; a turn fixed-effects (within-turn demeaned) regression
gives **98.9%**:

```
naive pooled OLS      beta_1 = 0.03187 s/nat   ( 57.9% of truth)
turn fixed-effects    beta_1 = 0.05438 s/nat   ( 98.9% of truth)   resid sd 0.0079
```

The reason: the per-turn intercept absorbs baseline effort, fatigue and the
entropy level. Left in the error term it contributes large between-turn variance
that is uncorrelated with the within-turn surprisal, attenuating the slope. Any
$J_C^{\max}$ built on a pooled $\beta_1$ is wrong by the same factor — and since
$J_C^{\max}$ sets the throttle, the error propagates straight into the governor.

### 2.2 The deconfounded estimator works in three of four phases

$$L_t = a_0 - c_H(t\,\Delta\tau) - e\,H_t + \text{noise},\qquad
\hat J_C = \hat c_H/\beta_1\cdot\nu_{\text{token}}$$

```
phase                     J_true    naive    deconfounded
grounded                     1.82     2.13          2.13     (+17%)
compression                  5.45     5.21          5.21     ( -4%)
repetition collapse          0.02     1.37          3.44     (  FAIL)
drift / ungrounded           1.09     2.49          1.05     ( -4%)
```

In the phases where $H$ is constant, the deconfounded estimator tracks the truth to
within 4–17%. In the drift phase it is accurate to 4% where the naive estimator is
off by 128%.

### 2.3 The repetition collapse breaks it — and this is structural, not noise

During a repetition collapse the model degenerates to low-entropy looping output.
Reading times fall. Residual load falls. **The true transferred information falls to
zero.** The naive estimator reports $J_C$ rising; so does the deconfounded one
(3.44 against a truth of 0.02). Step 4 of `validate.py` shows why:

```
phase                    cond     diagnosis
grounded                  inf     Delta H == 0: e unidentifiable (zero column)
compression               inf     Delta H == 0: e unidentifiable (zero column)
repetition collapse       inf     Delta H CONSTANT != 0: perfectly collinear with
                                  Delta tau -> c_H and e trade off freely
drift / ungrounded        inf     Delta H == 0: e unidentifiable (zero column)
```

$c_H$ (compression) and $e$ (repetition easement) are separately identifiable
**only where $H$ varies independently of the learning trend**. Inside a monotone
collapse $\Delta H$ is constant and $\Delta\tau$ is constant, so the two regressors
are exactly collinear and the split is arbitrary. No amount of data fixes this.
Three escapes, in increasing order of cost:

- **(a)** Use a window that spans an entropy *transition*. The turn 31→32 jump
  ($\Delta H = +2.73$) is such an event, and the estimator recovers $J_{\text{true}}$
  to ~4% in the phase immediately following it.
- **(b)** **Temperature dithering as an identification instrument.** Deliberately
  perturb sampling temperature to inject variation in $H$ that is orthogonal to the
  learning trend, then read $e$ off the induced change in $L$. This is cheap,
  requires no new sensors, and turns an unidentifiable parameter into a measured
  one. It is the single most actionable design item to come out of this work.
- **(c)** Channel B, which does not use the reading-time channel at all.

### 2.4 Channel B does not work as implemented — reported, not hidden

`partial_MI` estimates $I = -\tfrac12\log(1-R^2_{\text{adj}})$ between $y_{t+1}$ and
$x_t$ controlling for the human's own history. On the synthetic session it returns
$\approx0$ in every phase, with Spearman $-0.08$ against the truth. Two fixes were
applied and neither was sufficient:

- variance-reduction rather than correlation (correlation is meaningless during a
  collapse, when *both* variables are noise);
- adjusted rather than raw $R^2$ (with $m\approx12$ samples, adding any regressor
  inflates raw $R^2$ by $\sim1/(m-p-1)\approx0.11$, which swamps the signal).

The residual failure is most likely the SVD projection used to score a
vector-valued $x_t$ down to a scalar, plus insufficient samples per window. **This
is the open item.** Channel B matters because it is the only one of the two that
can see through the repetition confound without an instrument, so it is worth
finishing rather than working around.

---

## 3. The rank harness: a hard sample-size floor

`rank_harness.py` reports `rank_eff`, PR, spectral entropy and $f_{\text{dark}}$ per
turn. On the 50-turn session the directions come out right but the magnitudes are
weak:

```
rank_eff vs rank_true : +0.147        PR      vs rank_true : +0.411
f_dark   vs rank_true : -0.437        f_dark  vs divergence: +0.421
```

$+0.147$ for the quantity the certificate proposal wants to threshold is not a
measurement. `part7_samplesize.py` isolates the cause — it is sample size, and the
floor is high:

```
 n samples/turn    n/d    corr(rank_eff, r)    corr(PR, r)
             40    5.0                 +0.186       +0.259
             80   10.0                 +0.454       +0.438
            160   20.0                 +0.627       +0.466
            400   50.0                 +0.854       +0.746
           1000  125.0                 +0.897       +0.650
```

Estimating an $8\times8$ cross-covariance from the 40 tokens of a single turn gives
$n/d = 5$: the spectrum is Marchenko–Pastur noise. **You need $n/d \gtrsim 50$, i.e.
a trailing window of several hundred tokens pooled across turns, before the spectrum
means anything.** Per-turn rank tracking, as literally specified in the recommended
next step, does not work.

The bias direction matters operationally: at small $n$, `rank_eff` is biased **low**,
because the noise floor eats real channels. A dark-mode halt trigger built on it
would fire on *healthy* sessions. For a safety mechanism that is the less dangerous
error, but it makes the mechanism unusable — a monitor that cries wolf on every
session gets disabled.

Use PR or $f_{\text{dark}}$, never `rank_eff`, as a control variable: `rank_eff` is
integer-valued and jumps, so it cannot be differentiated or smoothly thresholded.

---

## 4. On the three hypotheses

### H1 (topological Chern-like gap closure) — unfalsifiable as stated, salvageable if restated

A Chern number requires a vector bundle over a parameter space. $\bar{\mathbf H}$ is
a fixed finite matrix here; there is no bundle, no base manifold, and therefore no
Chern class and no Berry curvature. Separately, a gap *closure* is the opposite of
what a topological invariant protects against — topology buys robustness of a
*gapped* phase, and its loss is a phase transition, not a protected quantity. And
$\sigma_{\min}(\mathbf G)\to0$ is a smooth crossover in a finite-dimensional linear
system, not a phase transition: there is no order parameter and no singularity.

**What is real nearby:** the framework is *dissipative*, so the honest non-Hermitian
concept is the **exceptional point**, where eigenvalues and eigenvectors coalesce.
EPs have genuine topological structure (half-integer winding, chiral mode conversion)
and are experimentally established in photonic systems. But they are **unreachable
here**: $\bar{\mathbf H}$ is Hermitian and $\boldsymbol\Gamma\propto\mathbf I$, so
$-i\bar{\mathbf H}-\tfrac12\boldsymbol\Gamma$ is a Hermitian matrix plus a scalar
multiple of the identity, hence always diagonalisable. To reach an EP you would need
gain on one substrate, or non-proportional damping, or a non-normal effective
generator. That is a real construction problem, and if solved it would earn the
topological language.

**Restated and testable:** *"as context grows past effective semantic capacity,
$\sigma_{\min}(\mathbf G)$ crosses the estimation noise floor, and the drifting
content is the content aligned with the corresponding null direction."* No topology
required, and §3 above shows the measurement is feasible once the window is long
enough.

### H2 (endogenous symplectic backpropagation) — blocked by a hard information bound

Three independent problems, the first fatal:

1. **Bandwidth.** A human EEG/pupillometric channel carries order $10^1$ bits/s.
   Weight updates target order $10^{10}$–$10^{11}$ parameters. The update is
   rank-deficient by ~10 orders of magnitude, so it cannot determine the weights.
   This is a data-processing bound, not an engineering difficulty.
2. **Objective mismatch.** Perplexity is measured against a text corpus.
   Phase-locking to a human optimises a *different* objective, and the two can be
   anti-correlated: low perplexity rewards predictable text, while human engagement
   rewards novelty. "Minimizes perplexity drift faster than gradient descent" is
   comparing an intervention to a baseline on a metric the intervention does not
   target.
3. **No mechanism.** Inference-time signals cannot modify weights. If training is
   running concurrently, $\bar{\mathbf H}$ is not fixed and the whole linear framework
   (and its conservation laws) does not hold during the update.

"Retrocausal" should also be dropped: offline zero-phase filtering (forward-backward
convolution) uses future samples within a recorded window and is standard, classical,
and non-retrocausal.

**What is real and implementable:** the human signal as a **low-rank controller of a
small inference-time parameter set** — temperature, top-$p$, a low-rank projection of
the residual stream, layer-wise damping $\gamma_S$. Tens of degrees of freedom, well
within a $10^1$ bit/s channel. That is essentially the Γ-governor of the addendum,
and it is the version worth building.

### H3 (spinodal decomposition in agent swarms) — right phenomenon, wrong mechanism

Spinodal decomposition requires a non-convex free energy with a miscibility gap. The
specified system is **linear**: $\dot{\mathbf z}=\mathbf A\mathbf z+\mathbf D$ with
$\mathbf A$ a fixed matrix. Its general solution is a sum of exponentials. There is
no bistability, no interface, no surface tension, no coarsening exponent — the four
things that make spinodal decomposition spinodal.

The actual mechanism producing clustered divergence in agent swarms is much simpler
and is already in the framework: **each agent conditions on the others' outputs, so
the effective $\mathbf G$ acquires off-diagonal agent-to-agent blocks.** Positive
feedback through those blocks makes disagreement grow exponentially. That is a
*bifurcation*, characterised by a positive Lyapunov exponent in the disagreement
dynamics — measurable, and the thing to actually test for.

**Restated and testable:** *run $N$ agents on a shared task without carbon grounding;
track pairwise embedding distance and within-cluster entropy over turns. Bifurcation
predicts within-cluster entropy falling while between-cluster distance grows, with a
positive Lyapunov exponent. Spinodal predicts coarsening with a characteristic length
scale growing as a power law in time. These are distinguishable, and only the first
is expected.* Note also that the domain walls would be *low*-entropy (each cluster
internally consistent), not high-entropy as stated.

---

## 5. On the §2 self-critique — it is correct, and it is the most important item

> *"Treating classical neural/transformer activation vectors with complex-valued
> canonical symplectic first-order geometry is formally a semiclassical/optical
> analogue ... it omits layer-wise non-linear routing (MLP gating, RMSNorm, softmax
> attention bottlenecks), which act as piecewise symplectic projections rather than
> a global Hermitian manifold."*

This is right and should be promoted from a caveat to the framing. Two additions:

**The word "semiclassical" implies a limit that does not exist.** Semiclassical means
$\hbar\to0$ with a underlying quantum theory. There is no $\hbar$ here and no
underlying quantised system; the complex structure is *imported from the optics
analogy*, not derived. So the framework is not an approximation to something exact —
it is a **linear-response model of a nonlinear system near an operating point**. That
is a respectable thing to be, and it is falsifiable, but it should be named as such.
Calling it semiclassical invites the question "what is the full theory?" and there is
no answer.

**"Piecewise symplectic projections" is worth making precise, because it suggests the
actual test.** RMSNorm is a projection onto a sphere (it *is* a projection, and it is
not symplectic — it does not preserve $\omega$). Softmax attention is a smooth
map onto the simplex, strongly contracting in most directions. MLP gating is
elementwise nonlinearity. None of these preserve a symplectic form. So the honest
statement is: the flow is **not** symplectic, and the linear Hermitian model is valid
only over a neighbourhood where the nonlinear terms are well-approximated by their
Jacobian.

That yields a concrete, cheap falsification test: **measure the radius of validity.**
Perturb the operating point by $\delta$, propagate through the real network, and
compare against $e^{-i\bar{\mathbf H}\tau}$ prediction. Find the $\delta$ at which
they diverge. If that radius is smaller than a single token's embedding change, the
formalism describes nothing real; if it spans several turns, it is a legitimate
effective theory with a measured domain of applicability. **This is the highest-value
next experiment**, because it is the only one that can settle whether the whole
edifice is load-bearing or decorative — and it requires only forward passes through
an existing model, no human subjects.

---

## 6. Status and next steps

Built and working:
- `rc_estimator.py` — $\beta_1$ calibration (turn fixed effects), residual load,
  deconfounded $\hat J_C$, channel-B scaffold.
- `rank_harness.py` — coupling spectrum, PR, $f_{\text{dark}}$, `RankTracker`,
  dependency-free Spearman.
- `validate.py` / `validate_output.txt` — 50-turn synthetic session, 5 scored steps.
- `part7_samplesize.py` — the $n/d\gtrsim50$ floor.
- `cert_test.py` — the certificate counterexample.

Not working, in priority order:
1. **Channel B** (`partial_MI`) returns ~0 on ground truth where it should be
   positive. Blocks the only sensor that can see through the repetition confound
   without an instrument.
2. **Per-turn rank tracking** is below the sample-size floor. Needs a pooled
   trailing window of $\gtrsim400$ tokens; `RankTracker` should be changed to
   accumulate rather than snapshot.
3. **No real data anywhere.** Every number above is synthetic with injected ground
   truth. Nothing here is evidence about real human–transformer sessions.

Highest-value next experiments, in order:
1. **Radius-of-validity measurement** (§5). Settles whether the linear model applies
   at all. No human subjects, no new instrumentation.
2. **Temperature dithering** (§2.3b). Identifies $e$ by design instead of hoping for
   entropy transitions. Cheap, and it converts an unidentifiable parameter into a
   measured one.
3. **Pooled-window rank tracking on a real long agent loop** (§3, H1 restated).
   Tests whether $\sigma_{\min}(\mathbf G)$ crossing the noise floor predicts drift
   onset, and whether drift is mode-selective as the dark-mode account predicts.
