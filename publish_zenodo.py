<<<<<<< HEAD
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
    
    # Simulate freezing master exports
    manifest = {
        "title": "Omni-Codex Ω & Cathedral-Engine: Paraconsistent Systems Architecture and Isomorphic Worldbuilding",
        "creators": [{"name": "Dallmier, Kenneth Wayne"}],
        "description": "Master architecture documentation and technical monographs for MLAOS-Prime and the Cathedral-Engine.",
        "upload_type": "publication",
        "publication_type": "section"
    }
    
    manifest_path = "build/zenodo/metadata.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"[Zenodo Inscription] Metadata staged at {manifest_path}. Ready for API transmission.")

if __name__ == "__main__":
    package_codex_specs()
=======
import json
import os

metadata = {
    "title": "MLAOS-Prime Cathedral Engine: Ash Archive Telemetry & Spectral State Ledger",
    "upload_type": "dataset",
    "description": "Exhaustive thermodynamic and mythotechnical telemetry logs from the MLAOS-Prime Cathedral Engine substrate.",
    "creators": [{"name": "Dallmier, Kenneth Wayne"}],
    "access_right": "open"
}

os.makedirs("dist", exist_ok=True)
with open("dist/metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("[+] Zenodo publication metadata successfully packaged in dist/metadata.json.")
>>>>>>> 8840e034f771ea0df4cd7dd3a804c61f34db7c1c
