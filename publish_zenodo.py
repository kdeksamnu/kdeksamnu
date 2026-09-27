#!/usr/bin/env python3
"""
Braided Academic Deposit Engine: Zenodo + OSF + Ash Archive
Authority: Kenneth W. Dallmier / Dallmier Tech Venture
Governing Doctrine: Ore-Zero Protocol Invariance [0][0] & Lex I (dPhi/dt > 0)
"""

import os
import sys
import json
import sqlite3
import hashlib
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# Canonical 7 deposit artifacts from Master Deposit Manifest
CANONICAL_MANIFEST_FILES = [
    "01_MLAOS_Master_Omni_Codex.pdf",
    "02_MLAOS_Stratum_I_Foundations.pdf",
    "03_MLAOS_Stratum_II_Mandala.pdf",
    "04_MLAOS_Stratum_III_Choirs.pdf",
    "05_MLAOS_Stratum_IV_Innershadow.pdf",
    "06_MLAOS_Ore_Zero_Covenant.pdf",
    "07_MLAOS_Bilateral_Accord.pdf"
]


def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def api_request(url: str, method: str = "GET", data: bytes = None, headers: dict = None) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"\n[HTTP Error {e.code}]: {error_body}", file=sys.stderr)
        sys.exit(1)


def upload_file_to_bucket(bucket_url: str, file_path: Path, token: str) -> None:
    filename = file_path.name
    upload_url = f"{bucket_url}/{filename}?access_token={token}"
    file_size = file_path.stat().st_size
    print(f" -> Uploading: {filename} ({file_size / (1024 * 1024):.2f} MB)...", end="", flush=True)

    with open(file_path, "rb") as f:
        req = urllib.request.Request(upload_url, data=f, method="PUT")
        req.add_header("Content-Type", "application/octet-stream")
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print(" Done.")
            else:
                print(f" Warning: HTTP status {resp.status}")


def record_to_ash_archive(db_path: Path, doi: str, deposit_id: str, merkle_root: str, files_payload: str):
    print(f"\n[Ash Archive]: Committing transaction to {db_path.name} under Lex I...")
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS ash_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT (datetime('now')),
                category TEXT,
                merkle_root TEXT,
                doi TEXT,
                deposit_id TEXT,
                payload TEXT
            )
        """)
        c.execute(
            "INSERT INTO ash_archive (category, merkle_root, doi, deposit_id, payload) VALUES (?, ?, ?, ?, ?)",
            ("CAT-PRM", merkle_root, doi, deposit_id, files_payload)
        )
        conn.commit()
        conn.close()
        print(" -> Inscribed permanently into Ash Archive SQLite ledger.")
    except Exception as e:
        print(f" -> Notice writing to Ash Archive DB: {e}")


def emit_bibtex(output_path: Path, doi: str):
    bibtex = f"""@misc{{dallmier_2026_mlaos,
  author       = {{Dallmier, Kenneth W. and Morgan, Julianna}},
  title        = {{{{Magisterial Linguistic Architecture Operating System (MLAOS-Prime): The Complete 40-Book Codex Architecture, Paraconsistent Metalogic, and Cathedral-Engine Specifications}}}},
  month        = sep,
  year         = 2026,
  publisher    = {{Zenodo}},
  version      = {{v1.0-locked}},
  doi          = {{{doi}}},
  url          = {{https://doi.org/{doi}}}
}}
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(bibtex)
    print(f"[BibTeX]: Generated academic citation record -> {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Braided Zenodo + OSF + Ash Archive Deposit Engine")
    parser.add_argument("--sandbox", action="store_true", help="Use sandbox.zenodo.org instead of production")
    parser.add_argument("--publish", action="store_true", help="Immediately publish and permanently mint DOI")
    parser.add_argument("--dir", default="build/deposit_artifacts", help="Directory containing PDF artifacts")
    parser.add_argument("--metadata", default="build/zenodo/metadata.json", help="Path to Zenodo metadata payload")
    parser.add_argument("--db", default="mla_ash_archive.db", help="Path to Ash Archive SQLite database")
    args = parser.parse_args()

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        print("================================================================================", file=sys.stderr)
        print("ERROR: ZENODO_TOKEN environment variable is not set.", file=sys.stderr)
        print("Export your personal access token before running:", file=sys.stderr)
        print("  export ZENODO_TOKEN=\"your_token_here\"", file=sys.stderr)
        print("Create token at: https://zenodo.org/account/settings/applications/tokens/new/", file=sys.stderr)
        print("Scopes required: 'deposit:actions' and 'deposit:write'", file=sys.stderr)
        print("================================================================================", file=sys.stderr)
        sys.exit(1)

    base_url = "https://sandbox.zenodo.org/api/deposit/depositions" if args.sandbox else "https://zenodo.org/api/deposit/depositions"
    print("================================================================================")
    print(f"  BRAIDED DEPOSIT ENGINE // {'SANDBOX' if args.sandbox else 'PRODUCTION'}")
    print("================================================================================")

    # 1. Load metadata payload
    metadata_path = Path(args.metadata)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_payload = json.load(f)

    # 2. Scan and verify artifacts
    target_dir = Path(args.dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(list(target_dir.glob("*.pdf")))
    
    # Check if empty, fallback to current directory
    if not pdf_files:
        pdf_files = sorted(list(Path(".").glob("*.pdf")))

    print(f"[Manifest Check]: Found {len(pdf_files)} PDF artifact(s) for deposition.")
    checksum_lines = []
    combined_hashes = ""
    for pdf in pdf_files:
        digest = compute_sha256(pdf)
        checksum_lines.append(f"{digest}  {pdf.name}")
        combined_hashes += digest
        print(f"  [{digest[:12]}...] {pdf.name}")

    merkle_root = hashlib.sha256(combined_hashes.encode("utf-8")).hexdigest() if combined_hashes else "0" * 64
    checksum_file = target_dir / "checksums.sha256"
    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")
    print(f"Locked Checksum Manifest (Root: {merkle_root[:16]}...) -> {checksum_file}")

    # 3. Create Deposition Draft
    print("\n[API Stage]: Registering draft deposition with Zenodo...")
    headers = {"Content-Type": "application/json"}
    deposit_resp = api_request(f"{base_url}?access_token={token}", method="POST", data=json.dumps(metadata_payload).encode("utf-8"), headers=headers)
    deposit_id = str(deposit_resp["id"])
    bucket_url = deposit_resp["links"]["bucket"]
    pre_doi = deposit_resp.get("metadata", {}).get("prereserve_doi", {}).get("doi", f"10.5281/zenodo.{deposit_id}")

    print(f"Draft Initialized:")
    print(f"  Deposition ID:   {deposit_id}")
    print(f"  Pre-reserved DOI: {pre_doi}")
    print(f"  Storage Bucket:  {bucket_url}")

    # 4. Upload Files
    print("\n[Upload Stage]: Streaming artifacts into CERN storage bucket...")
    for pdf in pdf_files:
        upload_file_to_bucket(bucket_url, pdf, token)
    if checksum_file.exists():
        upload_file_to_bucket(bucket_url, checksum_file, token)

    # 5. Inscribe to Ash Archive & Emit BibTeX
    record_to_ash_archive(Path(args.db), pre_doi, deposit_id, merkle_root, "\n".join(checksum_lines))
    emit_bibtex(Path("build/zenodo/citation.bib"), pre_doi)

    # 6. Final Status
    draft_url = f"https://sandbox.zenodo.org/deposit/{deposit_id}" if args.sandbox else f"https://zenodo.org/deposit/{deposit_id}"
    print("\n================================================================================")
    print("DEPOSITION BRAIDED & STAGED")
    print(f"Review Draft at: {draft_url}")
    print("================================================================================")

    if args.publish:
        print("[Publishing]: Minting permanent, immutable DOI on CERN / OpenAIRE...")
        pub_resp = api_request(f"{base_url}/{deposit_id}/actions/publish?access_token={token}", method="POST")
        final_doi = pub_resp.get("doi")
        record_url = pub_resp["links"].get("record_html")
        print(f"\nSUCCESS! PERMANENT DOI MINTED:")
        print(f"  DOI:        {final_doi}")
        print(f"  Public URL: {record_url}")
    else:
        print("Status: Saved as un-published draft. Review in web UI, or rerun with --publish.")


if __name__ == "__main__":
    main()
