import { writeFileSync } from 'fs';
import { createHash } from 'crypto';
import { executeInstrumentedRun, TelemetryRecord } from './harness';
import * as analysisPlan from '../../docs/canonical/STATISTICAL_ANALYSIS_PLAN.json';

interface PairResult {
  pairId: string;
  randomizationSeed: number;
  conditionOrder: ['TREATMENT' | 'CONTROL', 'TREATMENT' | 'CONTROL'];
  firstRun: TelemetryRecord;
  secondRun: TelemetryRecord;
  controlResult: TelemetryRecord;
  treatmentResult: TelemetryRecord;
  durationDeltaMs: number;
  thermalDeltaDiffCelsius: number;
  classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  outputHash: string;
}

interface CampaignReport {
  campaignId: string;
  campaignTimestamp: string;
  planVersion: string;
  totalPairs: number;
  pairs: PairResult[];
  statisticalTest: {
    testName: string;
    pValueDuration: number;
    pValueThermal: number;
    significanceThreshold: number;
    statisticallySignificant: boolean;
  };
  aggregateAnalysis: {
    meanDurationDeltaMs: number;
    meanThermalDeltaDiffCelsius: number;
    campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  };
}

function pseudoRandom(seed: number): number {
  const x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
}

// Simple two-tailed p-value approximation using normal approximation for large N (50 pairs)
function calculatePValue(controlValues: number[], treatmentValues: number[]): number {
  const n = controlValues.length;
  const meanControl = controlValues.reduce((a, b) => a + b, 0) / n;
  const meanTreatment = treatmentValues.reduce((a, b) => a + b, 0) / n;

  const varControl = controlValues.reduce((a, b) => a + Math.pow(b - meanControl, 2), 0) / (n - 1);
  const varTreatment = treatmentValues.reduce((a, b) => a + Math.pow(b - meanTreatment, 2), 0) / (n - 1);

  const se = Math.sqrt((varControl / n) + (varTreatment / n));
  if (se === 0) return 1.0;

  const tStat = (meanTreatment - meanControl) / se;
  // Approximate standard normal CDF for two-tailed p-value
  const z = Math.abs(tStat);
  const p = 2 * (1 - cumulativeNormal(z));
  return Number(p.toFixed(6));
}

function cumulativeNormal(z: number): number {
  const t = 1 / (1 + 0.2316419 * z);
  const d = 0.319381530;
  const p = 1 - (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-z * z / 2) * 
    (t * (d + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429)))));
  return p;
}

const targetPairs = analysisPlan.parameters.targetRepetitions;
const baseSeed = 30260929; // Distinct base seed for Campaign 002
const timestamp = new Date().toISOString();
const pairResults: PairResult[] = [];

const controlDurations: number[] = [];
const treatmentDurations: number[] = [];
const controlThermals: number[] = [];
const treatmentThermals: number[] = [];

let totalDurationDelta = 0;
let totalThermalDiff = 0;

for (let i = 1; i <= targetPairs; i++) {
  const pairId = `PAIR-002-${String(i).padStart(3, '0')}`;
  const pairSeed = baseSeed + i;
  
  const randVal = pseudoRandom(pairSeed);
  const order: ['TREATMENT' | 'CONTROL', 'TREATMENT' | 'CONTROL'] = randVal > 0.5 
    ? ['TREATMENT', 'CONTROL'] 
    : ['CONTROL', 'TREATMENT'];

  let firstRun: TelemetryRecord;
  let secondRun: TelemetryRecord;
  let controlRun: TelemetryRecord;
  let treatmentRun: TelemetryRecord;

  if (order[0] === 'TREATMENT') {
    treatmentRun = executeInstrumentedRun({ runId: `${pairId}-TRT`, seed: pairSeed, treatment: true, timestamp });
    controlRun = executeInstrumentedRun({ runId: `${pairId}-CTL`, seed: pairSeed, treatment: false, timestamp });
    firstRun = treatmentRun;
    secondRun = controlRun;
  } else {
    controlRun = executeInstrumentedRun({ runId: `${pairId}-CTL`, seed: pairSeed, treatment: false, timestamp });
    treatmentRun = executeInstrumentedRun({ runId: `${pairId}-TRT`, seed: pairSeed, treatment: true, timestamp });
    firstRun = controlRun;
    secondRun = treatmentRun;
  }

  controlDurations.push(controlRun.durationMs);
  treatmentDurations.push(treatmentRun.durationMs);
  controlThermals.push(controlRun.thermalDeltaCelsius);
  treatmentThermals.push(treatmentRun.thermalDeltaCelsius);

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

  const payload = JSON.stringify({ pairId, pairSeed, order, firstRun, secondRun, durationDelta, thermalDiff, classification });
  const outputHash = createHash('sha256').update(payload).digest('hex');

  pairResults.push({
    pairId,
    randomizationSeed: pairSeed,
    conditionOrder: order,
    firstRun,
    secondRun,
    controlResult: controlRun,
    treatmentResult: treatmentRun,
    durationDeltaMs: Number(durationDelta.toFixed(3)),
    thermalDeltaDiffCelsius: Number(thermalDiff.toFixed(3)),
    classification,
    outputHash
  });
}

const pValueDuration = calculatePValue(controlDurations, treatmentDurations);
const pValueThermal = calculatePValue(controlThermals, treatmentThermals);
const statisticallySignificant = (pValueDuration < analysisPlan.parameters.significanceThresholdP) || 
                                  (pValueThermal < analysisPlan.parameters.significanceThresholdP);

const meanDurationDelta = totalDurationDelta / targetPairs;
const meanThermalDiff = totalThermalDiff / targetPairs;

let campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
if (
  statisticallySignificant &&
  (Math.abs(meanDurationDelta) > analysisPlan.parameters.effectSizeThresholdDurationMs ||
   Math.abs(meanThermalDiff) > analysisPlan.parameters.effectSizeThresholdThermalC)
) {
  campaignClassification = 'OBSERVED';
}

const campaignReport: CampaignReport = {
  campaignId: 'CAMPAIGN-002',
  campaignTimestamp: timestamp,
  planVersion: analysisPlan.version,
  totalPairs: targetPairs,
  pairs: pairResults,
  statisticalTest: {
    testName: 'Student’s Two-Sample t-test (Two-Tailed)',
    pValueDuration,
    pValueThermal,
    significanceThreshold: analysisPlan.parameters.significanceThresholdP,
    statisticallySignificant
  },
  aggregateAnalysis: {
    meanDurationDeltaMs: Number(meanDurationDelta.toFixed(3)),
    meanThermalDeltaDiffCelsius: Number(meanThermalDiff.toFixed(3)),
    campaignClassification
  }
};

const outPath = `docs/canonical/STRESS_II_CAMPAIGN_002_REPORT.json`;
writeFileSync(outPath, JSON.stringify(campaignReport, null, 2));
console.log(`CAMPAIGN-002 execution complete. Archived to ${outPath}`);
