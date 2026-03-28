"""Unit tests for the pure allocation algorithm."""

from app.optimizer import allocate


def test_normal_allocation():
    """Standard case: cargos fit into tanks with some splitting."""
    cargos = [
        {"id": "C1", "volume": 500},
        {"id": "C2", "volume": 300},
    ]
    tanks = [
        {"id": "T1", "capacity": 400},
        {"id": "T2", "capacity": 400},
    ]
    result = allocate(cargos, tanks)

    allocs = result["tank_allocations"]
    loaded = result["cargo_loaded"]

    # C1 (500) is larger → processed first.
    # T1 (400) gets 400 of C1, T2 (400) gets remaining 100 of C1.
    # But T2 holds only one cargo ID, so C2 cannot share T2.
    # Actually: T1 fills 400 from C1, T2 fills remaining 100 from C1 → T2 used.
    # C2 has no tank left → only 500 loaded out of 800.

    # Wait — each tank holds only ONE cargo ID, so T2 takes the rest of C1 (100),
    # leaving no tank for C2.
    assert loaded["C1"] == 500
    assert loaded["C2"] == 0

    total = sum(a["allocated_volume"] for a in allocs)
    assert total == 500


def test_cargo_split_across_tanks():
    """A single cargo larger than any individual tank must split."""
    cargos = [{"id": "C1", "volume": 1000}]
    tanks = [
        {"id": "T1", "capacity": 600},
        {"id": "T2", "capacity": 500},
    ]
    result = allocate(cargos, tanks)
    allocs = result["tank_allocations"]

    # C1 should split: 600 into T1, 400 into T2.
    assert allocs[0]["allocated_volume"] == 600
    assert allocs[1]["allocated_volume"] == 400
    assert result["cargo_loaded"]["C1"] == 1000


def test_more_cargo_than_capacity():
    """Total cargo exceeds total tank capacity → partial load."""
    cargos = [
        {"id": "C1", "volume": 800},
        {"id": "C2", "volume": 700},
    ]
    tanks = [{"id": "T1", "capacity": 500}]
    result = allocate(cargos, tanks)

    # Only 500 can be loaded (all into C1 since it's largest).
    assert result["cargo_loaded"]["C1"] == 500
    assert result["cargo_loaded"]["C2"] == 0
    total = sum(a["allocated_volume"] for a in result["tank_allocations"])
    assert total == 500


def test_empty_cargos():
    """No cargos provided — tanks should all be empty."""
    result = allocate([], [{"id": "T1", "capacity": 500}])
    assert result["tank_allocations"][0]["allocated_volume"] == 0
    assert result["tank_allocations"][0]["cargo_id"] is None


def test_empty_tanks():
    """No tanks provided — nothing can be loaded."""
    result = allocate([{"id": "C1", "volume": 500}], [])
    assert result["tank_allocations"] == []
    assert result["cargo_loaded"]["C1"] == 0


def test_exact_fit():
    """Cargo volume exactly matches tank capacity."""
    cargos = [{"id": "C1", "volume": 500}]
    tanks = [{"id": "T1", "capacity": 500}]
    result = allocate(cargos, tanks)

    assert result["cargo_loaded"]["C1"] == 500
    assert result["tank_allocations"][0]["allocated_volume"] == 500


def test_assignment_data():
    """Run the exact dataset from the ShipIQ assessment PDF."""
    cargos = [
        {"id": "C1", "volume": 1234},
        {"id": "C2", "volume": 4352},
        {"id": "C3", "volume": 3321},
        {"id": "C4", "volume": 2456},
        {"id": "C5", "volume": 5123},
        {"id": "C6", "volume": 1879},
        {"id": "C7", "volume": 4987},
        {"id": "C8", "volume": 2050},
        {"id": "C9", "volume": 3678},
        {"id": "C10", "volume": 5432},
    ]
    tanks = [
        {"id": "T1", "capacity": 1234},
        {"id": "T2", "capacity": 4352},
        {"id": "T3", "capacity": 3321},
        {"id": "T4", "capacity": 2456},
        {"id": "T5", "capacity": 5123},
        {"id": "T6", "capacity": 1879},
        {"id": "T7", "capacity": 4987},
        {"id": "T8", "capacity": 2050},
        {"id": "T9", "capacity": 3678},
        {"id": "T10", "capacity": 5432},
    ]
    result = allocate(cargos, tanks)

    total_cargo = sum(c["volume"] for c in cargos)
    total_capacity = sum(t["capacity"] for t in tanks)
    total_loaded = sum(a["allocated_volume"] for a in result["tank_allocations"])

    # Cargo volume == tank capacity, so everything should load.
    assert total_cargo == total_capacity
    assert total_loaded == total_capacity
