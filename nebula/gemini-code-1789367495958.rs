#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum AuditDirection {
    Left,
    Right,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuditStep {
    pub direction: AuditDirection,
    pub sibling_hash: Hash256,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MerkleProof {
    pub leaf_index: usize,
    pub audit_path: Vec<AuditStep>,
}

impl MerkleProof {
    pub fn verify(&self, leaf_hash: &Hash256, expected_root: &Hash256) -> bool {
        let mut current = *leaf_hash;
        for step in &self.audit_path {
            match step.direction {
                AuditDirection::Left => {
                    current = Hash256::combine(&step.sibling_hash, &current);
                }
                AuditDirection::Right => {
                    current = Hash256::combine(&current, &step.sibling_hash);
                }
            }
        }
        current == *expected_root
    }
}

pub struct MerkleTransactionLedger {
    leaves: Vec<Hash256>,
    cached_root: Hash256,
}

impl MerkleTransactionLedger {
    pub fn new() -> Self {
        Self {
            leaves: Vec::new(),
            cached_root: Hash256::zero(),
        }
    }

    pub fn append(&mut self, leaf: &TransactionLeaf) -> (usize, Hash256) {
        let leaf_hash = leaf.to_leaf_hash();
        self.leaves.push(leaf_hash);
        self.cached_root = self.compute_root();
        (self.leaves.len() - 1, self.cached_root)
    }

    pub fn root(&self) -> Hash256 {
        self.cached_root
    }

    pub fn compute_root(&self) -> Hash256 {
        if self.leaves.is_empty() {
            return Hash256::zero();
        }
        let mut current_layer = self.leaves.clone();
        while current_layer.len() > 1 {
            let mut next_layer = Vec::with_capacity((current_layer.len() + 1) / 2);
            for chunk in current_layer.chunks(2) {
                if chunk.len() == 2 {
                    next_layer.push(Hash256::combine(&chunk[0], &chunk[1]));
                } else {
                    next_layer.push(Hash256::combine(&chunk[0], &chunk[0]));
                }
            }
            current_layer = next_layer;
        }
        current_layer[0]
    }

    pub fn generate_proof(&self, leaf_index: usize) -> Option<MerkleProof> {
        if leaf_index >= self.leaves.len() {
            return None;
        }

        let mut layers = Vec::new();
        layers.push(self.leaves.clone());

        while layers.last().unwrap().len() > 1 {
            let current = layers.last().unwrap();
            let mut next = Vec::with_capacity((current.len() + 1) / 2);
            for chunk in current.chunks(2) {
                if chunk.len() == 2 {
                    next.push(Hash256::combine(&chunk[0], &chunk[1]));
                } else {
                    next.push(Hash256::combine(&chunk[0], &chunk[0]));
                }
            }
            layers.push(next);
        }

        let mut proof_steps = Vec::new();
        let mut current_idx = leaf_index;

        for layer in layers.iter().take(layers.len() - 1) {
            let is_right_child = (current_idx % 2) == 1;
            let sibling_idx = if is_right_child {
                current_idx - 1
            } else {
                current_idx + 1
            };

            let sibling_hash = if sibling_idx < layer.len() {
                layer[sibling_idx]
            } else {
                layer[current_idx]
            };

            let direction = if is_right_child {
                AuditDirection::Left
            } else {
                AuditDirection::Right
            };

            proof_steps.push(AuditStep {
                direction,
                sibling_hash,
            });

            current_idx /= 2;
        }

        Some(MerkleProof {
            leaf_index,
            audit_path: proof_steps,
        })
    }
}