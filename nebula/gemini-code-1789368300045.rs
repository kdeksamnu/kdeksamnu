use crate::cathedral_ledger::Hash256;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub struct SpatialCoordinates {
    pub position: [f32; 3],
    pub extent: [f32; 3],
}

#[derive(Debug, Clone, PartialEq)]
pub struct DialetheicSpatialVolume {
    pub entity_id: u64,
    pub truth_state: BelnapTruth,
    pub shard_a_assertion: SpatialCoordinates,
    pub shard_b_assertion: Option<SpatialCoordinates>,
    pub superposition_epoch: u64,
}

pub struct DialetheicBuffer {
    active_incontradictions: HashMap<u64, DialetheicSpatialVolume>,
}

impl DialetheicBuffer {
    pub fn new() -> Self {
        Self {
            active_incontradictions: HashMap::new(),
        }
    }

    /// Registers a spatial state conflict between Shard A and Shard B.
    pub fn register_conflict(
        &mut self,
        entity_id: u64,
        epoch: u64,
        coord_a: SpatialCoordinates,
        coord_b: Option<SpatialCoordinates>,
    ) -> &DialetheicSpatialVolume {
        let truth = match coord_b {
            Some(_) => BelnapTruth::Both,
            None => BelnapTruth::True,
        };

        let volume = DialetheicSpatialVolume {
            entity_id,
            truth_state: truth,
            shard_a_assertion: coord_a,
            shard_b_assertion: coord_b,
            superposition_epoch: epoch,
        };

        self.active_incontradictions.insert(entity_id, volume);
        self.active_incontradictions.get(&entity_id).unwrap()
    }

    /// Drains contradictions that have reached the epoch boundary for Merkle DAG sealing.
    pub fn drain_epoch_incontradictions(&mut self, epoch: u64) -> Vec<DialetheicSpatialVolume> {
        let mut ready = Vec::new();
        let keys: Vec<u64> = self.active_incontradictions
            .iter()
            .filter(|(_, v)| v.superposition_epoch <= epoch)
            .map(|(k, _)| *k)
            .collect();

        for key in keys {
            if let Some(v) = self.active_incontradictions.remove(&key) {
                ready.push(v);
            }
        }
        ready
    }
}