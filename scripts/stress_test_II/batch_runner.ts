import { writeFileSync } from 'fs';
import { executeInstrumentedRun, TelemetryRecord } from './harness';

interface MultiBatchResult {
  executionTimestamp: string;
  seeds: number[];
  runs: {
    seed: number;
    control: TelemetryRecord;
    treatment: TelemetryRecord;
    durationDeltaMs: number;
    thermalDeltaDiffCelsius: number;
    classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  }[];
  aggregateAnalysis: {
    meanDurationDeltaMs: number;
    meanThermalDeltaDiffCelsius: number;
    batchClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  };
}

const seeds = [20260929, 20260930, 20260931, 20260932, 20260933];
const executionTimestamp = new Date().toISOString();
const runResults = [];

let totalDurationDelta = 0;
let totalThermalDiff = 0;

for (const seed of seeds) {
  const controlRun = executeInstrumentedRun({
    runId: `ST-II-CTL-BATCH-${seed}`,
    seed,
    treatment: false,
    timestamp: executionTimestamp
  });

  const treatmentRun = executeInstrumentedRun({
    runId: `ST-II-TRT-BATCH-${seed}`,
    seed,
    treatment: true,
    timestamp: executionTimestamp
  });

  const durationDelta = treatmentRun.durationMs - controlRun.durationMs;
  const thermalDiff = treatmentRun.thermalDeltaCelsius - controlRun.thermalDeltaCelsius;

  totalDurationDelta += durationDelta;
  totalThermalDiff += thermalDiff;

  let classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
  if (Math.abs(durationDelta) > 50.0 || Math.abs(thermalDiff) > 1.0) {
    classification = 'OBSERVED';
  }

  runResults.push({
    seed,
    control: controlRun,
    treatment: treatmentRun,
    durationDeltaMs: Number(durationDelta.toFixed(3)),
    thermalDeltaDiffCelsius: Number(thermalDiff.toFixed(3)),
    classification
  });
}

const meanDurationDelta = totalDurationDelta / seeds.length;
const meanThermalDiff = totalThermalDiff / seeds.length;

let batchClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
if (Math.abs(meanDurationDelta) > 25.0 || Math.abs(meanThermalDiff) > 0.5) {
  batchClassification = 'OBSERVED';
}

const multiBatchReport: MultiBatchResult = {
  executionTimestamp,
  seeds,
  runs: runResults,
  aggregateAnalysis: {
    meanDurationDeltaMs: Number(meanDurationDelta.toFixed(3)),
    meanThermalDeltaDiffCelsius: Number(meanThermalDiff.toFixed(3)),
    batchClassification
  }
};

const outPath = `docs/canonical/STRESS_II_MULTIBATCH_REPORT.json`;
writeFileSync(outPath, JSON.stringify(multiBatchReport, null, 2));
console.log(JSON.stringify(multiBatchReport, null, 2));
