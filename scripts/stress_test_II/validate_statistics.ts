import { readFileSync, writeFileSync } from 'fs';

interface CampaignReport {
  campaignId: string;
  totalPairs: number;
  pairs: {
    pairId: string;
    controlResult: { durationMs: number; thermalDeltaCelsius: number };
    treatmentResult: { durationMs: number; thermalDeltaCelsius: number };
  }[];
  statisticalTest: {
    testName: string;
    pValueDuration: number;
    pValueThermal: number;
  };
}

// Student's paired t-test implementation
function calculatePairedTTest(controlValues: number[], treatmentValues: number[]): { tStat: number; pValue: number } {
  const n = controlValues.length;
  const differences: number[] = [];
  for (let i = 0; i < n; i++) {
    differences.push(treatmentValues[i] - controlValues[i]);
  }

  const meanDiff = differences.reduce((a, b) => a + b, 0) / n;
  const varianceDiff = differences.reduce((a, b) => a + Math.pow(b - meanDiff, 2), 0) / (n - 1);
  const se = Math.sqrt(varianceDiff / n);

  if (se === 0) return { tStat: 0, pValue: 1.0 };

  const tStat = meanDiff / se;
  const z = Math.abs(tStat);
  const p = 2 * (1 - cumulativeNormal(z));
  return { tStat: Number(tStat.toFixed(4)), pValue: Number(p.toFixed(6)) };
}

function cumulativeNormal(z: number): number {
  const t = 1 / (1 + 0.2316419 * z);
  const d = 0.319381530;
  const p = 1 - (1 / Math.sqrt(2 * Math.PI)) * Math.exp(-z * z / 2) * 
    (t * (d + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429)))));
  return p;
}

const rawReport = readFileSync('docs/canonical/STRESS_II_CAMPAIGN_002_REPORT.json', 'utf8');
const campaign: CampaignReport = JSON.parse(rawReport);

const controlDurations = campaign.pairs.map(p => p.controlResult.durationMs);
const treatmentDurations = campaign.pairs.map(p => p.treatmentResult.durationMs);
const controlThermals = campaign.pairs.map(p => p.controlResult.thermalDeltaCelsius);
const treatmentThermals = campaign.pairs.map(p => p.treatmentResult.thermalDeltaCelsius);

const pairedDuration = calculatePairedTTest(controlDurations, treatmentDurations);
const pairedThermal = calculatePairedTTest(controlThermals, treatmentThermals);

const validationResult = {
  validatedAt: new Date().toISOString(),
  targetCampaign: campaign.campaignId,
  designCheck: 'Paired randomized control/treatment design requires a Paired t-test (evaluating within-pair differences) rather than an unpaired Two-Sample t-test.',
  previousUnpaired: {
    pValueDuration: campaign.statisticalTest.pValueDuration,
    pValueThermal: campaign.statisticalTest.pValueThermal
  },
  correctedPaired: {
    testName: 'Student’s Paired t-test (Two-Tailed)',
    pValueDuration: pairedDuration.pValue,
    tStatDuration: pairedDuration.tStat,
    pValueThermal: pairedThermal.pValue,
    tStatThermal: pairedThermal.tStat
  }
};

writeFileSync('docs/canonical/STRESS_II_CAMPAIGN_002_VALIDATION.json', JSON.stringify(validationResult, null, 2));
console.log(JSON.stringify(validationResult, null, 2));
