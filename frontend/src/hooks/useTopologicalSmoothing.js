import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

export function useTopologicalSmoothing(targetState, currentSequenceId) {
  const current = useRef({
    integrity: 1.0, thermal: 0.0, velocity: 0.0, logic: 0.0,
    lastSequenceId: 0
  });

  useFrame((state, delta) => {
    // CHRONOLOGICAL SHIELD: Reject stale or out-of-order packets
    if (targetState.sequence_id <= current.current.lastSequenceId) {
      return; // Ignore desynchronized network jitter
    }
    current.current.lastSequenceId = targetState.sequence_id;

    // TEMPORAL DECOUPLING: Exponential decay smoothing (10.0 = buttery cinematic glide)
    const smoothFactor = 1.0 - Math.exp(-delta * 10.0);

    current.current.integrity += (targetState.somatic_integrity - current.current.integrity) * smoothFactor;
    current.current.thermal += (targetState.thermal_load - current.current.thermal) * smoothFactor;
    current.current.velocity += (targetState.dialetheic_velocity - current.current.velocity) * smoothFactor;
    current.current.logic += (targetState.logic_state_encoded - current.current.logic) * smoothFactor;
  });

  return current.current;
}