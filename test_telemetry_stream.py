import urllib.request
import json

def test_health_and_docs():
    print("=" * 65)
    print("CATHEDRAL-ENGINE // TELEMETRY ENDPOINT VERIFICATION")
    print("=" * 65)
    
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/docs", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            print(f"[OK] FastAPI /docs Endpoint Responded with HTTP Status: {status}")
    except Exception as e:
        print(f"[ERROR] Failed to reach FastAPI endpoint: {e}")

if __name__ == "__main__":
    test_health_and_docs()
