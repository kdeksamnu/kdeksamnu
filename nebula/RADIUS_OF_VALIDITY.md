# Radius of validity: the linear Hermitian model, measured against a real transformer block

Answers the question posed in `RESULTS_estimators_and_rank.md` §5 — *is the linear
model load-bearing or decorative?* — by measurement rather than argument.

Code: `radius_of_validity.py` (Jacobian + δ sweep, dense and sparse),
`verdict.py` (eigenstructure, single-token response), `sanity.py` (sensitivity).
Requires `torch` (CPU is sufficient; float64 throughout so the Jacobian is not
noise-limited).

**Verdict: the linearisation is broken at the token boundary, and the thing it would
have to be — a Hermitian generator — it structurally is not. Two independent
failures, either of which is sufficient.**

---

## 1. Setup

A genuine nonlinear block, not a stand-in: pre-norm residual with RMSNorm → multi-head
causal **softmax** attention → residual → RMSNorm → **SwiGLU** MLP → residual. Three
distinct nonlinearities. `T=12` tokens, `D=32`, 4 heads, float64, random init.

The Jacobian is exact, from autograd — 384×384, verified against a central finite
difference to **8.7×10⁻¹⁰** relative error.

**A bug worth recording, because it produced a confident wrong answer.** The first
run reported `err ≈ 0.79` at *every* δ including δ→0, which looks like a spectacular
finding ("the linear model is useless at all scales") and was actually arithmetic.
The linearisation was written as $X_0 + d + Jd$, which assumes $f(X_0)=X_0$ — that
the block is the identity at the operating point. It is not; the residual branch
grows the stream by 1.34×, so $\lVert f(X_0)-X_0\rVert = 4.68$ and that constant
swamped everything. Correct Taylor expansion is $f(X_0) + Jd$. After the fix the
error is cleanly quadratic in δ ($1.08\times10^{-9}$ at $\delta=10^{-4}$, scaling as
$\delta^2$ to three digits), which is the signature of a correct first-order model.

**Lesson: a radius-of-validity measurement that does not converge to zero error as
δ→0 is not measuring nonlinearity, it is measuring a bug. Assert `err(δ→0) → 0`
before interpreting anything.**

---

## 2. The radius

$$\mathrm{err}(\delta)=\frac{\lVert f(X_0+d)-\big(f(X_0)+Jd\big)\rVert}{\lVert f(X_0)\rVert}$$

| tolerance | δ* dense (isotropic) | δ* sparse (single row) |
|---|---|---|
| mean err < 1% | 0.268 | **0.164** |
| mean err < 5% | 0.439 | **0.260** |

**The sparse radius is 0.61× the dense radius.** This matters and is easy to get
backwards: the isotropic sweep, which is the natural thing to compute, *overestimates*
how far the linear model reaches. A token does not perturb the whole residual stream
uniformly — it perturbs one row. Only the sparse number is load-bearing for a
per-token conservation law.

The radius is also **not a single number for the block**. Row-to-row spread at
δ=0.44 runs from 1.0×10⁻² (best position) to 7.2×10⁻² (worst), a factor of ~7.
Late positions see more attention mixing and linearise over a different range than
early ones. Any global δ* is already an idealisation of the thing it validates.

---

## 3. The token scale

With embeddings at std $1/\sqrt D$ and $X_0$ rows normalised to unit norm, one token
row has norm **1.000** — and a real transformer's residual stream has rows of
comparable norm to its embeddings, so this is the right scale, not an artefact.

Replacing one row with a fresh embedding, measured over 200 random tokens:

```
relative output change ||f(X0+d)-f(X0)|| / ||f(X0)|| :  mean 0.251   max 0.577
amplification ||dOut|| / ||dIn||                     :  mean 1.510   max 3.316
```

So:

- **δ_token = 1.000 vs δ*_sparse = 0.164 at 1% → 6.1× beyond the radius.**
- **δ_token = 1.000 vs δ*_sparse = 0.260 at 5% → 2.3× beyond the radius.**
- And a single token moves the block output by **25% of its entire norm** (mean).

The fracture is at the token boundary, exactly where the framework needs it not to
be. A per-token conservation law requires the map to be linear across one token
insertion; it is not, by a factor of 2–6.

One mitigating observation: the *finite* amplification at token scale is 1.51 (max
3.32), well below the local $\lVert J\rVert_2 = 7.91$. The nonlinearity **saturates**.
So the block is gentler at token scale than its own Jacobian suggests — which is
mildly encouraging for a nonlinear effective theory, and irrelevant for a linear one.

---

## 4. The Jacobian is not a Hermitian generator — the deeper failure

This is independent of the radius and survives even if the radius were large.

For $d\mathbf z/d\tau = -i\bar{\mathbf H}\mathbf z$ with $\bar{\mathbf H}$ Hermitian, the
generator $-i\bar{\mathbf H}$ is **antisymmetric**: eigenvalues purely imaginary, flow
unitary, charge exactly conserved. Measured:

```
||sym(J)||_F / ||J||_F   = 0.810        <- symmetric part carries 81% of J
||asym(J)||_F / ||J||_F  = 0.587
eigenvalues (384 total):
    Re(lambda) > 0       :   380        (99.0% expansive)
    Re(lambda) < 0       :     4
    purely real          :    62
    max Re(lambda)       : +2.249
    max |lambda|         :  2.536
||J||_2                  =  7.910
```

$J$ is **81% symmetric**. An antisymmetric generator would have a symmetric part of
exactly zero. And 99% of eigenvalues have positive real part, so the linearised flow
*expands* in almost every direction, with $\lVert J\rVert_2 = 7.91$ — it amplifies a
perturbation ~8× locally where a unitary flow would preserve norm exactly.

**Consequence: there is no conserved charge in the linearised block.** The diagonal
U(1) symmetry, the Noether charge $Q=n_C+n_S$, and the power-balance theorem all
presuppose a generator whose symmetric part vanishes. The measured symmetric part is
the dominant component. The conservation structure is not approximately present and
then broken by the nonlinearity — **it is absent already in the linearisation**, one
step before any nonlinearity is invoked.

---

## 5. Sensitivity: a trade-off, not an initialisation artefact

`sanity.py` varies block size and residual gain:

```
   residual growth    ||J||_2   delta*_sparse   sym(J)/||J||
            0.13         1.48          1.995          0.996
            1.13         8.90          0.588          0.824
            1.34         7.91          0.588          0.810
            1.60        11.79          0.588          0.800
            1.96        15.21          0.260          0.746
            8.69        75.54          0.260          0.710

  log-log fit:  delta* ~ growth^-0.51   (R^2 = 0.861)
                delta* ~ ||J||_2^-0.54
```

$\mathrm{sym}(J)/\lVert J\rVert$ stays in $[0.71, 0.996]$ in **every** configuration, so
the failure is structural, not bad luck with the seed.

But the trend is the interesting part, and it is a genuine result rather than a
caveat: **the closer the block is to the identity, the more symmetric its Jacobian and
the larger its linearisation radius — and the less computation it performs.** Both
limits are degenerate. At gain → 0 the model is vacuous and δ*→∞ because nothing
happens; at high gain δ* → 0. There is no regime in which a block is simultaneously
useful and well-approximated by $-i\bar{\mathbf H}\mathbf z$ across a token-scale
perturbation.

**Capability and linearisability are in direct tension.** That is a stronger statement
than "the linear model fails here," and it is the one worth carrying forward: it says
the failure is not fixable by choosing a better operating point, a better block, or a
better-trained model. Any block that does work has a non-Hermitian Jacobian and a
radius of order the token scale.

---

## 6. Caveats — stated before someone else states them

1. **Random init, not trained weights.** A trained block sits at a different operating
   point; growth ≈ 1.34 per block is not what a 32-layer transformer does (residual
   growth compounds and is controlled by LayerNorm). The *qualitative* findings —
   non-antisymmetric $J$, expansive spectrum, δ* at or below token scale — follow from
   softmax/RMSNorm/SiLU structure, not from the weights, and §5 shows they hold across
   a 66× range of gain. The *numbers* should be recomputed on a real checkpoint.
2. **One block.** Not a stack. Compounding across $L$ layers multiplies $\lVert J\rVert$
   and shrinks δ* further, so a full model is worse, not better.
3. **Small dims** ($T=12$, $D=32$) to keep the $O((TD)^2)$ Jacobian tractable. §5 shows
   $T=16,D=48$ and $T=8,D=64$ give the same verdict.
4. **RMSNorm makes the map scale-invariant**, so δ has no absolute meaning — only δ
   relative to $\lVert X_0\rVert$ is meaningful. All figures here are in those relative
   units, and the token scale (1.000) is quoted in the same units.

---

## 7. What this implies for the framework

Three options, in decreasing order of ambition:

**(a) Abandon the Hermitian picture, keep the balance laws.** The power-balance
theorem of `ADDENDUM` §1.2 does *not* require a Hermitian generator — it requires
$\mathrm{Re}\,\mathbf z^\dagger(-i\bar{\mathbf H})\mathbf z = 0$, which fails here. But the
*phenomenological* bookkeeping (drive in, sinks out, exchange between substrates) does
not require it either. Restate the framework as a **driven-dissipative balance law
with a measured, non-Hermitian coupling**, dropping all Noether/conservation language.
This keeps everything that was empirically interesting — Γ, the rank/dark-mode
structure, the governor — and discards only the part that was false.

**(b) Find the right linear object.** $J$ is not $-i\bar{\mathbf H}$, but it may be a
good model of something else. The measured $J$ is dominated by its symmetric part with
an expansive spectrum, which is the signature of a **gradient-like** flow
($\dot{\mathbf z} = -\nabla V$), not a Hamiltonian one. If the residual stream is
gradient-like near the operating point, the natural conserved-or-monotone quantity is
a **Lyapunov function**, not a Noether charge — and a monotone quantity supports
exactly the kind of "budget" and "sink" language the framework already uses, with
correct mathematics behind it. **This is the most promising direction and it is
cheap to test:** check whether $J$ is similar to a symmetric matrix, or whether
$\lVert f(X)\rVert$ is monotone along generation.

**(c) Go nonlinear and drop the effective theory.** If neither holds, the formalism is
a metaphor with good vocabulary and no domain of validity, and should be presented as
such.

**On the splat renderer:** the answer to "does the 122 ms grass patch inherit the heat
equations" is no, and now for a measured reason rather than a taste judgement. The
renderer is exact, integer-indexed and deterministic-by-construction; the dyad
formalism does not survive contact with the thing it was meant to describe. Shipping
the smaller trees is the better use of the week. The one item from the splat audit
worth acting on regardless: quantise depth to an integer grid before sorting, or
`seed(s) ≡ emission(t)` is aspirational rather than enforced, because WebGL2 does not
guarantee float32 rounding across drivers.

---

## 8. Reproduce

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
python3 radius_of_validity.py   # Jacobian, spectrum, dense+sparse delta sweep (~2 s)
python3 verdict.py              # eigenstructure, single-token response (~2 s)
python3 sanity.py               # 6-configuration sensitivity sweep (~25 s)
```
