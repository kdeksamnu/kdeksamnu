import os
import json
import sqlite3
import hashlib
import time
import concurrent.futures
from typing import Dict, Any, List, Tuple

DB_PATH = "cathedral_ash_archive.db"
CONCURRENT_WORKERS = 8
TRANSACTIONS_PER_WORKER = 250

class AshArchiveBenchmarkEngine:
    """
    High-Throughput Benchmark Engine for Chamber Sigma-12.
    Tests concurrent write throughput, WAL flush performance,
    and Lex I trigger overhead under multi-threaded load.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _initialize_db(self):
        """Ensures strata table and Lex I triggers are active."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ash_strata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                epoch INTEGER NOT NULL,
                branch TEXT NOT NULL,
                node_hash TEXT UNIQUE NOT NULL,
                parents_json TEXT NOT NULL,
                synthesis_merkle_root TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                logical_state TEXT DEFAULT 'NOMINAL',
                wal_sync_timestamp REAL NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_lex_i_update
            BEFORE UPDATE ON ash_strata
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Updates strictly forbidden.');
            END;
            """)
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_lex_i_delete
            BEFORE DELETE ON ash_strata
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Deletions strictly forbidden.');
            END;
            """)
            conn.commit()

    def _worker_task(self, worker_id: int, count: int) -> List[float]:
        """Executes a batch of append operations and records individual latencies."""
        latencies = []
        conn = self._get_connection()
        cursor = conn.cursor()

        for i in range(count):
            start = time.perf_counter()
            node_hash = hashlib.sha256(f"worker_{worker_id}_tx_{i}_{time.time()}".encode()).hexdigest()
            payload = json.dumps({"worker": worker_id, "tx_id": i, "state": "PARACONSISTENT_INGRESS"})
            merkle_root = hashlib.sha256(node_hash.encode()).hexdigest()

            cursor.execute("""
            INSERT INTO ash_strata (
                epoch, branch, node_hash, parents_json,
                synthesis_merkle_root, payload_json, logical_state, wal_sync_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                4, f"worker_branch_{worker_id}", node_hash, "[]",
                merkle_root, payload, "NOMINAL", time.time()
            ))
            conn.commit()
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            latencies.append(elapsed_ms)

        conn.close()
        return latencies

    def execute_benchmark(self) -> Dict[str, Any]:
        """Orchestrates parallel worker threads and gathers execution metrics."""
        total_transactions = CONCURRENT_WORKERS * TRANSACTIONS_PER_WORKER
        print("=================================================================")
        print("      CHAMBER Σ-12 // WAL HIGH-THROUGHPUT STRESS BENCHMARK       ")
        print("=================================================================")
        print(f" Workers          : {CONCURRENT_WORKERS}")
        print(f" Tx per Worker    : {TRANSACTIONS_PER_WORKER}")
        print(f" Total Strata Tx  : {total_transactions}")
        print(" Running concurrent ingestion...")

        overall_start = time.perf_counter()
        all_latencies: List[float] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as executor:
            futures = [
                executor.submit(self._worker_task, w_id, TRANSACTIONS_PER_WORKER)
                for w_id in range(CONCURRENT_WORKERS)
            ]
            for future in concurrent.futures.as_completed(futures):
                all_latencies.extend(future.result())

        total_duration = time.perf_counter() - overall_start
        tps = total_transactions / total_duration

        # Perform post-benchmark WAL checkpoint
        start_flush = time.perf_counter()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            chk = cursor.fetchone()
        flush_ms = (time.perf_counter() - start_flush) * 1000.0

        all_latencies.sort()
        p50 = all_latencies[int(len(all_latencies) * 0.50)]
        p95 = all_latencies[int(len(all_latencies) * 0.95)]
        p99 = all_latencies[int(len(all_latencies) * 0.99)]

        return {
            "total_tx": total_transactions,
            "duration_s": total_duration,
            "tps": tps,
            "p50_ms": p50,
            "p95_ms": p95,
            "p99_ms": p99,
            "flush_ms": flush_ms,
            "wal_busy": chk[0],
            "log_pages": chk[1],
            "checkpointed_pages": chk[2]
        }


if __name__ == "__main__":
    benchmark = AshArchiveBenchmarkEngine()
    metrics = benchmark.execute_benchmark()

    print("\n=================================================================")
    print("                 BENCHMARK PERFORMANCE MANIFEST                  ")
    print("=================================================================")
    print(f" Total Execution Time : {metrics['duration_s']:.3f} s")
    print(f" Write Throughput     : {metrics['tps']:.2f} Transactions/sec")
    print(f" Latency p50          : {metrics['p50_ms']:.3f} ms")
    print(f" Latency p95          : {metrics['p95_ms']:.3f} ms")
    print(f" Latency p99          : {metrics['p99_ms']:.3f} ms")
    print(f" Final WAL Flush      : {metrics['flush_ms']:.2f} ms (Pages: {metrics['checkpointed_pages']})")
    print("=================================================================")
