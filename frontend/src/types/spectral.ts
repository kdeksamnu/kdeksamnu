export type SpectralConstant =
  | 'gold_joy'
  | 'teal_curiosity'
  | 'blue_sorrow'
  | 'red_anger'
  | 'violet_fear'
  | 'emerald_love'
  | 'bronze_obsidian_null';

export type LogicState = 'True' | 'False' | 'Both' | 'Neither';

export interface SpectralResonanceIngest {
  event_id?: string;
  observer_id: string;
  primary_constant: SpectralConstant;
  secondary_constant?: SpectralConstant | null;
  magnitude: number;
  harmonic_phase?: number;
  topological_continuity?: boolean;
  micro_fracture_detected?: boolean;
}

export interface IngestResponse {
  status: 'integrated' | 'quarantined' | 'rejected';
  event_id: string;
  parent_hash: string;
  current_hash?: string;
  state_hash?: string;
  logic_state?: LogicState;
  harmonic_scar?: boolean;
  somatic_integrity?: number;
}
