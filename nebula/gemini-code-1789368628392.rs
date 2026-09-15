use crate::cathedral_ledger::{DagCommitNode, TransactionLeaf, TransactionOp};

pub struct ChunkEntry {
    pub seed: u64,
    pub topology_version: u32,
    pub current_key: Hash256,
    pub entities: BTreeMap<u64, Hash256>, // entity_id -> entity_state_hash
}

pub struct ChunkCacheManager {
    chunks: HashMap<ChunkId, ChunkEntry>,
    entity_to_chunk: HashMap<u64, ChunkId>,
}

impl ChunkCacheManager {
    pub fn new() -> Self {
        Self {
            chunks: HashMap::new(),
            entity_to_chunk: HashMap::new(),
        }
    }

    /// Associates an entity with a spatial chunk
    pub fn register_entity(&mut self, entity_id: u64, chunk_id: ChunkId, initial_hash: Hash256) {
        self.entity_to_chunk.insert(entity_id, chunk_id);
        let entry = self.chunks.entry(chunk_id).or_insert_with(|| ChunkEntry {
            seed: 0,
            topology_version: 1,
            current_key: Hash256::zero(),
            entities: BTreeMap::new(),
        });
        entry.entities.insert(entity_id, initial_hash);
    }

    /// Intercepts a committed Merkle DAG node and invalidates modified chunks
    pub fn process_commit(
        &mut self,
        commit: &DagCommitNode,
        mutated_txs: &[TransactionLeaf],
    ) -> Vec<(ChunkId, Hash256, Hash256)> {
        let mut dirty_chunks = HashMap::new();

        for tx in mutated_txs {
            // Extract entity ID from nonce/author or payload mapping
            let entity_id = tx.nonce;
            if let Some(&chunk_id) = self.entity_to_chunk.get(&entity_id) {
                dirty_chunks.insert(chunk_id, ());
                if let Some(entry) = self.chunks.get_mut(&chunk_id) {
                    match tx.op {
                        TransactionOp::EntityDespawn => {
                            entry.entities.remove(&entity_id);
                        }
                        TransactionOp::ComponentUpsert | TransactionOp::EntitySpawn => {
                            entry.entities.insert(entity_id, tx.payload_hash);
                        }
                        _ => {}
                    }
                }
            }
        }

        // Recompute keys for dirty chunks and emit invalidation events
        let mut invalidations = Vec::new();
        for chunk_id in dirty_chunks.keys() {
            if let Some(entry) = self.chunks.get_mut(chunk_id) {
                let new_key = CompositeChunkKeyGenerator::compute_key(
                    entry.seed,
                    entry.topology_version,
                    entry.entities.values().cloned(),
                );

                if new_key != entry.current_key {
                    let old_key = entry.current_key;
                    entry.current_key = new_key;
                    invalidations.push((*chunk_id, old_key, new_key));
                }
            }
        }

        invalidations
    }

    /// Procedural Seed Mutation Hook
    pub fn update_chunk_seed(&mut self, chunk_id: ChunkId, new_seed: u64) -> Option<(Hash256, Hash256)> {
        if let Some(entry) = self.chunks.get_mut(&chunk_id) {
            let old_key = entry.current_key;
            entry.seed = new_seed;
            entry.current_key = CompositeChunkKeyGenerator::compute_key(
                entry.seed,
                entry.topology_version,
                entry.entities.values().cloned(),
            );
            Some((old_key, entry.current_key))
        } else {
            None
        }
    }

    /// Topology Bump Hook (e.g., destructive CSG terrain edits or biome transitions)
    pub fn bump_topology_version(&mut self, chunk_id: ChunkId) -> Option<(Hash256, Hash256)> {
        if let Some(entry) = self.chunks.get_mut(&chunk_id) {
            let old_key = entry.current_key;
            entry.topology_version += 1;
            entry.current_key = CompositeChunkKeyGenerator::compute_key(
                entry.seed,
                entry.topology_version,
                entry.entities.values().cloned(),
            );
            Some((old_key, entry.current_key))
        } else {
            None
        }
    }
}