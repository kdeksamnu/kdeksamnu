#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DagCommitNode {
    pub commit_id: Hash256,
    pub parent_commit_ids: Vec<Hash256>, // Single parent for linear ticks, multiple for merges
    pub tick: u64,
    pub author_id: [u8; 16],
    pub transaction_merkle_root: Hash256,
    pub state_snapshot_root: Hash256,
}

impl DagCommitNode {
    pub fn new(
        parents: Vec<Hash256>,
        tick: u64,
        author_id: [u8; 16],
        tx_root: Hash256,
        state_root: Hash256,
    ) -> Self {
        let mut hasher = Sha256::new();
        for p in &parents {
            hasher.update(&p.0);
        }
        hasher.update(&tick.to_le_bytes());
        hasher.update(&author_id);
        hasher.update(&tx_root.0);
        hasher.update(&state_root.0);

        Self {
            commit_id: Hash256(hasher.finalize().into()),
            parent_commit_ids: parents,
            tick,
            author_id,
            transaction_merkle_root: tx_root,
            state_snapshot_root: state_root,
        }
    }
}

pub struct RollbackReconciler;

impl RollbackReconciler {
    /// Reconciles speculative client state against authoritative canonical root
    /// without pruning or deleting historical leaves.
    pub fn reconcile_divergence(
        common_ancestor: &DagCommitNode,
        canonical_server_commit: &DagCommitNode,
        speculative_client_commit: &DagCommitNode,
        compensating_txs: Vec<TransactionLeaf>,
    ) -> DagCommitNode {
        let mut tx_ledger = MerkleTransactionLedger::new();
        for tx in &compensating_txs {
            tx_ledger.append(tx);
        }

        // Emit a merge commit referencing both parents
        DagCommitNode::new(
            vec![
                canonical_server_commit.commit_id,
                speculative_client_commit.commit_id,
            ],
            canonical_server_commit.tick + 1,
            canonical_server_commit.author_id,
            tx_ledger.root(),
            canonical_server_commit.state_snapshot_root,
        )
    }
}