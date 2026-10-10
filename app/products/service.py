from sqlalchemy.orm import Session

from app.products.models import Product
from app.products.schemas import ProductCreate


def create_product(db: Session, data: ProductCreate) -> Product:
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def list_products(db: Session) -> list[Product]:
    return db.query(Product).all()
