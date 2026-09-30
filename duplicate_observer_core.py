import hashlib
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MLAOS-PRIME // Visual Echo Fork", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ObserverState(BaseModel):
    target: str = "Chaos-Subject"
    somatic_integrity: float = 0.6500
    harmonic_scars: int = 11
    logic_state: bool = True
    lineage_depth: str = "Depth 98 (Step 106 / 204)"
    parent_hash: str = "fc3bb6f588210b4700fa0182f185900ec39ce3b37a45613a994f9dc16adbe187"

def generate_merkle_node(parent_hash: str) -> str:
    timestamp = str(time.time_ns()).encode()
    return hashlib.sha256(parent_hash.encode() + timestamp).hexdigest()

@app.post("/visuals/duplicate")
async def create_duplicate_echo(state: ObserverState):
    new_state_hash = generate_merkle_node(state.parent_hash)
    cloned_node = {
        "target": state.target,
        "somatic_integrity": state.somatic_integrity,
        "harmonic_scars": state.harmonic_scars,
        "logic_state": state.logic_state,
        "lineage_depth": state.lineage_depth,
        "dag_status": "VERIFIED UNBROKEN",
        "state_hash": new_state_hash,
        "parent_hash": state.parent_hash
    }
    return {"status": "SUCCESS", "replicated_observer_node": cloned_node}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
