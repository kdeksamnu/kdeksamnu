use async_trait::async_trait;

#[async_trait]
pub trait LedgerStorage: Send + Sync {
    async fn append_transaction_leaf(&self, leaf: &TransactionLeaf) -> Result<u64, String>;
    async fn commit_dag_node(&self, node: &DagCommitNode) -> Result<(), String>;
    async fn get_dag_node(&self, commit_id: &Hash256) -> Result<Option<DagCommitNode>, String>;
    async fn get_latest_canonical_commit(&self) -> Result<Option<DagCommitNode>, String>;
}