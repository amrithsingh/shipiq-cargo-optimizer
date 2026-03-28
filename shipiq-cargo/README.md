# ShipIQ Cargo Optimization Service

A production-ready REST API that optimizes cargo loading into vessel tanks for maritime logistics.

## Problem

Given a set of **cargos** (each with a volume) and **tanks** (each with a capacity):
- **Maximize** total loaded cargo volume
- A cargo **may be split** across multiple tanks
- Each tank holds cargo from **only one** cargo ID

## Algorithm: Greedy Allocation

Since cargo splitting is allowed, every unit of cargo volume is interchangeable — there is no "fit" constraint. This means the problem reduces to simply filling tanks until we run out of cargo or capacity. The maximum loadable volume is always `min(total_cargo, total_capacity)`, regardless of order.

We sort cargos descending by volume and tanks descending by capacity, then greedily assign each cargo to the next available tank. This produces fewer splits and a more readable allocation, though the total loaded volume would be the same for any valid order.

**Why this isn't NP-hard:** Classic bin-packing is NP-hard because items cannot be split — you must decide which bin each whole item goes into. Allowing splits removes that combinatorial constraint entirely, making a simple greedy pass optimal in O(n log n) time (dominated by sorting).

### Trade-offs
- **Greedy vs. LP solver:** A linear programming solver would give the same optimal result here but adds dependency complexity. Greedy is simpler, faster, and equally optimal for this constraint set.
- **In-memory state:** No database — state lives in a module-level dict. Fine for a single-instance service; would need a shared store (Redis, DB) for multi-instance deployments.
- **One cargo per tank:** The constraint that each tank holds only one cargo ID means some tank capacity may go unused even if other cargos could fill it.

### Assumptions
- Cargo and tank IDs are unique within each input
- Volumes and capacities are positive numbers
- Input data is replaced entirely on each POST /input call

## API Endpoints

| Method | Path        | Description                         |
|--------|-------------|-------------------------------------|
| POST   | `/input`    | Submit cargo and tank data          |
| POST   | `/optimize` | Run allocation on submitted input   |
| GET    | `/results`  | Retrieve the last optimization result |
| GET    | `/`         | Health check                        |
| GET    | `/docs`     | Interactive Swagger UI (auto-generated) |

## Quick Start

### Without Docker

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

### With Docker

```bash
docker compose up --build
```

API: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

## Example Usage

```bash
# Submit input
curl -X POST http://localhost:8000/input \
  -H "Content-Type: application/json" \
  -d '{
    "cargos": [{"id":"C1","volume":5000},{"id":"C2","volume":3000}],
    "tanks":  [{"id":"T1","capacity":4000},{"id":"T2","capacity":3000}]
  }'

# Run optimization
curl -X POST http://localhost:8000/optimize

# Get results
curl http://localhost:8000/results
```

## Running Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Project Structure

```
shipiq-cargo/
├── app/
│   ├── main.py         # App entry point, mounts router
│   ├── router.py       # Route definitions
│   ├── service.py      # Orchestration layer
│   ├── optimizer.py    # Pure allocation algorithm
│   └── schemas.py      # Pydantic request/response models
├── tests/
│   ├── test_optimizer.py   # Unit tests for core logic
│   └── test_api.py         # Integration tests
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── DEPLOYMENT.md
└── README.md
```

## UI (Optional Frontend)

A minimal React app lives in the sibling `ui/` folder.

```bash
cd ui
npm install
npm run dev
```

Opens at `http://localhost:5173`. Requires the backend running on `http://localhost:8000`.
CORS is already enabled on the backend.

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions (AWS EC2, Railway, Render).
