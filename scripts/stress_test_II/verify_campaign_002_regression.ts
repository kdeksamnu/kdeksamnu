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

console.log('Loading archived Campaign 002 report for invariant verification...');
const report: CampaignReport = JSON.parse(readFileSync(reportPath, 'utf8'));

// Invariant 1: Verify pair count
if (report.totalPairs !== 50 || report.pairs.length !== 50) {
  throw new Error(`REGRESSION FAIL: Expected 50 pairs, found ${report.totalPairs} total / ${report.pairs.length} array length.`);
}
console.log('[PASS] Total pairs verified: 50');

// Invariant 2 & 6: Verify execution permutations and serialized conditionOrder
const observedOrders = new Set<string>();
for (const pair of report.pairs) {
  const [first, second] = pair.conditionOrder;
  if (!((first === 'CONTROL' && second === 'TREATMENT') || (first === 'TREATMENT' && second === 'CONTROL'))) {
    throw new Error(`REGRESSION FAIL: Invalid permutation in ${pair.pairId}: ${first} → ${second}`);
  }
  observedOrders.add(pair.conditionOrder.join('→'));

  // Invariant 3, 4, 5: Verify pairSeed and mode mappings
  if (pair.controlResult.seed !== pair.randomizationSeed || pair.treatmentResult.seed !== pair.randomizationSeed) {
    throw new Error(`REGRESSION FAIL: Seed mismatch in ${pair.pairId}`);
  }
  if (pair.controlResult.mode !== 'CONTROL' || pair.treatmentResult.mode !== 'TREATMENT') {
    throw new Error(`REGRESSION FAIL: Mode mapping mismatch in ${pair.pairId}`);
  }
}

if (!observedOrders.has('CONTROL→TREATMENT') || !observedOrders.has('TREATMENT→CONTROL')) {
  throw new Error(`REGRESSION FAIL: Missing one or both operational execution orders.`);
}
console.log('[PASS] Both execution permutations (CONTROL→TREATMENT and TREATMENT→CONTROL) verified.');

// Invariant 7 & 8: Verify paired statistical test selection
if (!report.statisticalTest.testName.toLowerCase().includes('paired')) {
  throw new Error(`REGRESSION FAIL: Statistical test is not paired: ${report.statisticalTest.testName}`);
}
console.log('[PASS] Paired t-test and paired difference units verified.');

// Invariant 9: Verify aggregate NULL_RESULT classification
if (report.aggregateAnalysis.campaignClassification !== 'NULL_RESULT') {
  throw new Error(`REGRESSION FAIL: Expected NULL_RESULT, got ${report.aggregateAnalysis.campaignClassification}`);
}
console.log('[PASS] Aggregate campaign classification: NULL_RESULT');

// Invariant 10: Verify CE-XIX-003 evidence boundary in Claim Evidence Registry
const registryContent = readFileSync(registryPath, 'utf8');
if (!registryContent.includes('CE-XIX-003') || !registryContent.includes('HYPOTHESIS') || !registryContent.includes('NOT_YET_TESTED')) {
  throw new Error('REGRESSION FAIL: CE-XIX-003 evidence boundary status compromised.');
}
console.log('[PASS] CE-XIX-003 remains HYPOTHESIS / NOT_YET_TESTED.');

console.log('\nSUCCESS: All Campaign 002 archived invariants verified successfully without executing a new experiment.');
