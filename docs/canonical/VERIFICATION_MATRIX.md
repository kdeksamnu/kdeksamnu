# Verification Matrix

**Status:** canonical experimental gate
**Structural source of truth:** frozen 48-chapter registry
**Rule:** no claim is marked measured or replicated without evidence.

| ID | Claim / Test | Chapter | Stress Test | Observable Variable | Instrument / Method | Experimental Procedure | Expected Result | Null Result | Actual Result | Run ID | Reproductions | Status | Archive Hash |
|---|---|---:|---:|---|---|---|---|---|---|---|---:|---|---|
| VM-001 | Contradiction containment | XIX, XXI | I, III | Logical state | Deterministic runtime harness | Inject `A` and `¬A` into the same proposition atom | State resolves to `BOTH`; no exception/explosion | State remains unresolved, crashes, or explodes | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-002 | Dimensional homogeneity | XVI, XX | II | Units of each Lagrangian term | Symbolic dimensional checker | Assign explicit dimensions and validate every additive term | All additive terms have identical dimensions | Any additive term has incompatible dimensions | PENDING | PENDING | 0 | NOT YET VERIFIED | PENDING |
| VM-003 | Belnap-Dunn lattice behavior | XIII, XXI | III | Truth/information ordering | Pure deterministic algebra tests | Exhaustively exercise defined lattice operations | Operations remain within `T/F/B/N` | Invalid state or logical explosion | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-004 | Archive persistence boundary | XXII, XXXIV–XXXV | IV | Hash lineage and restored state | Merkle/WAL test harness | Append, verify, migrate, and restore archive state | Historical lineage remains verifiable | Hash mismatch or historical overwrite | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-005 | Dialetheic buffer complexity | XXIII, XXXI | V | Insertion latency vs fixed buffer operation | Benchmark/performance counters | Repeat contradiction insertions at controlled loads | Intended insertion path remains bounded independently of downstream persistence | Runtime path scales with load or allocates dynamically | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-006 | Sovereign Spark initialization | XXIV | VI | Initialization state/hash consistency | Boot/integration harness | Initialize from fixed seed and verified archive root | Deterministic verified closed-loop state | Initialization diverges or verification fails | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-007 | Somatic rendering grounding | XXV | VII | Render transition vs telemetry input | Instrumented rendering harness | Replay telemetry with and without valid input checksums | Render updates occur only under valid input conditions | Uncorrelated render transition | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-008 | Decalogue enforcement | XXVI, XXX | VIII | Invariant violation handling | Runtime boundary tests | Attempt each defined prohibited transition | Violation is detected and quarantined | Unauthorized transition commits | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-009 | Codex compilation boundary | X, XXIX | IX | Compiler artifact hashes | Deterministic compiler tests | Compile identical source under fixed environment | Identical target artifacts/hashes | Non-deterministic output or semantic boundary violation | PENDING | PENDING | 0 | NOT YET TESTED | PENDING |
| VM-010 | Simulation/reality boundary | X, XXVIII | X | Distinction between specification, execution, and physical observation | Conformance review + runtime trace | Trace a claim through specification, implementation, execution, and observation | Causal layers remain explicitly distinct | Direct physical causation is asserted without an implementation path | PENDING | PENDING | 0 | NOT YET VERIFIED | PENDING |

## Status vocabulary

- `NOT YET TESTED`
- `NOT YET VERIFIED`
- `SUPPORTED`
- `REPLICATED`
- `INCONCLUSIVE`
- `FAILED`
- `NULL_RESULT`

## Evidence gate

This matrix intentionally contains no measured or replicated results. `Actual Result`, `Run ID`, reproduction count, and archive hash remain empty until experiments are executed and archived.
