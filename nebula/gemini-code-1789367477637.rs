use sha2::{Digest, Sha256};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Hash256(pub [u8; 32]);

impl Hash256 {
    pub fn zero() -> Self {
        Self([0u8; 32])
    }

    pub fn digest(data: &[u8]) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(data);
        Self(hasher.finalize().into())
    }

    pub fn combine(left: &Self, right: &Self) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(&left.0);
        hasher.update(&right.0);
        Self(hasher.finalize().into())
    }
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TransactionOp {
    EntitySpawn = 0x01,
    EntityDespawn = 0x02,
    ComponentUpsert = 0x03,
    ComponentRemove = 0x04,
    SpatialBoundarySever = 0x05,
    SpatialBoundaryMerge = 0x06,
    CustomDialetheicState = 0x07,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TransactionLeaf {
    pub tick: u64,
    pub author_id: [u8; 16],
    pub nonce: u64,
    pub op: TransactionOp,
    pub payload_hash: Hash256,
}

impl TransactionLeaf {
    pub fn to_leaf_hash(&self) -> Hash256 {
        let mut bytes = Vec::with_capacity(65);
        bytes.extend_from_slice(&self.tick.to_le_bytes());
        bytes.extend_from_slice(&self.author_id);
        bytes.extend_from_slice(&self.nonce.to_le_bytes());
        bytes.push(self.op as u8);
        bytes.extend_from_slice(&self.payload_hash.0);
        Hash256::digest(&bytes)
    }
}