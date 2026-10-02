import { z } from 'zod';

export const EpistemicProofSchema = z.object({
  proofId: z.string(),
  subClassification: z.enum(['empirical', 'deductive', 'dialectical', 'paraconsistent']),
  confidence: z.number().min(0).max(1),
  timestamp: z.string(),
});

export const InvocationSchema = z.object({
  id: z.string(),
  title: z.string(),
  tier: z.enum([
    'Discover',
    'Secret',
    'Transform',
    'Instant',
    'Master',
    'Proven',
    'Guaranteed',
    'Exclusive',
    'Effortless',
    'Ultimate',
  ]),
  proof: EpistemicProofSchema.optional(),
  tags: z.array(z.string()),
});

export type EpistemicProof = z.infer<typeof EpistemicProofSchema>;
export type Invocation = z.infer<typeof InvocationSchema>;
