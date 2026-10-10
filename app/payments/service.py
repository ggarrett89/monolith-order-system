import random
from decimal import Decimal

from sqlalchemy.orm import Session

from app.payments.models import Payment


# Failure rate for the simulated payment gateway.
# Set to 0.0 to always approve, 1.0 to always reject.
# Deliberately exposed so we can demo failures easily during the lab.
PAYMENT_FAILURE_RATE = 0.1


def process_payment(db: Session, user_id: int, amount: Decimal) -> Payment:
    """Simulate a payment gateway call.

    In the monolith this is a direct function call sharing the same DB session.
    When we extract ms-payments, this will become an HTTP call (REST phase)
    and then an async event (Kafka phase).

    Raises ValueError if the payment is rejected.
    """
    approved = random.random() >= PAYMENT_FAILURE_RATE

    payment = Payment(
        user_id=user_id,
        amount=amount,
        status="APPROVED" if approved else "REJECTED",
        reason=None if approved else "Simulated gateway rejection",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    if not approved:
        raise ValueError(f"Payment rejected: {payment.reason}")

    return payment


def get_payment(db: Session, payment_id: int) -> Payment | None:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def list_payments(db: Session) -> list[Payment]:
    return db.query(Payment).all()


def list_payments_by_user(db: Session, user_id: int) -> list[Payment]:
    return db.query(Payment).filter(Payment.user_id == user_id).all()
