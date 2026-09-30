import os
import json
import hashlib
import requests

ZENODO_API_URL = "https://zenodo.org/api/deposit/depositions"
ACCESS_TOKEN = os.getenv("ZENODO_ACCESS_TOKEN", "DUMMY_TOKEN_FOR_LOCAL_STAGING")

def generate_checksum(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def package_codex_specs():
    print("[Zenodo Inscription] Packaging 40-Book Codex master specifications...")
    os.makedirs("build/zenodo", exist_ok=True)
    
    manifest = {
        "repository": "kdeksamnu/kdeksamnu",
        "archive_stratum": "Ash-Archive-Master",
        "status": "synchronized"
    }
    
    manifest_path = "build/zenodo/manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        
    checksum = generate_checksum(manifest_path)
    print(f"[Zenodo Inscription] Manifest generated. SHA-256: {checksum}")

if __name__ == "__main__":
    package_codex_specs()
