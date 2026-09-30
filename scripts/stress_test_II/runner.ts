import { writeFileSync } from 'fs';
import { executeInstrumentedRun, TelemetryRecord } from './harness';

interface ExperimentBatchResult {
  seed: number;
  control: TelemetryRecord;
  treatment: TelemetryRecord;
  analysis: {
    durationDeltaMs: number;
    thermalDeltaDiffCelsius: number;
    classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  };
}

const seed = parseInt(process.argv[2] || '20260929', 10);
const timestamp = new Date().toISOString();

const controlRun = executeInstrumentedRun({
  runId: `ST-II-CTL-${seed}`,
  seed,
  treatment: false,
  timestamp
});

const treatmentRun = executeInstrumentedRun({
  runId: `ST-II-TRT-${seed}`,
  seed,
  treatment: true,
  timestamp
});

const durationDelta = treatmentRun.durationMs - controlRun.durationMs;
const thermalDiff = treatmentRun.thermalDeltaCelsius - controlRun.thermalDeltaCelsius;

// Evaluation Logic against predefined null thresholds
let classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
if (Math.abs(durationDelta) > 50.0 || Math.abs(thermalDiff) > 1.0) {
  classification = 'OBSERVED';
}

const batchResult: ExperimentBatchResult = {
  seed,
  control: controlRun,
  treatment: treatmentRun,
  analysis: {
    durationDeltaMs: Number(durationDelta.toFixed(3)),
    thermalDeltaDiffCelsius: Number(thermalDiff.toFixed(3)),
    classification
  }
};

const outPath = `docs/canonical/STRESS_II_BATCH_${seed}.json`;
writeFileSync(outPath, JSON.stringify(batchResult, null, 2));
console.log(JSON.stringify(batchResult, null, 2));
