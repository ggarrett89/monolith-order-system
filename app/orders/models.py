from sqlalchemy import Column, Integer, Numeric, String, ForeignKey

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    # Cross-domain references by ID only — no ORM relationships.
    # This mirrors what these will look like as separate microservices.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    # CREATED → CONFIRMED → CANCELLED
    status = Column(String, nullable=False, default="CREATED")
