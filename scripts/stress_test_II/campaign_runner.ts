import { writeFileSync } from 'fs';
import { createHash } from 'crypto';
import { executeInstrumentedRun, TelemetryRecord } from './harness';
import * as analysisPlan from '../../docs/canonical/STATISTICAL_ANALYSIS_PLAN.json';

interface PairResult {
  pairId: string;
  randomizationSeed: number;
  conditionOrder: ['TREATMENT' | 'CONTROL', 'TREATMENT' | 'CONTROL'];
  controlResult: TelemetryRecord;
  treatmentResult: TelemetryRecord;
  durationDeltaMs: number;
  thermalDeltaDiffCelsius: number;
  classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  outputHash: string;
}

interface CampaignReport {
  campaignTimestamp: string;
  planVersion: string;
  totalPairs: number;
  pairs: PairResult[];
  aggregateAnalysis: {
    meanDurationDeltaMs: number;
    meanThermalDeltaDiffCelsius: number;
    campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  };
}

// Simple deterministic pseudo-random generator based on seed
function pseudoRandom(seed: number): number {
  const x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
}

const targetPairs = analysisPlan.parameters.targetRepetitions;
const baseSeed = 20260929;
const timestamp = new Date().toISOString();
const pairResults: PairResult[] = [];

let totalDurationDelta = 0;
let totalThermalDiff = 0;

for (let i = 1; i <= targetPairs; i++) {
  const pairId = `PAIR-${String(i).padStart(3, '0')}`;
  const pairSeed = baseSeed + i;
  
  // Deterministic order derivation
  const randVal = pseudoRandom(pairSeed);
  const order: ['TREATMENT' | 'CONTROL', 'TREATMENT' | 'CONTROL'] = randVal > 0.5 
    ? ['TREATMENT', 'CONTROL'] 
    : ['CONTROL', 'TREATMENT'];

  const controlRun = executeInstrumentedRun({
    runId: `${pairId}-CTL`,
    seed: pairSeed,
    treatment: false,
    timestamp
  });

  const treatmentRun = executeInstrumentedRun({
    runId: `${pairId}-TRT`,
    seed: pairSeed,
    treatment: true,
    timestamp
  });

  const durationDelta = treatmentRun.durationMs - controlRun.durationMs;
  const thermalDiff = treatmentRun.thermalDeltaCelsius - controlRun.thermalDeltaCelsius;

  totalDurationDelta += durationDelta;
  totalThermalDiff += thermalDiff;

  let classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
  if (
    Math.abs(durationDelta) > analysisPlan.parameters.effectSizeThresholdDurationMs ||
    Math.abs(thermalDiff) > analysisPlan.parameters.effectSizeThresholdThermalC
  ) {
    classification = 'OBSERVED';
  }

  const payload = JSON.stringify({ pairId, pairSeed, order, controlRun, treatmentRun, durationDelta, thermalDiff, classification });
  const outputHash = createHash('sha256').update(payload).digest('hex');

  pairResults.push({
    pairId,
    randomizationSeed: pairSeed,
    conditionOrder: order,
    controlResult: controlRun,
    treatmentResult: treatmentRun,
    durationDeltaMs: Number(durationDelta.toFixed(3)),
    thermalDeltaDiffCelsius: Number(thermalDiff.toFixed(3)),
    classification,
    outputHash
  });
}

const meanDurationDelta = totalDurationDelta / targetPairs;
const meanThermalDiff = totalThermalDiff / targetPairs;

let campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
if (
  Math.abs(meanDurationDelta) > (analysisPlan.parameters.effectSizeThresholdDurationMs / 2) ||
  Math.abs(meanThermalDiff) > (analysisPlan.parameters.effectSizeThresholdThermalC / 2)
) {
  campaignClassification = 'OBSERVED';
}

const campaignReport: CampaignReport = {
  campaignTimestamp: timestamp,
  planVersion: analysisPlan.version,
  totalPairs: targetPairs,
  pairs: pairResults,
  aggregateAnalysis: {
    meanDurationDeltaMs: Number(meanDurationDelta.toFixed(3)),
    meanThermalDeltaDiffCelsius: Number(meanThermalDiff.toFixed(3)),
    campaignClassification
  }
};

const outPath = `docs/canonical/STRESS_II_CAMPAIGN_REPORT_50.json`;
writeFileSync(outPath, JSON.stringify(campaignReport, null, 2));
console.log(`Campaign execution complete. Archived to ${outPath}`);
