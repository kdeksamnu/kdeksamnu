#!/usr/bin/env python3
import json
import math
import hashlib
import time
from typing import Optional
from pydantic import BaseModel

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

if HAS_FASTAPI:
    app = FastAPI(title="Cathedral Asset Bridge")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class AssetRequest(BaseModel):
        prompt: str
        spectral_dominant: Optional[str] = "Teal/Curiosity"
        triz_limit_budget: Optional[float] = 0.28
        output_format: Optional[str] = "gaussian_splat_ply"
        splat_count: Optional[int] = 512

    class LedgerState:
        def __init__(self):
            self.merkle_root = "0x79935386C053F1A8"
            self.block_height = 835

    state = LedgerState()

    COLOR_MAP = {
        "Gold/Joy": [0.85, 0.68, 0.22],
        "Teal/Curiosity": [0.12, 0.52, 0.54],
        "Blue/Sorrow": [0.08, 0.18, 0.36],
        "Obsidian/Null": [0.04, 0.04, 0.06]
    }

    @app.post("/api/v1/assets/synthesize")
    def synthesize(req: AssetRequest):
        base_col = COLOR_MAP.get(req.spectral_dominant, [0.12, 0.52, 0.54])
        count = min(req.splat_count, 1024)
        
        splats = []
        for i in range(count):
            u = (i % 32) / 32.0 * math.pi * 2.0
            v = (i // 32) / 16.0 * math.pi
            r = 1.2 + 0.35 * math.sin(u * 4.0)
            x = r * math.sin(v) * math.cos(u)
            y = r * math.cos(v) + 2.0
            z = r * math.sin(v) * math.sin(u)
            splats.append({
                "pos": [round(x, 4), round(y, 4), round(z, 4)],
                "rgb": base_col,
                "alpha": 0.88,
                "scar_cost": req.triz_limit_budget
            })

        state.block_height += 1
        raw_seed = state.merkle_root + req.prompt + str(time.time())
        new_hash = "0x" + hashlib.sha256(raw_seed.encode()).hexdigest()[:16].upper()
        state.merkle_root = new_hash

        return {
            "status": "SYNTHESIZED",
            "block_hash": new_hash,
            "block_height": state.block_height,
            "spectral_dominant": req.spectral_dominant,
            "triz_scar_cost": req.triz_limit_budget,
            "nodes_added": len(splats),
            "splats": splats
        }

if __name__ == "__main__":
    if HAS_FASTAPI:
        print("Starting FastAPI synthesis endpoint at http://127.0.0.1:8000/api/v1/assets/synthesize")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        print("FastAPI not installed. Run: pip install fastapi uvicorn")
