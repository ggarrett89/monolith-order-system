from fastapi import FastAPI

from app.database import Base, engine
from app.inventory.router import router as inventory_router
from app.orders.router import router as orders_router
from app.payments.router import router as payments_router
from app.products.router import router as products_router
from app.users.router import router as users_router

# Import all models so SQLAlchemy registers them with the shared Base
# before create_all() is called. Order matters: parent tables first.
import app.users.models       # noqa: F401
import app.products.models    # noqa: F401
import app.inventory.models   # noqa: F401
import app.orders.models      # noqa: F401
import app.payments.models    # noqa: F401

# Create all tables on startup.
# In production this would be replaced by Alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Order Management System",
    description=(
        "Phase 1 — Modular Monolith. "
        "Domains are separated by directory but share one DB and one process. "
        "This is the starting point for the monolith-to-microservices journey."
    ),
    version="0.1.0",
)

app.include_router(users_router)
app.include_router(products_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(payments_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "application": "order-management-system",
        "version": "0.1.0",
        "architecture": "modular-monolith",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
