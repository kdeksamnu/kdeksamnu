import urllib.request
import json

endpoints = [
    "http://127.0.0.1:8000/health",
    "http://127.0.0.1:8000/api/v1/ash/merkle/root",
    "http://127.0.0.1:8000/api/v1/ash/query/temporal"
]

print("=" * 65)
print("CATHEDRAL-ENGINE // HEADLESS TELEMETRY ENDPOINT PROBE")
print("=" * 65)

for ep in endpoints:
    try:
        req = urllib.request.Request(ep, headers={"User-Agent": "CathedralAuditor/1.0"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            print(f"[OK] {ep} -> Status {res.status}")
            print(f"     Payload: {json.dumps(data)[:80]}...")
    except Exception as e:
        print(f"[ERROR] {ep} -> Failed: {e}")

print("=" * 65)
