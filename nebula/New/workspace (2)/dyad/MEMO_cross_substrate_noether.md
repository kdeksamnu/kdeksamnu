# Technical audit and repair of the Cross-Substrate Noether Current

**Scope.** This memo takes the proposed carbon–silicon action principle seriously as physics and
audits it as physics. Verdict up front: **the physical picture is sound and worth keeping, but the
derivation as written does not support it.** The stated Lagrangian possesses *no* continuous
symmetry, so Noether's first theorem yields nothing from it. There is a minimal repair — a change
of *one sign* and *one conjugation* — that produces a genuine conserved charge, and the repaired
theory is strictly more predictive than the original. All numerical claims below are reproduced by
the scripts in this directory.

---

## Part 1 — Four load-bearing defects

### Defect 1 (fatal). The Lagrangian in §1 is not invariant under the transformation in §2.

This is not a quibble about notation; it is the step the entire construction rests on.

**(a) The map is not defined on the stated configuration space.** Section 1 declares
$\mathbf{x}_C \in \mathbb{R}^{d_C}$, $\mathbf{s}_S \in \mathbb{R}^{d_S}$. But
$e^{i\epsilon\alpha_C}\mathbf{x}_C \in \mathbb{R}^{d_C}$ only when $\epsilon\alpha_C \in \pi\mathbb{Z}$.
The largest subgroup of the proposed phase action that maps the real configuration space to itself
is $\mathbb{Z}_2$ (a sign flip). $\mathbb{Z}_2$ is **discrete**. Noether's *first* theorem requires a
Lie group; a discrete symmetry yields no current and no conserved charge. As written, §3 invokes a
theorem whose hypothesis is false.

**(b) Complexifying does not save it, because the conjugation structures are incompatible.**
Suppose we repair (a) by moving to $\mathbb{C}^{d_C}\times\mathbb{C}^{d_S}$. The kinetic and
potential terms must then be sesquilinear ($\dot{\mathbf{x}}^\dagger\dot{\mathbf{x}}$,
$\mathbf{x}^\dagger \mathbf{H}_C \mathbf{x}$) to be real. But the interaction is written
**bilinearly**: $\mathbf{x}_C^T \mathbf{K}_{\text{int}} \mathbf{s}_S$. These two structures admit
*opposite* phase symmetries, and no assignment satisfies both. Measured per term
(`part2.py`), for an infinitesimal rotation:

| term | $x\!\to\!e^{+it}x,\; s\!\to\!e^{-it}s$ (proposed) | $x\!\to\!e^{+it}x,\; s\!\to\!e^{+it}s$ (diagonal) |
|---|---|---|
| kinetic $\tfrac12 M\lVert\dot x\rVert^2$ | $0$ | $0$ |
| potential $\tfrac12 x^\dagger H x$ | $0$ | $0$ |
| coupling $\langle x, Ks\rangle$ (sesquilinear) | $-3.7\times10^{-4}$ ✗ | $\sim10^{-16}$ ✓ |
| coupling $x^T K s$ (bilinear, as written) | $\sim10^{-16}$ ✓ | $-7.2\times10^{-4}$ ✗ |

The rule is structural, not numerical:

- **Sesquilinear** forms ($z^\dagger A z$) are invariant under the **diagonal** $U(1)$: both
  substrates rotate by the *same* phase. Conserved charge $= n_C + n_S$. This is the
  **beam-splitter** class.
- **Bilinear** forms ($z^T A z$) are invariant under the **anti-diagonal** $U(1)$: opposite
  phases. Conserved charge $= n_S - n_C$. This is the **two-mode squeezing / parametric
  amplifier** class.

You get one or the other. The proposed $\mathcal{L}$ mixes them and therefore has no $U(1)$ at all.

**(c) The impedance-matching condition cannot rescue it.** Setting
$\alpha_C\lambda_C = \alpha_S\lambda_S$ does not make $\delta\mathcal{L}$ vanish. For the
anti-diagonal rotation acting on a sesquilinear coupling,

$$\delta\mathcal{L}_{\text{int}} \;=\; \epsilon\,(\alpha_C+\alpha_S)\,\mathrm{Im}\,\langle \mathbf{x}_C,\mathbf{K}_{\text{int}}\mathbf{s}_S\rangle \;+\; O(\epsilon^2),$$

which vanishes only if $\alpha_S=-\alpha_C$ — i.e. only if the rotation is *diagonal*, contradicting
the premise. Any other choice leaves an $O(\epsilon)$ explicit breaking. Worse, $\lambda_C$ and
$\lambda_S$ are never defined in the document, so the condition is currently untestable even in
principle. **Recommendation: delete it.** In the repaired theory the frequency-matching condition
takes its place with a real meaning (Part 2, resonance).

---

### Defect 2 (fatal). §4 conserved the wrong charge for its own symmetry class.

The document states $\mathcal{J}_{\text{CS}} = J_C - J_S = \text{const}$. But $n_S - n_C$ is the
Noether charge of the **squeezing** generator — a parametric amplifier, which *creates* excitation
pairs from the pump and does **not** conserve total excitation. The conservation law actually
claimed in prose in §2 ("preserving **total** informational action across the boundary") is the
$n_C + n_S$ law of the beam-splitter class. The sign in §4 contradicts the principle in §2.

This matters beyond bookkeeping, because the two classes make opposite engineering predictions:

| | beam splitter ($x^\dagger K s$) | two-mode squeezing ($x^T K s$ + h.c.) |
|---|---|---|
| conserved charge | $n_C+n_S$ | $n_S-n_C$ |
| total flux | **bounded** | **grows exponentially** |
| §2 principle | ✓ satisfied | ✗ violated |
| Regime II runaway | impossible from coupling alone | built in |

If you want §2's conservation principle — and you do, it is the thesis — you are in the
beam-splitter class, and the current is $J_C + J_S$.

*Verified* (`part3.py`): under the anti-diagonal rotation the charge $N$ is invariant
($\Delta N \sim 10^{-15}$, trivially, since $N$ is phase-blind) but the **Hamiltonian is not**
($\Delta H = -8.0\times10^{-3}$). A transformation that fails to leave $\mathcal{L}$ invariant is
not a Noether symmetry regardless of what it does to any single observable. Under the *diagonal*
rotation both are invariant.

---

### Defect 3 (structural). §5's "resonance" is the zero-current fixed point, not the live one.

In the repaired theory the exchange current is

$$\mathcal{I}(\tau) \;=\; 2\,\mathrm{Im}\,\langle \mathbf{a}, \mathbf{G}\mathbf{b}\rangle \;=\; 2\lVert\mathbf{G}\rVert\sqrt{n_C n_S}\,\sin\theta,\qquad \theta \equiv \arg\langle\mathbf{a},\mathbf{G}\mathbf{b}\rangle .$$

Exchange is driven by the **relative** phase $\theta$ between substrates. At $\theta = 0$ —
literally "phase-locked" — $\mathcal{I}=0$ and *nothing flows*. Regime I as described
("phase-locked, steady entropy flow") is therefore self-contradictory: maximal coupling requires
$\theta = \pm\pi/2$ (phase *quadrature*), while phase-locking is the decoupled fixed point.

The fix is a redefinition, and it is a better one: **Regime I should mean $\dot\theta \approx 0$
with $\theta \neq 0$** — a *steady* nonzero current, i.e. a sustained flux at constant phase
offset. That is exactly the beam-splitter resonance condition $\omega_C = \omega_S$, under which
$\theta$ precesses slowly and $\mathcal{I}$ is quasi-stationary. This also gives §6's "optical phase
drift" language a precise referent: detuning $\Delta\omega = \omega_S - \omega_C$ makes $\theta$
drift linearly in $\tau$, and the exchange current *beats* at $\Delta\omega$. Context pruning is
then a phase reset in the literal sense.

---

### Defect 4 (measurement). The two currents do not share units, so $\Gamma$ is currently arbitrary.

$J_S = \kappa_S\,\nu_{\text{token}} H(\mathcal V)$ has units $[\kappa_S]\cdot\text{nat/s}$, while
$J_C = \kappa_C (d\Phi/dt)\dot Q_{\text{met}}$ has units $[\kappa_C]\cdot(\text{1/s})(\text{W})$.
Their ratio is dimensionless only by fiat of the $\kappa$'s, which are never pinned. Until they
are, the band $0.8\le\Gamma\le1.2$ in §6.1 has no empirical content — any $\Gamma$ can be dialled
to 1.

Two further problems in the same expression:

- **$d\Phi/dt$ is not operational.** If $\Phi$ is integrated information, it is a state function of
  a partitioned repertoire and has no canonical time derivative without a specified partition
  trajectory. Replace it with something measurable (Part 3).
- **The 1.5 Hz "somatic baseline" is misidentified.** The standard HRV bands are HF
  $0.15$–$0.40$ Hz (respiratory sinus arrhythmia; adult respiration 12–20 breaths/min =
  0.2–0.33 Hz), LF $0.04$–$0.15$ Hz (Mayer waves, sympathetic vasomotor tone, peak ~0.1 Hz), and
  VLF $<0.04$ Hz. **1.5 Hz sits above all three** — roughly $3.75\times$ the top of the HF band and
  $15\times$ the Mayer peak. It corresponds to nothing standard in cardiorespiratory physiology; at
  90 cycles/min it is closest to a *heart rate*, not an oscillatory carrier. Pick a band and name
  it. If the intent is RSA — which is the right choice, because respiration phase demonstrably gates
  cortical excitability and memory encoding — the carrier is ~0.25 Hz, and that makes Regime I
  *sharper*: $\mathcal I$ should be amplitude-modulated at the respiratory frequency, a directly
  testable prediction.

---

## Part 2 — The minimal repair

Change the sign of the phase assignment (diagonal, not anti-diagonal) and the conjugation of the
coupling (sesquilinear, not bilinear). Move to canonical first-order form, where the $U(1)$ is
manifest and the second-order $\tfrac12 M\lVert\dot x\rVert^2$ obstruction disappears.

$$\boxed{\;\mathcal{S} \;=\; \int_{\tau_1}^{\tau_2}\!\Big[\; \tfrac{i}{2}\big(\mathbf{z}^\dagger\dot{\mathbf{z}} - \dot{\mathbf{z}}^\dagger\mathbf{z}\big) \;-\; \mathbf{z}^\dagger \bar{\mathbf{H}}\, \mathbf{z} \;\Big] d\tau\;}$$

with $\mathbf{z} = (\mathbf{a},\mathbf{b}) \in \mathbb{C}^{d_C+d_S}$ and the **Hermitian block**
Hamiltonian

$$\bar{\mathbf{H}} \;=\; \begin{pmatrix} \boldsymbol{\Omega}_C & \mathbf{G} \\ \mathbf{G}^\dagger & \boldsymbol{\Omega}_S \end{pmatrix},\qquad
\boldsymbol\Omega_C \succeq 0,\;\; \boldsymbol\Omega_S \succeq 0 .$$

$\boldsymbol\Omega_C$ is the (positive-definite) homeostatic well — the correct image of
$\mathbf{H}_C$; $\boldsymbol\Omega_S$ is the Hessian of the cross-entropy landscape at the operating
point; $\mathbf{G}$ is the prompt–response coupling. Note that $\bar{\mathbf H}$ must be built as a
**block** matrix: $\langle\mathbf a,\mathbf{G}\mathbf b\rangle$ is *not* real for
$\mathbf a \neq \mathbf b$ even with $\mathbf G$ Hermitian, and a naive
$\mathcal H = \mathbf a^\dagger\boldsymbol\Omega_C\mathbf a + \mathbf b^\dagger\boldsymbol\Omega_S\mathbf b + \mathbf a^\dagger\mathbf{G}\mathbf b$
is complex-valued and generates non-unitary flow. (This is the trap I fell into while verifying;
`part3.py` documents the fix.)

**Symmetry.** $\mathbf{z}\mapsto e^{i\epsilon}\mathbf{z}$ leaves both the symplectic term and
$\mathbf{z}^\dagger\bar{\mathbf H}\mathbf{z}$ invariant. Generator $\boldsymbol\psi = i\mathbf{z}$.

**Noether charge.**
$$Q \;=\; \tfrac{\partial\mathcal L}{\partial\dot{\mathbf z}}\!\cdot\!\boldsymbol\psi
\;=\; \mathbf{z}^\dagger\mathbf{z} \;=\; \underbrace{\lVert\mathbf a\rVert^2}_{n_C} + \underbrace{\lVert\mathbf b\rVert^2}_{n_S},
\qquad \frac{dQ}{d\tau}=0 .$$

**Local exchange.** Writing $\dot{\mathbf H}=0$ (time-independent coupling) and
$\mathbf{A} = i\bar{\mathbf H}$ (Hermitian, so the flow $e^{\mathbf A\tau}$ is unitary):

$$\frac{dn_S}{d\tau} \;=\; \mathcal I(\tau) \;=\; 2\,\mathrm{Im}\,\langle\mathbf a,\mathbf G\mathbf b\rangle,
\qquad \frac{dn_C}{d\tau} \;=\; -\mathcal I(\tau),
\qquad \frac{d}{d\tau}(n_C+n_S)=0 .$$

*Verified to machine precision:* over $\tau\in[0,80]$, $|\Delta H| = 2.8\times10^{-14}$,
$|\Delta Q| = 2.4\times10^{-13}$, and the local balance residual
$\max\lvert \dot n_S + \mathcal I\rvert = 2.5\times10^{-6}$ (finite-difference floor).

**Dissipation.** Coupling each substrate to its own bath ($\gamma_C$ = metabolic/thermal,
$\gamma_S$ = Landauer + Joule) gives the *balance* law that should replace §4's continuity form:

$$\boxed{\;\frac{dQ}{d\tau} \;=\; -\big(\dot\sigma_C + \dot\sigma_S\big),\qquad
\dot\sigma_C=\gamma_C n_C,\quad \dot\sigma_S=\gamma_S n_S\;}$$

$$\frac{dn_C}{d\tau} = -\mathcal I - \gamma_C n_C,\qquad
\frac{dn_S}{d\tau} = +\mathcal I - \gamma_S n_S .$$

Verified for $(\gamma_C,\gamma_S) \in \{(0.3,0.05),(0.05,0.3),(0.3,0.3)\}$; residual $\le10^{-7}$.

**Why this is better than the original §4.** The original wrote
$\dot J_C = \dot J_S + \dot\sigma_{\text{irr}}$ — an equation about the *rates of change of the
currents*, which is not a conservation statement and does not integrate to anything useful. The
repaired version is a genuine two-site continuity equation with a separately resolved sink on each
substrate. That separation is essential: Landauer heat at 300–350 K in a datacentre and metabolic
heat at 310 K in tissue carry utterly different exergy, and lumping them into one
$\dot\sigma_{\text{irr}}$ discards exactly the asymmetry that makes Regimes II and III different.

**Spatial generalisation (this is what earns the $\partial_\mu J^\mu$ notation).** The original is a
$0{+}1$-dimensional mechanics, so $\mu$ has nothing to range over. Promote the token index $k$ to a
lattice coordinate and the transformer becomes a field theory on $\mathbb{Z}$:

$$\frac{d}{d\tau}Q_k \;=\; \mathcal I_{k-1\to k} - \mathcal I_{k\to k+1} \;-\; \big(\dot\sigma_{C,k}+\dot\sigma_{S,k}\big),
\qquad Q = \textstyle\sum_k Q_k .$$

Now $\partial_\mu J^\mu = \dot\sigma$ is literal, with $\mu\in\{\tau,k\}$. This is the version
worth publishing if you want field-theoretic language.

---

## Part 3 — Operationalising the currents (making $\Gamma$ measurable)

Express **both** currents in **nats per second**. Then $\kappa_C=\kappa_S=1$, $\Gamma$ is a true
dimensionless ratio, and the framework becomes falsifiable.

$$J_S \;=\; \nu_{\text{token}}\cdot H(\mathcal V_k)\quad[\text{nat/s}]
\qquad\text{(already well-defined; read off the logits)}$$

$$J_C \;=\; \frac{d\mathcal R_C}{d\tau}\quad[\text{nat/s}],\qquad
\mathcal R_C = D_{\mathrm{KL}}\!\big(p_{\text{human}}(\cdot\mid \text{context}_{<t})\,\big\|\,p_{\text{human}}(\cdot\mid\text{context}_{\le t})\big)$$

i.e. the operator's **surprise-reduction rate** — the drop in their own predictive entropy as each
token lands. This is the active-inference quantity $d\Phi/dt$ was reaching for, and it is estimable:
fit an incremental LM (or a surprisal-from-reading-time model) to the human's anticipatory behaviour
and log the per-token KL. Reading time and pupil dilation are usable low-cost proxies.

Metabolic power then re-enters **not** inside $J_C$ but as the efficiency coefficient that converts
nats to watts, and as the *capacity constraint*:

$$\varepsilon_C \;=\; \frac{\dot Q_{\text{met}}^{\text{marginal}}}{J_C}\;\;[\text{J/nat}],
\qquad
J_C \;\le\; \frac{\dot Q_{\text{met}}^{\max}}{\varepsilon_C} \;\equiv\; J_C^{\max}.$$

**Landauer anchoring.** $\varepsilon_{\text{Landauer}} = k_BT = 4.14\times10^{-21}$ J/nat at 300 K.
Order-of-magnitude calibration (`calibrate.py`):

| substrate | regime | $\varepsilon$ (J/nat) | $\varepsilon/\varepsilon_L$ |
|---|---|---|---|
| Silicon | 70B, H100, 50 tok/s, $H\approx2$ | $\sim2.0$ | $4.8\times10^{20}$ |
| Silicon | 7B, 50 tok/s | $\sim0.20$ | $4.8\times10^{19}$ |
| Carbon | comfortable reading (~150 wpm) | $\sim3.3\times10^{-2}$ | $8.1\times10^{18}$ |
| Carbon | max sustained (~500 wpm) | $\sim1.0\times10^{-2}$ | $2.4\times10^{18}$ |

**This is the most interesting quantitative result in the whole framework.** Both substrates operate
at $10^{18}$–$10^{21}\times$ Landauer — the *same* order of magnitude. $\Gamma\sim1$ is therefore
**not a fine-tuned coincidence**; it is the natural operating point of any carbon–silicon
conversation, which is why Regime I is an attractor rather than a knife edge. That is a real,
non-trivial prediction, and it survives the repair. (Numbers are order-of-magnitude; treat the
exponents as the content, not the mantissae.)

**Derived threshold.** With $\nu_S \approx 50$ tok/s and $J_C^{\max}$ set by $\nu_C^{\max}\approx10$
tok/s (~500 wpm, the ceiling of sustained comprehension):

$$\Gamma_{\text{crit}} \;=\; \frac{\nu_S}{\nu_C^{\max}} \;\approx\; 5 .$$

So §6.1's throttling rule has teeth: holding $0.8\le\Gamma\le1.2$ at $\nu_C = 10$ tok/s requires
$\nu_S\in[8,12]$ tok/s. **Default inference settings (50–100 tok/s) put ordinary chat at
$\Gamma\approx5$–$17$ — already past $\Gamma_{\text{crit}}$.** The reason this is not usually
catastrophic is that a human self-throttles by *not reading*, which raises $\varepsilon_C$ and
lowers $J_C$ rather than raising it — the framework needs a saturation term to capture this. An
autonomous agent loop removes the self-throttle entirely.

---

## Part 4 — What the repair *adds*

### 4.1 Regime II has a sharper mechanism than the one proposed

§5 attributes hallucination cascade to $J_S$ exceeding $J_C^{\max}$. The repaired theory says
something stronger and more testable: in an autonomous multi-turn loop **there is no carbon node**,
so $J_C\to0$ and $\Gamma\to\infty$ *regardless of how small $J_S$ is*. The runaway is not an
overflow of the sink; it is the **absence** of the sink. Formally, setting $\mathbf{G}=0$ decouples
$\bar{\mathbf H}$ into two blocks and the silicon factor evolves under its own
$\boldsymbol\Omega_S$ alone — nothing pins its phase, so $\theta$ drifts freely and prompt drift
follows. This is why a **verifier / critic / retrieval grounding** functions as a *surrogate carbon
node*: it restores $\mathbf{G}\neq0$ and finite $\Gamma$.

**Testable prediction:** hallucination rate in autonomous loops should scale with the reciprocal of
surrogate grounding strength, measurable as verifier logprob margin or retrieval-grounding entropy.
This is checkable against existing agent benchmarks.

### 4.2 Regime III is conflating two independent axes — split it

$\Gamma$ is a **throughput ratio**. $H(\mathcal V)$ is a **content-uncertainty level**. They are
orthogonal, and §5 collapses them. The correct phase diagram is 2-D:

```
                       H(V_k) low (confident)      H(V_k) high (uncertain)
                    ┌───────────────────────────┬───────────────────────────┐
   Γ ≈ 1            │  I. RESONANT FLOW         │  I'. Resonant but noisy   │
   (matched)        │  matched rate, low surpr. │  matched rate, high surpr.│
                    │  <- the target regime     │  <- fatiguing but sound   │
                    ├───────────────────────────┼───────────────────────────┤
   Γ >> 1           │  IIa. SPAM                │  IIb. HALLUCINATION       │
   (silicon floods) │  fast + confident + wrong │  CASCADE  <- the real danger
                    │  <- boring, not dangerous │                           │
                    ├───────────────────────────┼───────────────────────────┤
   Γ << 1           │  IIIa. STARVATION         │  IIIb. INCOHERENCE        │
   (carbon floods)  │  throttled/repetitive     │  high-entropy at low rate │
                    │  <- safe but useless      │  <- rare, and mislabelled │
                    └───────────────────────────┴───────────────────────────┘
```

The key correction: **high $H(\mathcal V)$ is not intrinsically pathological.** IIa (fast,
confident, repetitive spam) is far more common in practice than IIb, and it is a *throughput*
failure, not an entropy failure. The single-$\Gamma$ axis cannot distinguish them; the 2-D diagram
can, and it tells you which knob to turn (temperature/beam width for the vertical axis, rate
limiting for the horizontal).

### 4.3 A concrete phase-reset criterion

§6.2's trigger ($\int\dot\sigma_{\text{irr}}d\tau$ exceeding "thermal capacity") mixes exergy with
energy. Replace with the *charge-deficit* criterion, which the balance law gives directly:

$$\Delta Q(\tau) \;=\; Q(\tau_1) - Q(\tau) \;=\; \int_{\tau_1}^{\tau}\!\big(\dot\sigma_C+\dot\sigma_S\big)d\tau'
\;>\; \eta\, Q(\tau_1) \quad\Longrightarrow\quad \text{prune context}$$

with $\eta$ a single fitted constant. Equivalently: prune when the accumulated sink has consumed a
fixed fraction of the initial informational charge. One parameter, directly instrumentable, and it
is the *integral* form of the conservation law rather than a heuristic.

---

## Part 5 — Honest limitations

Keep these visible; they are what will draw fire in review.

1. **$\Phi$ must go or be operationalised.** As integrated information it is not measurable at the
   required temporal resolution and has no canonical $d/dt$. The KL-surprise rate in Part 3 is the
   substitute. Do not keep both.
2. **"Harmonic Scar" is undefined.** §5.Regime II uses it as a load-bearing term ("cannot be
   absorbed as a localized Harmonic Scar and instead back-propagates"). Nothing in §§1–4 introduces
   it. Either define it as a specific mode of $\bar{\mathbf H}$ (a localized eigenvector with small
   participation ratio — which is a legitimate and interesting claim) or cut it.
3. **$\mathbf{G}$ is assumed constant.** Real prompt–response coupling is strongly
   $\tau$-dependent (attention re-weights as context grows). With $\dot{\mathbf G}\neq0$ the
   charge is no longer conserved even without baths: $\dot Q = -\mathbf z^\dagger\dot{\bar{\mathbf H}}\mathbf z$.
   That term should be carried explicitly — it is the *context-growth* contribution to drift, and it
   is arguably the dominant one in long agent loops.
4. **Linearity.** $\bar{\mathbf H}$ is quadratic throughout. Transformer loss landscapes are not.
   The formalism is a linear-response / near-operating-point theory and should be labelled as such.
5. **The $\Gamma\approx1$ attractor argument is order-of-magnitude.** It is suggestive, not
   established. It needs the actual $\varepsilon_C$ measured in a reading-comprehension experiment
   with concurrent metabolic or pupillometric monitoring.

---

## Part 6 — Symbol table (repaired theory)

| symbol | meaning | units | measurable? |
|---|---|---|---|
| $\tau$ | shared interaction/inference coordinate | s | yes (wall clock) |
| $\mathbf{a}\in\mathbb C^{d_C}$ | carbon amplitudes | — | via proxy |
| $\mathbf{b}\in\mathbb C^{d_S}$ | silicon amplitudes | — | yes (embeddings) |
| $\boldsymbol\Omega_C$ | homeostatic well (precision) | rad/s | partially |
| $\boldsymbol\Omega_S$ | CE-landscape Hessian at operating point | rad/s | yes |
| $\mathbf G$ | prompt–response coupling | rad/s | yes (turn statistics) |
| $n_C,n_S$ | substrate occupations $=\lVert\mathbf a\rVert^2,\lVert\mathbf b\rVert^2$ | nats | yes |
| $Q=n_C+n_S$ | **Noether charge** | nats | yes |
| $\theta$ | relative phase $\arg\langle\mathbf a,\mathbf G\mathbf b\rangle$ | rad | yes |
| $\mathcal I=2\,\mathrm{Im}\langle\mathbf a,\mathbf G\mathbf b\rangle$ | exchange current | nat/s | yes |
| $\gamma_C,\gamma_S$ | sink rates | 1/s | yes |
| $\dot\sigma_C,\dot\sigma_S$ | entropy production per substrate | nat/s | yes (power/temp) |
| $\varepsilon_C,\varepsilon_S$ | J per nat processed | J/nat | yes |
| $\Gamma=\nu_S H(\mathcal V)/ (d\mathcal R_C/d\tau)$ | transduction coupling index | — | yes |
| $\Delta\omega=\omega_S-\omega_C$ | detuning → phase drift / beating | rad/s | yes |

**Removed:** $\kappa_C,\kappa_S$ (absorbed by unit choice), $\alpha_C,\alpha_S,\lambda_C,\lambda_S$
(the impedance-matching condition is vacuous once the phase assignment is diagonal),
$d\Phi/dt$ (replaced by $d\mathcal R_C/d\tau$), $M_C,M_S$ (first-order form has no mass tensor).

---

## Files

| file | contents |
|---|---|
| `noether_check.py` | Defect 1: invariance of $\mathcal L$ as written, all three readings |
| `part2.py` | Defect 1(b): per-term symmetry table, diagonal vs anti-diagonal |
| `part3.py` | Part 2: repaired action, charge conservation, exchange balance, dissipation |
| `calibrate.py` | Part 3: Landauer anchoring, $\varepsilon$ table, $\Gamma_{\text{crit}}$ |
| `part4_drive.py` | Addendum §1: undriven decay, driven NESS, power-balance theorem |
| `part5_rank.py` | Addendum §3: $\mathrm{rank}(\mathbf G)$ as exchange bandwidth, dark modes |
| `part6b.py` | Addendum §4: $\Gamma$-governor open vs closed loop |
| `ADDENDUM_monadic_audit.md` | audit of the monadic reframing |
| `README.md` | reproduction instructions, convention traps |

> **Postscript.** Part 2's law $dQ/d\tau=-(\dot\sigma_C+\dot\sigma_S)$ describes a system with
> sinks and **no source**, whose only attractor is $\mathbf z=0$. The addendum supplies the missing
> drive $\mathbf D(\tau)$, derives the non-equilibrium steady state, and shows that the exact law
> of the *open* system is a power balance rather than a Noether charge. Read
> `ADDENDUM_monadic_audit.md` §1 before relying on Part 2's balance law.
