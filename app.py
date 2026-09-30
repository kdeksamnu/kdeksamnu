from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, field_validator
import re

app = FastAPI()

class SecurityError(Exception):
    """Custom exception for security verification failures."""
    pass

class BaseTaskPayload(BaseModel):
    pass

class PaymentTaskData(BaseTaskPayload):
    deduplication_key: str = Field(..., min_length=16, max_length=128)
    task_id: str = Field(..., min_length=16, max_length=64, pattern=r"^[a-zA-Z0-9_\-]+$")

    @field_validator("task_id")
    @classmethod
    def verify_control_tokens(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_\-]+$", v):
            raise SecurityError(f"Control token violation detected in task_id: {v}")
        return v

@app.post("/api/v1/payments/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_payment_task(payload: PaymentTaskData):
    try:
        return {
            "status": "crystallized",
            "task_id": payload.task_id,
            "deduplication_key": payload.deduplication_key
        }
    except SecurityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
