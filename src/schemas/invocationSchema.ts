import { z } from 'zod';

export const EpistemicSubClassificationSchema = z.enum([
  'Empirical',
  'Somatic',
  'Architectonic',
  'Dialetheic',
  'Isomorphic',
]);

export const EpistemicProofSchema = z.object({
  subClassification: EpistemicSubClassificationSchema,
  statement: z.string().min(10, 'Proof statement must be substantiated'),
  harmonicIndex: z.string().optional(),
});

export const InvocationSchema = z.object({
  number: z.number().int().min(1).max(10),
  title: z.string().min(1),
  word: z.string().min(1),
  stage: z.enum(['Preparation', 'Invocation', 'Attunement', 'Crystallization', 'Integration']),
  mechanism: z.string().min(1),
  condition: z.string().min(1),
  failureMode: z.string().min(1),
  hiddenCost: z.string().min(1),
  dialetheicPair: z.object({
    thesis: z.string().min(1),
    antithesis: z.string().min(1),
  }),
  resolution: z.string().min(1),
  biologicalProof: EpistemicProofSchema,
  architecturalProof: EpistemicProofSchema,
});
