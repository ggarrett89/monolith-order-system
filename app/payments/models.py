from sqlalchemy import Column, Integer, Numeric, String, ForeignKey

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    # Cross-domain reference by ID only — no ORM relationship.
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    # APPROVED | REJECTED
    status = Column(String, nullable=False)
    # Free-text reason — useful for debugging failures in the monolith
    # and will become a structured event payload later in the Kafka phase.
    reason = Column(String, nullable=True)
