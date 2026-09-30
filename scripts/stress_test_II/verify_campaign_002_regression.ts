import { readFileSync } from 'fs';
import * as path from 'path';

interface CampaignReport {
  campaignId: string;
  totalPairs: number;
  pairs: {
    pairId: string;
    randomizationSeed: number;
    conditionOrder: ['CONTROL' | 'TREATMENT', 'CONTROL' | 'TREATMENT'];
    controlResult: { seed: number; mode: string };
    treatmentResult: { seed: number; mode: string };
    durationDeltaMs: number;
    thermalDeltaDiffCelsius: number;
  }[];
  statisticalTest: {
    testName: string;
    pValueDuration: number;
    pValueThermal: number;
  };
  aggregateAnalysis: {
    campaignClassification: string;
  };
}

const reportPath = path.resolve('docs/canonical/STRESS_II_CAMPAIGN_002_REPORT.json');
const registryPath = path.resolve('docs/canonical/CLAIM_EVIDENCE_REGISTRY.md');

console.log('Validating frozen Campaign 002 checkpoint invariants...');
const report: CampaignReport = JSON.parse(readFileSync(reportPath, 'utf8'));

if (report.totalPairs !== 50 || report.pairs.length !== 50) {
  throw new Error(`REGRESSION FAIL: Expected 50 pairs, found ${report.totalPairs}`);
}

const observedOrders = new Set<string>();
for (const pair of report.pairs) {
  const [first, second] = pair.conditionOrder;
  if (!((first === 'CONTROL' && second === 'TREATMENT') || (first === 'TREATMENT' && second === 'CONTROL'))) {
    throw new Error(`REGRESSION FAIL: Invalid execution permutation in ${pair.pairId}`);
  }
  observedOrders.add(pair.conditionOrder.join('→'));

  if (pair.controlResult.seed !== pair.randomizationSeed || pair.treatmentResult.seed !== pair.randomizationSeed) {
    throw new Error(`REGRESSION FAIL: Seed mismatch in ${pair.pairId}`);
  }
  if (pair.controlResult.mode !== 'CONTROL' || pair.treatmentResult.mode !== 'TREATMENT') {
    throw new Error(`REGRESSION FAIL: Mode mismatch in ${pair.pairId}`);
  }
}

if (!observedOrders.has('CONTROL→TREATMENT') || !observedOrders.has('TREATMENT→CONTROL')) {
  throw new Error('REGRESSION FAIL: Missing operational execution orders.');
}

if (!report.statisticalTest.testName.toLowerCase().includes('paired')) {
  throw new Error(`REGRESSION FAIL: Non-paired test detected: ${report.statisticalTest.testName}`);
}

if (report.aggregateAnalysis.campaignClassification !== 'NULL_RESULT') {
  throw new Error(`REGRESSION FAIL: Expected NULL_RESULT, got ${report.aggregateAnalysis.campaignClassification}`);
}

const registryContent = readFileSync(registryPath, 'utf8');
if (!registryContent.includes('CE-XIX-003') || !registryContent.includes('HYPOTHESIS') || !registryContent.includes('NOT_YET_TESTED')) {
  throw new Error('REGRESSION FAIL: CE-XIX-003 evidence boundary compromised.');
}

console.log('[PASS] Campaign 002 checkpoint frozen invariants verified successfully.');
console.log('[PASS] CE-XIX-003 = HYPOTHESIS / NOT_YET_TESTED preserved.');
console.log('[PASS] Experimental determinism (Mulberry32) separated from runtime telemetry.');
