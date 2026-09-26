#!/usr/bin/env python3
"""
Zenodo Automated Deposit & DOI Minting Script
Authority: Kenneth W. Dallmier / Dallmier Tech Venture
Target: 40-Book Codex Architecture & Cathedral-Engine Specifications
"""

import os
import sys
import json
import hashlib
import argparse
import urllib.request
import urllib.error
from pathlib import Path


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


def main():
    parser = argparse.ArgumentParser(description="Automated Zenodo DOI Deposit for MLAOS-Prime")
    parser.add_argument("--sandbox", action="store_true", help="Use sandbox.zenodo.org instead of production")
    parser.add_argument("--publish", action="store_true", help="Immediately publish and permanently mint DOI")
    parser.add_argument("--dir", default=".", help="Directory containing PDF artifacts to deposit")
    parser.add_argument("--metadata", default="build/zenodo/metadata.json", help="Path to metadata payload JSON")
    args = parser.parse_args()

    token = os.environ.get("ZENODO_TOKEN")
    if not token:
        print("================================================================================", file=sys.stderr)
        print("ERROR: ZENODO_TOKEN environment variable is not set.", file=sys.stderr)
        print("Export your personal access token before running:", file=sys.stderr)
        print("  export ZENODO_TOKEN=\"your_token_here\"", file=sys.stderr)
        print("Generate token at: https://zenodo.org/account/settings/applications/tokens/new/", file=sys.stderr)
        print("Scopes required: 'deposit:actions' and 'deposit:write'", file=sys.stderr)
        print("================================================================================", file=sys.stderr)
        sys.exit(1)

    base_url = "https://sandbox.zenodo.org/api/deposit/depositions" if args.sandbox else "https://zenodo.org/api/deposit/depositions"
    print(f"[Zenodo Client]: Operating against {'SANDBOX' if args.sandbox else 'PRODUCTION'}: {base_url}")

    # 1. Load metadata payload
    metadata_path = Path(args.metadata)
    if not metadata_path.exists():
        print(f"ERROR: Metadata payload not found at {metadata_path}", file=sys.stderr)
        sys.exit(1)

    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_payload = json.load(f)

    # 2. Lock SHA-256 Checksums
    target_dir = Path(args.dir)
    pdf_files = sorted(list(target_dir.glob("*.pdf")))
    checksum_file = target_dir / "checksums.sha256"

    print(f"\n[Checksum Stage]: Hashing {len(pdf_files)} PDF artifact(s)...")
    checksum_lines = []
    for pdf in pdf_files:
        digest = compute_sha256(pdf)
        checksum_lines.append(f"{digest}  {pdf.name}")
        print(f"  {digest[:16]}...  {pdf.name}")

    with open(checksum_file, "w", encoding="utf-8") as f:
        f.write("\n".join(checksum_lines) + "\n")
    print(f"Locked checksum manifest to: {checksum_file}")

    # 3. Create Deposition Draft
    print("\n[API Stage]: Creating initial deposition draft...")
    create_url = f"{base_url}?access_token={token}"
    headers = {"Content-Type": "application/json"}
    deposit_resp = api_request(create_url, method="POST", data=json.dumps(metadata_payload).encode("utf-8"), headers=headers)

    deposit_id = deposit_resp["id"]
    bucket_url = deposit_resp["links"]["bucket"]
    print(f"Draft Created Successfully.")
    print(f"  Deposition ID: {deposit_id}")
    print(f"  Storage Bucket: {bucket_url}")

    # 4. Upload Files
    print("\n[Upload Stage]: Uploading PDF artifacts and checksum manifest...")
    for pdf in pdf_files:
        upload_file_to_bucket(bucket_url, pdf, token)
    if checksum_file.exists():
        upload_file_to_bucket(bucket_url, checksum_file, token)

    # 5. Review or Publish
    draft_url = f"https://sandbox.zenodo.org/deposit/{deposit_id}" if args.sandbox else f"https://zenodo.org/deposit/{deposit_id}"
    print("\n================================================================================")
    print("DEPOSITION STAGED & READY FOR VERIFICATION")
    print(f"Review Draft at: {draft_url}")
    print("================================================================================")

    if args.publish:
        print("[Publishing]: Minting permanent, immutable DOI...")
        publish_url = f"{base_url}/{deposit_id}/actions/publish?access_token={token}"
        pub_resp = api_request(publish_url, method="POST")
        doi = pub_resp.get("doi")
        record_url = pub_resp["links"].get("record_html")
        print(f"\nSUCCESS! PERMANENT DOI MINTED:")
        print(f"  DOI:        {doi}")
        print(f"  Public URL: {record_url}")
    else:
        print("Deposition saved as draft. Review in the web UI, or pass --publish to mint the DOI.")


if __name__ == "__main__":
    main()
