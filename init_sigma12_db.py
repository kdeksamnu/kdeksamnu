import sqlite3

def deploy_schema():
    conn = sqlite3.connect("cathedral_engine_sigma12.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    schema_sql = """
    CREATE TABLE IF NOT EXISTS ash_nodes (
        node_hash TEXT PRIMARY KEY,
        branch_name TEXT NOT NULL,
        epoch INTEGER NOT NULL,
        merkle_root TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS ash_dag_edges (
        parent_hash TEXT NOT NULL,
        child_hash TEXT NOT NULL,
        edge_type TEXT DEFAULT 'branch',
        PRIMARY KEY (parent_hash, child_hash),
        FOREIGN KEY (parent_hash) REFERENCES ash_nodes(node_hash),
        FOREIGN KEY (child_hash) REFERENCES ash_nodes(node_hash)
    );

    CREATE TABLE IF NOT EXISTS ash_transactions (
        tx_hash TEXT PRIMARY KEY,
        node_hash TEXT NOT NULL,
        leaf_index INTEGER NOT NULL,
        payload_json TEXT NOT NULL,
        FOREIGN KEY (node_hash) REFERENCES ash_nodes(node_hash)
    );

    CREATE INDEX IF NOT EXISTS idx_dag_edges_parent ON ash_dag_edges(parent_hash);
    CREATE INDEX IF NOT EXISTS idx_dag_edges_child ON ash_dag_edges(child_hash);
    CREATE INDEX IF NOT EXISTS idx_transactions_node ON ash_transactions(node_hash);

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_nodes_no_update
    BEFORE UPDATE ON ash_nodes BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes are strictly immutable.');
    END;

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_nodes_no_delete
    BEFORE DELETE ON ash_nodes BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes cannot be purged.');
    END;

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_dag_edges_no_update
    BEFORE UPDATE ON ash_dag_edges BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: DAG lineage edges are strictly immutable.');
    END;

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_dag_edges_no_delete
    BEFORE DELETE ON ash_dag_edges BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: DAG lineage edges cannot be purged.');
    END;

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_tx_no_update
    BEFORE UPDATE ON ash_transactions BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: Archive transactions are strictly immutable.');
    END;

    CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_tx_no_delete
    BEFORE DELETE ON ash_transactions BEGIN
        SELECT RAISE(ABORT, 'Violation of Lex I: Archive transactions cannot be purged.');
    END;
    """
    
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("[CHAMBER Σ-12] Ash Archive Merkle DAG schema deployed successfully under Lex I governance.")

if __name__ == "__main__":
    deploy_schema()
