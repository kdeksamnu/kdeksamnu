# Campaign 002: Evidence Boundary Audit & Reproducibility Manifest

## 1. Reproducibility Manifest

* **Campaign ID:** `CAMPAIGN-002`
* **Frozen Analysis-Plan Version:** `1.0.1-frozen`
* **Base Seed:** `20260929`
* **Pair Count:** `50`
* **Randomization Algorithm:** Seeded Mulberry32 PRNG (`seed + pairIndex`)
* **Execution-Order Rule:** Operational permutation per pair (`CONTROL→TREATMENT` or `TREATMENT→CONTROL` determined by PRNG draw)
* **Statistical Method:** Student's Paired Two-Tailed t-test (Two-sided p-value derived via regularized incomplete beta function on within-pair differences)
* **Evidence-Boundary Status:** Runtime telemetry `NULL_RESULT` / `CE-XIX-003` remains `HYPOTHESIS / NOT_YET_TESTED`
* **Repository Commit Checkpoint:** `93978ac36cdb61a55b4045a0c8984570cdfdcc0b`

---

## 2. Evidence Boundary Audit

### What Campaign 002 Measured
* **Runtime Telemetry:** Collected 50 paired execution iterations comparing control and treatment execution durations ($\Delta t$ in milliseconds) and baseline thermal metrics ($\Delta T$ in degrees Celsius).
* **Statistical Distribution:** Evaluated within-pair differences under a paired experimental design using a two-tailed Student's paired $t$-test.
* **Result:** Yielded non-significant $p$-values ($\ge 0.01$) failing to exceed pre-defined effect-size thresholds, resulting in a formal **`NULL_RESULT`**.

### What Campaign 002 Did Not Measure
* **Physical Causation:** It did not measure, capture, or validate any physical state transition, molecular deformation, or topological modification within the substrate.
* **Harmonic Scar Manifestation:** It did not demonstrate the physical existence of a Harmonic Scar or validate field-theoretic resonance claims under MLAOS-Prime axioms.

### Epistemic Separation Rule
* **Runtime/Telemetry `NULL_RESULT`** is strictly separated from **Physical Harmonic Scar Demonstration**. 
* Statistical non-significance in software execution loops governs software performance telemetry only; it neither confirms nor disproves metaphysical or architectural theorems in the 40-Book Codex.
* **`CE-XIX-003`** remains classified as **`HYPOTHESIS / NOT_YET_TESTED`**.
