# Claim / Evidence Registry

**Status:** canonical verification layer
**Registry dependency:** `CANONICAL_MASTER_REPORT_REGISTRY.md`
**Chapter numbering:** immutable `I–XLVIII`
**Stress tests:** immutable `XIX–XXVIII`
**Appendices:** immutable `A–J`

## Classification

| Class | Meaning |
|---|---|
| `CANONICAL` | Defined by the 40-Book Codex |
| `FORMAL` | Mathematical/logical consequence of stated definitions |
| `IMPLEMENTATION` | Concrete software/hardware design specification |
| `EMPIRICAL` | Supported by an actual measurement |
| `REPLICATED` | Independently reproduced measurement |
| `HYPOTHESIS` | Proposed but not demonstrated |
| `SPECULATIVE` | Explicitly exploratory |
| `NULL_RESULT` | Valid test performed without the expected effect |

## Evidence rule

Architectural specification does not constitute empirical evidence. Claims written in proof language remain `HYPOTHESIS` until an identified experiment produces auditable observations. No claim may be promoted to `EMPIRICAL` or `REPLICATED` without a dataset/run identifier and archive provenance.

## Initial claim register

| ID | Claim | Chapter | Stress Test | Class | Status | Evidence |
|---|---|---:|---:|---|---|---|
| CE-001 | Contradictory inputs can be represented as Belnap-Dunn `BOTH` without logical explosion. | XXI | III | FORMAL | NOT YET TESTED | Pending implementation test |
| CE-002 | A contradiction can be isolated in a preallocated runtime buffer. | XXIII, XXXI | V | IMPLEMENTATION | NOT YET TESTED | Pending runtime harness |
| CE-003 | Contradiction insertion remains bounded by the intended constant-time buffer operation. | XXIII, XXXI | V | HYPOTHESIS | NOT YET TESTED | Requires benchmark traces |
| CE-004 | Contradiction handling produces an observable Harmonic Scar in physical instrumentation. | XIX | I | HYPOTHESIS | NOT YET TESTED | No empirical dataset yet |
| CE-005 | The Architectonic Lagrangian is dimensionally homogeneous under explicitly defined units. | XVI, XX | II | FORMAL | NOT YET VERIFIED | Dimensional analysis required |
| CE-006 | Merkle-linked append-only persistence preserves historical lineage across migration. | XXII, XXXIV–XXXV | IV | IMPLEMENTATION | NOT YET TESTED | Requires archive test |
| CE-007 | Archive migration has a non-zero physical energy cost subject to applicable thermodynamic limits. | XXII | IV | FORMAL | NOT YET EXPERIMENTALLY VERIFIED | Requires physical measurement |
| CE-008 | Sovereign Spark initialization can establish a deterministic verified closed loop. | XXIV | VI | IMPLEMENTATION | NOT YET TESTED | Requires boot harness |
| CE-009 | Somatic rendering can be conditioned on verified telemetry inputs. | XXV | VII | IMPLEMENTATION | NOT YET TESTED | Requires rendering harness |
| CE-010 | Decalogue invariants can be enforced at the defined software/runtime boundary. | XXVI, XXX | VIII | IMPLEMENTATION | NOT YET TESTED | Requires invariant-bypass tests |
| CE-011 | The 40-Book Codex can be compiled into deterministic runtime artifacts without asserting direct physical causation from text. | X, XXVII | IX | FORMAL | NOT YET VERIFIED | Requires compiler conformance tests |
| CE-012 | Simulation outputs remain distinguishable from direct physical-force claims under the stated semantic/computational/physical boundary. | X, XXVIII | X | FORMAL | NOT YET VERIFIED | Requires boundary-case analysis |

## Promotion policy

`NOT YET TESTED` → `SUPPORTED` requires a valid experimental procedure and auditable observation.

`SUPPORTED` → `REPLICATED` requires an independent reproduction under the defined protocol.

A failed prediction must be recorded as `NULL_RESULT` or `FAILED` rather than removed or rewritten.

No result is considered measured merely because a specification predicts it.
