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
