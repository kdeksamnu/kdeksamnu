use crate::cathedral_ledger::Hash256;
use sha2::{Digest, Sha256};
use std::collections::{BTreeMap, HashMap};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct ChunkId(pub [i32; 3]);

pub struct CompositeChunkKeyGenerator;

impl CompositeChunkKeyGenerator {
    pub fn compute_key(
        seed: u64,
        topology_version: u32,
        entity_hashes: impl IntoIterator<Item = Hash256>,
    ) -> Hash256 {
        let mut sum_accum = [0u64; 4];
        for hash in entity_hashes {
            for i in 0..4 {
                let start = i * 8;
                let limb = u64::from_le_bytes(hash.0[start..start + 8].try_into().unwrap());
                sum_accum[i] = sum_accum[i].wrapping_add(limb);
            }
        }

        let mut sum_bytes = [0u8; 32];
        for (i, val) in sum_accum.iter().enumerate() {
            sum_bytes[i * 8..(i + 1) * 8].copy_from_slice(&val.to_le_bytes());
        }

        let mut hasher = Sha256::new();
        hasher.update(&seed.to_le_bytes());
        hasher.update(&topology_version.to_le_bytes());
        hasher.update(&sum_bytes);

        Hash256(hasher.finalize().into())
    }
}