"""Route definitions for the Cargo Optimization API."""

# APIRouter groups related endpoints, like a Blueprint in Flask.
from fastapi import APIRouter, HTTPException

from app.schemas import InputPayload, OptimizationResult
from app import service

# `prefix` prepends to all routes in this router; `tags` groups them in the
# auto-generated Swagger docs at /docs.
router = APIRouter(prefix="", tags=["cargo"])


@router.post("/input")  # Maps POST /input to this function.
def submit_input(payload: InputPayload):
    """Accept cargo and tank data for a future optimization run."""
    service.store_input(payload)
    return {
        "status": "ok",
        "cargos_received": len(payload.cargos),
        "tanks_received": len(payload.tanks),
        "cargos": payload.cargos,
        "tanks": payload.tanks,
    }


@router.post("/optimize", response_model=OptimizationResult)
def optimize():
    """Run allocation on the last submitted input."""
    if service.get_stored_input() is None:
        raise HTTPException(
            status_code=400,
            detail="No input data found. Submit cargo/tank data via POST /input first.",
        )
    return service.run_optimization()


@router.get("/results", response_model=OptimizationResult)
def get_results():
    """Return the most recent allocation result."""
    result = service.get_stored_result()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No results available. Run POST /optimize first.",
        )
    return result
