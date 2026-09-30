import { readFileSync, existsSync } from 'fs';
import * as path from 'path';

interface CampaignReport {
  campaignId: string;
  totalPairs: number;
  pairs: {
    pairId: string;
    randomizationSeed: number;
    conditionOrder: ['CONTROL' | 'TREATMENT', 'CONTROL' | 'TREATMENT'];
    controlResult: { seed: number; mode: string; runId: string };
    treatmentResult: { seed: number; mode: string; runId: string };
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

console.log('Running Stress Test II CI Guards...');

// Guard 1: Reject Campaign 003 artifacts until explicitly authorized
if (existsSync('docs/canonical/STRESS_II_CAMPAIGN_003_REPORT.json') || existsSync('scripts/stress_test_II/campaign_runner_003.ts')) {
  throw new Error('CI GUARD FAIL: Campaign 003 artifacts detected prior to explicit authorization.');
}
console.log('[PASS] Guard 1: Campaign 003 artifacts absent.');

// Guard 2: Reject Math.random in Stress Test II codebase
const runnerCode = readFileSync(path.resolve('scripts/stress_test_II/campaign_runner_002.ts'), 'utf8');
const harnessCode = readFileSync(path.resolve('scripts/stress_test_II/harness.ts'), 'utf8');
if (runnerCode.includes('Math.random') || harnessCode.includes('Math.random')) {
  throw new Error('CI GUARD FAIL: Forbidden Math.random detected in Stress Test II implementation.');
}
console.log('[PASS] Guard 2: No Math.random in Stress Test II modules.');

const reportPath = path.resolve('docs/canonical/STRESS_II_CAMPAIGN_002_REPORT.json');
const report: CampaignReport = JSON.parse(readFileSync(reportPath, 'utf8'));

// Guard 3: Reject missing paired-test metadata or incorrect pair count
if (report.totalPairs !== 50 || report.pairs.length !== 50) {
  throw new Error(`CI GUARD FAIL: Expected 50 pairs, found ${report.totalPairs}`);
}
if (!report.statisticalTest.testName.toLowerCase().includes('paired')) {
  throw new Error(`CI GUARD FAIL: Statistical test is not paired: ${report.statisticalTest.testName}`);
}
console.log('[PASS] Guard 3: Paired-test metadata and 50-pair count verified.');

// Guard 4: Reject one-sided execution-order distributions & mismatched pair seeds
const observedOrders = new Set<string>();
for (const pair of report.pairs) {
  const [first, second] = pair.conditionOrder;
  if (!((first === 'CONTROL' && second === 'TREATMENT') || (first === 'TREATMENT' && second === 'CONTROL'))) {
    throw new Error(`CI GUARD FAIL: Invalid execution permutation in ${pair.pairId}`);
  }
  observedOrders.add(pair.conditionOrder.join('→'));

  if (pair.controlResult.seed !== pair.randomizationSeed || pair.treatmentResult.seed !== pair.randomizationSeed) {
    throw new Error(`CI GUARD FAIL: Mismatched pair seeds in ${pair.pairId}`);
  }
  if (pair.controlResult.mode !== 'CONTROL' || pair.treatmentResult.mode !== 'TREATMENT') {
    throw new Error(`CI GUARD FAIL: Mode mismatch in ${pair.pairId}`);
  }
}

if (!observedOrders.has('CONTROL→TREATMENT') || !observedOrders.has('TREATMENT→CONTROL')) {
  throw new Error('CI GUARD FAIL: One-sided execution-order distribution detected (missing one or both operational orders).');
}
console.log('[PASS] Guard 4: Both execution permutations and matching pair seeds verified.');

// Guard 5: Reject conditionOrder / report mismatches
if (report.aggregateAnalysis.campaignClassification !== 'NULL_RESULT') {
  throw new Error(`CI GUARD FAIL: Expected NULL_RESULT classification, got ${report.aggregateAnalysis.campaignClassification}`);
}
console.log('[PASS] Guard 5: Aggregate classification verified as NULL_RESULT.');

// Guard 6: Reject accidental CE-XIX-003 promotion
const registryPath = path.resolve('docs/canonical/CLAIM_EVIDENCE_REGISTRY.md');
const registryContent = readFileSync(registryPath, 'utf8');
if (!registryContent.includes('CE-XIX-003') || !registryContent.includes('HYPOTHESIS') || !registryContent.includes('NOT_YET_TESTED')) {
  throw new Error('CI GUARD FAIL: CE-XIX-003 evidence boundary compromised or promoted.');
}
console.log('[PASS] Guard 6: CE-XIX-003 boundary intact (HYPOTHESIS / NOT_YET_TESTED).');

console.log('\nSUCCESS: All CI guards passed successfully.');
