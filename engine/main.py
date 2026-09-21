from fastapi import FastAPI
from engine.api.routes import spectral, observers, chain, factions, cathedral

app = FastAPI(
    title="MLAOS-PRIME // Engine",
    description="The mythotechnical execution layer. Commercialized via Dallmier Tech Venture.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(spectral.router)
app.include_router(observers.router)
app.include_router(chain.router)
app.include_router(factions.router)
app.include_router(cathedral.router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "resonant", "system": "mlaos-prime"}

from fastapi.responses import FileResponse

@app.get("/visuals", tags=["Visual Echo"])
async def visual_echo():
    """Serves the Three.js Somatic Observer Visualizer."""
    return FileResponse("visualizer.html")
