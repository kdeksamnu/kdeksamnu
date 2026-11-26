from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="MLAOS Cathedral Core - Option B", version="1.0.0")

class RichErrorResponse(BaseModel):
    error: str = Field(..., description="Machine-readable error category code.")
    message: str = Field(..., description="Human-readable safe error message.")
    fields: dict | list | None = Field(None, description="Optional validation details or field errors.")

@app.exception_handler(StarletteHTTPException)
async def rich_http_exception_handler(request: Request, exc: StarletteHTTPException):
    error_code_map = {
        400: "bad_request",
        401: "unauthenticated",
        403: "forbidden",
        404: "resource_not_found",
        409: "conflict_state"
    }
    code = error_code_map.get(exc.status_code, "http_error")
    return JSONResponse(
        status_code=exc.status_code,
        content=RichErrorResponse(
            error=code,
            message=str(exc.detail),
            fields=None
        ).model_dump()
    )

@app.exception_handler(RequestValidationError)
async def rich_validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=RichErrorResponse(
            error="validation_error",
            message="Request parameters failed schema validation checks.",
            fields=exc.errors()
        ).model_dump()
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "error_envelope": "option_b"}

@app.post("/old-man/confirm-move")
async def confirm_move_guarded(session_id: str, current_user_id: str = "user_sigma_7"):
    # Simulated non-enumerating IDOR tenancy guard
    owner_registry = {"session_sigma_01": "user_sigma_7"}
    owner = owner_registry.get(session_id)
    
    if not owner or owner != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or unauthorized access."
        )
    return {"success": True, "session_id": session_id}
