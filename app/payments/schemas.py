from decimal import Decimal

from pydantic import BaseModel


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    status: str
    reason: str | None

    model_config = {"from_attributes": True}
