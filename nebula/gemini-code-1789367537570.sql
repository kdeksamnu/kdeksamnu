-- Append-Only Transaction Log
CREATE TABLE IF NOT EXISTS ledger_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tick BIGINT NOT NULL,
    author_id BLOB NOT NULL,          -- 16-byte UUID / ID
    nonce BIGINT NOT NULL,
    op_code SMALLINT NOT NULL,
    payload_hash BLOB NOT NULL,       -- 32-byte SHA-256
    leaf_hash BLOB NOT NULL UNIQUE,   -- 32-byte SHA-256
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ledger_tx_tick ON ledger_transactions(tick);

-- Append-Only DAG Commit Nodes
CREATE TABLE IF NOT EXISTS dag_commits (
    commit_id BLOB PRIMARY KEY,       -- 32-byte SHA-256
    tick BIGINT NOT NULL,
    author_id BLOB NOT NULL,
    tx_merkle_root BLOB NOT NULL,
    state_snapshot_root BLOB NOT NULL,
    is_canonical BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Multi-parent DAG Linkages (enabling non-destructive branching & merges)
CREATE TABLE IF NOT EXISTS dag_commit_parents (
    child_commit_id BLOB NOT NULL,
    parent_commit_id BLOB NOT NULL,
    parent_order INT DEFAULT 0,
    PRIMARY KEY (child_commit_id, parent_commit_id),
    FOREIGN KEY (child_commit_id) REFERENCES dag_commits(commit_id)
);