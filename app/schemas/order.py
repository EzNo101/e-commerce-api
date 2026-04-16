from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.models.order import OrderStatus, PaymentStatus


class CheckoutRequest(BaseModel):
    payment_method: str | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_time: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    order_number: str
    user_id: int
    order_status: OrderStatus
    payment_status: PaymentStatus
    total_amount: int
    currency: str = Field(min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    stripe_payment_intent_id: str | None = None
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    order_status: OrderStatus | None = None
    payment_status: PaymentStatus | None = None

    model_config = ConfigDict(extra="forbid")


class CheckoutResponse(BaseModel):
    order: OrderResponse
    client_secret: str

    model_config = ConfigDict(from_attributes=True)
