use async_trait::async_trait;

#[derive(Debug, Clone)]
pub struct ChunkVectorPayload {
    pub chunk_key: Hash256,
    pub chunk_id: ChunkId,
    pub seed: u64,
    pub topology_version: u32,
    pub merkle_root: Hash256,
    pub tick: u64,
    pub embedding: Vec<f32>,
}

#[derive(Debug, Clone)]
pub struct ChunkQueryFilter {
    pub min_tick: Option<u64>,
    pub required_topology: Option<u32>,
}

#[derive(Debug, Clone)]
pub struct ChunkQueryResult {
    pub chunk_key: Hash256,
    pub chunk_id: ChunkId,
    pub score: f32,
}

#[async_trait]
pub trait VectorStoreAdapter: Send + Sync {
    async fn upsert_chunk(&self, payload: &ChunkVectorPayload) -> Result<(), String>;
    async fn delete_chunk(&self, chunk_key: &Hash256) -> Result<(), String>;
    async fn query_nearest(
        &self,
        query_vector: &[f32],
        top_k: usize,
        filter: Option<ChunkQueryFilter>,
    ) -> Result<Vec<ChunkQueryResult>, String>;
}