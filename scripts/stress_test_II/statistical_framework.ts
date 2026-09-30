import { writeFileSync } from 'fs';

interface StatisticalAnalysisPlan {
  version: string;
  timestamp: string;
  parameters: {
    targetRepetitions: number;
    significanceThresholdP: number;
    effectSizeThresholdDurationMs: number;
    effectSizeThresholdThermalC: number;
  };
  randomizedExecutionProtocol: string;
}

const plan: StatisticalAnalysisPlan = {
  version: '1.0.0-frozen',
  timestamp: new Date().toISOString(),
  parameters: {
    targetRepetitions: 50,
    significanceThresholdP: 0.01,
    effectSizeThresholdDurationMs: 25.0,
    effectSizeThresholdThermalC: 0.50
  },
  randomizedExecutionProtocol: 'Condition order (Control vs Treatment) must be randomized per run pair using a seeded PRNG to eliminate temporal drift confounds, with execution strictly reflecting the randomized order.'
};

writeFileSync('docs/canonical/STATISTICAL_ANALYSIS_PLAN.json', JSON.stringify(plan, null, 2));
console.log('Statistical analysis framework generator corrected (STATISTICAL_ANALYSIS_PLAN.json).');
