"""
Pure cargo-to-tank allocation algorithm. No FastAPI imports here.

Algorithm: Greedy allocation with cargo splitting.

Why greedy works optimally here:
    When cargo splitting is allowed, every unit of volume is interchangeable —
    there's no "fit" constraint that forces awkward packing. This means we can
    simply pour cargo into tanks until either all cargo is loaded or all tanks
    are full. The problem reduces to: min(total_cargo, total_capacity) will
    always be loaded regardless of assignment order.

    We still sort cargos descending (largest first) and tanks descending
    (largest first) so that the allocation is clean — large cargos fill large
    tanks first, producing fewer splits and a more intuitive result. But the
    total volume loaded is the same for any valid greedy order.

    This is fundamentally different from classic bin-packing (NP-hard) because
    bin-packing forbids splitting — an item must go into exactly one bin.
    Allowing splits removes that combinatorial constraint entirely.
"""


def allocate(
    cargos: list[dict], tanks: list[dict]
) -> dict:
    """
    Allocate cargos into tanks using a greedy approach.

    Args:
        cargos: [{"id": str, "volume": float}, ...]
        tanks:  [{"id": str, "capacity": float}, ...]

    Returns:
        {
          "tank_allocations": [{"tank_id", "cargo_id", "allocated_volume"}, ...],
          "cargo_loaded": {"cargo_id": loaded_volume, ...}
        }
    """
    # Sort both lists descending so large items meet large containers first.
    sorted_cargos = sorted(cargos, key=lambda c: c["volume"], reverse=True)
    sorted_tanks = sorted(tanks, key=lambda t: t["capacity"], reverse=True)

    # Track how much of each cargo remains to be loaded.
    remaining = {c["id"]: c["volume"] for c in sorted_cargos}

    # Build an ordered queue of cargo IDs to process.
    cargo_queue = [c["id"] for c in sorted_cargos]

    tank_allocations: list[dict] = []
    cargo_idx = 0  # pointer into cargo_queue

    for tank in sorted_tanks:
        cap = tank["capacity"]

        # Skip to the next cargo that still has remaining volume.
        while cargo_idx < len(cargo_queue) and remaining[cargo_queue[cargo_idx]] <= 0:
            cargo_idx += 1

        if cargo_idx >= len(cargo_queue):
            # No more cargo to load — tank stays empty.
            tank_allocations.append(
                {"tank_id": tank["id"], "cargo_id": None, "allocated_volume": 0.0}
            )
            continue

        cid = cargo_queue[cargo_idx]
        fill = min(cap, remaining[cid])
        remaining[cid] -= fill

        tank_allocations.append(
            {"tank_id": tank["id"], "cargo_id": cid, "allocated_volume": fill}
        )

    # Compute how much of each cargo was actually loaded.
    cargo_loaded: dict[str, float] = {}
    for c in cargos:
        original = c["volume"]
        cargo_loaded[c["id"]] = round(original - remaining[c["id"]], 4)

    return {
        "tank_allocations": tank_allocations,
        "cargo_loaded": cargo_loaded,
    }
