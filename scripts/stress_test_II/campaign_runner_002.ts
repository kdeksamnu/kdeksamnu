import { writeFileSync } from 'fs';
import { createHash } from 'crypto';
import { executeInstrumentedRun, TelemetryRecord } from './harness';
import * as analysisPlan from '../../docs/canonical/STATISTICAL_ANALYSIS_PLAN.json';

type Condition = 'CONTROL' | 'TREATMENT';

interface PairResult {
  pairId: string;
  randomizationSeed: number;
  conditionOrder: [Condition, Condition];
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
    design: string;
    pValueDuration: number;
    pValueThermal: number;
    statisticallySignificant: boolean;
    significanceThresholdP: number;
  };
  aggregateAnalysis: {
    meanDurationDeltaMs: number;
    meanThermalDeltaDiffCelsius: number;
    campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE';
  };
}

// Improved PRNG using Mulberry32 to guarantee robust distribution of order permutations
function mulberry32(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s += 0x6D2B79F5;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = t + Math.imul(t ^ (t >>> 7), 61 | t) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function randomizedConditionOrder(seed: number): [Condition, Condition] {
  const rand = mulberry32(seed)();
  return rand < 0.5 ? ['CONTROL', 'TREATMENT'] : ['TREATMENT', 'CONTROL'];
}

function mean(values: number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function sampleVariance(values: number[]): number {
  const m = mean(values);
  return values.reduce((sum, value) => sum + (value - m) ** 2, 0) / (values.length - 1);
}

function logGamma(z: number): number {
  const coefficients = [
    676.5203681218851,
    -1259.1392167224028,
    771.32342877765313,
    -176.61502916214059,
    12.507343278686905,
    -0.13857109526572012,
    9.9843695780195716e-6,
    1.5056327351493116e-7
  ];

  if (z < 0.5) {
    return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * z)) - logGamma(1 - z);
  }

  z -= 1;
  let x = 0.99999999999980993;
  for (let i = 0; i < coefficients.length; i++) {
    x += coefficients[i] / (z + i + 1);
  }

  const t = z + coefficients.length - 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}

function betaContinuedFraction(a: number, b: number, x: number): number {
  const maxIterations = 200;
  const epsilon = 3e-14;
  const tiny = 1e-300;

  let qab = a + b;
  let qap = a + 1;
  let qam = a - 1;
  let c = 1;
  let d = 1 - qab * x / qap;
  if (Math.abs(d) < tiny) d = tiny;
  d = 1 / d;
  let h = d;

  for (let m = 1; m <= maxIterations; m++) {
    const m2 = 2 * m;
    let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1 + aa / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;
    h *= d * c;

    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < tiny) d = tiny;
    c = 1 + aa / c;
    if (Math.abs(c) < tiny) c = tiny;
    d = 1 / d;

    const delta = d * c;
    h *= delta;
    if (Math.abs(delta - 1) < epsilon) break;
  }

  return h;
}

function regularizedIncompleteBeta(x: number, a: number, b: number): number {
  if (x <= 0) return 0;
  if (x >= 1) return 1;

  const logBeta = logGamma(a) + logGamma(b) - logGamma(a + b);
  const front = Math.exp(
    a * Math.log(x) +
    b * Math.log1p(-x) -
    logBeta
  );

  if (x < (a + 1) / (a + b + 2)) {
    return front * betaContinuedFraction(a, b, x) / a;
  }

  return 1 - front * betaContinuedFraction(b, a, 1 - x) / b;
}

function studentTCdf(absT: number, degreesOfFreedom: number): number {
  if (absT === 0) return 0.5;
  const x = degreesOfFreedom / (degreesOfFreedom + absT ** 2);
  const ibeta = regularizedIncompleteBeta(
    x,
    degreesOfFreedom / 2,
    0.5
  );
  return 1 - 0.5 * ibeta;
}

function pairedTTestPValue(differences: number[]): number {
  if (differences.length < 2) return 1;

  const m = mean(differences);
  const variance = sampleVariance(differences);
  if (variance === 0) return m === 0 ? 1 : 0;

  const standardError = Math.sqrt(variance / differences.length);
  const t = Math.abs(m / standardError);
  const df = differences.length - 1;
  const upperTail = 1 - studentTCdf(t, df);
  return Math.max(0, Math.min(1, 2 * upperTail));
}

const targetPairs = analysisPlan.parameters.targetRepetitions;
const baseSeed = 20260929;
const timestamp = new Date().toISOString();
const pairResults: PairResult[] = [];
const durationDifferences: number[] = [];
const thermalDifferences: number[] = [];

for (let i = 1; i <= targetPairs; i++) {
  const pairId = `PAIR-${String(i).padStart(3, '0')}`;
  const pairSeed = baseSeed + i;

  const order = randomizedConditionOrder(pairSeed);

  const firstRun = executeInstrumentedRun({
    runId: `${pairId}-${order[0]}`,
    seed: pairSeed,
    treatment: order[0] === 'TREATMENT',
    timestamp
  });

  const secondRun = executeInstrumentedRun({
    runId: `${pairId}-${order[1]}`,
    seed: pairSeed,
    treatment: order[1] === 'TREATMENT',
    timestamp
  });

  const controlRun =
    order[0] === 'CONTROL' ? firstRun : secondRun;

  const treatmentRun =
    order[0] === 'TREATMENT' ? firstRun : secondRun;

  if (controlRun.treatment !== false) {
    throw new Error(`${pairId}: control observation is not CONTROL`);
  }

  if (treatmentRun.treatment !== true) {
    throw new Error(`${pairId}: treatment observation is not TREATMENT`);
  }

  if (controlRun.seed !== pairSeed || treatmentRun.seed !== pairSeed) {
    throw new Error(`${pairId}: paired observations do not share pair seed`);
  }

const durationDelta = treatmentRun.durationMs - controlRun.durationMs;
  const thermalDiff = treatmentRun.thermalDeltaCelsius - controlRun.thermalDeltaCelsius;
  durationDifferences.push(durationDelta);
  thermalDifferences.push(thermalDiff);

  let classification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
  if (
    Math.abs(durationDelta) > analysisPlan.parameters.effectSizeThresholdDurationMs ||
    Math.abs(thermalDiff) > analysisPlan.parameters.effectSizeThresholdThermalC
  ) {
    classification = 'OBSERVED';
  }

  const payload = JSON.stringify({
    pairId,
    pairSeed,
    conditionOrder: order,
    controlRun,
    treatmentRun,
    durationDelta,
    thermalDiff,
    classification
  });
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

const meanDurationDelta = mean(durationDifferences);
const meanThermalDiff = mean(thermalDifferences);
const pValueDuration = pairedTTestPValue(durationDifferences);
const pValueThermal = pairedTTestPValue(thermalDifferences);
const statisticallySignificant =
  pValueDuration < analysisPlan.parameters.significanceThresholdP ||
  pValueThermal < analysisPlan.parameters.significanceThresholdP;

let campaignClassification: 'NULL_RESULT' | 'OBSERVED' | 'INCONCLUSIVE' = 'NULL_RESULT';
if (
  statisticallySignificant &&
  (
    Math.abs(meanDurationDelta) > analysisPlan.parameters.effectSizeThresholdDurationMs ||
    Math.abs(meanThermalDiff) > analysisPlan.parameters.effectSizeThresholdThermalC
  )
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
    testName: "Paired Student's t-test (two-tailed)",
    design: 'Matched control/treatment observations within each randomized pair',
    pValueDuration: Number(pValueDuration.toFixed(6)),
    pValueThermal: Number(pValueThermal.toFixed(6)),
    statisticallySignificant,
    significanceThresholdP: analysisPlan.parameters.significanceThresholdP
  },
  aggregateAnalysis: {
    meanDurationDeltaMs: Number(meanDurationDelta.toFixed(3)),
    meanThermalDeltaDiffCelsius: Number(meanThermalDiff.toFixed(3)),
    campaignClassification
  }
};

writeFileSync('docs/canonical/STRESS_II_CAMPAIGN_002_REPORT.json', JSON.stringify(campaignReport, null, 2));
console.log('Campaign 002 re-executed with Mulberry32 order randomization.');
