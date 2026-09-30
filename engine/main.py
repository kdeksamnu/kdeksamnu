from fastapi import FastAPI
from engine.api.routes import observers

app = FastAPI(
    title="MLAOS-Prime Ash Archive Engine",
    version="1.0.0"
)

app.include_router(observers.router, prefix="/api/v1", tags=["Observers"])

@app.get("/health")
def health_check():
    return {"status": "operational", "substrate": "Ash Archive active"}

@app.get("/visuals")
def visuals_status():
    return {"visualizer": "Three.js voxel rendering pipeline online"}

@app.get("/spatial/extract")
def spatial_extract(resolution: int = 64):
    from engine.spatial.extractor import SpatialExtractor
    ext = SpatialExtractor(resolution=resolution)
    return ext.extract_stratum()
