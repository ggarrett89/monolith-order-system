from sqlalchemy.orm import Session

from app.inventory import service as inventory_service
from app.orders.models import Order
from app.orders.schemas import OrderCreate
from app.payments import service as payment_service
from app.products import service as product_service
from app.users import service as user_service


def create_order(db: Session, data: OrderCreate) -> Order:
    """Create an order.

    Deliberately synchronous and coupled — this is the "bad monolith"
    behaviour we will later replace with:
      - async events (Kafka)
      - Saga pattern for distributed transactions
      - separate databases per service

    Flow:
        1. Validate user exists
        2. Validate product exists
        3. Reserve stock  ← inventory coupling
        4. Process payment ← payments coupling
        5. Persist order
    """
    # 1. Validate user
    user = user_service.get_user(db, data.user_id)
    if not user:
        raise ValueError(f"User not found: id={data.user_id}")

    # 2. Validate product and calculate total
    product = product_service.get_product(db, data.product_id)
    if not product:
        raise ValueError(f"Product not found: id={data.product_id}")

    total = product.price * data.quantity

    # 3. Reserve stock (raises ValueError if insufficient)
    inventory_service.reserve_stock(db, data.product_id, data.quantity)

    # 4. Process payment (raises ValueError if payment fails)
    # NOTE: if payment fails AFTER stock was reserved we must roll back.
    # This is the distributed-transaction problem we will solve with Saga later.
    try:
        payment_service.process_payment(db, user_id=data.user_id, amount=total)
    except ValueError:
        # Compensating transaction: release the reserved stock
        inventory_service.release_stock(db, data.product_id, data.quantity)
        raise

    # 5. Persist order
    order = Order(
        user_id=data.user_id,
        product_id=data.product_id,
        quantity=data.quantity,
        total=total,
        status="CONFIRMED",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def list_orders(db: Session) -> list[Order]:
    return db.query(Order).all()


def cancel_order(db: Session, order_id: int) -> Order:
    order = get_order(db, order_id)
    if not order:
        raise ValueError(f"Order not found: id={order_id}")

    if order.status == "CANCELLED":
        raise ValueError("Order is already cancelled")

    # Compensating transaction: release stock
    inventory_service.release_stock(db, order.product_id, order.quantity)

    order.status = "CANCELLED"
    db.commit()
    db.refresh(order)
    return order
