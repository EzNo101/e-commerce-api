from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)

    model_config = ConfigDict(extra="forbid")


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)

    model_config = ConfigDict(extra="forbid")


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_time: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total: Decimal
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
