# monolith-order-system

Phase 1 of the **monolith → microservices** learning journey.

A **modular monolith** built with FastAPI + PostgreSQL. Each business domain
(users, products, inventory, orders, payments) is isolated in its own package
with its own models, schemas, service layer, and router — but they all share
one process and one database.

This is the intentional starting point. The coupling between domains is visible
and documented so we have concrete reasons to split it later.

---

## Architecture

```
monolith-order-system/
├── app/
│   ├── users/          # User management
│   ├── products/       # Product catalogue
│   ├── inventory/      # Stock levels (separate from products)
│   ├── orders/         # Order lifecycle + compensating transactions
│   ├── payments/       # Simulated payment gateway
│   ├── database.py     # Shared SQLAlchemy engine + Base
│   └── main.py         # FastAPI app — wires all routers
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Request flow for `POST /orders`

```
POST /orders
    │
    ├── 1. validate user exists         (users domain)
    ├── 2. validate product exists      (products domain)
    ├── 3. reserve_stock()              (inventory domain)
    ├── 4. process_payment()            (payments domain)
    │       └── if REJECTED → release_stock()  ← compensating tx
    └── 5. persist Order (status=CONFIRMED)
```

This synchronous coupling across domains is exactly what we will eliminate
when we move to microservices + Kafka + Saga pattern.

---

## Deliberate architectural problems (learning points)

| Problem | Where | Future solution |
|---|---|---|
| All domains share one DB | `app/database.py` | One DB per service |
| Orders directly calls inventory | `orders/service.py` | Async event (Kafka) |
| Orders directly calls payments | `orders/service.py` | Saga orchestration |
| Cannot deploy domains independently | `app/main.py` | Separate services |
| Cannot scale inventory without scaling everything | `docker-compose.yml` | K8s HPA per service |

---

## Quickstart

### Prerequisites

- Docker + Docker Compose

### Run

```bash
docker compose up --build
```

The app starts at [http://localhost:8000](http://localhost:8000)
Interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

### Stop

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

---

## Local development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env if your local PostgreSQL uses different credentials

uvicorn app.main:app --reload
```

---

## API reference

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/` | App info |
| GET | `/health` | Health check |

### Users

| Method | Path | Description |
|---|---|---|
| POST | `/users` | Create user |
| GET | `/users` | List users |
| GET | `/users/{id}` | Get user |

### Products

| Method | Path | Description |
|---|---|---|
| POST | `/products` | Create product |
| GET | `/products` | List products |
| GET | `/products/{id}` | Get product |

### Inventory

| Method | Path | Description |
|---|---|---|
| POST | `/inventory` | Create inventory record for a product |
| GET | `/inventory` | List all inventory |
| GET | `/inventory/{product_id}` | Get stock for a product |
| PATCH | `/inventory/{product_id}` | Update stock quantity |

### Orders

| Method | Path | Description |
|---|---|---|
| POST | `/orders` | Create order (reserves stock + processes payment) |
| GET | `/orders` | List orders |
| GET | `/orders/{id}` | Get order |
| POST | `/orders/{id}/cancel` | Cancel order (releases stock) |

### Payments

| Method | Path | Description |
|---|---|---|
| GET | `/payments` | List all payments |
| GET | `/payments/{id}` | Get payment |
| GET | `/payments/user/{user_id}` | List payments for a user |

---

## Sample walkthrough

```bash
# 1. Create a user
curl -s -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}' | jq

# 2. Create a product
curl -s -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Kubernetes Course", "price": 99.90}' | jq

# 3. Create an inventory record for the product
curl -s -X POST http://localhost:8000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 20}' | jq

# 4. Place an order
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 1, "quantity": 2}' | jq

# 5. Check inventory was decremented
curl -s http://localhost:8000/inventory/1 | jq

# 6. Check payment was recorded
curl -s http://localhost:8000/payments/user/1 | jq
```

> The payment gateway has a **10% simulated failure rate**. If an order returns
> `400 Payment rejected`, the stock will have been automatically released.
> Retry the order to confirm this behaviour.

---

## Roadmap

```
Phase 1  ✅  Modular Monolith          ← you are here
Phase 2      Kubernetes deployment
Phase 3      Extract ms-orders + REST communication
Phase 4      Extract ms-inventory + ms-payments
Phase 5      Kafka — event-driven communication
Phase 6      Saga pattern
Phase 7      Observability (Prometheus + Grafana + Jaeger)
Phase 8      Argo CD + Argo Rollouts
Phase 9      AWS EKS
```

---

## Repository map

| Repository | Description |
|---|---|
| `monolith-order-system` | This repo — Phase 1 |
| `ms-orders` | Orders microservice (Phase 3+) |
| `ms-inventory` | Inventory microservice (Phase 4+) |
| `ms-payments` | Payments microservice (Phase 4+) |
| `ms-users` | Users microservice (Phase 4+) |
| `gitops-k8s` | Argo CD manifests for all services |
| `infrastructure-lab` | Terraform + cluster configs |
