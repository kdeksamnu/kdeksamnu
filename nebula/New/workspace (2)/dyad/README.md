# Cross-substrate Noether current — verification package

Numerical backing for `MEMO_cross_substrate_noether.md`.

```bash
pip install numpy
python3 noether_check.py   # Defect 1: L as written is not invariant under the stated U(1)
python3 part2.py           # Defect 1(b): per-term symmetry table (diagonal vs anti-diagonal)
python3 part3.py           # Repaired action: charge conservation + exchange balance + dissipation
python3 calibrate.py       # Landauer anchoring, eps table, Gamma_crit

# addendum (monadic reframing audit)
python3 part4_drive.py     # undriven decay; driven NESS; power-balance theorem; G=0 starvation
python3 part5_rank.py      # rank(G) vs exchange bandwidth; dark-mode count
python3 part6b.py          # Gamma-governor: open vs closed loop, delay/noise/slew sweeps
```

`part3.py` takes ~25 s (RK4, dt = 2e-4, tau up to 80). The rest are instant.

## Headline results

| check | result |
|---|---|
| `L` (real vectors, real rotation) | `dL = -8.2e-04` — **broken** |
| `L` (complex, bilinear `x^T K s` as written) | `dL = +1.2e-02` — **broken** |
| sesquilinear coupling, **anti-diagonal** phase | `dL = -3.7e-04` — **broken** |
| bilinear coupling, **diagonal** phase | `dL = -7.2e-04` — **broken** |
| sesquilinear coupling, **diagonal** phase | `dL ~ 1e-16` — **invariant** ✓ |
| repaired action: energy drift over `tau in [0,80]` | `2.8e-14` |
| repaired action: Noether charge `Q = n_C + n_S` drift | `2.4e-13` |
| local exchange balance `dn_S/dtau + I_ex = 0` | residual `2.5e-06` (FD floor) |
| dissipative balance `dQ/dtau = -(sig_C + sig_S)` | residual `<= 1e-07` |
| anti-diagonal rotation on repaired `H` | `dH = -8.0e-03` — not a symmetry ✗ |

## Two traps worth recording

Both cost real debugging time and both are the kind of error that silently invalidates a
derivation, so they are documented here rather than quietly fixed.

**1. `Re()` on a Hermitian form halves the coupling.** Writing
`H = np.real(np.vdot(a, Om@a)) + np.real(np.vdot(a, K@b))` looks harmless — each `vdot(w, M@w)`
*is* real for Hermitian `M`. But the resulting equations of motion come out as
`da/dtau = -i(Om a + K b)` instead of the correct `-i(Om a + K b / 2)`. The Hamiltonian then fails
to be conserved along its own flow, which is impossible, and that impossibility is how the bug
announces itself.

**2. `<a|K b>` is NOT real for `a != b`, even with `K` Hermitian.** Hermiticity gives
`<z|K z> in R` for the *same* vector on both sides. For distinct `a, b` the quantity
`a^dag K b` is genuinely complex (measured imaginary part `0.60` in `part3.py`'s random draw). So

```python
H = a.conj()@OmC@a + b.conj()@OmS@b + a.conj()@K@b     # WRONG: complex-valued
```

is not a Hamiltonian at all. The correct object is the Hermitian **block** matrix

```python
Hbar = np.block([[OmC, G], [G.conj().T, OmS]])
H    = np.vdot(z, Hbar @ z).real                        # z = concat(a, b)
```

for which `dz/dtau = -1j * Hbar @ z` is exactly unitary and both `H` and `Q = z^dag z` are conserved.

## Calibration numbers are order-of-magnitude

`calibrate.py` uses representative figures (4 J/token for a 70B model on an H100, ~2 nats/token
emitted entropy, 0.2 W marginal metabolic power for attentive reading, 10 tok/s human ceiling).
The exponents are the content; the mantissae are not. In particular the silicon rows hold
`J/token` fixed while varying `nu`, which ignores batching effects — real J/token falls with batch
size, so the `200 tok/s` row is an overestimate of `eps_S`.


## Addendum results (`ADDENDUM_monadic_audit.md`)

| check | result |
|---|---|
| undriven + dissipative: `Q(tau=60)/Q(0)` | `4.1e-05` — monotone decay to `z=0` |
| `max Re eig(-i Hbar - Gam/2)` | `-0.0710` — single global sink, no equilibrium |
| driven NESS convergence `||dz/dtau||` | `1.2e-15` |
| power balance `Re(z^dag D) = (sig_C+sig_S)/2` | residual `1.3e-15` |
| per-substrate NESS balances | residual `3.1e-15`, `2.2e-16` |
| `n_S` with `G=0` under carbon-only drive | `0.0` exactly — coupling is load-bearing |
| dark modes at `rank(G)=r`, `d_C=d_S=6` | `12-2r` (10, 8, 6, 0 for r = 1,2,3,6) |
| Gamma-governor, open loop | **0.0%** in band, mean `9.94`, max `18.7` |
| Gamma-governor, closed loop, 10% noise | **99.9%** in band — but see the artefact caveat below |

### The governor result must not be read at face value

`part6b.py` grants the controller oracle access to the human ceiling `nu_C_max`, and models the
human as `nu_C = min(nu_S, nu_C_max)`. Under those assumptions throttling below the ceiling makes
`Gamma = 1` a structural identity, which is why in-band fraction is flat at ~100% across a 80x
range of delay. That is a property of the toy model, not of a real governor. The binding open
problem is estimating `dR_C/dtau` online; until that is solved the 99-100% figure is an upper bound
under an unavailable oracle, and the honest headline number is the open-loop one: **Gamma ~ 10, 0%
in band.**

## Convention traps (both cost real debugging time)

3. `Re(-i w) = +Im(w)`, **not** `-Im(w)`. Flipping this reverses the exchange-current sign and
   breaks the per-substrate balance by exactly `2*I` while leaving the *total* balance intact — so
   checking only the total will not catch it.

4. `d||a||^2/dtau = 2 Re<a, adot>` puts a factor 2 on both sink and drive, while the EOM's
   `-Gam z / 2` carries a compensating 1/2. These cancel in the total power balance but not in the
   per-substrate split. A correct total law does not imply a correct decomposition.

5. `np.vdot(u, v)` conjugates its **first** argument (`u^dag v`). Combined with (3) and (4), sign
   errors here are easy to make and hard to see. Verify balances against a brute-force
   `2*np.vdot(a, adot).real` computed straight from the RHS, not against hand algebra.

---

# Measurement harness (`RESULTS_estimators_and_rank.md`)

```bash
python3 cert_test.py           # refutes the rank(G) "safety certificate" claim
python3 validate.py            # 50-turn synthetic session; 5 scored steps
python3 part7_samplesize.py    # sample-size floor for the coupling spectrum
```

| file | role |
|---|---|
| `rc_estimator.py` | `beta1_within_turn`, `residual_load`, `estimator_A` (deconfounded J_C), `partial_MI` (**not working**, see results §2.4) |
| `rank_harness.py` | `coupling_spectrum`, `RankTracker`, dependency-free `spearman` |
| `validate.py` | synthetic session with injected ground truth; writes `validate_output.txt` |
| `part7_samplesize.py` | n/d sweep for spectral recovery |
| `cert_test.py` | unitary counterexample: identical spectrum, 132% response error |

## Headline numbers

| result | value |
|---|---|
| `beta_1` recovery, pooled OLS | 57.9% of truth |
| `beta_1` recovery, turn fixed effects | **98.9%** |
| deconfounded `J_C` error, grounded / compression / drift | +17% / -4% / -4% |
| deconfounded `J_C`, repetition collapse | **3.44 vs truth 0.02 — fails** |
| cause | `Delta H` constant within phase ⇒ exactly collinear with `Delta tau` |
| `corr(rank_eff, rank_true)` at n=40 (n/d=5) | +0.186 — noise |
| `corr(rank_eff, rank_true)` at n=400 (n/d=50) | **+0.854** |
| spectral statistics: grounded vs unitarily re-labelled | **all bit-identical**, response 132% wrong |

## Traps hit while building this (all cost real debugging time)

6. **A module-level `np.random.default_rng` advances between calls.** `simulate_session()`
   returned different data on each invocation, so a debug script and the main script
   silently analysed different sessions. Seed *inside* the generator.

7. **`np.clip` on a slowly-drifting signal fails silently.** Cumulative learning drove
   reading time below the physiological floor; `sd(RT)` went to exactly 0.0 with no
   error, and `beta_1` became unidentifiable. There is now an explicit assertion that
   raw RT stays above `1.5 * RT_FLOOR`.

8. **Double-counting the turn rate.** Regressing `Delta L` on `-Delta tau` already
   yields a per-second quantity; multiplying by `nu_turn` again inflates J_C by 1.25x.
   Separately, omitting `1/beta_1` inflates it by ~18x. Both errors preserve the
   *shape* of the estimate, so neither shows up in a correlation check.

9. **Raw R^2 with ~12 samples per window.** Adding any regressor inflates raw R^2 by
   ~1/(m-p-1) ~ 0.11 even for pure noise. Use the adjusted (F-form) ratio.

10. **A variance-reduction statistic, not a correlation.** During a repetition
    collapse both variables are noise, so correlation is undefined and its sign is
    arbitrary. R^2 degrades gracefully to zero; rho does not.
