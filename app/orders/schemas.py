from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(gt=0)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total: Decimal
    status: str

    model_config = {"from_attributes": True}
