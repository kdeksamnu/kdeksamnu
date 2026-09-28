from fastapi import FastAPI, Request
import time
from engine.api.routes import observers, spectral, chain, factions, cathedral

app = FastAPI(
    title="MLAOS-Prime Ash Archive Engine",
    version="1.0.0"
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.4f}"
    return response


app.include_router(observers.router, prefix="/api/v1", tags=["Observers"])
app.include_router(spectral.router)
app.include_router(chain.router)
app.include_router(factions.router)
app.include_router(cathedral.router)

@app.get("/health")
def health_check():
    return {"status": "resonant", "substrate": "Ash Archive active"}

@app.get("/visuals")
def visuals_status():
    return {"visualizer": "Three.js voxel rendering pipeline online"}

@app.get("/spatial/extract")
def spatial_extract(resolution: int = 64):
    from engine.spatial.extractor import SpatialExtractor
    ext = SpatialExtractor(resolution=resolution)
    return ext.extract_stratum()
