# Stress Test II: Instrumentation Boundary

**Status:** PROTOCOL
**Evidence status:** NOT_YET_TESTED
**Related claim:** CE-XIX-003
**Related chapter:** XIX
**Related stress test:** II

## 1. Purpose

Determine whether a deterministic contradiction event produces a measurable physical signal distinguishable from baseline variation.

## 2. Frozen Causal Chain

A ∧ ¬A
→ Belnap BOTH
→ deterministic runtime transition
→ buffer/archive event
→ instrumentation timestamp
→ telemetry acquisition
→ correlation analysis
→ evidence review

No physical effect is assumed.

## 3. Instrumentation Channels

### Thermal

Measure temperature and temperature derivative at the available hardware/software sampling boundary.

### Acoustic

Measure acoustic output only where an appropriate microphone/sensor boundary exists.

### Electrical

Measure externally observable electrical/power characteristics only through supported instrumentation. Do not infer electrical behavior from CPU utilization alone.

### Timing / Performance

Record monotonic timestamps, execution duration, CPU utilization, scheduler/runtime events, and other reproducible software telemetry.

## 4. Experimental Groups

### CONTROL

- identical runtime
- identical seed
- contradiction disabled

### TREATMENT

- identical runtime
- identical seed
- A = TRUE
- ¬A = TRUE
- Belnap state = BOTH

### REPEAT

Multiple independently recorded treatment runs.

## 5. Required Event Record

Each run must retain:

- run_id
- seed
- specification_hash
- code_commit
- runtime_version
- operating_system
- hardware_identifier
- monotonic_start
- contradiction_event_timestamp
- contradiction_event_hash
- instrumentation timestamps
- raw measurements
- baseline measurements
- analysis method
- output hash

## 6. Temporal Correlation

The contradiction event is the reference event.

Measurements must be aligned against that event rather than merely compared by wall-clock time.

No temporal proximity alone constitutes causation.

Correlation does not establish causation.

## 7. Controls

The experiment must account for:

- ordinary runtime variance
- thermal drift
- background processes
- scheduler variation
- sensor resolution
- sampling frequency
- measurement noise
- repeated-run variance

## 8. Result Classes

NOT_YET_TESTED

No physical measurement has been acquired.

NULL_RESULT

Instrumentation completed successfully but no predefined physical effect was detected.

INCONCLUSIVE

Measurement occurred, but data quality or experimental control was insufficient for a determination.

OBSERVED

A predefined signal was detected.

REPRODUCED

The predefined signal was observed across independent repeated runs under controlled conditions.

FALSIFIED

The experiment provides evidence inconsistent with the stated hypothesis.

Failed instrumentation is not a NULL_RESULT.

## 9. Evidence Promotion Gate

CE-XIX-003 remains:

Classification: HYPOTHESIS
Status: NOT_YET_TESTED

It may not become SUPPORTED merely because:

- the telemetry schema exists
- Stress Test II executes
- a sensor reports a fluctuation
- a correlation is visually apparent
- the runtime becomes slower
- temperature changes
- power consumption changes

Promotion requires traceable measurements, predefined analysis, appropriate controls, adequate data quality, reproducibility where required, and evidence review.

## 10. Physical Harmonic Scar Boundary

The term "Harmonic Scar" remains a canonical hypothesis.

No physical phenomenon is assumed to correspond to the term before measurement establishes an operationally defined observable.

The required chain is:

canonical term
→ operational definition
→ measurable variable
→ controlled observation
→ analysis
→ replication
→ evidence review

The canonical term itself does not constitute a measurement.

## 11. Archive Requirements

Raw data must be retained alongside:

- run identifier
- commit hash
- configuration
- instrument metadata
- analysis output
- output hashes

Derived summaries must never replace raw measurements.

Every derived result must remain traceable to its source measurements.

## 12. Failure Policy

Failed instrumentation does not count as a NULL_RESULT.

A missing sensor, unavailable API, malformed dataset, timestamp failure, or corrupted recording is recorded as FAILED / INVALID RUN.

An invalid run must not be used as positive or negative physical evidence.

## 13. Verification Output

The final Stress Test II record must explicitly distinguish:

IMPLEMENTATION
OBSERVATION
CORRELATION
REPLICATION
INTERPRETATION

No interpretation may be promoted into observation.

No correlation may be promoted into causation.

No observation may be promoted into replication without independent repeated runs.

## 14. Evidence Boundary

The current canonical evidence boundary is:

CE-XIX-001  SUPPORTED
CE-XIX-002  SUPPORTED
CE-XIX-003  HYPOTHESIS / NOT_YET_TESTED

This protocol does not modify that classification.

Stress Test I establishes computational evidence concerning deterministic Belnap contradiction handling and runtime containment.

Stress Test II defines the boundary at which physical measurements may begin.

The existence of this protocol is not physical evidence.

The existence of telemetry infrastructure is not physical evidence.

A successful Stress Test II execution is not, by itself, evidence of a Harmonic Scar.

## 15. Falsification Requirement

The experiment must specify in advance what observations would count against the hypothesis.

Examples include:

- no measurable difference between controlled treatment and control
- observed effects disappearing under repeated runs
- effects attributable to known thermal drift
- effects attributable to scheduler/runtime variance
- effects attributable to measurement noise
- effects disappearing when the contradiction condition is removed
- failure to reproduce a predefined signal under controlled conditions

The protocol must not be rewritten after observing the data merely to make an outcome appear confirmatory.

## 16. Correlation and Causation

Correlation analysis is permitted where appropriate.

Possible predefined methods include:

- Pearson correlation
- rank correlation
- cross-correlation
- event-window analysis
- treatment/control distribution comparison

A strong correlation does not by itself establish that the contradiction event caused the measured physical signal.

The primary comparison is between controlled treatment and control distributions, with the contradiction event providing the temporal reference point.

## 17. Reproducibility

A result considered for promotion beyond OBSERVED must include:

- independent repeated runs
- preserved run identifiers
- preserved code commit
- preserved configuration
- preserved instrument metadata
- preserved raw measurements
- deterministic identification of the contradiction event
- reproducible analysis
- output hashes

Reproduction must not silently reuse the same output artifact as an independent measurement.

## 18. Canonical Interpretation Rule

The canonical report may describe:

- the architecture
- the hypothesis
- the computational implementation
- the instrumentation procedure
- the measurements
- the statistical analysis
- the observed results
- the limitations

It may not describe an unmeasured physical Harmonic Scar as an established physical fact.

Until the evidence gate is crossed, all physical Harmonic Scar language remains explicitly hypothetical.

## 19. Current Status

Protocol: COMPLETE
Physical instrumentation: NOT_YET_TESTED
CE-XIX-003: HYPOTHESIS / NOT_YET_TESTED

The next engineering task is implementation of the actual Stress Test II measurement boundary.

No canonical evidence promotion occurs as a consequence of this protocol alone.
