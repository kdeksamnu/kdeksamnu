from fastapi import FastAPI
from engine.api.routes import visuals, spectral

app = FastAPI(title="MLAOS-Prime // Cathedral-Engine Core")

app.include_router(visuals.router)
app.include_router(spectral.router)

@app.get("/")
def read_root():
    return {"status": "resonant", "engine": "MLAOS-Prime"}
