from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.inventory import service
from app.inventory.schemas import InventoryCreate, InventoryResponse, InventoryUpdate

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db)):
    return service.create_inventory(db, data)


@router.get("", response_model=list[InventoryResponse])
def list_inventory(db: Session = Depends(get_db)):
    return service.list_inventory(db)


@router.get("/{product_id}", response_model=InventoryResponse)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    inventory = service.get_inventory_by_product(db, product_id)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory record for product_id={product_id}",
        )
    return inventory


@router.patch("/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    inventory = service.get_inventory_by_product(db, product_id)
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No inventory record for product_id={product_id}",
        )
    inventory.quantity = data.quantity
    db.commit()
    db.refresh(inventory)
    return inventory
