from sqlalchemy import Column, Integer, ForeignKey

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    # References products.id but no ORM relationship — intentional.
    # When we extract this into ms-inventory, this FK will become
    # a cross-service reference resolved via API call, not a JOIN.
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
