"""
Service layer — orchestrates the optimizer and builds structured responses.

This sits between the router (HTTP layer) and the optimizer (pure logic),
keeping each layer focused on a single responsibility.
"""

from app.optimizer import allocate
from app.schemas import (
    CargoSummary,
    InputPayload,
    OptimizationResult,
    OptimizationSummary,
    TankAllocation,
)


# ── In-memory state (no database needed) ────────────────────────
_state: dict = {
    "input": None,   # last submitted InputPayload
    "result": None,   # last computed OptimizationResult
}


def store_input(payload: InputPayload) -> None:
    _state["input"] = payload
    _state["result"] = None  # clear stale results when new input arrives


def get_stored_input() -> InputPayload | None:
    return _state["input"]


def get_stored_result() -> OptimizationResult | None:
    return _state["result"]


def run_optimization() -> OptimizationResult:
    """Run the greedy optimizer on the last submitted input and cache the result."""
    payload = _state["input"]

    # Convert Pydantic models to plain dicts for the optimizer.
    cargos = [{"id": c.id, "volume": c.volume} for c in payload.cargos]
    tanks = [{"id": t.id, "capacity": t.capacity} for t in payload.tanks]

    raw = allocate(cargos, tanks)

    # ── Build per-tank response ──
    total_capacity = sum(t.capacity for t in payload.tanks)

    tank_allocs = []
    for ta in raw["tank_allocations"]:
        # Find the original tank capacity for utilization calculation.
        orig_cap = next(t.capacity for t in payload.tanks if t.id == ta["tank_id"])
        util = (ta["allocated_volume"] / orig_cap * 100) if orig_cap > 0 else 0.0
        tank_allocs.append(
            TankAllocation(
                tank_id=ta["tank_id"],
                cargo_id=ta["cargo_id"],
                allocated_volume=round(ta["allocated_volume"], 2),
                utilization_pct=round(util, 2),
            )
        )

    # ── Build per-cargo response ──
    cargo_summaries = []
    for c in payload.cargos:
        loaded = raw["cargo_loaded"].get(c.id, 0.0)
        cargo_summaries.append(
            CargoSummary(
                cargo_id=c.id,
                total_volume=c.volume,
                loaded_volume=round(loaded, 2),
                fully_loaded=abs(loaded - c.volume) < 0.01,
            )
        )

    # ── Build summary ──
    total_loaded = sum(ta.allocated_volume for ta in tank_allocs)
    summary = OptimizationSummary(
        total_loaded_volume=round(total_loaded, 2),
        total_capacity=round(total_capacity, 2),
        overall_efficiency_pct=round(
            (total_loaded / total_capacity * 100) if total_capacity > 0 else 0.0, 2
        ),
    )

    result = OptimizationResult(
        tank_allocations=tank_allocs,
        cargo_summaries=cargo_summaries,
        summary=summary,
    )
    _state["result"] = result
    return result
