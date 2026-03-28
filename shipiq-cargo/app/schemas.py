"""Pydantic models for request validation and response serialization."""

# BaseModel is the core Pydantic class — FastAPI uses it to auto-validate
# incoming JSON and serialize outgoing responses.
from pydantic import BaseModel


# ── Request Models ──────────────────────────────────────────────

class CargoItem(BaseModel):
    id: str
    volume: float


class TankItem(BaseModel):
    id: str
    capacity: float


class InputPayload(BaseModel):
    cargos: list[CargoItem]
    tanks: list[TankItem]


# ── Response Models ─────────────────────────────────────────────

class TankAllocation(BaseModel):
    tank_id: str
    cargo_id: str | None
    allocated_volume: float
    utilization_pct: float


class CargoSummary(BaseModel):
    cargo_id: str
    total_volume: float
    loaded_volume: float
    fully_loaded: bool


class OptimizationSummary(BaseModel):
    total_loaded_volume: float
    total_capacity: float
    overall_efficiency_pct: float


class OptimizationResult(BaseModel):
    tank_allocations: list[TankAllocation]
    cargo_summaries: list[CargoSummary]
    summary: OptimizationSummary
