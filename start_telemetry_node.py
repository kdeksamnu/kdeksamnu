import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print("CATHEDRAL-ENGINE // SPECTRAL TELEMETRY FASTAPI NODE")
    print("=" * 65)
    print("Initializing Uvicorn server on http://127.0.0.1:8000 ...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
