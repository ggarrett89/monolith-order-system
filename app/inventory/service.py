from sqlalchemy.orm import Session

from app.inventory.models import Inventory
from app.inventory.schemas import InventoryCreate


def create_inventory(db: Session, data: InventoryCreate) -> Inventory:
    inventory = Inventory(product_id=data.product_id, quantity=data.quantity)
    db.add(inventory)
    db.commit()
    db.refresh(inventory)
    return inventory


def get_inventory_by_product(db: Session, product_id: int) -> Inventory | None:
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def list_inventory(db: Session) -> list[Inventory]:
    return db.query(Inventory).all()


def reserve_stock(db: Session, product_id: int, quantity: int) -> Inventory:
    """Decrease stock by quantity. Raises ValueError if insufficient stock.

    Called by the orders service during order creation.
    This is the coupling point we will eliminate when we extract
    ms-inventory and ms-orders into separate services.
    """
    inventory = get_inventory_by_product(db, product_id)

    if not inventory:
        raise ValueError(f"No inventory record found for product_id={product_id}")

    if inventory.quantity < quantity:
        raise ValueError(
            f"Insufficient stock: requested={quantity}, available={inventory.quantity}"
        )

    inventory.quantity -= quantity
    db.commit()
    db.refresh(inventory)
    return inventory


def release_stock(db: Session, product_id: int, quantity: int) -> Inventory:
    """Increase stock by quantity (used on order cancellation)."""
    inventory = get_inventory_by_product(db, product_id)

    if not inventory:
        raise ValueError(f"No inventory record found for product_id={product_id}")

    inventory.quantity += quantity
    db.commit()
    db.refresh(inventory)
    return inventory
