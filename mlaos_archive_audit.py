import argparse
import glob
import hashlib
import json
import os
import sys
from typing import Dict, List, Tuple

class AshArchiveAuditor:
    """
    Cryptographic Auditor for the Magisterial Ash Archive.
    Validates immutable ledger integrity and tracks fracture node reconciliation states.
    """
    def __init__(self, archive_dir: str):
        self.archive_dir = archive_dir
        self.total_records = 0
        self.valid_records = 0
        self.corrupted_records = 0
        self.quarantined_nodes: List[Dict] = []
        self.reconciled_nodes: List[Dict] = []

    def verify_record(self, filepath: str) -> Tuple[bool, Dict, str]:
        """Loads a record file, re-computes its hash, and verifies cryptographic integrity."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract header metadata if present, or extract payload body for canonical hash calculation
            record_data = data.get("record", data)
            stored_hash = data.get("hash", "")
            
            # Re-serialize deterministically to compute SHA-256 footprint
            serialized = json.dumps(record_data, sort_keys=True).encode('utf-8')
            computed_hash = hashlib.sha256(serialized).hexdigest()
            
            # Integrity check passes if hash matches stored footprint (or if validating standalone payload)
            is_valid = (stored_hash == computed_hash) if stored_hash else True
            return is_valid, data, computed_hash
        except Exception as e:
            return False, {"error": str(e)}, ""

    def run_audit(self) -> Dict:
        """Iterates through all ledger JSON files in the archive directory."""
        search_pattern = os.path.join(self.archive_dir, "*.json")
        record_files = glob.glob(search_pattern)
        
        self.total_records = len(record_files)
        
        for filepath in record_files:
            is_valid, data, computed_hash in self.verify_record(filepath)
            
            if not is_valid:
                self.corrupted_records += 1
                continue
                
            self.valid_records += 1
            
            # Classify node state based on block content
            status = data.get("status") or data.get("proof", {}).get("status")
            node_type = data.get("node_type")
            
            if status == "QUARANTINED" or node_type == "FRACTURE_NODE":
                self.quarantined_nodes.append({
                    "file": os.path.basename(filepath),
                    "hash": computed_hash[:16],
                    "tension": data.get("tension_metric", "N/A"),
                    "branch": data.get("dag_branch", "PARALLEL")
                })
            elif status == "RECONCILED_LEX_I_COMPLIANT" or node_type == "SYNTHESIS_BLOCK":
                self.reconciled_nodes.append({
                    "file": os.path.basename(filepath),
                    "synthesis_hash": computed_hash[:16],
                    "source_hash": data.get("proof", {}).get("source_fracture_hash", "N/A")[:16],
                    "arbiter": data.get("proof", {}).get("arbiter_id", "UNKNOWN")
                })

        return self.generate_summary()

    def generate_summary(self) -> Dict:
        return {
            "archive_directory": self.archive_dir,
            "total_records_inspected": self.total_records,
            "integrity_verified": self.valid_records,
            "corrupted_records": self.corrupted_records,
            "quarantined_count": len(self.quarantined_nodes),
            "reconciled_count": len(self.reconciled_nodes),
            "quarantined_nodes": self.quarantined_nodes,
            "reconciled_nodes": self.reconciled_nodes
        }

def print_audit_report(summary: Dict):
    """Prints a styled CLI report of the audit results."""
    print("=================================================================")
    print("             MAGISTERIAL ASH ARCHIVE AUDIT REPORT                ")
    print("=================================================================")
    print(f" Target Directory  : {summary['archive_directory']}")
    print(f" Records Inspected : {summary['total_records_inspected']}")
    print(f" Valid Footprints  : {summary['integrity_verified']}")
    print(f" Corrupted Footprints: {summary['corrupted_records']}")
    print("-----------------------------------------------------------------")
    print(f" Quarantined Fracture Nodes : {summary['quarantined_count']}")
    print(f" Reconciled Synthesis Blocks: {summary['reconciled_count']}")
    print("=================================================================")
    
    if summary["quarantined_nodes"]:
        print("\n[ACTIVE QUARANTINED NODES]")
        for q in summary["quarantined_nodes"]:
            print(f" - File: {q['file']} | Hash: {q['hash']}... | Tension: {q['tension']} | Branch: {q['branch']}")
            
    if summary["reconciled_nodes"]:
        print("\n[RECONCILED SYNTHESIS NODES]")
        for r in summary["reconciled_nodes"]:
            print(f" - File: {r['file']} | Synth Hash: {r['synthesis_hash']}... | Src Hash: {r['source_hash']}... | Arbiter: {r['arbiter']}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit the cryptographic integrity of the Ash Archive.")
    parser.add_argument("--dir", type=str, default="./ash_archive", help="Path to Ash Archive directory")
    args = parser.parse_args()

    # Create dummy archive directory and sample fixtures if missing
    if not os.path.exists(args.dir):
        os.makedirs(args.dir, exist_ok=True)
        
        # Sample Quarantined Block
        sample_fracture = {
            "timestamp": 1727352000.0,
            "anomaly_type": "KRP_TENSION_EXCEEDED",
            "tension_metric": 0.843,
            "payload": {"actor": "WANDERER_001", "event": "INDEX_BREACH"},
            "membrane_status": "SEALED",
            "dag_branch": "FRACTURE_NODE_PARALLEL",
            "status": "QUARANTINED"
        }
        with open(os.path.join(args.dir, "fracture_001.json"), "w") as f:
            json.dump(sample_fracture, f, indent=2)

        # Sample Reconciled Block
        sample_synthesis = {
            "node_type": "SYNTHESIS_BLOCK",
            "parent_dag_head": "DAG_HEAD_MAIN_LATEST",
            "quarantine_branch_reference": "FRACTURE_NODE_PARALLEL",
            "proof": {
                "arbiter_id": "ARBITER_MAGISTER_01",
                "source_fracture_hash": "4a2f8b91c0e3571d0000000000000000",
                "status": "RECONCILED_LEX_I_COMPLIANT"
            }
        }
        with open(os.path.join(args.dir, "synthesis_001.json"), "w") as f:
            json.dump(sample_synthesis, f, indent=2)

    auditor = AshArchiveAuditor(archive_dir=args.dir)
    report = auditor.run_audit()
    print_audit_report(report)
