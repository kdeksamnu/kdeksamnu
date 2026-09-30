import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from engine.core.merkle import MerkleArchiveVerifier
from engine.core.persistence import AppendOnlyLedger


def run_harness():
  ledger = AppendOnlyLedger("ash_archive.db")

  # Seed an initial event if ledger is empty to test chain verification
  parent = (
      "0000000000000000000000000000000000000000000000000000000000000000"
  )
  payload = "genesis_anchor_block"
  current = MerkleArchiveVerifier.compute_hash(parent, payload)
  ledger.append_event("event_genesis_harness", payload, parent, current)

  result = MerkleArchiveVerifier.verify_chain("ash_archive.db")
  print(f"[*] Ash Archive Verification Output: {result}")


if __name__ == "__main__":
  run_harness()
